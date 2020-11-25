from pathlib import Path

from handwriting.handwritten_path import HandwrittenPath
from handwriting.path_group import PathGroup


class SignatureDictionaryIterator:

    def __init__(self, obj):
        self.obj = obj
        self.cur_group = 0
        self.cur_variant = 0

    def next(self) -> HandwrittenPath:
        """Iterates step forwards and returns current element"""
        if len(self.obj) == 0:
            return None

        self.cur_variant += 1
        if self.cur_variant >= len(self.obj[self.cur_group]):
            # go to next loop
            self.cur_variant = 0
            self.cur_group = (self.cur_group + 1) % len(self.obj)

        return self.current()

    def prev(self) -> HandwrittenPath:
        """Iterates step backwards and returns current element"""
        if len(self.obj) == 0:
            return None

        self.cur_variant -= 1
        if self.cur_variant < 0:
            # go to next loop
            self.cur_group -= 1
            if self.cur_group < 0:
                self.cur_group = len(self.obj) - 1
            self.cur_variant = len(self.obj[self.cur_group]) - 1

        return self.current()

    def current(self) -> HandwrittenPath:
        if 0 <= self.cur_group < len(self.obj):
            if 0 <= self.cur_variant < len(self.obj[self.cur_group]):
                return self.obj[self.cur_group][self.cur_variant]
        return None

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

        # dictionary holds indices of path_groups list
        self._path_groups = path_groups if path_groups is not None else []

    def __len__(self):
        return len(self._path_groups)

    def __str__(self):
        return f"{self.name} [{len(self._path_groups)}]"

    def __getitem__(self, group_i):
        """
        Uses pair of values to access
        :param group_i: index of group
        :return: group
        """

        # calls to dictionary will raise exceptions if indices not correct
        return self._path_groups[group_i]

    def __contains__(self, item):
        return item in self._path_groups

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self._path_groups, other._path_groups))


    def get_iterator(self):
        return SignatureDictionaryIterator(self)

    def save_file(self, file_name=None):
        file_name = file_name if file_name is not None else Path(self.name).with_suffix(self.dictionary_suffix)
        with file_name.open('wb+') as fout:
            for group in self._path_groups:
                group.write_to_stream(fout)

    def remove_by_index(self, group_i, variant_i):
        """
        Removes path variant from group if it exists
        :param group_i:     index of group
        :param variant_i:   index of path variant
        """
        if 0 <= group_i < len(self._path_groups):
            group = self._path_groups[group_i]
            if 0 <= variant_i < len(group):
                group.remove_by_index(variant_i)
                return True
        return False


    @staticmethod
    def from_file(file_path):
        """Returns instance of SignatureDictionary from file"""
        with file_path.open('rb') as fin:
            new_dictionary = SignatureDictionary(file_path.name[:file_path.name.index('.')])
            while True:
                read_object = PathGroup.read_next(fin)
                if read_object is not None:
                    new_dictionary.append_group(read_object)
                else:
                    break
            return new_dictionary

    def append_group(self, path_group):
        self._path_groups.append(path_group)

    def append_path(self, group_index, path):
        if 0 <= group_index < len(self._path_groups):
            self._path_groups[group_index].append_path(path)
        else:
            raise ValueError('group index invalid')
