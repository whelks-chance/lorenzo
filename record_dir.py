import os
import json
import pprint
import re
import requests
import settings

all_exts = []
all_exts_size = []


def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return 'l.' + re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace(' ', '_')


# tags is a dict, must have 'dataset_name'
def save_dataset(tags):
    extras = []
    tags_cleaned = {}
    description = ''

    for key, value in tags.items():
        # print('converting', key, convert(key), value)
        if value:
            extras.append({
                'key': convert(key),
                'value': value
            })
            tags_cleaned[convert(key)] = value

    for description_key in settings.description_keys:
        if description_key in tags_cleaned:
            description += '\n\n' + tags_cleaned[description_key]
    description = description.strip()

    dataset_dict = {
        'name': re.sub(
            r'[^\x61-\x7A]|\x40|\x55|\x137', r'',
            tags_cleaned['l.dataset_name'].lower()
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
        "title": tags_cleaned['l.dataset_name'],
    }

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
    # print(response.content)
    print(response.text)

def print_file(path):

    with open(path,  'r') as file_handle:
        print(file_handle.read())


def json_to_keyvalue(path):
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
    save_dataset(data)
    return data


# Original crawling code from https://stackoverflow.com/a/25226267/2943238 Emanuele Paolini
def path_to_dict(path):
    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
    else:
        d['type'] = "file"
        d['ext'] = '.'.join(d['name'].split('.')[1:])
        d['size'] = os.path.getsize(path)
        all_exts.append(d['ext'])
        all_exts_size.append({
            'size': d['size'],
            'path': path
        })

        # if int(d['size']) < 2000:
        #     print('\n', path)
        #     print(d['size'])
        #     print_file(path)

        if 'sub' in d['name'] and 'task' in d['name'] and d['ext'].endswith('json'):
            json_to_keyvalue(path)

    return d


dir_struc = path_to_dict('/home/ianh/cubric/lorenzo/sub-meguk0354')


print(pprint.pformat(
    dir_struc
))

print()
print(all_exts)
print(len(all_exts))

with open('dir_struc.json', 'w') as struc_file:
    struc_file.write(json.dumps(dir_struc, indent=4))