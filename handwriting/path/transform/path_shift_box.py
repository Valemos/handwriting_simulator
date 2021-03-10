from collections import Collection
from typing import Iterator, List

from handwriting.path.curve.curve import Curve
from handwriting.path.curve.i_line_iterable import ILineIterable
from handwriting.path.curve.point import Point
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.i_curve_collection import ICurveCollection


class PathShiftBox(ICurveCollection):
    """
    wrapper around Handwritten path or Curve
    to shift it according to it's borders

    if box_size is smaller than
    """

    def __init__(self, path: ICurveCollection, box_size=None):
        """
        Parameters
        ----------
        path        iterable path
        box_size    collection of two numbers (width, height)
        """
        self.box_position: Point = Point(0, 0)
        self.path = path

        self.box, self.box_size = self.get_box_parameters(self.path, box_size)
        self.rectangle_shift: Point = self.get_rectangle_shift(self.box, self.box_size)

    def set_position(self, point):
        self.box_position = point

    def get_position(self):
        return self.box_position

    def get_iterator(self, shift: Point = None) -> Iterator:
        shift.shift_inplace(self.rectangle_shift)
        return self.path.get_iterator(shift)

    def get_lines(self, shift: Point = None):
        shift.shift_inplace(self.rectangle_shift)
        return self.path.get_lines(shift)

    def get_curves(self) -> List[Curve]:
        return self.path.get_curves()

    @staticmethod
    def get_path_box(path: ICurveCollection, position=None):
        """Returns list of 4 values with path borders in order: left right top bottom"""

        if path.points_count() < 2:
            # path iterator will not return any pair of points
            return [0] * 4

        box = None
        for point1, point2 in path.get_iterator(position):
            if box is None:
                box = [point1.x, point1.x, point1.y, point1.y]

            box[0] = min(box[0], point1.x, point2.x)
            box[1] = max(box[1], point1.x, point2.x)

            box[2] = min(box[2], point1.y, point2.y)
            box[3] = max(box[3], point1.y, point2.y)

        return box

    @classmethod
    def get_rectangle_shift(cls, path_box, size) -> Point:
        """
        Rectangle will be aligned to bottom left corner
        top left corner is (0, 0)
        y axis is inverted

        path_box: contains box from function get_path_box()
        """
        shift = Point(0, 0)
        # displacement from start to left border
        shift.x -= path_box[0]
        # desired box height minus displacement down from beginning
        shift.y += size[1] - path_box[3]

        return shift

    def get_border_path(self):
        path = HandwrittenPath()

        cur_point = self.box_position.copy()
        path.append_absolute(cur_point)

        cur_point.x += self.box_size[0]  # go left
        path.append_absolute(cur_point.copy())
        cur_point.y += self.box_size[1]  # go down
        path.append_absolute(cur_point.copy())
        cur_point.x -= self.box_size[0]  # go right
        path.append_absolute(cur_point.copy())
        cur_point.y -= self.box_size[1]  # go up
        path.append_absolute(cur_point.copy())

        return path

    def get_box_parameters(self, path, desired_size):
        if not isinstance(desired_size, Collection) or len(desired_size) != 2:
            raise ValueError("box size must be a tuple of size 2 (width, height)")

        box = self.get_path_box(path)
        return box, (
            self.get_box_dimension(box[0], box[1], desired_size[0]),  # width
            self.get_box_dimension(box[2], box[3], desired_size[1])   # height
        )

    @staticmethod
    def get_box_dimension(border_start, border_end, desired=None):
        border_size = border_end - border_start
        if desired is None:
            return border_size

        return desired if desired >= border_size else border_size
