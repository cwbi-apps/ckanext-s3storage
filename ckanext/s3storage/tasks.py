import os
from .uploader import S3Uploader
import ckan.plugins.toolkit as toolkit

def upload_resource_file(resource_id, dataset_id, filepath, filename):
    """Background task: upload resource and update CKAN."""
    uploader = S3Uploader()
    with open(filepath, "rb") as f:
        url = uploader.upload_fileobj(f, dataset_id, resource_id, filename)

    context = {"model": toolkit.model, "user": toolkit.c.user}
    data_dict = {"id": resource_id, "url": url}
    toolkit.get_action("resource_update")(context, data_dict)

    os.remove(filepath)