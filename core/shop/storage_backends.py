# your_app/storage_backends.py
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class LiaraStorage(S3Boto3Storage):

    def url(self, name, parameters=None, expire=None, http_method=None):
        base_url = 'https://storage.liatoy.com'  
        name = name.lstrip('/')  
        return f"{base_url}/{name}"
