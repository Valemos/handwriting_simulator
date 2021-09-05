from abc import ABCMeta, abstractmethod
from collections import Iterator
from typing import Tuple

from handwriting.path.curve.point import Point


class ILinesIterator(Iterator, metaclass=ABCMeta):
    @abstractmethod
    def __next__(self) -> Tuple[Point, Point]:
        pass
