from typing import Tuple

from handwriting.misc.i_lines_iterator import ILinesIterator
from handwriting.path.curve.point import Point


class CurveLinesIterator(ILinesIterator):

    def __init__(self, points_iterator):
        self.points_iterator = points_iterator
        self.cur_point = self.points_iterator.cur_point
        self.prev_point = None
        self._finished = False

    def __next__(self) -> Tuple[Point, Point]:
        self.prev_point = self.cur_point

        try:
            self.cur_point = next(self.points_iterator)
        except StopIteration:
            self._finished = True
        finally:
            return self.prev_point, self.cur_point

    def set_finished(self, finished):
        self._finished = finished

    def is_finished(self):
        return self._finished
