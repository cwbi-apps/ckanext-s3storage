import os
import mimetypes
import boto3
from boto3.s3.transfer import TransferConfig
import ckan.plugins.toolkit as toolkit

MULTIPART_CONFIG = TransferConfig(
    multipart_threshold=100*1024*1024,
    multipart_chunksize=100*1024*1024,
    max_concurrency=10,
    use_threads=True
)

def get_s3_client():
    region = toolkit.config.get("ckan.s3.region")
    return boto3.client("s3", region_name=region)

def generate_presigned_url(url):
    bucket = toolkit.config.get("ckan.s3.bucket")
    key = url.split(".amazonaws.com/")[-1]
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=3600
    )

class S3Uploader:

    def __init__(self, old_filename=None):
        self.bucket = toolkit.config.get("ckan.s3.bucket")
        self.client = get_s3_client()
        self.old_filename = old_filename

    def upload_fileobj(self, fileobj, dataset_id, resource_id, original_filename):
        filename = os.path.basename(original_filename or "resource.bin")
        key = f"datasets/{dataset_id}/resources/{resource_id}/{filename}"
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        self.client.upload_fileobj(
            fileobj,
            self.bucket,
            key,
            ExtraArgs={"ContentType": content_type, "ServerSideEncryption": "AES256"},
            Config=MULTIPART_CONFIG
        )

        region = toolkit.config.get("ckan.s3.region")
        return f"https://{self.bucket}.s3.{region}.amazonaws.com/{key}"

    def delete(self, url):
        if not url or "amazonaws.com" not in url:
            return
        key = url.split(".amazonaws.com/")[-1]
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
        except Exception:
            pass