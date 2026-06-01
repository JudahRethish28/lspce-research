from moto import mock_aws
import boto3
import os
import json

LOGS_DIR = "data/synthetic_logs"

TENANT_ACCOUNTS = {
    "tenant-a": "123456789012",
    "tenant-b": "234567890123",
    "tenant-c": "345678901234"
}

def setup_moto_environment(s3_client):
    """
    Create buckets and upload all synthetic logs.
    Must be called INSIDE an active @mock_aws context.
    Receives the s3_client so it uses the same mock session.
    """
    # Create one bucket per tenant
    for tenant in TENANT_ACCOUNTS:
        bucket = f"{tenant}-evidence"
        s3_client.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={
                "LocationConstraint": "ap-south-1"
            }
        )

    # Upload all log files using CloudTrail-style paths
    uploaded = 0
    for fname in os.listdir(LOGS_DIR):
        if not fname.endswith(".json"):
            continue

        tenant = fname.split("_log_")[0]
        account_id = TENANT_ACCOUNTS.get(tenant, "000000000000")

        # Real CloudTrail S3 path format
        key = (
            f"AWSLogs/{account_id}/CloudTrail/"
            f"ap-south-1/2025/05/{fname}"
        )

        with open(f"{LOGS_DIR}/{fname}", "rb") as f:
            s3_client.put_object(
                Bucket=f"{tenant}-evidence",
                Key=key,
                Body=f.read()
            )
        uploaded += 1

    print(f"[Setup] Uploaded {uploaded} files to mocked S3.")
    return uploaded


@mock_aws
def run_pipeline(warrant_path: str, plan_path: str) -> dict:
    """
    The @mock_aws decorator here creates the mock context.
    All setup, collection, and evaluation happen inside
    this single function — within the same mock session.
    """
    # Step 1: Create the S3 client INSIDE the mock context
    s3 = boto3.client("s3", region_name="ap-south-1")

    # Step 2: Setup the environment using that client
    setup_moto_environment(s3)

    # Step 3: Now run your pipeline stages
    # (scope validation, evidence collection, PII detection, etc.)
    # All boto3 calls here hit the same mocked S3
    # ...
    
    print("Pipeline started")

    return {"status": "complete"}

if __name__ == "__main__":
    result = run_pipeline("", "")
    print(result)