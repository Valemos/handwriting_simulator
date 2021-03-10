from pathlib import Path

from handwriting.path.curve.point import Point
from handwriting.path.path_group import PathGroup
from handwriting.path.signature_dictionary_iterator import SignatureDictionaryIterator
from handwriting.path.transform.path_shift_box import PathShiftBox


class SignatureDictionary:
    """
    Contains multiple PathGroup canvas_objects and can give access to any object
    using PathGroup name and variant_index of an object in that group

    composite key
    """

    dictionary_suffix = '.dict'
    default_path = Path('signature').with_suffix(dictionary_suffix)

    def __init__(self, name='', groups: list = None):
        """
        We transform path groups list to internal dict_manager
        to enable access by indexing
        :param name:
        :param groups:
        """
        self.name = name

        # dict_manager holds indices of groups list
        self.groups = groups if groups is not None else []
        self.groups_dict = {group.name: group for group in self.groups}

    def __len__(self):
        return len(self.groups)

    def __str__(self):
        return f"{self.name}: {len(self.groups)}"

    def __getitem__(self, group_id):
        if isinstance(group_id, str):
            if group_id in self.groups_dict:
                return self.groups_dict[group_id]
        elif isinstance(group_id, int):
            if 0 <= group_id < len(self.groups):
                return self.groups[group_id]
        return None

    def __contains__(self, item):
        return item in self.groups

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.groups, other.groups))

    def __iter__(self):
        return iter(self.groups)

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
            for group in self.groups:
                group.write_to_stream(fout)

    def remove_group(self, group_i):
        """
        Deletes group for given index or group name
        :return: next group variant index
        """

        if isinstance(group_i, str):
            if self.remove_group_by_name(group_i):
                return self.get_group_index(group_i)

        elif isinstance(group_i, int):
            if self.remove_group_by_index(group_i):
                return self.get_group_index(group_i)

        return 0

    def remove_group_by_index(self, group_i):
        if self.group_in_bounds(group_i):
            del self.groups_dict[self.groups[group_i].name]
            self.groups.pop(group_i)
            return True

        return False

    def remove_group_by_name(self, group_name):
        if group_name in self.groups_dict:
            self.groups.remove(self.groups_dict[group_name])
            del self.groups_dict[group_name]
            return True

        return False

    def remove_variant(self, group_i, variant_i):
        """
        Removes path variant from group if it exists

        If we deleted all path variants, nothing will change

        :param group_i:     variant_index of group
        :param variant_i:   variant_index of path variant
        :return: returns new indices to replace previous deleted indices
        """

        if 0 <= group_i < len(self.groups):
            group = self.groups[group_i]
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
        self.groups.append(path_group)
        self.groups_dict[path_group.name] = path_group

    def append_path(self, group_index, path):
        if 0 <= group_index < len(self.groups):
            self.groups[group_index].append_path(path)
        else:
            raise ValueError('group index invalid')

    def check_group_exists(self, group_name):
        return group_name in self.groups_dict

    def get_group_index_by_name(self, group_name):
        if group_name in self.groups_dict:
            return list(self.groups_dict.keys()).index(group_name)
        else:
            return None

    def group_in_bounds(self, group_i):
        return 0 <= group_i < len(self.groups)

    def get_group_index(self, index):
        return index % len(self.groups) if len(self.groups) > 0 else 0

    def get_max_letter_size(self):
        """Returns collection of two values (width, height)"""
        max_size = [0, 0]
        for group in self.groups:
            for letter in group:
                letter.set_position(Point(0, 0))
                box = PathShiftBox.get_path_box(letter)
                box_width = PathShiftBox.get_box_dimension(box[0], box[1])
                box_height = PathShiftBox.get_box_dimension(box[2], box[3])
                max_size[0] = max(box_width, max_size[0])
                max_size[1] = max(box_height, max_size[1])

        return max_size
