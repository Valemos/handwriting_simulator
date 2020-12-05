from pathlib import Path

from handwriting.path_management.handwritten_path import HandwrittenPath
from handwriting.path_management.path_group import PathGroup

from handwriting.step_functions import *
from handwriting.cyclic_iterator import CyclicIterator, EmptyIterator

class SignatureDictionaryPathsIterator:

    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.group_iter = CyclicIterator(self.dictionary.path_groups)
        self._update_variant()

    def _update_variant(self):
        if self.group_iter.current() is not None:
            self.variant_iter = self.group_iter.current().get_iterator()
        else:
            self.variant_iter = EmptyIterator()

    def next(self) -> HandwrittenPath:
        """Iterates one step forward"""

        self.variant_iter.next()
        if self.variant_iter.object_index == 0:
            # pages_iterator jumped to next loop
            self.group_iter.next()
            self._update_variant()

    def prev(self) -> HandwrittenPath:
        """Iterates step backwards and returns current element"""

        self.variant_iter.prev()
        if self.variant_iter.object_index == self.variant_iter.get_max():
            # pages_iterator jumped to next loop
            self.group_iter.prev()
            self._update_variant()

    def current(self) -> HandwrittenPath:
        return self.variant_iter.current()

    def current_group(self) -> PathGroup:
        return self.group_iter.current()

    def select(self, group_i: int, variant_i: int = None):
        """Assignes indices according to arguments if they are in allowed range"""
        self.group_iter.select(group_i)
        self._update_variant()
        self.variant_iter.select(variant_i if variant_i is not None else 0)

    def delete_group(self):
        if self.group_iter.current() is not None:
            idx = self.dictionary.remove_group(self.group_iter.object_index)
            self.group_iter.select(idx)
            self._update_variant()

    def delete_current(self):
        if self.group_iter.current() is not None:
            if self.variant_iter.current() is not None:
                idx = self.dictionary.remove_variant(self.group_iter.object_index, self.variant_iter.object_index)
                self.group_iter.select(idx[0])
                self._update_variant()
                self.variant_iter.select(idx[1])


class SignatureDictionary:
    """
    Contains multiple PathGroup objects and can give access to any object
    using PathGroup name and index of an object in that group

    composite key
    """

    default_path = Path('signature.dict')
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
        self.path_groups = path_groups if path_groups is not None else []
        self.groups_dict = {group.name: group for group in self.path_groups}

    def __len__(self):
        return len(self.path_groups)

    def __str__(self):
        return f"{self.name}: {len(self.path_groups)}"

    def __getitem__(self, group_name):
        if group_name in self.groups_dict:
            return self.groups_dict[group_name]
        else:
            print("Error, cannot find group")
            return None

    def __contains__(self, item):
        return item in self.path_groups

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.path_groups, other.path_groups))

    def __iter__(self):
        return iter(self.path_groups)

    def get_iterator(self):
        """Returns bidirectional pages_iterator for path groups and their variants"""
        return SignatureDictionaryPathsIterator(self)

    def get_save_path(self, file_name: Path = None):
        return \
            file_name.with_suffix(self.dictionary_suffix) \
            if file_name is not None else \
            Path(self.name).with_suffix(self.dictionary_suffix)

    def save_file(self, file_name: Path = None):
        file_name = self.get_save_path(file_name)
        with file_name.open('wb+') as fout:
            for group in self.path_groups:
                group.write_to_stream(fout)

    def remove_group(self, group_i):
        """
        Deletes group on current index
        :return: new group index
        """

        if 0 <= group_i < len(self.path_groups):
            if self.path_groups[group_i].name in self.groups_dict:
                del self.groups_dict[self.path_groups[group_i].name]
            self.path_groups.pop(group_i)
            return group_i % len(self.path_groups) if len(self.path_groups) > 0 else 0
        return 0

    def remove_variant(self, group_i, variant_i):
        """
        Removes path variant from group if it exists

        If we deleted all path variants, nothing will change

        :param group_i:     index of group
        :param variant_i:   index of path variant
        :return: returns new indices to replace previous deleted indices
        """

        if 0 <= group_i < len(self.path_groups):
            group = self.path_groups[group_i]
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
        self.path_groups.append(path_group)
        self.groups_dict[path_group.name] = path_group

    def append_path(self, group_index, path):
        if 0 <= group_index < len(self.path_groups):
            self.path_groups[group_index].append_path(path)
        else:
            raise ValueError('group index invalid')
