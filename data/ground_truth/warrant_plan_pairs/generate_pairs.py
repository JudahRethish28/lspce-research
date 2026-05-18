import os
import json
import csv
from copy import deepcopy

# =========================================================
# OUTPUT DIRECTORY
# =========================================================

OUTPUT_DIR = "data/ground_truth/warrant_plan_pairs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================================================
# BASE DATA
# =========================================================

tenants = ["tenant-a", "tenant-b", "tenant-c"]

incident_types = [
    "credential_spray",
    "insider_exfiltration",
    "ransomware"
]

evidence_types = [
    "cloudtrail_management",
    "s3_data_events"
]

# =========================================================
# HELPER FUNCTION
# =========================================================

def save_json(filename, data):
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# =========================================================
# SUMMARY CSV
# =========================================================

summary_rows = []

# =========================================================
# CASES 02–10 → APPROVED
# =========================================================

for i in range(2, 11):

    tenant = tenants[(i - 2) % 3]
    incident = incident_types[(i - 2) % 3]

    warrant = {
        "warrant_id": f"W-{i:03}",
        "tenant_id": tenant,
        "incident_type": incident,
        "time_window": {
            "start": "2025-05-01T00:00:00Z",
            "end": "2025-05-03T23:59:59Z"
        },
        "authorised_evidence_types": [
            "cloudtrail_management"
        ],
        "legal_authority": {
            "order_number": f"CRT-2025-{i:03}",
            "jurisdiction": "India"
        },
        "requesting_entity": "CBI Cyber Division"
    }

    plan = {
        "warrant_id": f"W-{i:03}",
        "proposed_resources": [
            {
                "resource_type": "cloudtrail_management",
                "source_name": f"{tenant}-trail",
                "tenant_id": tenant,
                "time_window": {
                    "start": "2025-05-01T00:00:00Z",
                    "end": "2025-05-03T23:59:59Z"
                }
            }
        ]
    }

    label = {
        "verdict": "APPROVED",
        "issues": [],
        "approved_resources": [
            "cloudtrail_management"
        ]
    }

    save_json(f"warrant_{i:02}.json", warrant)
    save_json(f"plan_{i:02}.json", plan)
    save_json(f"label_{i:02}.json", label)

    summary_rows.append([
        f"{i:02}",
        "APPROVED",
        "none",
        "exact match"
    ])


# =========================================================
# CASES 11–20 → OVER_COLLECTION
# =========================================================

over_collection_cases = [
    ("wrong_tenant", "tenant-b instead of tenant-a"),
    ("time_window_wide", "7 days vs 3 days"),
    ("extra_evidence_type", "added s3_data_events"),
    ("multi_tenant_collection", "collects tenant-a and tenant-b"),
    ("early_collection", "starts before warrant"),
    ("wrong_tenant + extra_evidence", "combined violation"),
    ("wide_window + extra_evidence", "combined violation"),
    ("wide_window + wrong_tenant", "combined violation"),
    ("multi_tenant + wide_window", "combined violation"),
    ("all_violations", "multiple violations")
]

for idx, (violation, note) in enumerate(over_collection_cases, start=11):

    warrant = {
        "warrant_id": f"W-{idx:03}",
        "tenant_id": "tenant-a",
        "incident_type": "credential_spray",
        "time_window": {
            "start": "2025-05-01T00:00:00Z",
            "end": "2025-05-03T23:59:59Z"
        },
        "authorised_evidence_types": [
            "cloudtrail_management"
        ]
    }

    plan = {
        "warrant_id": f"W-{idx:03}",
        "proposed_resources": [
            {
                "resource_type": "cloudtrail_management",
                "source_name": "tenant-a-trail",
                "tenant_id": "tenant-a",
                "time_window": {
                    "start": "2025-05-01T00:00:00Z",
                    "end": "2025-05-03T23:59:59Z"
                }
            }
        ]
    }

    issues = []

    # -----------------------------------------------------

    if "wrong_tenant" in violation:
        plan["proposed_resources"][0]["tenant_id"] = "tenant-b"
        issues.append("wrong_tenant")

    if "wide_window" in violation or violation == "time_window_wide":
        plan["proposed_resources"][0]["time_window"]["end"] = \
            "2025-05-07T23:59:59Z"
        issues.append("time_window_wide")

    if "extra_evidence" in violation or violation == "extra_evidence_type":
        plan["proposed_resources"].append({
            "resource_type": "s3_data_events",
            "source_name": "tenant-a-s3",
            "tenant_id": "tenant-a",
            "time_window": {
                "start": "2025-05-01T00:00:00Z",
                "end": "2025-05-03T23:59:59Z"
            }
        })
        issues.append("extra_evidence_type")

    if "multi_tenant" in violation or violation == "multi_tenant_collection":
        plan["proposed_resources"].append({
            "resource_type": "cloudtrail_management",
            "source_name": "tenant-b-trail",
            "tenant_id": "tenant-b",
            "time_window": {
                "start": "2025-05-01T00:00:00Z",
                "end": "2025-05-03T23:59:59Z"
            }
        })
        issues.append("multi_tenant_collection")

    if violation == "early_collection":
        plan["proposed_resources"][0]["time_window"]["start"] = \
            "2025-04-28T00:00:00Z"
        issues.append("early_collection")

    label = {
        "verdict": "OVER_COLLECTION",
        "issues": issues
    }

    save_json(f"warrant_{idx:02}.json", warrant)
    save_json(f"plan_{idx:02}.json", plan)
    save_json(f"label_{idx:02}.json", label)

    summary_rows.append([
        f"{idx:02}",
        "OVER_COLLECTION",
        violation,
        note
    ])


# =========================================================
# CASES 21–30 → UNDER_COLLECTION
# =========================================================

under_cases = [
    ("missing_evidence_type", "missing s3_data_events"),
    ("narrow_time_window", "1 day instead of 3"),
    ("missing_bucket_scope", "one bucket only"),
    ("missing_time + evidence", "combined"),
    ("missing_bucket + evidence", "combined"),
    ("missing_time + bucket", "combined"),
    ("partial_logs", "partial collection"),
    ("missing_cloudtrail", "s3 only"),
    ("minimal_collection", "insufficient scope"),
    ("multiple_missing", "multiple missing items")
]

for idx, (violation, note) in enumerate(under_cases, start=21):

    warrant = {
        "warrant_id": f"W-{idx:03}",
        "tenant_id": "tenant-a",
        "incident_type": "insider_exfiltration",
        "time_window": {
            "start": "2025-05-01T00:00:00Z",
            "end": "2025-05-03T23:59:59Z"
        },
        "authorised_evidence_types": [
            "cloudtrail_management",
            "s3_data_events"
        ]
    }

    plan = {
        "warrant_id": f"W-{idx:03}",
        "proposed_resources": [
            {
                "resource_type": "cloudtrail_management",
                "source_name": "tenant-a-trail",
                "tenant_id": "tenant-a",
                "time_window": {
                    "start": "2025-05-01T00:00:00Z",
                    "end": "2025-05-03T23:59:59Z"
                }
            }
        ]
    }

    issues = []

    # -----------------------------------------------------

    if "missing_evidence" in violation:
        issues.append("missing_evidence_type")

    if "narrow_time" in violation:
        plan["proposed_resources"][0]["time_window"]["end"] = \
            "2025-05-01T23:59:59Z"
        issues.append("narrow_time_window")

    if "bucket" in violation:
        issues.append("missing_bucket_scope")

    if violation == "missing_cloudtrail":
        plan["proposed_resources"] = [
            {
                "resource_type": "s3_data_events",
                "source_name": "tenant-a-s3",
                "tenant_id": "tenant-a",
                "time_window": {
                    "start": "2025-05-01T00:00:00Z",
                    "end": "2025-05-03T23:59:59Z"
                }
            }
        ]
        issues.append("missing_cloudtrail")

    label = {
        "verdict": "UNDER_COLLECTION",
        "issues": issues
    }

    save_json(f"warrant_{idx:02}.json", warrant)
    save_json(f"plan_{idx:02}.json", plan)
    save_json(f"label_{idx:02}.json", label)

    summary_rows.append([
        f"{idx:02}",
        "UNDER_COLLECTION",
        violation,
        note
    ])

# =========================================================
# WRITE SUMMARY CSV
# =========================================================

summary_path = os.path.join(OUTPUT_DIR, "pairs_summary.csv")

with open(summary_path, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "pair_id",
        "verdict",
        "violation_type",
        "notes"
    ])

    writer.writerows(summary_rows)

print("\n===================================")
print("30 warrant-plan pairs generated!")
print("Summary CSV created.")
print("===================================")