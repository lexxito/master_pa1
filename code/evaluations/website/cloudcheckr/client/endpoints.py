endpoints = {
  'get_accounts': {
    'path': '/account.json/get_accounts',
    'method': 'GET'
  },
  'get_best_practices': {
    'path': '/best_practice.json/get_best_practices',
    'method': 'GET'
  },
  'create_aws_account': {
    'path': '/account.json/add_account_v3',
    'params': ['account_name', 'aws_access_key', 'aws_secret_key'],
    'method': 'GET'
  },
  'get_account': {
    'path': '/account.json/get_account',
    'params': ['account_id'],
    'method': 'GET'
  },
  'delete_account': {
    'path': '/account.json/delete_account',
    'params': ['account_name'],
    'method': 'GET'
  }

}
