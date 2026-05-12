import json, random
from datetime import datetime, timedelta
from faker import Faker
from tenant_profiles import TENANTS

fake = Faker()

def make_cloudtrail_event(tenant, event_name, timestamp,
                          is_attack=False):
    user = random.choice(tenant["users"])
    bucket = random.choice(tenant["buckets"])
    account = tenant["account_id"]
    return {
        "eventVersion": "1.09",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": fake.uuid4(),
            "arn": f"arn:aws:iam::{account}:user/{user}",
            "accountId": account,
            "userName": user,
            "sessionContext": {
                "sessionIssuer": {},
                "attributes": {
                    "mfaAuthenticated": "false" if is_attack
                                        else "true",
                    "creationDate": timestamp.isoformat()
                }
            }
        },
        "eventTime": timestamp.isoformat() + "Z",
        "eventSource": "s3.amazonaws.com",
        "eventName": event_name,
        "awsRegion": tenant["region"],
        "sourceIPAddress": (
            fake.ipv4() if is_attack
            else fake.ipv4_private()
        ),
        "userAgent": "aws-cli/2.0",
        "requestParameters": {
            "bucketName": bucket,
            "key": f"data/{fake.file_name()}"
        },
        "responseElements": None,
        "requestID": fake.uuid4(),
        "eventID": fake.uuid4(),
        "readOnly": event_name in ["GetObject","ListBucket"],
        "resources": [{
            "ARN": f"arn:aws:s3:::{bucket}",
            "accountId": account,
            "type": "AWS::S3::Bucket"
        }],
        "eventType": "AwsApiCall",
        "managementEvent": False,
        "recipientAccountId": account
    }