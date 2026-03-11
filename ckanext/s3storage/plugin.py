import tempfile
from rq import Queue
from redis import Redis

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from .uploader import S3Uploader, generate_presigned_url
from .tasks import upload_resource_file


class S3StoragePlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.IUploader)
    plugins.implements(plugins.IResourceController)
    plugins.implements(plugins.IConfigurer)

    # -----------------------
    # CKAN Config
    # -----------------------

    def update_config(self, config):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "public")

    # -----------------------
    # IUploader Interface
    # -----------------------

    def get_uploader(self, upload_to, old_filename=None):
        if upload_to == "resource":
            return self

    def upload(self, fileobj):
        dataset_id = toolkit.request.form.get("package_id")
        resource_id = toolkit.request.form.get("id")
        original_filename = toolkit.request.form.get("upload")

        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(fileobj.read())
        tmp.close()

        redis_conn = Redis(
            host=toolkit.config.get("ckan.rq.redis_host", "localhost"),
            port=int(toolkit.config.get("ckan.rq.redis_port", 6379)),
            db=int(toolkit.config.get("ckan.rq.redis_db", 0))
        )

        q = Queue(connection=redis_conn)

        q.enqueue(
            upload_resource_file,
            resource_id,
            dataset_id,
            tmp.name,
            original_filename
        )

        return "Uploading to S3 in background..."

    # -----------------------
    # IResourceController Hooks
    # -----------------------

    def after_resource_show(self, context, resource_dict):
        url = resource_dict.get("url")

        if url and "amazonaws.com" in url:
            resource_dict["url"] = generate_presigned_url(url)

        return resource_dict

    def before_resource_delete(self, context, resource_dict):
        uploader = S3Uploader()
        uploader.delete(resource_dict.get("url"))