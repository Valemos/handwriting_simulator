from collections import Collection
from dataclasses import dataclass
from typing import Iterator, List, Tuple

from handwriting.misc.i_lines_iterator import ILinesIterator
from handwriting.misc.i_positionable import IPositionable
from handwriting.path.curve.curve import Curve
from handwriting.path.curve.i_line_iterable import ILinesIterable
from handwriting.path.curve.point import Point
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.i_curve_collection import ICurveCollection


@dataclass
class Box:
    min_x: float
    max_x: float
    min_y: float
    max_y: float

    def get_size_x(self):
        return self.max_x - self.min_x

    def get_size_y(self):
        return self.max_y - self.min_y

    def get_size(self):
        return self.get_size_x(), self.get_size_y()


class PathShiftBox(ICurveCollection, IPositionable):
    """
    wrapper around Handwritten path or Curve
    to shift it according to it's borders

    if box_size is smaller than
    """

    def __init__(self, path: ICurveCollection):
        """
        Parameters
        ----------
        path        iterable path
        box_size    collection of two numbers (width, height)
        """
        self.box_position: Point = Point(0, 0)
        self.path = path

        self.box = self.get_lines_box(self.path.get_lines())
        self.box_size = self.box.get_size()
        self.rectangle_shift: Point = self.get_rectangle_shift(self.box)

    def set_position(self, point):
        self.box_position = point

    def get_position(self):
        return self.box_position

    def get_lines(self, shift: Point = None):
        return self.path.get_lines(self.get_iterator_shift(shift))

    def get_iterator_shift(self, position):
        if position is None:
            return self.rectangle_shift
        else:
            return position.shift(self.rectangle_shift)

    def get_curves(self) -> List[Curve]:
        return self.path.get_curves()

    @staticmethod
    def get_lines_box(lines_iterator: ILinesIterator) -> Box:

        try:
            point1, point2 = next(lines_iterator)
        except StopIteration:
            return Box(0, 0, 0, 0)

        box = Box(min_x=point1.x, max_x=point1.x, min_y=point1.y, max_y=point1.y)

        for point1, point2 in lines_iterator:
            box.min_x = min(box.min_x, point1.x, point2.x)
            box.max_x = max(box.max_x, point1.x, point2.x)

            box.min_y = min(box.min_y, point1.y, point2.y)
            box.max_y = max(box.max_y, point1.y, point2.y)

        return box

    @classmethod
    def get_rectangle_shift(cls, box: Box) -> Point:
        """
        Rectangle will be aligned to bottom left corner
        top left corner is (0, 0)
        y axis is inverted

        path_box: contains box from function get_path_box()
        """
        shift = Point(0, 0)
        # displacement from start to left border
        shift.x -= box.min_x
        # desired box height minus displacement down from beginning
        shift.y += box.get_size_y() - box.max_y

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

    def extend_height(self, new_height):
        """shift path down to match desired box height"""
        if new_height < self.box_size[1]:
            raise ValueError("new height was less than original height")

