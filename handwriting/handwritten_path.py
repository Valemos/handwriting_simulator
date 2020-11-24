from handwriting.curve import Point, Curve


class HandwrittenPathIterator:
    """
    this class returns pairs of points to properly draw lines on canvas
    """

    def __init__(self, obj):
        self.obj = obj

    def __next__(self):
        pass


class HandwrittenPath:
    """
    Contains name for path and list of curves (objects of type Curve),
    which represent separate sets of shifts
    """

    def __init__(self, path_name, curves: list = None):
        if curves is None:
            self.curves = []
        else:
            self.curves = curves

        self.name = path_name
        self.position = Point(0, 0)
        self._iter_curve = None

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.curves, other.curves))

    def __len__(self):
        return sum((len(curve) for curve in self.curves))



    def copy(self):
        return HandwrittenPath(str(self.name), list(self.curves))

    def get_bytes(self):

        # make name length % 4 == 0 to read and check for letter end correctly
        name_bytes = bytearray(self.name[:256].encode('utf-8'))
        size_byte = bytes((len(name_bytes)).to_bytes(1, 'big'))
        out_bytes = size_byte + name_bytes

        # save curves in bytes with
        for curve in self.curves:
            if len(curve) != 0:
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

    def set_position(self, x, y):
        """
        Sets absolute position of current path to iterate through it and get
        :param x:
        :param y:
        """
        self.curves[0].set_position(Point(x, y))

    def append_to_file(self, file_name):
        """
        Appends this instance of HandwrittenPath to file
        it can already contain other instances, so this method also adds binary size
        to read exactly one object from file in future

        :param file_name: pathlib.Path object where to append current object
        """
        with file_name.open('ab+') as fout:
            path_bytes = self.get_bytes()
            fout.write(len(path_bytes).to_bytes(4, 'big'))
            fout.write(path_bytes)

    @staticmethod
    def read_next(input_stream):
        """
        Reads object size and bytes of this size from input_stream

        :param input_stream: byte stream to read from
        :return: bytes for current object
        """
        size_bytes = input_stream.read(4)
        if size_bytes != b'':
            read_len = int.from_bytes(size_bytes, 'big')
            return input_stream.read(read_len)
        else:
            return b''

    def new_curve(self):
        """
        Creates new curve, to write shifts to it
        """
        self.curves.append(Curve())

    def append_shift(self, point: Point):
        """
        Appends relative shift point to last curve
        :param point:
        """
        self.curves[-1].append_shift(point)

    def append_absolute(self, point: Point):
        self.curves[-1].append_absolute(point)
