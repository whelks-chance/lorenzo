import os
import json
import pprint
import re
import requests
import sys

import settings
from extract_bid_filename_data import extract_bids_filename_data


class CKANbidsImport:
    def __init__(self):
        self.errors = []
        self.all_exts = []
        self.all_exts_size = []
        self.file_data = {}

    def print_all(self, dir_struc):

        print(pprint.pformat(
            dir_struc
        ))

        print()
        print(self.all_exts)
        print(len(self.all_exts))

        print()
        print(self.file_data)

        print()
        print(self.errors)

    def convert(self, name, pre='bids_', post=''):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return '{}{}{}'.format(
            pre,
            re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace(' ', '_'),
            post
        )


    # tags is a dict, must have 'dataset_name'
    def save_dataset(self, tags):
        extras = []
        tags_cleaned = {}
        description = ''

        for key, value in tags.items():
            # print('converting', key, convert(key), value)
            if value:
                extras.append({
                    'key': self.convert(key),
                    'value': value
                })
                tags_cleaned[self.convert(key)] = value

        for description_key in settings.description_keys:
            if description_key in tags_cleaned:
                description += '\n\n' + tags_cleaned[description_key]
        description = description.strip()

        dataset_dict = {
            'name': re.sub(
                r'[^\x61-\x7A]|\x40|\x55|\x137', r'',
                tags_cleaned['bids_dataset_name'].lower()
            ),
            'owner_org': settings.ckan_org_name,

            "license_title": None,
            "maintainer": None,
            "private": False,
            "maintainer_email": None,
            "num_tags": 0,
            "author": None,
            "author_email": None,
            "state": "active",
            "version": None,
            "type": "dataset",
            "resources": [
            ],
            "num_resources": 0,
            # "tags": [tags],
            "groups": [
            ],
            "license_id": None,
            "isopen": None,
            "url": None,
            "notes": description,
            "extras": extras,
            "title": tags_cleaned['bids_dataset_name'],
        }

        dataset_name = ''
        print(json.dumps(dataset_dict))
        # Make the HTTP request.
        response = requests.post(
            settings.ckan_url + '/api/action/package_create',
            headers={
                'Authorization': settings.ckan_api_key,
                'content-type': 'application/json'
            },
            data=json.dumps(dataset_dict))
        print(response.status_code)
        print(response.reason)
        print(response.text)

        response_obj = response.json()
        if response_obj['success']:
            dataset_name = response_obj['result']['name']
        else:
            if response.reason == 'Conflict':
                print("\n\nConflict Error, will update instead\n\n")

                response2 = requests.post(
                    settings.ckan_url + '/api/action/package_update',
                    headers={
                        'Authorization': settings.ckan_api_key,
                        'content-type': 'application/json'
                    },
                    data=json.dumps(dataset_dict))

                print(response2.status_code)
                print(response2.reason)
                print(response2.text)
                response_obj2 = response2.json()
                dataset_name = response_obj2['result']['name']

        self.add_resource(
            'Source - zip',
            dataset_name,
            '/home/ianh/cubric/lorenzo/sub-meguk0354/meg/sub-meguk0354_task-resteyesopen_meg.json.zip',
            '',
            "application/zip"
        )

        self.add_resource(
            'Source - json',
            dataset_name,
            '/home/ianh/cubric/lorenzo/sub-meguk0354/meg/sub-meguk0354_task-resteyesopen_meg.json',
            '',
            "application/json"
        )

    def add_resource(self, resource_name, dataset_name, filepath, url, mimetype):
        data = {
            "package_id": dataset_name,
            # "url": url,
            "name": resource_name,
            # "format": "text/html"
            "mimetype": mimetype
        }
        print('\n\n', data, '\n\n')

        response = requests.post(
            settings.ckan_url + '/api/action/resource_create',
            data=data,
            headers={
                "X-CKAN-API-Key": settings.ckan_api_key,
                # 'content-type': 'multipart/form-data'
            },
            files=[('upload', open(filepath, 'rb'))]
        )

        print(response.status_code)
        print(response.reason)
        print(response.text)
        response_obj = response.json()

    def print_file(self, path):

        with open(path,  'r') as file_handle:
            print(file_handle.read())

    def json_to_keyvalue(self, path, save=False):
        print('JSON', path)

        data = {
            'subject': '',
            'task': '',
            'type': ''
        }

        # sub-meguk0354_task-resteyesopen_meg.json
        # sub - meguk0354_fid.json

        name_without_ext = str(os.path.basename(path)).replace('.json', '')
        path_arr = name_without_ext.split('_')
        print(path_arr)

        if path_arr[0].startswith('sub-'):
            data['subject'] = path_arr[0].replace('sub-', '')

        if path_arr[1].startswith('task-'):
            data['task'] = path_arr[1].replace('task-', '')

        data['type'] = path_arr[2]

        with open(path,  'r') as file_handle:
            json_blob = json.load(file_handle)

            for key in json_blob.keys():
                if key in data:
                    print('key already present', key)
                if json_blob[key] and not isinstance(json_blob[key], dict):
                    data[key] = json_blob[key]

        data['dataset_name'] = name_without_ext
        print(pprint.pformat(data))
        if save:
            self.save_dataset(data)
        return data

    # Original crawling code from https://stackoverflow.com/a/25226267/2943238 Emanuele Paolini
    def path_to_dict(self, path):
        d = {'name': os.path.basename(path)}
        # print('Found : ', d['name'])

        if not os.access(path, os.R_OK):
            print('Cannot access ', path)
            return d

        if d['name'].startswith('.') or d['name'].startswith('__'):
            return d

        if os.path.isdir(path):
            d['type'] = "directory"

            d['children'] = [self.path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]

            d['type'] = "file"
            d['ext'] = '.'.join(d['name'].split('.')[1:])
            d['size'] = str(os.path.getsize(path))
            self.all_exts.append(d['ext'])
            self.all_exts_size.append({
                'size': str(d['size']),
                'path': str(path)
            })

            # if int(d['size']) < 2000:
            #     print('\n', path)
            #     print(d['size'])
            #     print_file(path)

            print(d['name'])

            self.file_data[path] = extract_bids_filename_data(d['name'])

            # if 'sub' in d['name'] and 'task' in d['name'] and d['ext'].endswith('json'):
            #     self.json_to_keyvalue(path)

        return d


if __name__ == '__main__':
    print(sys.argv)

    cbi = CKANbidsImport()

    path = '/home/ianh/cubric/lorenzo/sub-meguk0354'

    if len(sys.argv) > 1:
        path = sys.argv[1]

    try:
        os.mkdir('json')
    except:
        pass

    for ds in os.listdir(path):
        if ds.startswith('sub'):

            dir_struc = cbi.path_to_dict(os.path.join(path, ds))

            cbi.print_all(dir_struc)
            output_file = os.path.join('./json', '{}.json'.format(ds))

            with open(output_file, 'w') as struc_file:
                struc_file.write(json.dumps(dir_struc, indent=4))
