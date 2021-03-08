from copy import deepcopy

from handwriting.path.curve.point import Point
from handwriting.path.handwritten_path import HandwrittenPath


class PathTransformer:

    def __init__(self, path: HandwrittenPath):
        self.original_path = path
        self.transformed_path = None
        self.previous_transforms = {}  # stores parameters for previous transformations

    def is_repeated_transform(self, function, *params):
        previous_params = None
        if function in self.previous_transforms:
            previous_params = self.previous_transforms[function]

        # store current parameters for next check
        self.previous_transforms[function] = params

        return previous_params == params

    def transform(self, x_scale=1, y_scale=1):
        """general function for any type of transformation"""

        if x_scale == 1 and y_scale == 1:
            return self.original_path

        if self.is_repeated_transform(self._scale_inplace, x_scale, y_scale):
            # return previously transformed path
            return self.transformed_path
        else:
            # new transformation must be applied to original path
            self.transformed_path = self.path_copy()

        for curve in self.transformed_path.components:
            self._scale_inplace(curve.start_shift, x_scale, y_scale)
            curve.components = [self._scale_inplace(i, x_scale, y_scale) for i in curve.components]

        self.coalesce_points(self.transformed_path)

        return self.transformed_path

    def path_copy(self):
        return deepcopy(self.original_path)

    @staticmethod
    def _scale_inplace(point: Point, x_scale: float, y_scale: float):
        point.x *= x_scale
        point.y *= y_scale
        return point

    @staticmethod
    def coalesce_points(path: HandwrittenPath):
        """
        gathers all small steps and stores them as floats in "change"
        if one of coordinates (or both) changes more than by one after some number of points,
        new shift point is generated conserving step that are smaller than 1
        """

        # todo update start shifts while collecting points
        # todo also collect leftover shift from start shift after rounding

        for curve in path.components:
            curve_points = curve.components
            new_curve_points = []
            change: Point = Point(0, 0)
            i = 0

            while i < len(curve_points):
                while change.in_range(-1, 1):
                    change.shift_inplace(curve_points[i])
                    i += 1

                new_point = Point(round(change.x), round(change.y))

                # conserve all changes that are less than integer value
                change -= new_point
                new_curve_points.append(new_point)

            # replace all elements of shifts list with new shifts
            curve.components.clear()
            curve.components.extend(new_curve_points)
