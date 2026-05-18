from schemas.validate import validate

test_warrant = {
  "warrant_id": "W-001",
  "tenant_id": "tenant-a",
  "incident_type": "credential_spray",
  "time_window": {
    "start": "2025-05-01T00:00:00Z",
    "end":   "2025-05-03T23:59:59Z"
  },
  "authorised_evidence_types": ["cloudtrail_management"],
  "legal_authority": {
    "order_number": "CRT-2025-001",
    "jurisdiction": "India"
  },
  "requesting_entity": "CBI Cyber Division" 
}

ok, err = validate(test_warrant, "warrant")
print("Valid:" if ok else f"Error: {err}")