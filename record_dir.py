import os
import json
import pprint
import re
from abc import ABCMeta, abstractmethod

import requests
import sys

import settings
from extract_bid_filename_data import extract_bids_filename_data


class CKANbidsImport:
    def __init__(self):
        self.current_bids_dataset = BidsDataset()
        self.ds_dirs = []
        self.subject_files = []
        self.errors = []
        self.all_exts = []
        self.all_exts_size = []
        self.file_data = {}
        self.dataset_info = {}

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

                # self.add_resource(
                #     'Source - zip',
                #     dataset_name,
                #     '/home/ianh/cubric/lorenzo/sub-meguk0354/meg/sub-meguk0354_task-resteyesopen_meg.json.zip',
                #     '',
                #     "application/zip"
                # )
                #
                # self.add_resource(
                #     'Source - json',
                #     dataset_name,
                #     '/home/ianh/cubric/lorenzo/sub-meguk0354/meg/sub-meguk0354_task-resteyesopen_meg.json',
                #     '',
                #     "application/json"
                # )

    def add_resource(self, resource_name, dataset_name, filepath, url, mimetype):
        data = {
            "package_id": dataset_name,
            # "url": url,
            "name": resource_name,
            # "format": "text/html"
            "mimetype": mimetype
        }
        print('\n\nresource_create data', data, '\n\n')

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

        print('\n\n Adding resource_view_create')
        data = {
            "view_type": 'filetree_view',
            "title": 'File Tree',
            "resource_id": response_obj['result']['id']
        }
        response = requests.post(
            settings.ckan_url + '/api/action/resource_view_create',
            data=json.dumps(data),
            headers={
                "X-CKAN-API-Key": settings.ckan_api_key,
                'content-type': 'application/json'
            }
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
        # print(pprint.pformat(data))
        if save:
            self.save_dataset(data)
        return data

    # def is_gla_format(self, filename):
    #     basename = os.path.basename(filename)
    #     parent_dir = os.path.basename(os.path.dirname(filename))
    #     return os.path.isdir(filename) and basename.endswith('_meg') and parent_dir == 'meg'
    #
    # def is_fif_dataset(self, filename):
    #     basename = os.path.basename(filename)
    #     parent_dir = os.path.basename(os.path.dirname(filename))
    #     print(basename, '-----', parent_dir)
    #     return basename.startswith('sub-') and basename.endswith('.fif') and parent_dir == 'meg'
    #
    # def is_meg_dataset(self, filename):
    #     basename = os.path.basename(filename)
    #     parent_dir = os.path.basename(os.path.dirname(filename))
    #     return os.path.isdir(filename) and \
    #            basename.startswith('sub') and \
    #            basename.endswith('.ds') and \
    #            parent_dir == 'meg'

    # Original crawling code from https://stackoverflow.com/a/25226267/2943238 Emanuele Paolini
    def path_to_dict(self, path):
        d = {
            'name': os.path.basename(path),
            'full_path': path
        }

        if not os.access(path, os.R_OK):
            print('Cannot access ', path)
            self.errors.append('Cannot access {}'.format(path))
            return d

        if d['name'].startswith('.') or d['name'].startswith('__'):
            return d

        self.current_bids_dataset.record_if_dataset(path)
        # # print('\nChecking', path, self.is_meg_dataset(path))
        # if self.is_meg_dataset(path):
        #     print('Is MEG')
        #     self.current_bids_dataset.add_meg_dataset(path)
        #     # print('\n\nDS folder', d, '\n\n')
        #     self.ds_dirs.append(d)
        #
        # if self.is_fif_dataset(path):
        #     print('Is fif')
        #     self.current_bids_dataset.add_fif_dataset(path)
        #     # print('\n\nDS folder', d, '\n\n')
        #     self.ds_dirs.append(d)
        #
        # if self.is_gla_format(path):
        #     print('Is gla')
        #     self.current_bids_dataset.add_gla_dataset(path)
        #     # print('\n\nDS folder', d, '\n\n')
        #     self.ds_dirs.append(d)

        if os.path.isdir(path):
            d['type'] = "directory"

            d['children'] = [
                self.path_to_dict(
                    os.path.join(path, x)
                ) for x in os.listdir(path)
            ]

        else:
            d['type'] = "file"
            d['ext'] = '.'.join(d['name'].split('.')[1:])
            d['size'] = str(os.path.getsize(path))
            self.all_exts.append(d['ext'])
            self.all_exts_size.append({
                'size': str(d['size']),
                'path': str(path)
            })

            if d['name'].startswith('sub'):
                self.subject_files.append(d)

        filename_metadata = extract_bids_filename_data(d['name'])
        self.file_data[path] = filename_metadata
        d['filename_metadata'] = filename_metadata

        for k in filename_metadata.keys():
            if not k.startswith('_'):
                self.dataset_info[k] = filename_metadata[k]

                # if 'sub' in d['name'] and 'task' in d['name'] and d['ext'].endswith('json'):
                #     self.json_to_keyvalue(path)

        return d

    def get_dataset_info(self, json_blob):
        dataset_name = json_blob['filename_metadata']['sub']

        data_dict = {
            'dataset_name': dataset_name
        }

        field_maps = {
            'sub': 'Subject',
            'task': 'Task',
            'meg': 'MEG Extension',
            'ses': 'Session',
            'run': 'Run',
            'proc': 'Processed'
        }

        for k in json_blob['dataset_info'].keys():
            if k in field_maps:
                data_dict[field_maps[k]] = json_blob['dataset_info'][k]

        return data_dict

    def parse_metadata_json(self, path):
        files = list(os.listdir(path))
        for f in files[:2]:
            filepath = os.path.join(path, f)
            # print(filepath)

            if '.ds.json' in f:
                with open(filepath, 'r') as fp1:
                    json_blob = json.load(fp1)

                    self.add_resource(
                        json_blob['name'],
                        json_blob['filename_metadata']['sub'],
                        filepath=filepath, url=None,
                        mimetype='application/json'
                    )
            elif '-subjects.json':
                pass
            else:
                with open(filepath, 'r') as fp2:
                    json_blob = json.load(fp2)

                    data_dict = self.get_dataset_info(json_blob)

                    self.save_dataset(data_dict)


class BidsResource(metaclass=ABCMeta):
    MEG = 1
    FIF = 2
    GLA = 3

    def __init__(self, dataset):
        self.dataset = dataset
        self.type = type

    def basename(self):
        return os.path.basename(self.dataset).split('_meg')[0]

    def get_meg_ext(self):
        idx = os.path.basename(self.dataset).rfind('_meg')
        return os.path.basename(self.dataset)[idx:]

    def get_subject(self):
        return self.basename().split('_')[0].split('-')[1]

    def get_task(self):
        bits = self.basename().split('_')
        for bit in bits:
            if 'task' in bit:
                return bit.split('-')[1]

    def get_session(self):
        bits = self.basename().split('_')
        for bit in bits:
            if 'ses' in bit:
                return bit.split('-')[1]

    def get_aquisition(self):
        bits = self.basename().split('_')
        for bit in bits:
            if 'acq' in bit:
                return bit.split('-')[1]

    def get_processed(self):
        bits = self.basename().split('_')
        for bit in bits:
            if 'proc' in bit:
                return bit.split('-')[1]

    def get_run(self):
        bits = self.basename().split('_')
        for bit in bits:
            if 'run' in bit:
                return bit.split('-')[1]

    def get_resource_description(self):
        return '{}\nSubject: {}\n' \
               'Meg ext: {}\n' \
               'Task: {}\n'.format(
                    self.dataset,
                    self.get_subject(),
                    self.get_meg_ext(),
                    self.get_task()
                )

    @staticmethod
    @abstractmethod
    def matches_pattern(filename):
        raise NotImplementedError


class CDFBidsResource(BidsResource):

    @staticmethod
    def matches_pattern(filename):
        basename = os.path.basename(filename)
        parent_dir = os.path.basename(os.path.dirname(filename))
        return os.path.isdir(filename) and \
               basename.startswith('sub') and \
               '_task-' in basename and \
               basename.endswith('_meg.ds') and \
               parent_dir == 'meg'


class FIFBidsResource(BidsResource):

    @staticmethod
    def matches_pattern(filename):
        basename = os.path.basename(filename)
        parent_dir = os.path.basename(os.path.dirname(filename))
        print(basename, '-----', parent_dir)
        return basename.startswith('sub-') and \
               '_task-' in basename and \
               basename.endswith('_meg.fif') and \
               parent_dir == 'meg'


class GLABidsResource(BidsResource):

    @staticmethod
    def matches_pattern(filename):
        basename = os.path.basename(filename)
        parent_dir = os.path.basename(os.path.dirname(filename))
        return os.path.isdir(filename) and \
               basename.startswith('sub-') and \
               '_task-' in basename and \
               basename.endswith('_meg') and \
               parent_dir == 'meg'


class BidsDataset:

    def __init__(self):

        self.dataset_resources = []
        self.dataset_info = {}
        self.root_dir = ''
        self.root_path = ''

    def known_dataset_types(self):
        return [CDFBidsResource, FIFBidsResource, GLABidsResource]

    def get_resources(self):
        return self.dataset_resources

    def __repr__(self):
        # return str(self.get_resources())
        return str(self.__dict__)

    def description(self):
        description_text = 'Bids Dataset\nHas {} MEG dataset(s).\n'.format(
            len(self.dataset_resources)
        )
        description_text += 'Root folder is {}\n'.format(self.root_dir)
        description_text += 'Root path is {}\n'.format(self.root_path)
        description_text += 'Resources: {}'.format(self.get_resource_descriptions())

        return description_text

    def get_resource_descriptions(self):
        description = ''
        for r in self.get_resources():
            description += str(r.get_resource_description()) + '\n'
        return description

    def record_if_dataset(self, path):
        for t in self.known_dataset_types():
            if t.matches_pattern(path):
                print('Match {}, {}'.format(t, path))
                self.dataset_resources.append(t(path))


if __name__ == '__main__':

    bids_datasets = []

    cbi = CKANbidsImport()
    # sub-meguk0354
    # path = '/home/ianh/cubric/lorenzo/'

    path = '/home/ianh/PycharmProjects/lorenzo/data'

    if len(sys.argv) > 1:
        path = sys.argv[1]

    try:
        # making output directory
        os.mkdir('json')
    except:
        pass

    for ds in os.listdir(path):
        # print(ds)
        # loop through sub dirs, look for sub-
        dir_path = os.path.join(path, ds)
        if ds.startswith('sub') and os.path.isdir(dir_path):

            bids_dataset = BidsDataset()

            cbi.current_bids_dataset = bids_dataset

            # The main workhorse of the import class
            # Takes a folder and traverses the whole structure,
            # looking for meg datasets and sidecars files
            # to add as resources to a bids dataset
            # returns a complex dict of the folder structure
            # internally updates the current_bids_dataset with what it discovered along the way
            dir_struc = cbi.path_to_dict(dir_path)
            dir_struc['dataset_info'] = cbi.dataset_info

            bids_dataset.dataset_info = cbi.dataset_info
            bids_dataset.root_dir = ds
            bids_dataset.root_path = dir_path

            # cbi.print_all(dir_struc)
            output_file = os.path.join('./json', '{}.json'.format(ds))

            with open(output_file, 'w') as struc_file:
                struc_file.write(json.dumps(dir_struc, indent=4))

            for ds_dir in cbi.ds_dirs:
                output_file = os.path.join('./json', '{}.json'.format(ds_dir['name']))

                with open(output_file, 'w') as ds_struc_file:
                    ds_struc_file.write(json.dumps(ds_dir, indent=4))

            output_file = os.path.join('./json', '{}-subjects.json'.format(ds))
            with open(output_file, 'w') as subject_files_file:
                subject_files_file.write(json.dumps(cbi.subject_files, indent=4))

            # Reset things for the next dir
            cbi.ds_dirs = []
            cbi.subject_files = []
            cbi.dataset_info = {}

            bids_datasets.append(bids_dataset)

    with open('errors.log', 'w') as err_file:
        err_file.write(
            json.dumps(
                sorted(cbi.errors),
                indent=4)
        )

    for bd in bids_datasets:
        assert isinstance(bd, BidsDataset)
        print('\n***\n')
        print(bd.description())

        # cbi.parse_live_json('./json_live')

