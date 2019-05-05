from requests.exceptions import ConnectionError
from evaluations import system
from evaluations.decorator import Decorators
from manageiq_client.api import ManageIQClient as MiqApi

list_of_containers = []
for container in system.docker_containers_get('manage'):
    list_of_containers.append(container.short_id)


class Evaluation:
    def __init__(self, manageiq_aws_access_key, manageiq_aws_secret_key, manageiq_home_directory,
                 manageiq_endpoint='https://127.0.0.1:8443/', manageiq_username='admin',
                 manageiq_password='smartvm', manageiq_region='us-east-2', manageiq_provider_name='API_call',
                 manageiq_ports=None, manageiq_docker_image='manageiq/manageiq:gaprindashvili-3'):
        if manageiq_ports is None:
            manageiq_ports = {'443/tcp': 8443}
        self.manageiq_home_directory = manageiq_home_directory
        self.manageiq_aws_access_key = manageiq_aws_access_key
        self.manageiq_aws_secret_key = manageiq_aws_secret_key
        self.manageiq_endpoint = manageiq_endpoint
        self.manageiq_username = manageiq_username
        self.manageiq_password = manageiq_password
        self.manageiq_region = manageiq_region
        self.manageiq_provider_name = manageiq_provider_name
        self.manageiq_ports = manageiq_ports
        self.manageiq_docker_image = manageiq_docker_image
        try:
            self.client = MiqApi(self.manageiq_endpoint + 'api',
                                 dict(user=self.manageiq_username, password=self.manageiq_password), verify_ssl=False)
        except ConnectionError:
            self.client = None
        self.provider = None

    @Decorators.tagging('*:System:Download')
    @Decorators.timing(output=True)
    def download_sources(self):
        system.docker_pull(self.manageiq_docker_image)
        size, volume = system.docker_get_images_sizes('manageiq')
        return {'size': size, 'volume': volume}

    @Decorators.tagging('*:System:Start')
    @Decorators.timing()
    def start_docker_container(self):
        system.docker_run(image=self.manageiq_docker_image, port=self.manageiq_ports)
        system.wait_service(self.manageiq_endpoint, ssl_enable=False)
        self.__init__(self.manageiq_aws_access_key, self.manageiq_aws_secret_key, self.manageiq_home_directory)

    @Decorators.tagging('*:System:Stop')
    @Decorators.timing()
    def stop_docker_container(self):
        system.docker_container_stop_and_delete('manageiq')

    @Decorators.tagging('*:System:Remove')
    @Decorators.timing()
    def delete_sources(self):
        system.docker_delete_images()
        system.delete_dir(self.manageiq_home_directory)

    @Decorators.tagging('AWS:Provider:Create')
    @Decorators.docker_consumption(list_of_containers)
    @Decorators.timing()
    def create_aws_provider(self, aws_access_key=None, aws_secret_key=None, provider_name=None,
                            provider_region=None):
        if not aws_access_key:
            aws_access_key = self.manageiq_aws_access_key
        if not aws_secret_key:
            aws_secret_key = self.manageiq_aws_secret_key
        if not provider_name:
            provider_name = self.manageiq_provider_name
        if not provider_region:
            provider_region = self.manageiq_region
        response = self.client.post(self.manageiq_endpoint + 'api/providers',
                                    type='ManageIQ::Providers::Amazon::CloudManager',
                                    name=provider_name, provider_region=provider_region,
                                    credentials={'userid': aws_access_key,
                                                 'password': aws_secret_key})
        self.provider = response['results'][0]['id']

    @Decorators.tagging('*:Provider:Sync')
    @Decorators.docker_consumption(list_of_containers)
    @Decorators.timing()
    def sync_aws_provider(self):
        while True:
            if self.client.collections.flavors.all:
                return

    @Decorators.tagging('*:Provider:List')
    @Decorators.docker_consumption(list_of_containers)
    @Decorators.timing()
    def list_of_providers(self):
        while True:
            if self.client.collections.providers.all:
                return

    @Decorators.tagging('*:Provider:Delete')
    @Decorators.docker_consumption(list_of_containers)
    @Decorators.timing()
    def delete_provider(self, provider=None):
        if not provider:
            provider = self.provider
        self.client.delete(self.manageiq_endpoint + 'api/providers/' + str(provider))
        while True:
            if not self.client.collections.flavors.all:
                return
