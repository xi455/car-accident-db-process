from pathlib import Path

import boto3
import environ

env = environ.Env()
env_file = Path(__file__).parent / ".env"

if env_file.exists():
    env.read_env()

session = boto3.Session(
    aws_access_key_id=env("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=env("AWS_SECRET_ACCESS_KEY"),
    region_name=env("AWS_ACCESS_NAME"),
)
s3 = session.client("s3", endpoint_url=env("AWS_ACCESS_URL"))

# 範例：列出 S3 存儲桶
response = s3.list_buckets()
# print('S3 存儲桶列表:', response['Buckets'])

bucket_name = "lost-and-found"
response = s3.list_objects(Bucket=bucket_name)
objects = response["Contents"]

for obj in objects:
    print(obj)
