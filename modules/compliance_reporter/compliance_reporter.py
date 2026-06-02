"""
Compliance Reporter — Extended Version

Now consumes:
  1. Pre-collection scope verdict (from Gemini scope validator)
  2. Post-collection PII exposure report (from exposure analyser)
  3. Post-collection verdict reassessment (from scope_validator)
  4. Original warrant (for case metadata)

Produces a single unified compliance report that is the
final output of the LSPCE pipeline.
"""
import json
from datetime import datetime, timezone

def generate_compliance_report(
    warrant:          dict,
    scope_pre:        dict,
    exposure_report:  dict,
    final_verdict:    dict,
    output_path:      str
) -> dict:

    # Determine regulatory relevance based on detected PII.
    # Presence of PII does not automatically imply a violation;
    # cross-tenant exposure is treated as the primary compliance risk.
    gdpr_relevant  = exposure_report["total_findings"] > 0
    dpdpa_relevant = exposure_report["total_findings"] > 0
    cross_tenant    = exposure_report["violation_count"] > 0

    # Determine specific GDPR clauses
    clauses = []
    if exposure_report["total_findings"] > 0:
        clauses.append({
            "regulation":  "GDPR",
            "article":     "Article 5(1)(b)",
            "principle":   "Purpose Limitation",
            "reason": "PII entities present in evidence package",
            "action_required": (
                "Verify all PII is necessary for the stated "
                "forensic purpose"
            )
        })
    if cross_tenant:
        clauses.append({
            "regulation":  "GDPR",
            "article":     "Article 5(1)(a)",
            "principle":   "Lawfulness and Fairness",
            "triggered_by": "Cross-tenant PII detected",
            "action_required": (
                "Evidence package contains PII belonging to "
                "tenants outside the warrant scope. "
                "Collection is unlawful as constructed."
            )
        })
        clauses.append({
            "regulation":  "DPDPA 2023",
            "section":     "Section 8",
            "principle":   "Obligations of Data Fiduciary",
            "triggered_by": "Cross-tenant PII detected",
            "action_required": (
                "CSP as data fiduciary has exposed personal "
                "data of non-warrant data principals. "
                "Immediate remediation required."
            )
        })

    report = {
        "report_metadata": {
            "generated_at":   datetime.now(timezone.utc).isoformat() + "Z",
            "warrant_id":     warrant.get("warrant_id"),
            "tenant_id":      warrant.get("tenant_id"),
            "incident_type":  warrant.get("incident_type"),
            "lspce_version":  "1.0"
        },
        "stage_1_pre_collection": {
            "verdict":     scope_pre.get("verdict"),
            "issues":      scope_pre.get("issues", []),
            "confidence":  scope_pre.get("confidence", 0)
        },
        "stage_2_pii_detection": {
            "total_pii_entities":    exposure_report["total_findings"],
            "cross_tenant_count":    exposure_report["violation_count"],
            "same_tenant_count":     len(exposure_report["same_tenant_pii"]),
            "unknown_count":         len(exposure_report["unknown_entities"]),
            "exposure_level":        exposure_report["exposure_level"],
            "violations_by_type":    exposure_report["violations_by_entity_type"],
            "cross_tenant_details":  exposure_report["cross_tenant_violations"]
        },
        "stage_3_final_verdict": {
            "verdict":        final_verdict["post_collection_verdict"],
            "recommendation": final_verdict["recommendation"],
            "explanation":    final_verdict["explanation"]
        },
        "regulatory_analysis": {
            "gdpr_relevant":  gdpr_relevant,
            "dpdpa_relevant": dpdpa_relevant,
            "cross_tenant_exposure": cross_tenant,
            "clauses":         clauses
        },
        "summary": (
            f"Warrant {warrant.get('warrant_id')} for tenant "
            f"{warrant.get('tenant_id')}: "
            f"Pre-collection verdict was {scope_pre.get('verdict')}. "
            f"Post-collection analysis found "
            f"{exposure_report['total_findings']} PII entities "
            f"({exposure_report['violation_count']} cross-tenant). "
            f"Final recommendation: {final_verdict['recommendation']}."
        )
    }

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    return report