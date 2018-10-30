import os
import json
import pprint
import re
import requests
import sys
import settings
from BidsResource.BidsDataset import BidsDataset
from BidsResource.BidsResource import BidsResource, CDFBidsResource, FIFBidsResource, GLABidsResource
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


    # extras is a dict, must have 'dataset_name'
    def save_dataset(self, unclean_extras, tags, description=''):
        extras = []
        tags_cleaned = {}

        for key, value in unclean_extras.items():
            # print('converting', key, convert(key), value)
            if value:
                extras.append({
                    'key': self.convert(key),
                    'value': value
                })
                tags_cleaned[self.convert(key)] = value

        # for description_key in settings.description_keys:
        #     if description_key in tags_cleaned:
        #         description += '\n\n {} : {}'.format(description_key, tags_cleaned[description_key])
        # description = description.strip()

        dataset_name = re.sub(
                r'[^\x61-\x7A]|\x40|\x55|\x137', r'',
                tags_cleaned['bids_dataset_name'].lower())

        dataset_dict = {
            'name': dataset_name,
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
            "tags": tags,
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
        return dataset_name

    def add_resource(self, resource_name, dataset_name, filepath, url, mimetype,
                     type='datafile', extra_info=None):

        include_file_upload = True
        if include_file_upload:
            # If file, the content is figured out by the requests module,
            # and the data is passed as a dict
            data = {
                "package_id": dataset_name,
                "url": 'file://{}'.format(filepath),
                "name": resource_name,
                "mimetype": mimetype,
                "type": type,
                "filepath": filepath,
            }
            if extra_info:
                data.update(extra_info)
            print('\n\nresource_create data', data, '\n\n')
            response = requests.post(
                settings.ckan_url + '/api/action/resource_create',
                # data=json.dumps(data),
                data=data,
                headers={
                    "X-CKAN-API-Key": settings.ckan_api_key,
                    # 'content-type': 'multipart/form-data'
                },
                files=[('upload', open(filepath, 'rb'))]
            )
        else:
            # If no file, the content-type is application/json,
            # and data is json dumped to string
            data = {
                "package_id": dataset_name,
                "url": 'file://{}'.format(filepath),
                "name": resource_name,
                "mimetype": mimetype,
                "type": type
            }
            print('\n\nresource_create data', data, '\n\n')
            response = requests.post(
                settings.ckan_url + '/api/action/resource_create',
                data=json.dumps(data),
                headers={
                    "X-CKAN-API-Key": settings.ckan_api_key,
                    'content-type': 'application/json'
                },
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

        self.current_bids_dataset.record_if_dataset(path, d)

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

                    self.save_dataset(data_dict, [])


class BidsSidecarJSON(BidsResource):

    @staticmethod
    def name():
        return 'BidsSidecarJSON'

    @staticmethod
    def matches_pattern(filename):
        basename = os.path.basename(filename)
        parent_dir = os.path.basename(os.path.dirname(filename))
        return basename.startswith('sub-') and \
               '_task-' in basename and \
               basename.endswith('_meg.json') and \
               parent_dir == 'meg'


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
            bids_dataset.dir_struc = dir_struc
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

        new_info = bd.dataset_info
        new_info['dataset_name'] = bd.dataset_resources[0].get_subject()
        print(new_info)

        description = 'BIDS MEG Dataset for Subject {}. \n\n'.format(new_info['dataset_name'])
        tasks = []
        tags = []
        for r in bd.dataset_resources:
            assert isinstance(r, BidsResource)

            # for key, value in r.get_resource_description_dict().items():
            #     if value:
            #         description += '{} : {}<br>\n\n'.format(key, value)
            rdd = r.get_resource_description_dict()
            if 'Task' in rdd:
                tasks.append(r.get_resource_description_dict()['Task'])
            tags.extend([
                {
                    'name': r.get_subject(),
                    'vocabulary_id:': 'bids_project'
                },
                {
                    'name': r.get_task(),
                    'vocabulary_id:': 'bids_task'
                },
                {
                    'name': r.get_meg_ext(),
                    'vocabulary_id:': 'bids_meg_ext'
                }
            ])
        description += 'Tasks: ' + ', '.join(tasks)
        dataset_name = cbi.save_dataset(new_info, tags, description=description)
        if dataset_name:
            for rs in bd.get_resources_sidecars():
                for key, filepath in rs.items():
                    position_within_dataset = bd.position_within_dataset(filepath)

                    cbi.add_resource(
                        resource_name=os.path.basename(filepath),
                        dataset_name=dataset_name,
                        filepath=filepath,
                        url='',
                        mimetype='application/*',
                        extra_info={
                            'resource_filepath': position_within_dataset
                        }
                    )

            for r in bd.dataset_resources:
                assert isinstance(r, BidsResource)
                get_resource_definition_file = r.get_resource_definition_file()

                position_within_dataset = bd.position_within_dataset(r.dataset)

                cbi.add_resource(
                    resource_name=r.basename(),
                    dataset_name=dataset_name,
                    filepath=get_resource_definition_file,
                    url='',
                    mimetype=r.get_meg_ext(),
                    type='BidsResource',
                    extra_info={
                        'resource_filepath': position_within_dataset
                    }
                )

        # cbi.parse_live_json('./json_live')

