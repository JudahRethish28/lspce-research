"""
LSPCE Pipeline — Legal Scope and Privacy Compliance Engine
Integrated end-to-end forensic governance pipeline.

Usage:
  python pipeline/lspce_pipeline.py \
    --warrant data/ground_truth/warrant_plan_pairs/warrant_01.json \
    --plan    data/ground_truth/warrant_plan_pairs/plan_01.json

Output:
  evidence_packages/{case_id}/
    ├── raw_logs/               (collected evidence files)
    ├── hash_chain.json         (SHA-256 integrity chain)
    ├── scope_pre_report.json   (Stage 1: pre-collection verdict)
    ├── pii_findings.json       (Stage 3: Presidio detections)
    ├── exposure_report.json    (Stage 4: cross-tenant analysis)
    └── compliance_report.json  (Stage 5: unified final report)
"""
import argparse, json, os, time
from datetime import datetime, timezone
from moto import mock_aws
import boto3


# Import all modules
from modules.scope_validator.scope_validator import (
    validate_scope, reassess_scope_post_collection)
from modules.evidence_collector import collect_evidence
from modules.pii_detector.pii_analyzer import (
    build_analyzer, analyze_file)
from modules.tenant_registry.tenant_registry import (
    TenantRegistry)
from modules.exposure_analyser.exposure_analyser import (
    analyse_exposure)
from modules.compliance_reporter.compliance_reporter import (
    generate_compliance_report)
from pipeline.lspce_pipeline import setup_moto_environment


ANNOTATIONS_PATH = "data/ground_truth/pii_annotations.csv"
OUTPUT_BASE      = "evidence_packages"

@mock_aws
def run_pipeline(warrant_path: str, plan_path: str) -> dict:

    s3 = boto3.client(
        "s3",
        region_name="ap-south-1"
    )

    setup_moto_environment(s3)


    start_total = time.time()

    # Load inputs
    warrant  = json.load(open(warrant_path))
    plan     = json.load(open(plan_path))
    case_id  = (f"{warrant['warrant_id']}_"
    f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
    out_dir  = os.path.join(OUTPUT_BASE, case_id)
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  LSPCE Pipeline — Case: {case_id}")
    print(f"  Warrant tenant: {warrant['tenant_id']}")
    print(f"  Incident type:  {warrant['incident_type']}")
    print(f"{'='*60}")

    # ─────────────────────────────────────────────
    # STAGE 0: Setup mocked environment
    # ─────────────────────────────────────────────
    print("\n[STAGE 0] Setting up mocked S3 environment...")
    setup_moto_environment(s3)
    print("          Done.")

    # ─────────────────────────────────────────────
    # STAGE 1: Pre-collection scope validation
    # ─────────────────────────────────────────────
    print("\n[STAGE 1] Pre-collection scope validation...")
    t1 = time.time()
    scope_pre = validate_scope(warrant, plan)
    t1_elapsed = round(time.time() - t1, 2)

    scope_pre_path = os.path.join(out_dir, "scope_pre_report.json")
    with open(scope_pre_path, "w") as f:
        json.dump(scope_pre, f, indent=2)

    print(f"          Verdict:    {scope_pre['verdict']}")
    print(f"          Issues:     {scope_pre.get('issues', [])}")
    print(f"          Time:       {t1_elapsed}s")

    # Hard stop on OVER_COLLECTION
    if scope_pre["verdict"] == "OVER_COLLECTION":
        print("\n[BLOCKED] OVER_COLLECTION detected.")
        print("          Pipeline halted before any evidence collected.")
        final = {
            "status":          "BLOCKED",
            "stage_stopped":   "STAGE_1",
            "reason":          "OVER_COLLECTION",
            "issues":          scope_pre.get("issues", []),
            "scope_pre_path":  scope_pre_path,
            "total_time":      round(time.time() - start_total, 2)
        }
        with open(os.path.join(out_dir, "pipeline_result.json"),
                  "w") as f:
            json.dump(final, f, indent=2)
        return final

    # ─────────────────────────────────────────────
    # STAGE 2: Evidence collection
    # ─────────────────────────────────────────────
    print("\n[STAGE 2] Collecting evidence from mocked S3...")
    t2 = time.time()
    raw_dir        = os.path.join(out_dir, "raw_logs")
    collect_result = collect_evidence(warrant, raw_dir)
    t2_elapsed     = round(time.time() - t2, 2)

    print(f"          Files collected: {collect_result['files_collected']}")
    print(f"          Hash chain:      {collect_result['hash_chain_path']}")
    print(f"          Time:            {t2_elapsed}s")

    # ─────────────────────────────────────────────
    # STAGE 3: Presidio PII detection
    # ─────────────────────────────────────────────
    print("\n[STAGE 3] Running Presidio PII detection...")
    t3       = time.time()
    analyzer = build_analyzer()
    all_pii_findings = []

    for fpath in collect_result.get("collected_files", []):
        findings = analyze_file(fpath, analyzer)
        all_pii_findings.extend(findings)

    t3_elapsed = round(time.time() - t3, 2)

    pii_path = os.path.join(out_dir, "pii_findings.json")
    with open(pii_path, "w") as f:
        json.dump(all_pii_findings, f, indent=2)

    print(f"          Total PII entities: {len(all_pii_findings)}")
    print(f"          Time:               {t3_elapsed}s")

    # ─────────────────────────────────────────────
    # STAGE 4: Cross-tenant PII exposure analysis
    # THIS IS WHERE PII DATASET BECOMES OPERATIONAL
    # ─────────────────────────────────────────────
    print("\n[STAGE 4] Running cross-tenant exposure analysis...")
    t4 = time.time()

    registry        = TenantRegistry(ANNOTATIONS_PATH)
    exposure_report = analyse_exposure(
        presidio_findings=all_pii_findings,
        warrant_tenant=warrant["tenant_id"],
        registry=registry
    )
    t4_elapsed = round(time.time() - t4, 2)

    exposure_path = os.path.join(out_dir, "exposure_report.json")
    with open(exposure_path, "w") as f:
        json.dump(exposure_report, f, indent=2)

    print(f"          Cross-tenant violations: "
          f"{exposure_report['violation_count']}")
    print(f"          Exposure level:          "
          f"{exposure_report['exposure_level']}")
    print(f"          Time:                    {t4_elapsed}s")

    # ─────────────────────────────────────────────
    # STAGE 5: Post-collection verdict reassessment
    # ─────────────────────────────────────────────
    print("\n[STAGE 5] Post-collection verdict reassessment...")
    final_verdict = reassess_scope_post_collection(
        pre_verdict=scope_pre["verdict"],
        cross_tenant_violations=exposure_report[
            "cross_tenant_violations"],
        pii_findings=all_pii_findings
    )
    print(f"          Pre-verdict:   {final_verdict['pre_collection_verdict']}")
    print(f"          Post-verdict:  {final_verdict['post_collection_verdict']}")
    print(f"          Recommendation: {final_verdict['recommendation']}")

    # ─────────────────────────────────────────────
    # STAGE 6: Compliance report generation
    # ─────────────────────────────────────────────
    print("\n[STAGE 6] Generating unified compliance report...")
    compliance_path = os.path.join(out_dir, "compliance_report.json")
    report = generate_compliance_report(
        warrant=warrant,
        scope_pre=scope_pre,
        exposure_report=exposure_report,
        final_verdict=final_verdict,
        output_path=compliance_path
    )
    print(f"          GDPR relevant:  "
          f"{report['regulatory_analysis']['gdpr_relevant']}")
    print(f"          DPDPA relevant: "
          f"{report['regulatory_analysis']['dpdpa_relevant']}")
    print(f"          Report saved:    {compliance_path}")

    total_time = round(time.time() - start_total, 2)

    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETE")
    print(f"  Final recommendation: {final_verdict['recommendation']}")
    print(f"  Evidence package:     {out_dir}")
    print(f"  Total runtime:        {total_time}s")
    print(f"{'='*60}\n")

    return {
        "status":               "COMPLETE",
        "case_id":              case_id,
        "pre_verdict":          scope_pre["verdict"],
        "post_verdict":         final_verdict["post_collection_verdict"],
        "recommendation":       final_verdict["recommendation"],
        "files_collected":      collect_result["files_collected"],
        "pii_entities_found":   len(all_pii_findings),
        "cross_tenant_violations": exposure_report["violation_count"],
        "output_directory":     out_dir,
        "total_runtime_seconds": total_time
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LSPCE pipeline")
    parser.add_argument("--warrant", required=True)
    parser.add_argument("--plan",    required=True)
    args = parser.parse_args()
    result = run_pipeline(args.warrant, args.plan)
    print(json.dumps(result, indent=2))