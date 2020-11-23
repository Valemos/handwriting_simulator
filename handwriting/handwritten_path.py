from handwriting.curve import Point, Curve


class HandwrittenPath:

    def __init__(self, path_name, curves: Curve = None):

        if curves is None:
            self.curves = []
        else:
            self.curves = curves

        self.name = path_name


    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.curves, other.curves))

    def copy(self):
        return HandwrittenPath(str(self.name), list(self.curves))

    def get_bytes(self):

        # make name length % 4 == 0 to read and check for letter end correctly
        name_bytes = bytearray(self.name[:256].encode('utf-8'))
        size_byte = bytes((len(name_bytes)).to_bytes(1, 'big'))
        out_bytes = size_byte + name_bytes

        # save curves in bytes with
        for curve in self.curves:
            curve_bytes = curve.get_bytes()
            length_bytes = (len(curve_bytes)).to_bytes(4, byteorder='big')
            out_bytes += length_bytes + curve_bytes

        return out_bytes

    @staticmethod
    def from_bytes(path_bytes):
        name_len = int.from_bytes(path_bytes[:1], 'big')
        byte_i = 1 + name_len

        new_obj = HandwrittenPath((path_bytes[1: byte_i]).decode('utf-8'))
        curves = []
        while byte_i < len(path_bytes):
            curve_len = int.from_bytes(path_bytes[byte_i: byte_i + 4], byteorder='big')
            byte_i += 4

            curves.append(Curve.from_bytes(path_bytes[byte_i: byte_i + curve_len]))
            byte_i += curve_len

        new_obj.curves = curves
        return new_obj


    def set_points(self, points):
        self.points = points
        self.shifts = Curve(points)

    def append_to_file(self, file_name):
        """
        Appends this instance of HandwrittenPath to file
        it can already contain other instances, so this method also adds binary size
        to read exactly one object from file in future
        """
        with file_name.open('ab+') as fout:
            path_bytes = self.get_bytes()
            fout.write(len(path_bytes).to_bytes(4, 'big'))
            fout.write(path_bytes)


    @staticmethod
    def read_file(file_path):
        """Reads list of HandwrittenPath instances from given file"""

        paths_list = []
        with file_path.open('rb') as fin:
            size_bytes = fin.read(4)
            while size_bytes != b'':
                path_size = int.from_bytes(size_bytes, 'big')
                paths_list.append(HandwrittenPath.from_bytes(fin.read(path_size)))

                size_bytes = fin.read(4)
                if size_bytes == b'':
                    break

        return paths_list
