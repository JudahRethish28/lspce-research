from modules.exposure_analyser.exposure_analyser import analyse_exposure
from modules.tenant_registry.tenant_registry import TenantRegistry

registry = TenantRegistry("data/ground_truth/pii_annotations.csv")

# Pick two real entity_text values from your CSV:
# one from tenant-a, one from tenant-b
# Look up actual values in your pii_annotations.csv

# Simulate: warrant is for tenant-a
# Finding 1: entity belongs to tenant-a (expected, not a violation)
# Finding 2: entity belongs to tenant-b (cross-tenant violation)

synthetic_findings = [
    {"entity_type": "PERSON",     "entity_text": "alice.chen",
     "file": "tenant-a_log_00.json", "start": 100, "end": 109},
    {"entity_type": "AWS_ACCOUNT_ID", "entity_text": "234567890123",
     "file": "tenant-a_log_00.json", "start": 200, "end": 212},
]

result = analyse_exposure(
    presidio_findings=synthetic_findings,
    warrant_tenant="tenant-a",
    registry=registry
)

print(f"Total findings:         {result['total_findings']}")
print(f"Cross-tenant:           {result['violation_count']}")
print(f"Exposure level:         {result['exposure_level']}")
print(f"Violations:             {result['cross_tenant_violations']}")