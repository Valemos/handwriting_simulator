from abc import abstractmethod, ABCMeta

from handwriting.misc.i_lines_iterator import ILinesIterator
from handwriting.path.curve.point import Point


class ILinesIterable(metaclass=ABCMeta):

    @abstractmethod
    def get_lines(self, shift: Point = None) -> ILinesIterator:
        pass
