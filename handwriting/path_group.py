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
        self.save_file = save_file if save_file is not None else Path(self.save_file_format.format(name))

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.paths, other.paths))

    def append_path(self, another_path: HandwrittenPath):
        """appends path to group and to paths file"""

        self.paths.append(another_path)
        another_path.append_to_file(self.save_file)

    @staticmethod
    def from_file(file_path):
        """
        Reads HandwrittenPaths from file
        returns instance of PathGroup with fields
        name        from name of file without suffix
        paths       read from file
        save_file   the same as given file
        """

        paths = []
        with file_path.open('rb') as fin:
            path_bytes = HandwrittenPath.read_next(fin)
            while path_bytes != b'':
                paths.append(HandwrittenPath.from_bytes(path_bytes))
                path_bytes = HandwrittenPath.read_next(fin)

        name = file_path.name
        group_name = name[:name.index('.')] if '.' in name else name
        return PathGroup(group_name, paths, file_path)

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