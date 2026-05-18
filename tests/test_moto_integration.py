import boto3, json, os
from moto import mock_aws

SYNTHETIC_DIR = "data/synthetic_logs"

@mock_aws
def test_upload_and_retrieve_logs():
    s3 = boto3.client("s3", region_name="ap-south-1")

    # Create one bucket per tenant
    for tenant in ["tenant-a", "tenant-b", "tenant-c"]:
        s3.create_bucket(
            Bucket=f"{tenant}-evidence",
            CreateBucketConfiguration={
                "LocationConstraint": "ap-south-1"}
        )

    # Upload all log files for tenant-a
    uploaded = 0
    for fname in os.listdir(SYNTHETIC_DIR):
        if fname.startswith("tenant-a"):
            with open(f"{SYNTHETIC_DIR}/{fname}") as f:
                content = f.read()
            s3.put_object(
                Bucket="tenant-a-evidence",
                Key=f"cloudtrail/{fname}",
                Body=content.encode()
            )
            uploaded += 1

    # Retrieve and verify
    response = s3.list_objects_v2(Bucket="tenant-a-evidence")
    assert response["KeyCount"] == uploaded
    print(f"Uploaded and verified {uploaded} files. Test passed.")

test_upload_and_retrieve_logs()