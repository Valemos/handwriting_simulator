from abc import ABCMeta, abstractmethod
from typing import List

from handwriting.path.curve.curve import Curve
from handwriting.path.curve.i_line_iterable import ILineIterable
from handwriting.misc.i_positionable import IPositionable


class ICurveCollection(ILineIterable, IPositionable, metaclass=ABCMeta):

    @abstractmethod
    def get_curves(self) -> List[Curve]:
        pass

    def points_count(self):
        total = 0
        for component in self.get_curves():
            if isinstance(component, ICurveCollection):
                total += component.points_count()
            else:
                total += len(component)

        return total
