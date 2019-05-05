import json
import requests
from evaluations import system
from evaluations.decorator import Decorators

list_of_containers = []
for container in system.docker_containers_get('mist'):
    list_of_containers.append(container.short_id)


class Evaluation:
    def __init__(self, mist_aws_access_key, mist_aws_secret_key, mist_token, mist_home_directory,
                 mist_name='serh@zhaw.ch', mist_pass='123987', mist_endpoint='http://127.0.0.1',
                 mist_github_source='https://github.com/mistio/mist.io/releases/download/v3.0.0/docker-compose.yml',
                 mist_region='us-east-2', mist_provider_name='Test'):
        self.mist_home_directory = mist_home_directory
        self.mist_token = mist_token
        self.mist_aws_access_key = mist_aws_access_key
        self.mist_aws_secret_key = mist_aws_secret_key
        self.mist_name = mist_name
        self.mist_pass = mist_pass
        self.mist_github_source = mist_github_source
        self.mist_endpoint = mist_endpoint
        self.mist_region = mist_region
        self.mist_provider_name = mist_provider_name
        self.mist_headers = {'Authorization': self.mist_token}
        self.mist_provider_id = None

    @Decorators.tagging('*:System:Download')
    @Decorators.timing(output=True)
    def download_sources(self):
        system.wget_download(self.mist_home_directory, self.mist_github_source)
        system.docker_compose_command('pull', self.mist_home_directory)
        size, volume = system.docker_get_images_sizes('mist')
        return {'size': size, 'volume': volume}

    @Decorators.tagging('*:System:Start')
    @Decorators.timing()
    def start_docker_compose(self):
        system.docker_compose_command('up', self.mist_home_directory, method='Popen')
        system.wait_service(self.mist_endpoint)
        system.docker_create_user(self.mist_home_directory,
                                  login=self.mist_name, password=self.mist_pass)

    @Decorators.tagging('*:System:Stop')
    @Decorators.timing()
    def down_docker_compose(self):
        system.docker_compose_command('down', self.mist_home_directory)

    @Decorators.tagging('*:System:Remove')
    @Decorators.timing()
    def delete_sources(self):
        system.docker_delete_images()
        system.delete_dir(self.mist_home_directory)

    @Decorators.tagging('AWS:Provider:Create')
    @Decorators.docker_consumption(list_of_containers)
    @Decorators.timing()
    def create_amazon_provider(self, aws_secret_key=None, aws_access_key=None, region=None, name=None):
        if not name:
            name = self.mist_provider_name
        if not aws_access_key:
            aws_access_key = self.mist_aws_access_key
        if not aws_secret_key:
            aws_secret_key = self.mist_aws_secret_key
        if not region:
            region = self.mist_region
        output = requests.post(self.mist_endpoint + '/api/v1/clouds', headers=self.mist_headers, data=json.dumps(
            {'title': name,
             'provider': 'ec2',
             'region': region,
             'api_key': aws_access_key,
             'api_secret': aws_secret_key}
        ))
        self.mist_provider_id = json.loads(output.content)['id']

    @Decorators.tagging('*:Provider:List')
    @Decorators.docker_consumption(list_of_containers)
    @Decorators.timing()
    def list_of_providers(self):
        requests.get(self.mist_endpoint + '/api/v1/clouds', headers=self.mist_headers)

    @Decorators.tagging('*:Provider:Delete')
    @Decorators.docker_consumption(list_of_containers)
    @Decorators.timing()
    def delete_amazon_provider(self, provider_id=None):
        if not provider_id:
            if self.mist_provider_id:
                provider_id = self.mist_provider_id
            else:
                raise Exception("Provide provider id")
        requests.delete(self.mist_endpoint + '/api/v1/clouds' + '/' + provider_id, headers=self.mist_headers)
