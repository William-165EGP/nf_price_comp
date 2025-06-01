import boto3
import os

bucket = "netflix-cache"
prefix = "fullcache/"

s3 = boto3.client(
    "s3",
    endpoint_url="https://69cb72428a55ae914f068cb56005e51d.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
)

resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
if "Contents" in resp:
    for obj in resp["Contents"]:
        print("Deleting", obj["Key"])
        s3.delete_object(Bucket=bucket, Key=obj["Key"])