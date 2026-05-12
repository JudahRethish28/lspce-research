import json, os, random
from datetime import datetime, timedelta
from cloudtrail_generator import make_cloudtrail_event
from tenant_profiles import TENANTS

BASE_TIME = datetime(2025, 5, 1, 9, 0, 0)
OUT_DIR = "../data/synthetic_logs"
os.makedirs(OUT_DIR, exist_ok=True)

ATTACK_PATTERNS = {
    "credential_spray": [
        ("ConsoleLogin", True)] * 30 + [("GetObject", True)] * 10,
    "insider_exfiltration": [
        ("GetObject", True)] * 25 + [("ListBucket", True)] * 15,
    "ransomware": [
        ("PutObject", True)] * 20 + [("DeleteObject", True)] * 20
}

file_count = 0
for tenant_id, tenant in TENANTS.items():
    for file_num in range(17):   # ~17 files per tenant = 51 total
        events = []
        is_attack_file = file_num < 8   # first 8 are attack files
        pattern = (ATTACK_PATTERNS[tenant["scenario"]]
                   if is_attack_file
                   else [("GetObject", False)] * 20)
        for i, (event_name, is_attack) in enumerate(pattern):
            ts = BASE_TIME + timedelta(hours=i, minutes=file_num*3)
            events.append(make_cloudtrail_event(
                tenant, event_name, ts, is_attack))
        filename = f"{OUT_DIR}/{tenant_id}_log_{file_num:02d}.json"
        with open(filename, "w") as f:
            json.dump({"Records": events}, f, indent=2)
        file_count += 1

print(f"Generated {file_count} log files.")