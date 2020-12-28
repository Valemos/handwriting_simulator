from abc import ABC, abstractmethod
from collections import Iterator

from handwriting.path.curve.point import Point


class ICurveIterable(ABC):

    @abstractmethod
    def get_last_point(self, shift_amount: Point = None):
        pass

    @abstractmethod
    def get_iterator(self, shift: Point = None) -> Iterator:
        pass

    @abstractmethod
    def get_lines(self, shift=None):
        pass
