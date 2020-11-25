from pathlib import Path

from handwriting.path_group import PathGroup


class SignatureDictionary:
    """
    Contains multiple PathGroup objects and can give access to any object
    using PathGroup name and index of an object in that group

    composite key
    """

    dictionary_suffix = '.dict'

    def __init__(self, name='', path_groups=None):
        self.name = name
        self.save_path = Path(name).with_suffix(self.dictionary_suffix)
        self.path_groups = {gr.name: gr for gr in path_groups} if path_groups is not None else {}

    def __getitem__(self, group_name: str, index: int = 0):
        """
        Uses pair of values to access
        :param group_name:  name of group user wants to access
        :param index:       index of object to get from group
        :return:
        """

        # calls to this dictionary will raise exceptions if indices not correct
        return self.path_groups[group_name].paths[index]

    def __contains__(self, item):
        return item in self.path_groups

    def save_file(self, file_name=None):
        file_name = file_name if file_name is not None else Path(self.name)

    def from_file(self, file_path):
        # todo: write file loading
        pass
