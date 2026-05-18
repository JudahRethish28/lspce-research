import boto3, json, os, hashlib
from moto import mock_aws

def collect_evidence(warrant: dict, output_dir: str):
    """Stub collector — downloads tenant logs from mocked S3."""
    tenant_id = warrant["tenant_id"]
    bucket = f"{tenant_id}-evidence"
    os.makedirs(output_dir, exist_ok=True)

    s3 = boto3.client("s3", region_name="ap-south-1")
    objects = s3.list_objects_v2(Bucket=bucket)
    hash_chain = []

    for obj in objects.get("Contents", []):
        key = obj["Key"]
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read()

        # Save file
        local_path = os.path.join(output_dir, key.replace("/","_"))
        with open(local_path, "wb") as f:
            f.write(content)

        # Hash it immediately
        sha256 = hashlib.sha256(content).hexdigest()
        hash_chain.append({"file": key, "sha256": sha256})

    # Save hash chain
    with open(f"{output_dir}/hash_chain.json","w") as f:
        json.dump(hash_chain, f, indent=2)

    return hash_chain