from handwriting.path_management.curve import Point, Curve
from handwriting.path_management.stream_savable_collection import StreamSavableCollection


class HandwrittenPathLinesIterator:
    """
    this class returns pairs of points to properly draw lines on canvas
    """

    def __init__(self, obj):
        self.path = obj

        # cannot use list pages_iterator because it will not update on container change
        self.curve_index = 0
        self.point_iterator = None
        self.cur_curve = None
        self.prev_point = None
        self.cur_point = None

    def __next__(self):
        if self.cur_point is None:
            if self.curve_index >= len(self.path):
                raise StopIteration

            self.point_iterator = self.path[self.curve_index].get_shifted_iterator()
            self.prev_point = next(self.point_iterator)
            self.cur_point = next(self.point_iterator)
        else:
            try:
                # move to next line
                self.prev_point = self.cur_point
                self.cur_point = next(self.point_iterator)
            except StopIteration:  # if curve pages_iterator stopped, than it is the last point

                # go one step forward in curves list
                if self.curve_index < len(self.path) - 1:
                    self.curve_index += 1
                    self.start_iterating_next_line()
                else:
                    raise StopIteration

        return self.prev_point, self.cur_point

    def start_iterating_next_line(self):
        self.point_iterator = self.get_curve_iterator()
        if len(self.path[self.curve_index]) == 1:
            self.prev_point = next(self.point_iterator)
            self.cur_point = self.prev_point
        else:
            self.prev_point = next(self.point_iterator)
            self.cur_point = next(self.point_iterator)

    def get_curve_iterator(self):
        return self.path[self.curve_index].get_shifted_iterator(self.prev_point)

    def new_curve(self, point):
        self.path.new_curve(point)

    def append_absolute(self, point):
        self.path.append_absolute(point)


class HandwrittenPath(StreamSavableCollection):
    """
    Contains name for path and list of components (canvas_objects of type Curve),
    which represent separate sets of shifts
    """

    child_class = Curve

    def __init__(self, name, curves: list = None):
        self.name = name
        super().__init__(curves if curves is not None else [])

    def __len__(self):
        return len(self.components)

    def __iter__(self):
        return HandwrittenPathLinesIterator(self)

    def __getitem__(self, i):
        return self.components[i]

    def set_position(self, point: Point):
        """
        Sets absolute position of current path
        to iterate through it and get all points shifted relative to new position

        Updates last absolute points for each Curve in self.components
        :param point: new position for path
        """
        if len(self.components) > 0:
            self.components[0].set_position(point)
            last_point = self.components[0].calc_last_point()
            for curve in self.components[1:]:
                last_point = curve.calc_last_point(last_point)

    def get_position(self):
        if len(self.components) > 0:
            return self.components[0].get_position()
        else:
            return Point(0, 0)

    def new_curve(self, first_point):
        curve = Curve()
        curve.calc_last_point(self.components[-1].last_absolute_point if len(self.components) > 0 else None)
        curve.append_absolute(first_point)
        self.components.append(curve)

    def append_shift(self, point: Point):
        self.components[-1].append_shift(point)

    def append_absolute(self, point: Point):
        if len(self.components) > 0:
            self.components[-1].append_absolute(point)
        else:
            self.new_curve(point)

    def empty(self):
        return self.name == '' and super().empty()

    @staticmethod
    def empty_instance():
        return HandwrittenPath('', [])

    @staticmethod
    def read_name(stream):
        return HandwrittenPath.stream_read_str(stream)

    def write_name(self, stream):
        HandwrittenPath.stream_write_str(stream, self.name)
