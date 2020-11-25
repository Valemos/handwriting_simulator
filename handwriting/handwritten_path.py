from handwriting.curve import Point, Curve


class HandwrittenPathIterator:
    """
    this class returns pairs of points to properly draw lines on canvas
    """

    def __init__(self, obj):
        self.obj = obj
        self.curve_iterator = iter(obj.curves)
        self.point_iterator = None
        self.cur_curve = None
        self.prev_point = None
        self.cur_point = None

    def __next__(self):
        if self.cur_point is None:
            self.cur_curve = next(self.curve_iterator)
            self.point_iterator = iter(self.cur_curve)
            self.prev_point = next(self.point_iterator)
            self.cur_point = next(self.point_iterator)
        else:
            try:
                # move to next line
                self.prev_point = self.cur_point
                self.cur_point = next(self.point_iterator)
            except StopIteration:  # if curve iterator stopped go to next curve
                self.cur_curve = next(self.curve_iterator)
                self.cur_curve.shift(self.prev_point)
                self.point_iterator = iter(self.cur_curve)
                self.prev_point = next(self.point_iterator)
                self.cur_point = next(self.point_iterator)

        return self.prev_point, self.cur_point


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

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.curves, other.curves))

    def __len__(self):
        return sum((len(curve) for curve in self.curves))

    def __iter__(self):
        return HandwrittenPathIterator(self)

    def copy(self):
        return HandwrittenPath(str(self.name), list(self.curves))

    def get_bytes(self):
        """
        Records HandwrittenPath.name length and than name itself

        If name is empty, but curves list is not,
        writs 4 zero bytes to indicate that name is empty, and continue writing Curve objects

        If name is not empty, but path does not contain any Curves,
        writs name as usual, and instead of no bytes at all for Curves list,
        writs zero length for Curves objects list

        If object is empty, or in other words name and curves are empty, we return b''

        :return: binary representation of this object
        """
        # make name length % 4 == 0 to read and check for letter end correctly
        name_bytes = self.name[:256].encode('utf-8')
        name_size = (len(name_bytes)).to_bytes(1, 'big')
        out_bytes = name_size + name_bytes

        # save curves in bytes with
        for curve in self.curves:
            if len(curve) != 0:
                curve_bytes = curve.get_bytes()
                out_bytes += curve_bytes

        return out_bytes

    @staticmethod
    def read_next(byte_stream):
        """
        Function assumes, that first byte is a length N of an object name
        than it reads N bytes, decodes it as HandwrittenPath name
        and than reads Curve objects from the same byte stream

        If N is zero, than it indicates, that object has no name, but still contains Curve objects

        If N is not zero, reads the name, than reads first object

        :param byte_stream: stream to read from
        :return: New HandwrittenPath object, or None, if this object was empty
        """

        # if bytestream does not contain any bytes, name_len equals to 0
        name_len = int.from_bytes(byte_stream.read(1), 'big')

        # if name_len is zero, than new_path.name will be empty string ''
        new_path = HandwrittenPath((byte_stream.read(name_len)).decode('utf-8'))


        # check if first Curve object is not empty
        first_curve = Curve.read_next(byte_stream)
        if first_curve is not None:
            curves = [first_curve]
            while True:
                read_curve = Curve.read_next(byte_stream)
                if read_curve is not None:
                    curves.append(read_curve)
                else:
                    break
            new_path.curves = curves

        # if first curve object was empty, but name was not, new_path still will be returned
        return new_path if not new_path.empty() else None

    def set_position(self, point: Point):
        """
        Sets absolute position of current path
        to iterate through it and get all points shifted relative to new position
        :param point: new position for path
        """
        self.curves[0].set_position(point)

    def get_position(self):
        return self.curves[0].shifts[0]

    def write_to_stream(self, byte_stream):
        """
        Appends binary representation of this instance of HandwrittenPath to byte stream
        stream can already contain other instances

        :param byte_stream: byte stream object with method .write where to write current object
        """
        byte_stream.write(self.get_bytes())

    def new_curve(self, first_point):
        """
        This function must be called after user click
        Creates new curve, to write shifts to it
        Also if this curve is not first, calculates shift relative to end of last curve
        :param first_point: next absolute point to start Curve with
        """

        # (0, 0) point will not shift first point of a Curve
        # and absolute value will be recorded as first value
        last_point = self.curves[-1].last_absolute_point if len(self.curves) > 0 else Point(0, 0)
        self.curves.append(Curve([first_point.get_shift(last_point)]))

    def append_shift(self, point: Point):
        """
        Appends shift point relative to last curve
        :param point: shift amount
        """
        self.curves[-1].append_shift(point)

    def append_absolute(self, point: Point):
        """
        Appends absolute value of point to last curve
        :param point: absolute position
        """
        self.curves[-1].append_absolute(point)

    def empty(self):
        """
        To read objects from files correctly, we assume that empty object is the object
        which have name '' and at the same time curves list is empty

        if name is not empty, this path could have no objects in it.
        but, at the same time, have a name

        if name is empty, but objects is not, it is also a valid object,
        because we do not necessarly need a name to access this path from PathGroup
        """
        return self.name == '' and len(self.curves) == 0
