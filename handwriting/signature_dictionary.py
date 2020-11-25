from pathlib import Path
from handwriting.path_group import PathGroup

class SignatureDictionary:
    """
    Contains multiple PathGroup objects and can give access to any object
    using PathGroup name and index of an object in that group

    composite key
    """

    dictionary_suffix = '.dict'

    def __init__(self, name='', path_groups: list = None):
        """
        We transform path groups list to internal dictionary
        to enable access by indexing
        :param name:
        :param path_groups:
        """
        self.name = name
        self._save_path = Path(name).with_suffix(self.dictionary_suffix)
        self._path_groups = {gr.name: gr for gr in path_groups} if path_groups is not None else {}

    def __str__(self):
        return f"{self.name} {{{len(self._path_groups)}}}"

    def __getitem__(self, group_name: str, index: int = 0):
        """
        Uses pair of values to access
        :param group_name:  name of group user wants to access
        :param index:       index of object to get from group
        :return:
        """

        # calls to this dictionary will raise exceptions if indices not correct
        return self._path_groups[group_name].components[index]

    def __contains__(self, item):
        return item in self._path_groups

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self._path_groups.values(), other._path_groups.values()))

    def keys(self):
        return self._path_groups.keys()

    def values(self):
        return self._path_groups.values()

    def items(self):
        return self._path_groups.items()

    def save_file(self, file_name=None):
        file_name = file_name if file_name is not None else Path(self.name).with_suffix(self.dictionary_suffix)
        with file_name.open('wb+') as fout:
            for group_name, group in self.items():
                group.write_to_stream(fout)

    @staticmethod
    def from_file(file_path):
        """Returns instance of SignatureDictionary from file"""
        with file_path.open('rb') as fin:
            new_dictionary = SignatureDictionary(file_path.name[:file_path.name.index('.')])
            while True:
                read_object = PathGroup.read_next(fin)
                if read_object is not None:
                    new_dictionary.append(read_object)
                else:
                    break
            return new_dictionary

    def append(self, path_group):
        self._path_groups[path_group.name] = path_group
