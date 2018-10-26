import os

from BidsResource.BidsResource import CDFBidsResource, FIFBidsResource, GLABidsResource


class BidsDataset:

    def __init__(self, known_dataset_types=None):

        # self.sidecar_files = []
        self.dataset_resources = []
        self.dataset_info = {}
        self.root_dir = ''
        self.root_path = ''
        self.known_dataset_types = [CDFBidsResource, FIFBidsResource,
                                    GLABidsResource]
        if known_dataset_types is not None:
            self.known_dataset_types = known_dataset_types

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
        # description_text += 'Dict : {}'.format(self.dir_struc)

        return description_text

    def get_resource_descriptions(self):
        description = ''
        for r in self.get_resources():
            description += str(r.get_resource_description()) + '\n'

        description += 'Sidecar files:\n'
        for s in self.get_resources_sidecars():
            description += str(s) + '\n'

        return description

    def is_inside_dataset(self, path, resource_type):
        # print('Checking {} is in a resource of type {}'.format(path, resource_type.name()))
        if os.path.dirname(path) == path:
            return False
        else:
            if resource_type.matches_pattern(path):
                return True
            else:
                return self.is_inside_dataset(os.path.dirname(path), resource_type)

    def record_if_dataset(self, path, folder_dict):
        is_inside_dataset = False
        for t in self.known_dataset_types:
            if t.matches_pattern(path):
                print('Match {}, {}'.format(t, path))
                self.dataset_resources.append(t(path, folder_dict))

                return
            is_inside_dataset = self.is_inside_dataset(path, t)
            if is_inside_dataset:
                print('is_inside_dataset', is_inside_dataset)
                break

            # Far too brute forced
            # if not is_inside_dataset and os.path.isfile(path):
            #     self.sidecar_files.append(path)

    def get_resources_sidecars(self):
        all_sidecars = []
        for r in self.get_resources():
            all_sidecars.append(r.resource_sidecars)
        return all_sidecars

