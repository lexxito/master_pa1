from evaluations.decorator import Decorators
from client.client import CloudCheckr


class Evaluation:
    def __init__(self, cloudcheckr_admin_access_key, cloudcheckr_aws_access_key, cloudcheckr_aws_secret_key,
                 cloudcheckr_account_name='Amaz'):
        self.cloudcheckr_admin_access_key = cloudcheckr_admin_access_key
        self.cloudcheckr_aws_access_key = cloudcheckr_aws_access_key
        self.cloudcheckr_aws_secret_key = cloudcheckr_aws_secret_key
        self.cloudcheckr_client = CloudCheckr(access_key=self.cloudcheckr_admin_access_key)
        self.cloudcheckr_account_id = None
        self.cloudcheckr_account_name = cloudcheckr_account_name

    @Decorators.tagging('AWS:Provider:Create')
    @Decorators.timing()
    def create_aws_provider(self, account_name=None, aws_access_key=None, aws_secret_key=None):
        if not aws_access_key:
            aws_access_key = self.cloudcheckr_aws_access_key
        if not aws_secret_key:
            aws_secret_key = self.cloudcheckr_aws_secret_key
        if not account_name:
            account_name = self.cloudcheckr_account_name
        output = self.cloudcheckr_client.create_aws_account(account_name=account_name, aws_access_key=aws_access_key,
                                                            aws_secret_key=aws_secret_key)
        self.cloudcheckr_account_id = output['cc_account_id']

    @Decorators.tagging('*:Provider:Sync')
    @Decorators.timing()
    def sync_aws_account(self):
        while True:
            output = self.cloudcheckr_client.get_account(account_id=self.cloudcheckr_account_id)
            if output['LastUpdated']:
                return

    @Decorators.tagging('*:Provider:List')
    @Decorators.timing()
    def list_of_providers(self):
        self.cloudcheckr_client.get_accounts()

    @Decorators.tagging('*:Provider:Delete')
    @Decorators.timing()
    def delete_provider(self, account_name=None):
        if not account_name:
            account_name = self.cloudcheckr_account_name
        self.cloudcheckr_client.delete_account(account_name=account_name)
