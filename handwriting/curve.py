import pickle

from handwriting.point import Point
from handwriting.stream_savable import StreamSavable


class CurveIterator:
    """
    This class iterates through shifts in Curve
    and returns absolute values of points
    """
    def __init__(self, obj, initial_shift=None):
        self.obj = obj
        self.first_point = obj.components[0] if len(obj.components) > 0 else None

        # current point must be initialized with last_absolute_point
        # to correctly continue iterations relative to last curve
        self.cur_point = initial_shift if initial_shift is not None else Point(0, 0)

        # cannot use list iterator because it will not update if container was changed
        self.shift_index = 0

    def __next__(self):
        """
        Each iteration shifts previous point by next shift value from Curve shifts
        :return: next element
        """

        if self.first_point is None:
            raise StopIteration

        if 0 <= self.shift_index < len(self.obj):
            # self.obj.components contains list of shifts relative to previous point
            self.cur_point = self.cur_point.shift(self.obj[self.shift_index])
            self.shift_index += 1
            return self.cur_point
        else:
            raise StopIteration


class Curve(StreamSavable):
    """
    Contains set of shifts for handwritten path
    with each point stored as shift relative to previous point
    """


    def __init__(self, shifts=None):
        self.components = [] if shifts is None else shifts

        # absolute point used to calculate next shift point for append handler
        self.last_absolute_point = self.calc_last_point()

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.components, other.components))

    def __len__(self):
        return len(self.components)

    def __getitem__(self, i):
        return self.components[i]

    def get_shifted_iterator(self, shift: Point = None):
        return CurveIterator(self, shift)

    def get_position(self):
        if len(self.components) > 0:
            return self.components[0]
        else:
            return Point(0, 0)

    def set_position(self, point: Point):
        """
        Zero position in shift list plays a role of shift relative to (0, 0) position
        :param point: point to set position to
        """
        self.components[0] = point

    def shift(self, amount: Point):
        """
        components curve's first point with some displacement

        :param amount: shift amount
        """
        self.components[0] = self.components[0].shift(amount)

    @staticmethod
    def convert_abs_to_shifts(abs_points: list):
        """
        Takes as input list of Point objects
        :param abs_points: list of absolute points
        :return:
        """
        new_points = [abs_points[0]]
        prev_point = abs_points[0]
        for point in abs_points[1:]:
            new_points.append(point.prev_point.get_shift(prev_point))
            prev_point = point
        return new_points

    def append_shift(self, point: Point):
        self.components.append(point)
        self.last_absolute_point = self.last_absolute_point.shift(point)

    def append_absolute(self, point: Point):
        """
        Method appends shift relative to previous absolute point recorded in self.last_absolute_point
        value of self.last_absolute_point is changed for the next append operation
        """

        self.components.append(point.get_shift(self.last_absolute_point))
        self.last_absolute_point = point

    @staticmethod
    def from_absolute(abs_points: list):
        """Returns instance of Curve for absolute values of points"""
        if len(abs_points) == 0:
            return Curve()

        new_curve = Curve()
        for p in abs_points:
            new_curve.append_absolute(p)
        return new_curve

    def calc_last_point(self):
        """
        Method calculates absolute position of last point using self.shifts list.
        First point in self.shifts is considered as a starting point.
        Each next point is a relative shift from previous point.

        If shifts list is empty, resulting point is considered to be (0, 0)

        :returns absolute value for last point in shifts list
        """
        if len(self.components) == 0:
            return Point(0, 0)

        point = self.components[0]
        for i in range(1, len(self.components)):
            point = point.shift(self.components[i])
        return point


    # object saving

    @classmethod
    def read_next(cls, byte_stream):
        """
        This handler assumes, that first 4 bytes on top of file stream is length of a pickle object
        and reads N bytes from stream to deserialize shifts list and create Curve object from it

        loads shifts list from bytes and initializes Curve object
        :param byte_stream: stream of bytes to read from
        :return: new Curve object or None, if object was empty or not corrupted.
        """

        try:
            curve_len = byte_stream.read(4)
            N = int.from_bytes(curve_len, 'big')
            if N == 0:
                return None
            else:
                return Curve(pickle.loads(byte_stream.read(N)))

        except pickle.UnpicklingError:
            print("error loading curve from bytes")
            return None

    def write_to_stream(self, byte_stream):
        """
        dump shifts list to bytes
        if list is empty, write 4 zero bytes to indicate empty object
        """
        if len(self.components) == 0:
            byte_stream.write(bytes(4))
            return

        try:
            b = pickle.dumps(self.components)
            len_b = (len(b)).to_bytes(4, byteorder='big')
            byte_stream.write(len_b)
            byte_stream.write(b)
        except pickle.PicklingError:
            print("error saving curve to bytes")

    @staticmethod
    def empty_instance():
        return Curve()
