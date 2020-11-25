from pathlib import Path
import os

from handwriting.stream_savable_collection import StreamSavableCollection
from handwriting.handwritten_path import HandwrittenPath

class PathGroup(StreamSavableCollection):
    """contains several versions of the same handwritten path"""

    save_file_format = "{0}.hndw"
    temp_file = Path("temp.bin")

    child_class = HandwrittenPath

    def __init__(self, name, paths=None, save_file=None):
        super().__init__(paths if paths is not None else [])

        self.name = name

    def __str__(self):
        return f"{self.name}: {len(self.components)}"

    def initialize_save_path(self, save_file=None):
        if save_file is None:
            self.save_file = Path(self.save_file_format.format('components' if self.name == '' else self.name))
        else:
            self.save_file = save_file

    def initialize_save_file(self, save_file=None):
        """
        Must be called before append operations only once
        writes name of path group to file
        """
        self.initialize_save_path(save_file)
        with self.save_file.open('wb+') as fout:
            self.stream_write_str(self.name, fout)

    @staticmethod
    def read_name(stream):
        return PathGroup.stream_read_str(stream)

    def write_name(self, stream):
        PathGroup.stream_write_str(self.name, stream)

    def append_path(self, another_path: HandwrittenPath):
        """
        must call initialize_save_file before append operations
        appends path to group and to components file
        """

        self.components.append(another_path)
        with self.save_file.open('ab+') as fout:
            another_path.write_to_stream(fout)

    def save_to_file(self, file_mode='ab+', file_path=None):
        """
        Appends bytes from write_to_stream to save file, or, if provided, to file_path with given file write mode

        :param file_mode: file write mode, one of 'a' or 'w' for open() method
        :param file_path: path, where to save current object,
                            if it is None object will be saved to default _save_path
        """
        file_path = file_path if file_path is not None else self.save_file

        with file_path.open(file_mode) as fout:
            self.write_to_stream(fout)

    def append_to_file(self, file_path=None):
        file_path = file_path if file_path is not None else self.save_file

        with file_path.open('ab+') as fout:
            self.write_to_stream(fout)

    def remove_by_index(self, index):
        """
        Removes path form list by index
        Reads file and at the same time writes necessary data to temp file
        Renames temp file to self.save_file
        """

        self.components.pop(index)
        current_index = 0
        temp_file = Path('temp.bin')
        with self.save_file.open('rb') as fin, temp_file.open("wb+") as fout:
            while True:
                obj_bytes = HandwrittenPath.read_next(fin)
                if obj_bytes != b'':
                    if current_index != index:
                        fout.write(obj_bytes)
                        fout.write(len(obj_bytes).to_bytes(4, 'big'))
                    current_index += 1
                else:
                    break


        os.remove(self.save_file)
        os.rename(temp_file, self.save_file)

    def empty(self):
        return self.name == '' and super().empty()

    @staticmethod
    def empty_instance():
        return PathGroup('', [])

    @staticmethod
    def from_file(file_path):
        with file_path.open('rb') as fin:
            return PathGroup.read_next(fin)
