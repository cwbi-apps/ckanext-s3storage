
# CKAN S3 Storage Extension (ckanext-s3storage)

A production-ready CKAN storage plugin for storing resource files in Amazon S3.

Features:

- Multipart uploads for large files (100MB+ parts)
- Dataset-organized folder structure
- Deterministic object keys using dataset and resource IDs
- Presigned download URLs
- Automatic cleanup on resource delete
- Server-side encryption (AES256)
- Background uploads (non-blocking CKAN UI)
- Minimal UI showing "Uploading to S3..." while files upload
- Supports files up to 50 GB+ via background uploads

---

## Requirements

- CKAN 2.9 – 2.11
- Python 3.10+
- AWS credentials (IAM role or environment variables)
- Redis server (for background job queue)
- RQ Python package

---

## Installation

1. Clone the extension:

```bash
git clone https://github.com/your-org/ckanext-s3storage.git
cd ckanext-s3storage
pip install -e .
```

2. Install dependencies:

```bash
pip install boto3 rq redis
```

3. Update `ckan.ini`:

```ini
ckan.plugins = s3storage
ckan.s3.bucket = my-ckan-bucket
ckan.s3.region = us-east-1
ckan.rq.redis_host = localhost
ckan.rq.redis_port = 6379
ckan.rq.redis_db = 0
```

4. Start an RQ worker to process background uploads:

```bash
rq worker --url redis://localhost:6379
```

---

## Usage

- Upload resources via CKAN UI or API as normal.
- For large files, the plugin will upload them in the background.
- While uploading, the resource list will show **"Uploading to S3..."**.
- Once the upload completes, the link is automatically replaced with a presigned S3 URL valid for 1 hour.

---

## Features

| Feature | Status |
|---------|--------|
| CKAN UI & API uploads | ✅ |
| Multipart uploads | ✅ |
| Dataset folder + deterministic keys | ✅ |
| Presigned download URLs | ✅ |
| Automatic S3 cleanup | ✅ |
| Server-side encryption (AES256) | ✅ |
| Background uploads (non-blocking) | ✅ |
| Large files 50 GB+ | ✅ |
| Minimal UI feedback | ✅ |

---

## Optional UI Polling

To show live upload progress:

- Inline in template: the extension includes a small JS snippet in `resource_item.html` that polls the resource every 5 seconds and updates the link automatically.
- For production, you can move the JS to `ckanext/s3storage/public/js/background_upload_poll.js` and include it via:

```html
<script src="{{ h.url_for_static('/s3storage/js/background_upload_poll.js') }}"></script>
```

---

## S3 Best Practices

- Enable **server-side encryption** (AES256 or KMS).
- Enable lifecycle rules for multipart upload cleanup:

```json
{
  "AbortIncompleteMultipartUpload": {
    "DaysAfterInitiation": 7
  }
}
```

- Optionally transition older files to **Glacier** for cost savings.

---

## Development

- Use the `resource_item.html` snippet for UI changes.
- All background uploads are handled via RQ workers.
- Presigned URLs are generated dynamically for downloads.

---

## License

MIT License

---

## Author

CWBI / USACE CKAN Deployment Team
