import json
from abc import ABCMeta, abstractmethod
import os


class BidsResource(metaclass=ABCMeta):
    MEG = 1
    FIF = 2
    GLA = 3

    def __init__(self, dataset, folder_dict=None):
        self.folder_dict = folder_dict
        self.dataset = dataset
        # self.type = type
        self.resource_sidecars = {}

        self.check_for_sidecars()
        # self.path_dict = path_to_dict(dataset)

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

    def get_resource_definition_file(self):
        output_file = os.path.join('./json', '{}.json'.format(self.folder_dict['name']))

        with open(output_file, 'w') as ds_struc_file:
            ds_struc_file.write(json.dumps(self.folder_dict, indent=4))
        return output_file

    @staticmethod
    @abstractmethod
    def matches_pattern(filename):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def name():
        raise NotImplementedError

    def check_for_sidecars(self):
        for f in os.listdir(os.path.dirname(self.dataset)):
            print(f)
            if f.startswith('sub-{}'.format(self.get_subject())):

                if '_task-{}'.format(self.get_task()) in f:
                    print('Sidecar : {}'.format(f))
                    full_path = os.path.join(os.path.dirname(self.dataset), f)

                    if f.endswith('_events.tsv'):
                        self.resource_sidecars['events'] = full_path
                        print('     Events sidecar')
                    if f.endswith('_meg.json'):
                        self.resource_sidecars['meg_json'] = full_path
                        print('     JSON sidecar')
                    if f.endswith('_channels.tsv'):
                        self.resource_sidecars['channels'] = full_path
                        print('     Channels sidecar')

                else:
                    if f.endswith('_coordsystem.json'):
                        self.resource_sidecars['coords'] = full_path
                        print('     Coords sidecar')
                    if '_headshape' in f:
                        self.resource_sidecars['headshape'] = full_path
                        print('     Headshape sidecar')
                    if '_fid.json' in f:
                        self.resource_sidecars['fid'] = full_path
                        print('     FID sidecar')
                    if '_fidinfo.json' in f:
                        print('     FIDinfo sidecar')
                        self.resource_sidecars['fid_info'] = full_path

class CDFBidsResource(BidsResource):
    @staticmethod
    def name():
        return 'CDFBidsResource'

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
    def name():
        return 'FIFBidsResource'

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
    def name():
        return 'GLABidsResource'

    @staticmethod
    def matches_pattern(filename):
        basename = os.path.basename(filename)
        parent_dir = os.path.basename(os.path.dirname(filename))
        return os.path.isdir(filename) and \
               basename.startswith('sub-') and \
               '_task-' in basename and \
               basename.endswith('_meg') and \
               parent_dir == 'meg'
