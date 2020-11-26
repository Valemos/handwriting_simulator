import io

from handwriting.curve import Point, Curve
from handwriting.stream_savable_collection import StreamSavableCollection


class HandwrittenPathIterator:
    """
    this class returns pairs of points to properly draw lines on canvas
    """

    def __init__(self, obj):
        self.obj = obj

        # cannot use list iterator because it will not update on container change
        self.curve_index = 0
        self.point_iterator = None
        self.cur_curve = None
        self.prev_point = None
        self.cur_point = None

    def __next__(self):
        if self.cur_point is None:
            if 0 <= self.curve_index < len(self.obj.components):
                self.cur_curve = self.obj[self.curve_index]
            else:
                raise StopIteration

            self.point_iterator = self.cur_curve.get_shifted_iterator()
            self.prev_point = next(self.point_iterator)
            self.cur_point = next(self.point_iterator)
        else:
            try:
                # move to next line
                self.prev_point = self.cur_point
                self.cur_point = next(self.point_iterator)
            except StopIteration:  # if curve iterator stopped, than it is the last point

                # go one step forward in curves list
                self.curve_index += 1
                if 0 <= self.curve_index < len(self.obj):
                    self.cur_curve = self.obj[self.curve_index]
                else:
                    self.curve_index -= 1
                    raise StopIteration

                # save previous absolute position to next curve to iteratre relative to new absolute position
                self.point_iterator = self.cur_curve.get_shifted_iterator(self.prev_point)
                self.prev_point = next(self.point_iterator)
                self.cur_point = next(self.point_iterator)

        return self.prev_point, self.cur_point


class HandwrittenPath(StreamSavableCollection):
    """
    Contains name for path and list of components (objects of type Curve),
    which represent separate sets of shifts
    """


    child_class = Curve

    def __init__(self, name, curves: list = None):
        self.name = name
        super().__init__(curves if curves is not None else [])

    def __len__(self):
        return len(self.components)

    def __iter__(self):
        """
        This iterator changes last_absolute_point values inside Curves according to new object position
        :return: iterator
        """
        return HandwrittenPathIterator(self)

    def __getitem__(self, i):
        return self.components[i]

    def set_position(self, point: Point):
        """
        Sets absolute position of current path
        to iterate through it and get all points shifted relative to new position
        :param point: new position for path
        """
        self.components[0].set_position(point)

    def get_position(self):
        if len(self.components) > 0:
            return self.components[0].get_position()
        else:
            return Point(0, 0)

    def new_curve(self, first_point):
        """
        This handler must be called after user click
        Creates new curve, to write shifts to it

        Also if this curve is not first, calculates shift relative to end of last curve

        :param first_point: next absolute point to start Curve with
        """

        # (0, 0) point will not shift first first point of a Curve
        # and absolute value will be recorded as first value
        last_point = self.components[-1].last_absolute_point if len(self.components) > 0 else Point(0, 0)
        self.components.append(Curve([first_point.get_shift(last_point)]))

    def append_shift(self, point: Point):
        """
        Appends shift point relative to last curve
        :param point: shift amount
        """
        self.components[-1].append_shift(point)

    def append_absolute(self, point: Point):
        """
        Appends absolute value of point to last curve
        :param point: absolute position
        """
        self.components[-1].append_absolute(point)

    def empty(self):
        return self.name == '' and super().empty()

    @staticmethod
    def empty_instance():
        return HandwrittenPath('', [])

    @staticmethod
    def read_name(stream):
        return HandwrittenPath.stream_read_str(stream)

    def write_name(self, stream):
        HandwrittenPath.stream_write_str(self.name, stream)
