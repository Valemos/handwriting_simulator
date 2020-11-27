from pathlib import Path

from handwriting.handwritten_path import HandwrittenPath
from handwriting.path_group import PathGroup

from handwriting.step_functions import *

class SignatureDictionaryPathsIterator:

    def __init__(self, obj):
        self.obj = obj
        self.cur_group = 0
        self.cur_variant = 0

    def next(self) -> HandwrittenPath:
        """Iterates step forwards and returns current element"""
        if len(self.obj) == 0:
            return None

        self.cur_variant = step_forwards(self.cur_variant, len(self.obj[self.cur_group]) - 1)
        if self.cur_variant == 0:
            self.cur_group = step_forwards(self.cur_group, len(self.obj) - 1)

    def prev(self) -> HandwrittenPath:
        """Iterates step backwards and returns current element"""
        if len(self.obj) == 0:
            return None

        mx = len(self.obj[self.cur_group]) - 1
        self.cur_variant = step_backwards(self.cur_variant, mx)
        if self.cur_variant == mx:
            self.cur_group = step_backwards(self.cur_group, len(self.obj) - 1)
            # by this moment group has changed and we need to correct current variant
            self.cur_variant = len(self.obj[self.cur_group]) - 1

    def current(self) -> HandwrittenPath:
        if 0 <= self.cur_group < len(self.obj):
            if 0 <= self.cur_variant < len(self.obj[self.cur_group]):
                return self.obj[self.cur_group][self.cur_variant]
        return None

    def current_group(self) -> PathGroup:
        if 0 <= self.cur_group < len(self.obj):
            return self.obj[self.cur_group]
        return None

    def select(self, group_i: int, variant_i: int = None):
        """Assignes indices according to arguments if they are in allowed range"""
        if 0 <= group_i < len(self.obj):
            self.cur_group = group_i
            if variant_i is None:
                self.cur_variant = 0
            elif 0 <= variant_i < len(self.obj[group_i]):
                self.cur_variant = variant_i

    def delete_group(self):
        if 0 <= self.cur_group < len(self.obj):
            self.cur_group = self.obj.remove_group(self.cur_group)

    def delete_current(self):
        if 0 <= self.cur_group < len(self.obj):
            if 0 <= self.cur_variant < len(self.obj[self.cur_group]):
                self.cur_group, self.cur_variant = self.obj.remove_variant(self.cur_group, self.cur_variant)


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

        # dictionary holds indices of path_groups list
        self._path_groups = path_groups if path_groups is not None else []

    def __len__(self):
        return len(self._path_groups)

    def __str__(self):
        return f"{self.name}: {len(self._path_groups)}"

    def __getitem__(self, group_i):
        return self._path_groups[group_i]

    def __contains__(self, item):
        return item in self._path_groups

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self._path_groups, other._path_groups))

    def __iter__(self):
        return iter(self._path_groups)

    def get_iterator(self):
        """Returns bidirectional iterator for path groups and their variants"""
        return SignatureDictionaryPathsIterator(self)

    def get_save_path(self, file_name: Path = None):
        return \
            file_name.with_suffix(self.dictionary_suffix) \
            if file_name is not None else \
            Path(self.name).with_suffix(self.dictionary_suffix)

    def save_file(self, file_name: Path = None):
        file_name = self.get_save_path(file_name)
        with file_name.open('wb+') as fout:
            for group in self._path_groups:
                group.write_to_stream(fout)

    def remove_group(self, group_i):
        """
        Deletes group on current index
        :return: new group index
        """

        if 0 <= group_i < len(self._path_groups):
            self._path_groups.pop(group_i)
            return group_i % len(self._path_groups) if len(self._path_groups) > 0 else 0
        return 0

    def remove_variant(self, group_i, variant_i):
        """
        Removes path variant from group if it exists

        If we deleted all path variants, nothing will change

        :param group_i:     index of group
        :param variant_i:   index of path variant
        :return: returns new indices to replace previous deleted indices
        """

        if 0 <= group_i < len(self._path_groups):
            group = self._path_groups[group_i]
            if 0 <= variant_i < len(group):
                group.remove_by_index(variant_i)
                return group_i, variant_i % len(group) if len(group) > 0 else 0
            return group_i, 0
        return 0, 0

    @staticmethod
    def from_file(file_path):
        """Returns instance of SignatureDictionary from file"""
        try:
            with file_path.open('rb') as fin:
                new_dictionary = SignatureDictionary(file_path.name[:file_path.name.index('.')])
                while True:
                    read_object = PathGroup.read_next(fin)
                    if read_object is not None:
                        new_dictionary.append_group(read_object)
                    else:
                        break
                return new_dictionary
        except OSError:
            return None

    def append_group(self, path_group):
        self._path_groups.append(path_group)

    def append_path(self, group_index, path):
        if 0 <= group_index < len(self._path_groups):
            self._path_groups[group_index].append_path(path)
        else:
            raise ValueError('group index invalid')
