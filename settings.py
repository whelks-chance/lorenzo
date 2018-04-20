ckan_url = ''
ckan_org_name = ''
ckan_api_key = ''

description_keys = [
    'bids_type',
    'bids_subject',
    'bids_task_description',
    'bids_task_name',
    'bids_dataset_name'
]

try:
    from settings_local import *
except ImportError:
    pass


