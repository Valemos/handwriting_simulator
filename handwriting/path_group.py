from pathlib import Path
import os

from handwriting.handwritten_path import HandwrittenPath

class PathGroup:
    """contains several versions of the same handwritten path"""

    save_file_format = "{0}.hndw"
    temp_file = Path("temp.bin")

    def __init__(self, name, paths=None, save_file=None):
        self.name = name
        self.paths = paths if paths is not None else []
        self.initialize_save_file(save_file)

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.paths, other.paths))

    def initialize_save_file(self, save_file):
        """
        Must be called before any append operation
        writes name of path group to file
        """
        self.save_file = save_file if save_file is not None else Path(self.save_file_format.format(self.name))
        with self.save_file.open('wb+') as fout:
            self.write_name_to_stream(self.name, fout)

    def append_path(self, another_path: HandwrittenPath):
        """appends path to group and to paths file"""

        self.paths.append(another_path)
        with self.save_file.open('ab+'):
            another_path.write_to_stream(self.save_file)

    def append_to_file(self, file_path=None):
        """
        Appends current group name length and name itself to file,
        than appends each HandwrittenPath object to the same file

        :param file_path: path, where to save current object,
                            if it is None object will be saved to default save_path
        """
        file_path = file_path if file_path is not None else self.save_file

        with file_path.open('ab+') as fout:
            self.write_to_stream(fout)

    # todo: move EXACTLY THE SAME code from classes PathGroup, HandwrittenPath to separate class

    @staticmethod
    def write_name_to_stream(name, stream):
        """
        Writes name length and name itself to string
        :param name:
        :param stream:
        """
        name_bytes = name[:256].encode('utf-8')
        name_size = (len(name_bytes)).to_bytes(1, 'big')
        stream.write(name_size)
        stream.write(name_bytes)

    @staticmethod
    def read_name_from_stream(stream):
        # if byte_stream does not contain any bytes, name_len equals to 0
        name_len = int.from_bytes(stream.read(1), 'big')

        # if name_len is zero, than empty string '' will be returned
        return (stream.read(name_len)).decode('utf-8')


    def write_to_stream(self, byte_stream):
        """
        Writes object binary representation to byte stream
        :param byte_stream: stream where to write
        """

        self.write_name_to_stream(self.name, byte_stream)
        for path in self.paths:
            path.write_to_stream(byte_stream)

    @staticmethod
    def read_next(byte_stream):
        """
        Function assumes, that first byte is a length N of an object name
        than it reads N bytes, decodes it as PathGroup name
        and than reads HandwrittenPath objects from the same byte stream

        If N is zero, than it indicates, that object has no name, but still contains HandwrittenPath objects

        If N is not zero, reads the name, than reads first object

        :param byte_stream: stream to read from
        :return: New PathGroup object, or None, if this object was empty
        """

        # if byte_stream does not contain any bytes, name_len equals to 0
        name_len = int.from_bytes(byte_stream.read(1), 'big')

        # if name_len is zero, than new_path.name will be empty string ''
        new_group = PathGroup((byte_stream.read(name_len)).decode('utf-8'))
        new_group = PathGroup('')

        # check if first Curve object is not empty
        first_path = HandwrittenPath.read_next(byte_stream)
        if first_path is not None:
            paths = [first_path]
            while True:
                read_curve = HandwrittenPath.read_next(byte_stream)
                if read_curve is not None:
                    paths.append(read_curve)
                else:
                    break
            new_group.paths = paths

        return new_group if not new_group.empty() else None

    def empty(self):
        """Emptyness criteria is the same as it HandwrittenPath"""
        return self.name == '' and len(self.paths) == 0

    def remove_by_index(self, index):
        """
        removes path form list by index
        reads file and at the same time writes necessary data to temp file
        renames temp file to self.save_file
        """

        self.paths.pop(index)
        current_index = 0
        with self.save_file.open('rb') as fin, self.temp_file.open("wb+") as fout:
            path_bytes = HandwrittenPath.read_next(fin)
            while path_bytes != b'':
                if current_index != index:
                    fout.write(len(path_bytes).to_bytes(4, 'big'))
                    fout.write(path_bytes)

                path_bytes = HandwrittenPath.read_next(fin)
                current_index += 1

        os.remove(self.save_file)
        os.rename(self.temp_file, self.save_file)
