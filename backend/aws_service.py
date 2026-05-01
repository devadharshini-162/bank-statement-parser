import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# =========================================================================
# AWS S3 CLOUD STORAGE ABSTRACTION
# =========================================================================
# In a real SaaS application, you CANNOT save files to local folders like 'uploads/' 
# because container servers (like Render) wipe their disks on every restart.
# Instead, we upload files to Amazon S3 (Simple Storage Service). 
# 
# How to use this when you create an AWS account:
# 1. Create an IAM User with S3 Full Access.
# 2. Add AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, and AWS_BUCKET_NAME to your .env
#
# Right now, since you don't have an AWS account yet, we built a "fallback" mock 
# so your local code continues to run smoothly!

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
) if AWS_ACCESS_KEY_ID else None

def upload_to_s3(file_path: str, object_name: str) -> bool:
    """
    Uploads a file (like our generated Excel statement) securely into your AWS S3 Bucket.
    If no AWS keys are provided, it silently skips this step.
    """
    if not s3_client or not AWS_BUCKET_NAME:
        print(f"[MOCK AWS] Skipping real S3 upload for {object_name}. No AWS keys found in .env")
        return False
        
    try:
        s3_client.upload_file(file_path, AWS_BUCKET_NAME, object_name)
        print(f"[AWS] Successfully uploaded {object_name} to bucket {AWS_BUCKET_NAME}")
        return True
    except NoCredentialsError:
        print("[AWS] ERROR: Credentials not available")
        return False
    except ClientError as e:
        print(f"[AWS] ERROR: {e}")
        return False

def generate_presigned_url(object_name: str, expiration=3600) -> str:
    """
    Generate a presigned URL to share an S3 object securely.
    Normally, S3 buckets are PRIVATE. A presigned URL generates a temporary link
    (valid for 1 hour by default) so ONLY logged-in users can download the Excel file.
    
    If AWS is not setup, it falls back to the old local download link!
    """
    if not s3_client or not AWS_BUCKET_NAME:
        # Fallback to local server download if AWS isn't plugged in yet!
        return f"/download/{object_name}"

    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': AWS_BUCKET_NAME, 'Key': object_name},
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        print(f"[AWS] ERROR generating presigned URL: {e}")
        return f"/download/{object_name}"
