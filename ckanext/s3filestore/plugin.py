# encoding: utf-8
import ckan.plugins as plugins
import ckantoolkit as toolkit
from ckan.config.declaration import Declaration, Key

import ckanext.s3filestore.uploader
from ckanext.s3filestore.views import resource, uploads
from ckanext.s3filestore.click_commands import upload_resources, upload_assets


class S3FileStorePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IUploader)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        # We need to register the following templates dir in order
        # to fix downloading the HTML file instead of previewing when
        # 'webpage_view' is enabled
        toolkit.add_template_directory(config_, 'theme/templates')

    # IConfigDeclaration
    def declare_config_options(self, declaration: Declaration, key: Key):
        
        # Declare all configuration options, including validators, for the s3filestore plugin.
        # This uses the correct built-in validator names.
        
        declaration.annotate("CKAN S3 Filestore General Config")

        # Credentials and bucket configuration (strings, no validators needed)
        declaration.declare('ckanext.s3filestore.aws_bucket_name').set_description("S3 bucket name.")
        declaration.declare('ckanext.s3filestore.region_name').set_description("AWS region of the bucket.")
        declaration.declare('ckanext.s3filestore.signature_version', 's3v4').set_description("S3 signature version.")
        declaration.declare('ckanext.s3filestore.aws_access_key_id').set_description("AWS access key ID.")
        declaration.declare('ckanext.s3filestore.aws_secret_access_key').set_description("AWS secret access key.")
        declaration.declare('ckanext.s3filestore.aws_is_public', False).set_validators("boolean_validator")

        # IAM role-based authentication (boolean)
        declaration.declare('ckanext.s3filestore.aws_use_ami_role', False).set_validators("boolean_validator")

        # Storage path and fallback
        declaration.declare('ckanext.s3filestore.aws_storage_path').set_description("Path to prepend to S3 keys.")
        declaration.declare('ckanext.s3filestore.filesystem_download_fallback', False).set_validators("boolean_validator")

        # ACL and visibility settings
        declaration.declare('ckanext.s3filestore.acl', 'public-read').set_description("ACL for new files.")
        declaration.declare('ckanext.s3filestore.non_current_acl', 'private').set_description("ACL for old file versions.")
        declaration.declare('ckanext.s3filestore.acl.async_update', True).set_validators("boolean_validator")

        # S3 endpoint and addressing style
        declaration.declare('ckanext.s3filestore.addressing_style', 'auto').set_description("S3 addressing style.")
        declaration.declare('ckanext.s3filestore.host_name').set_description("Hostname for S3-compatible services.")

        # URL and download behavior
        declaration.declare('ckanext.s3filestore.use_filename', False).set_validators("boolean_validator")
        declaration.declare('ckanext.s3filestore.download_proxy').set_description("Proxy URL for downloads.")

        # Caching and expiry settings (integers) - Using the correct 'int_validator'
        declaration.declare('ckanext.s3filestore.signed_url_expiry', 3600).set_validators("int_validator")
        declaration.declare('ckanext.s3filestore.signed_url_cache_window', 1800).set_validators("int_validator")
        declaration.declare('ckanext.s3filestore.public_url_cache_window', 86400).set_validators("int_validator")
        declaration.declare('ckanext.s3filestore.acl_cache_window', 2592000).set_validators("int_validator")

        # Cleanup and background job settings
        declaration.declare('ckanext.s3filestore.delete_non_current_days', -1).set_validators("int_validator")
        declaration.declare('ckanext.s3filestore.queue', 'default').set_description("RQ queue for background jobs.")
        declaration.declare('ckanext.s3filestore.check_access_on_startup', True).set_validators("boolean_validator")


    # IConfigurable

    def configure(self, config):
        # Certain config options must exists for the plugin to work. Raise an
        # exception if they're missing.
        missing_config = "{0} is not configured. Please amend your .ini file."
        config_options = (
            'ckanext.s3filestore.aws_bucket_name',
            'ckanext.s3filestore.region_name',
            'ckanext.s3filestore.signature_version'
        )

        if not config.get('ckanext.s3filestore.aws_use_ami_role'):
            config_options += ('ckanext.s3filestore.aws_access_key_id',
                               'ckanext.s3filestore.aws_secret_access_key')

        for option in config_options:
            if not config.get(option, None):
                raise RuntimeError(missing_config.format(option))

        # Check that options actually work, if not exceptions will be raised
        if toolkit.asbool(
                config.get('ckanext.s3filestore.check_access_on_startup',
                           True)):
            ckanext.s3filestore.uploader.BaseS3Uploader().get_s3_bucket(
                config.get('ckanext.s3filestore.aws_bucket_name'))

    # IUploader

    def get_resource_uploader(self, data_dict):
        '''Return an uploader object used to upload resource files.'''
        return ckanext.s3filestore.uploader.S3ResourceUploader(data_dict)

    def get_uploader(self, upload_to, old_filename=None):
        '''Return an uploader object used to upload general files.'''
        return ckanext.s3filestore.uploader.S3Uploader(upload_to,
                                                       old_filename)

    # IBlueprint

    def get_blueprint(self):
        blueprints = resource.get_blueprints() +\
                     uploads.get_blueprints()
        return blueprints

    # IClick

    def get_commands(self):
        return [upload_resources, upload_assets]
