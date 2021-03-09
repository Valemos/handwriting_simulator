from abc import ABC, abstractmethod
from collections import Iterator

from handwriting.path.curve.point import Point


class ILineIterable(ABC):

    @abstractmethod
    def get_iterator(self, shift: Point = None) -> Iterator:
        pass

    @abstractmethod
    def get_lines(self, shift: Point = None):
        pass
