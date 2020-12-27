from handwriting.path_management.curve import Point, Curve
from handwriting.path_management.path_lines_iterator import PathLinesIterator
from handwriting.path_management.stream_savable_collection import StreamSavableCollection


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
        return PathLinesIterator(self)

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
