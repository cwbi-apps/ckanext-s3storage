from setuptools import setup, find_packages

version = "0.0.1"

setup(
    name="ckanext-s3storage",
    version=version,
    description="CKAN S3 resource storage backend",
    url="https://github.com/cwbi-apps/ckanext-s3storage",
    author="CWBI",
    license="MIT",
    packages=find_packages(),
    namespace_packages=["ckanext"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "boto3>=1.28",
        "rq",
        "redis"
    ],
    entry_points="""
        [ckan.plugins]
        s3storage=ckanext.s3storage.plugin:S3StoragePlugin
    """,
)