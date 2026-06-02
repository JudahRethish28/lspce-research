"""
Cross-Tenant PII Exposure Analyser

Takes Presidio detection results and the TenantRegistry,
and identifies any PII entities that belong to tenants
other than the warrant tenant.

This is the novel runtime component that connects:
  - Presidio PII detection output
  - Ground truth annotation data (via TenantRegistry)
  - Legal warrant scope (warrant_tenant)

Into a cross-tenant privacy violation assessment.
"""

def analyse_exposure(
    presidio_findings: list,
    warrant_tenant:    str,
    registry           # TenantRegistry instance
) -> dict:
    """
    Analyses PII findings for cross-tenant exposure.

    presidio_findings: list of dicts from pii_analyzer.analyze_file()
    warrant_tenant:    the tenant the warrant is issued for
    registry:          TenantRegistry instance

    Returns a structured exposure report.
    """
    cross_tenant_violations = []
    same_tenant_pii         = []
    unknown_entities        = []

    for finding in presidio_findings:
        entity_text = finding.get("entity_text", "")
        owners      = registry.get_owning_tenants(entity_text)

        if not owners:
            # Entity detected by Presidio but not in ground truth
            # annotations — treat as unknown, do not flag as violation
            unknown_entities.append(finding)

        elif warrant_tenant not in owners:
            # Entity belongs to a different tenant
            cross_tenant_violations.append({
                **finding,
                "owning_tenants":  list(owners),
                "warrant_tenant":  warrant_tenant,
                "violation_type":  "CROSS_TENANT_PII_EXPOSURE",
                "severity":        "HIGH"
            })

        else:
            # Entity belongs to the warrant tenant — expected
            same_tenant_pii.append(finding)

    # Compute exposure summary
    entity_type_violations = {}
    for v in cross_tenant_violations:
        et = v["entity_type"]
        entity_type_violations[et] = (
            entity_type_violations.get(et, 0) + 1)

    exposure_level = (
        "CRITICAL"  if len(cross_tenant_violations) > 10  else
        "HIGH"      if len(cross_tenant_violations) > 0   else
        "LOW"       if len(same_tenant_pii) > 0            else
        "NONE"
    )

    return {
        "warrant_tenant":            warrant_tenant,
        "total_findings":            len(presidio_findings),
        "cross_tenant_violations":   cross_tenant_violations,
        "same_tenant_pii":           same_tenant_pii,
        "unknown_entities":          unknown_entities,
        "violation_count":           len(cross_tenant_violations),
        "exposure_level":            exposure_level,
        "violations_by_entity_type": entity_type_violations
    }