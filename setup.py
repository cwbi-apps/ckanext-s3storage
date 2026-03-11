from setuptools import setup, find_packages

setup(
    name="ckanext-s3storage",
    version="0.4",
    packages=find_packages(),
    namespace_packages=["ckanext"],
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