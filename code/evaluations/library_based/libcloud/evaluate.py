from evaluations import system
from evaluations.decorator import Decorators
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from libcloud.storage.types import Provider as S_Provider
from libcloud.storage.providers import get_driver as s_get_driver


class Evaluation:
    def __init__(self, libcloud_aws_access_key, libcloud_aws_secret_key, libcloud_home_directory,
                 libcloud_env_directory='env', libcloud_region='us-east-2'):
        self.libcloud_home_directory = libcloud_home_directory
        self.libcloud_aws_access_key = libcloud_aws_access_key
        self.libcloud_aws_secret_key = libcloud_aws_secret_key
        self.libcloud_env_directory = libcloud_env_directory
        s_cls = s_get_driver(S_Provider.S3)
        self.libcloud_region = libcloud_region
        self.default_name = 'default'
        self.bucket_name = None
        self.libcloud_drivers = []
        self.libcloud_s_drivers = [s_cls(self.libcloud_aws_access_key, self.libcloud_aws_secret_key)]

    @Decorators.tagging('*:System:Download')
    @Decorators.timing(output=True)
    def download_sources(self):
        system.libcloud_bash_command('libcloud_download', self.libcloud_home_directory, self.libcloud_env_directory)
        size, volume = system.get_folder_size(self.libcloud_home_directory)
        return {'size': size, 'volume': volume}

    @Decorators.tagging('*:System:Start')
    @Decorators.timing()
    def install_library(self):
        system.libcloud_bash_command('libcloud_install', self.libcloud_home_directory, self.libcloud_env_directory)

    @Decorators.tagging('*:System:Stop')
    @Decorators.timing()
    def uninstall_library(self):
        system.libcloud_bash_command('libcloud_download', self.libcloud_home_directory, self.libcloud_env_directory)

    @Decorators.tagging('*:System:Remove')
    @Decorators.timing()
    def delete_sources(self):
        system.delete_dir(self.libcloud_home_directory)

    @Decorators.tagging('AWS:Provider:Create')
    @Decorators.python_consumption()
    @Decorators.timing()
    def create_amazon_client(self, aws_access_key=None, aws_secret_key=None, region=None):
        if not aws_access_key:
            aws_access_key = self.libcloud_aws_access_key
        if not aws_secret_key:
            aws_secret_key = self.libcloud_aws_secret_key
        if not region:
            region = self.libcloud_region
        cls = get_driver(Provider.EC2)
        driver = cls(aws_access_key, aws_secret_key, region=region)
        self.libcloud_drivers.append(driver)
        driver.list_nodes()

    @Decorators.tagging('*:Provider:List')
    @Decorators.python_consumption()
    @Decorators.timing()
    def list_of_providers(self):
        for driver in self.libcloud_drivers:
            driver.list_nodes()

    @Decorators.tagging('*:Provider:Delete')
    @Decorators.python_consumption()
    @Decorators.timing()
    def delete_provider(self):
        del self.libcloud_drivers[0]

    @Decorators.tagging('AWS:Bucket:Create')
    @Decorators.python_consumption()
    @Decorators.timing()
    def create_aws_bucket(self, bucket_name):
        self.libcloud_s_drivers[0].create_container(bucket_name)
        self.bucket_name = bucket_name

    @Decorators.tagging('AWS:Bucket:Delete')
    @Decorators.python_consumption()
    @Decorators.timing()
    def delete_aws_bucket(self, bucket_name=None):
        if not bucket_name:
            bucket_name = self.bucket_name
        container = self.libcloud_s_drivers[0].get_container(container_name=bucket_name)
        for s_object in self.libcloud_s_drivers[0].list_container_objects(container):
            self.libcloud_s_drivers[0].delete_object(s_object)
        self.libcloud_s_drivers[0].delete_container(container)

    @Decorators.tagging('AWS:File:Upload')
    @Decorators.python_consumption()
    @Decorators.timing()
    def upload_file(self, filepath, object_name=None, bucket_name=None):
        if not bucket_name:
            bucket_name = self.bucket_name
        if not object_name:
            object_name = self.default_name
        container = self.libcloud_s_drivers[0].get_container(container_name=bucket_name)
        self.libcloud_s_drivers[0].upload_object(file_path=filepath,
                                                 container=container,
                                                 object_name=object_name)

    @Decorators.tagging('AWS:File:Download')
    @Decorators.python_consumption()
    @Decorators.timing()
    def download_file(self, storage_folder, object_name=None, bucket_name=None):
        if not bucket_name:
            bucket_name = self.bucket_name
        if not object_name:
            object_name = self.default_name
        s_object = self.libcloud_s_drivers[0].get_object(bucket_name, object_name)
        self.libcloud_s_drivers[0].download_object(s_object, storage_folder, overwrite_existing=True)

    @Decorators.tagging('AWS:File:Delete')
    @Decorators.python_consumption()
    @Decorators.timing()
    def delete_file(self, object_name=None, bucket_name=None):
        if not bucket_name:
            bucket_name = self.bucket_name
        if not object_name:
            object_name = self.default_name
        s_object = self.libcloud_s_drivers[0].get_object(bucket_name, object_name)
        self.libcloud_s_drivers[0].delete_object(s_object)
