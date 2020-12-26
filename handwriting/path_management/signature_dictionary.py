from pathlib import Path

from handwriting.path_management.path_group import PathGroup
from handwriting.path_management.signature_dictionary_iterator import SignatureDictionaryIterator


class SignatureDictionary:
    """
    Contains multiple PathGroup canvas_objects and can give access to any object
    using PathGroup name and variant_index of an object in that group

    composite key
    """

    default_path = Path('signature.dict')
    dictionary_suffix = '.dict'

    def __init__(self, name='', path_groups: list = None):
        """
        We transform path groups list to internal dict_manager
        to enable access by indexing
        :param name:
        :param path_groups:
        """
        self.name = name

        # dict_manager holds indices of path_groups list
        self.path_groups = path_groups if path_groups is not None else []
        self.path_groups_dict = {group.name: group for group in self.path_groups}

    def __len__(self):
        return len(self.path_groups)

    def __str__(self):
        return f"{self.name}: {len(self.path_groups)}"

    def __getitem__(self, group_id):
        if isinstance(group_id, str):
            if group_id in self.path_groups_dict:
                return self.path_groups_dict[group_id]
        elif isinstance(group_id, int):
            if 0 <= group_id < len(self.path_groups):
                return self.path_groups[group_id]
        return None

    def __contains__(self, item):
        return item in self.path_groups

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.path_groups, other.path_groups))

    def __iter__(self):
        return iter(self.path_groups)

    def get_iterator(self):
        """Returns bidirectional pages_iterator for path groups and their variants"""
        return SignatureDictionaryIterator(self)

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
        Deletes group on current variant_index
        :return: new group variant_index
        """

        if 0 <= group_i < len(self.path_groups):
            if self.path_groups[group_i].name in self.path_groups_dict:
                del self.path_groups_dict[self.path_groups[group_i].name]
            self.path_groups.pop(group_i)
            return group_i % len(self.path_groups) if len(self.path_groups) > 0 else 0
        return 0

    def remove_variant(self, group_i, variant_i):
        """
        Removes path variant from group if it exists

        If we deleted all path variants, nothing will change

        :param group_i:     variant_index of group
        :param variant_i:   variant_index of path variant
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
        self.path_groups_dict[path_group.name] = path_group

    def append_path(self, group_index, path):
        if 0 <= group_index < len(self.path_groups):
            self.path_groups[group_index].append_path(path)
        else:
            raise ValueError('group variant_index invalid')

    def check_group_exists(self, group_name):
        return group_name in self.path_groups_dict

    def get_group_index_by_name(self, group_name):
        if group_name in self.path_groups_dict:
            return list(self.path_groups_dict.keys()).index(group_name)
        else:
            return None
