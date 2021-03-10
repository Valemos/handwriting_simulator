from pathlib import Path

from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.cyclic_iterator import CyclicIterator
from handwriting.path.stream_savable_collection import IStreamSavableCollection


class PathGroup(IStreamSavableCollection):
    """contains several versions of the same handwritten path"""

    save_file_format = "{0}.hndw"
    default_file_name = 'paths'

    def __init__(self, name, paths=None, save_file=None):
        super().__init__(paths)

        self.name = name
        self.save_file = save_file
        self.initialize_save_path(self.save_file)

    def __str__(self):
        return f"{self.name}: {len(self.components)}"

    def __iter__(self):
        return iter(self.components)

    def get_iterator(self):
        return CyclicIterator(self.components)

    def initialize_save_path(self, save_file=None):
        if save_file is None:
            self.save_file = Path(self.save_file_format.format(self.default_file_name if self.name == '' else self.name))
        else:
            self.save_file = save_file

    def append_path(self, another_path: HandwrittenPath):
        """
        appends path to group and to components file
        """

        self.components.append(another_path)

    def save_to_file(self, file_mode='ab+', file_path=None):
        """
        Appends bytes from write_to_stream to save file, or, if provided, to file_path with given file write mode

        :param file_mode: file write mode, one of 'a' or 'w' for open() method
        :param file_path: path, where to save current object,
                            if it is None object will be saved to default _save_path
        """
        self.initialize_save_path(file_path)
        with self.save_file.open(file_mode) as fout:
            self.write_to_stream(fout)

    def append_to_file(self, file_path=None):
        self.initialize_save_path(file_path)
        with self.save_file.open('ab+') as fout:
            self.write_to_stream(fout)

    def remove_by_index(self, index):
        """Removes HandwrittenPath form list by variant_index"""
        self.components.pop(index)

    def empty(self):
        return self.name == '' and len(self.components) > 0

    @staticmethod
    def empty_instance():
        return PathGroup('', [])

    @staticmethod
    def from_file(file_path):
        with file_path.open('rb') as fin:
            return PathGroup.read_next(fin)
