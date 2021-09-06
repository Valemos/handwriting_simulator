from pathlib import Path

from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.misc.cyclic_iterator import CyclicIterator
from handwriting.misc.stream_savable import IStreamSavable
from handwriting.path.i_collection import ICollection


class PathGroup(ICollection, IStreamSavable):
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

    def get_paths_iterator(self):
        return CyclicIterator(self.components)

    def initialize_save_path(self, save_file=None):
        if save_file is None:
            self.save_file = Path(self.save_file_format.format(self.default_file_name if self.name == '' else self.name))
        else:
            self.save_file = save_file

    def append_path(self, another_path: HandwrittenPath):
        self.components.append(another_path)

    def save_to_file(self, file_mode='ab+', file_path=None):
        self.initialize_save_path(file_path)
        with self.save_file.open(file_mode) as fout:
            self.write_to_stream(fout)

    def append_to_file(self, file_path=None):
        self.initialize_save_path(file_path)
        with self.save_file.open('ab+') as fout:
            self.write_to_stream(fout)

    def remove_by_index(self, index):
        self.components.pop(index)

    @staticmethod
    def empty_instance():
        return PathGroup('', [])

    @staticmethod
    def from_file(file_path: Path):
        with file_path.open('rb') as fin:
            return PathGroup.read_next(fin)
