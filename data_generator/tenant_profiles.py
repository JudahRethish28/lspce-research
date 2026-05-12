from faker import Faker
fake = Faker()

TENANTS = {
    "tenant-a": {
        "tenant_id": "tenant-a",
        "account_id": "123456789012",
        "scenario": "credential_spray",
        "users": ["alice.chen","bob.kumar","carol.smith"],
        "buckets": ["tenant-a-data","tenant-a-backup"],
        "region": "ap-south-1"
    },
    "tenant-b": {
        "tenant_id": "tenant-b",
        "account_id": "234567890123",
        "scenario": "insider_exfiltration",
        "users": ["david.raj","eve.patel","frank.nair"],
        "buckets": ["tenant-b-finance","tenant-b-hr"],
        "region": "ap-south-1"
    },
    "tenant-c": {
        "tenant_id": "tenant-c",
        "account_id": "345678901234",
        "scenario": "ransomware",
        "users": ["grace.iyer","henry.das","iris.menon"],
        "buckets": ["tenant-c-prod","tenant-c-archive"],
        "region": "ap-south-1"
    }
}