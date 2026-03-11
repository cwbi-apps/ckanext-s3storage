from setuptools import setup, find_packages

setup(
    name="ckanext-s3storage",
    version="0.0.1",
    url='https://github.com/cwbi-apps/ckanext-s3storage',
    packages=find_packages(include=["ckanext", "ckanext.*"],exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=["ckanext"],
    include_package_data=True,
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