# Scope Validation Violation Taxonomy

This taxonomy defines the categories of legal scope
violations used by the LSPCE forensic scope validator.

## OVER_COLLECTION Violations

1. wrong_tenant
The collection plan targets a tenant different from
the tenant authorised in the legal warrant.

2. time_window_too_wide
The collection plan includes evidence outside the
authorised investigation time window.

3. extra_evidence_type
The plan includes evidence types not permitted
by the warrant.

4. multi_tenant_collection
The plan attempts to collect evidence from multiple
tenants when only a single tenant is authorised.

## UNDER_COLLECTION Violations

5. time_window_too_narrow
The collection plan omits part of the authorised
time range specified in the warrant.

6. missing_evidence_type
The plan fails to collect one or more authorised
evidence types.

7. partial_collection
The plan incompletely collects authorised evidence
resources or time ranges.

## COMBINED VIOLATIONS

8. combined_violations
Multiple scope violations occur simultaneously
within the same collection plan.