from copy import deepcopy

from handwriting.path.curve.point import Point
from handwriting.path.i_curve_collection import ICurveCollection
from handwriting.path.transform.i_path_transformer import IPathTransformer


class PathTransformer(IPathTransformer):

    def __init__(self, path: ICurveCollection, inplace=False):
        super().__init__(path, inplace)

    def scale(self, x_scale=1, y_scale=1):
        if self.transform_if_not_repeated(self.scale, x_scale, y_scale):
            return

        # default values does not requires
        if x_scale == 1 and y_scale == 1:
            return

        for curve in self.transformed.get_curves():
            self._scale_inplace(curve.start, x_scale, y_scale)
            curve.components = [self._scale_inplace(i, x_scale, y_scale) for i in curve.components]

        # round shifts to integer values
        self.coalesce_points(self.transformed)

    @staticmethod
    def _scale_inplace(point: Point, x_scale: float, y_scale: float):
        point.x *= x_scale
        point.y *= y_scale
        return point

    @staticmethod
    def coalesce_points(path: ICurveCollection):
        """
        gathers all small steps and stores them as floats in "change"
        if one of coordinates (or both) changes more than by one after some number of points,
        new shift point is generated conserving leftover step that are smaller than 1
        """

        for curve in path.get_curves():
            curve_points = curve.components
            new_curve_points = []

            change: Point = curve.start
            curve.start = Point(round(change.x), round(change.y))
            change -= curve.start

            i = 0
            while i < len(curve_points):
                while change.in_range(-1, 1) and i < len(curve_points):
                    change.shift_inplace(curve_points[i])
                    i += 1

                new_point = Point(round(change.x), round(change.y))

                # conserve all changes that are less than integer value
                change -= new_point
                new_curve_points.append(new_point)

            # replace all elements of shifts list with new shifts
            curve.components.clear()
            curve.components.extend(new_curve_points)
