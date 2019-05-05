from evaluations.decorator import Decorators
import boto
import boto.s3
from boto.s3.key import Key


class Evaluation:
    def __init__(self, aws_access_key, aws_secret_key):
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.default_name = 'default'
        self.conn = boto.connect_s3(aws_access_key, aws_secret_key)
        self.bucket_name = None

    @Decorators.tagging('AWS:Bucket:Create')
    @Decorators.python_consumption()
    @Decorators.timing()
    def create_aws_bucket(self, bucket_name):
        self.conn.create_bucket(bucket_name)
        self.bucket_name = bucket_name

    @Decorators.tagging('AWS:Bucket:Delete')
    @Decorators.python_consumption()
    @Decorators.timing()
    def delete_aws_bucket(self, bucket_name=None):
        if not bucket_name:
            bucket_name = self.bucket_name
        bucket = self.conn.get_bucket(bucket_name)
        for key in bucket.list():
            key.delete()
        self.conn.delete_bucket(bucket_name)

    @Decorators.tagging('AWS:File:Upload')
    @Decorators.python_consumption()
    @Decorators.timing()
    def upload_file_aws(self, file_path, object_name=None, bucket_name=None):
        if not bucket_name:
            bucket_name = self.bucket_name
        if not object_name:
            object_name = self.default_name
        bucket = self.conn.get_bucket(bucket_name)
        bucket_key = Key(bucket)
        bucket_key.name = object_name
        bucket_key.set_contents_from_filename(file_path)

    @Decorators.tagging('AWS:File:Download')
    @Decorators.python_consumption()
    @Decorators.timing()
    def download_file_aws(self, storage_folder, object_name=None, bucket_name=None):
        if not bucket_name:
            bucket_name = self.bucket_name
        if not object_name:
            object_name = self.default_name
        bucket = self.conn.get_bucket(bucket_name)
        bucket_key = Key(bucket)
        bucket_key.key = object_name
        bucket_key.get_contents_to_filename(storage_folder + object_name)

    @Decorators.tagging('AWS:File:Delete')
    @Decorators.python_consumption()
    @Decorators.timing()
    def delete_file_aws(self, object_name=None, bucket_name=None):
        if not bucket_name:
            bucket_name = self.bucket_name
        if not object_name:
            object_name = self.default_name
        bucket = self.conn.get_bucket(bucket_name)
        bucket_key = Key(bucket)
        bucket_key.key = object_name
        bucket.delete_key(bucket_key)
