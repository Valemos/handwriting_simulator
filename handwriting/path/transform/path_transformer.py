from copy import deepcopy

from handwriting.path.curve.point import Point
from handwriting.path.handwritten_path import HandwrittenPath


class PathTransformer:

    def __init__(self, path: HandwrittenPath):
        self.original_path: HandwrittenPath = path
        self.transformed_path: HandwrittenPath = None
        self.previous_transforms = {}  # stores parameters for previous transformations

    def is_repeated_transform(self, function, *params):
        previous_params = None
        if function in self.previous_transforms:
            previous_params = self.previous_transforms[function]

        # store current parameters for next check
        self.previous_transforms[function] = params

        return previous_params == params

    def transform_invalid(self, function, *params):
        if self.is_repeated_transform(function, *params):
            return True
        else:
            # new transformation must be applied to original path
            self.transformed_path = self.path_copy()
            return True

    def path_copy(self):
        return deepcopy(self.original_path)

    def scale_path(self, x_scale=1, y_scale=1):
        if self.transform_invalid(self.scale_path, x_scale, y_scale):
            return self.transformed_path

        # default values does not requires
        if x_scale == 1 and y_scale == 1:
            return self.transformed_path

        for curve in self.transformed_path.components:
            self._scale_inplace(curve.start_shift, x_scale, y_scale)
            curve.components = [self._scale_inplace(i, x_scale, y_scale) for i in curve.components]

        # round shifts to integer values
        self.coalesce_points(self.transformed_path)

    def shift_path_rectangle(self, rect_height=None, rect_width=None):
        """
        Calculates borders for current path
        and shifts it to BOTTOM LEFT CORNER of given rectangle size
        top left corner at (0, 0) and y axis is downwards

        if rect_height or rect_width is None,
        they will be assigned with current path borders dimension
        """
        if self.transform_invalid(self.shift_path_rectangle, rect_height, rect_width):
            return self.transformed_path

        self.transformed_path.set_position(Point(0, 0))
        x_borders, y_borders = self.get_rectangle(self.transformed_path)

        rect_height = self.get_border_size(y_borders, rect_height)
        rect_width = self.get_border_size(x_borders, rect_width)

        rectangle_shift = Point(0, 0)
        rectangle_shift.x = x[0]

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
        new shift point is generated conserving leftover step that are smaller than 1
        """

        for curve in path.components:
            curve_points = curve.components
            new_curve_points = []

            change: Point = curve.start_shift
            curve.start_shift = Point(round(change.x), round(change.y))
            change -= curve.start_shift

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

    @staticmethod
    def get_border_size(borders, desired_size):
        border_size = borders[1] - borders[0]
        return border_size if border_size > desired_size else desired_size
