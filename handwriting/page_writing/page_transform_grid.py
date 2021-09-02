from handwriting.path.curve.point import Point

import numpy as np
from numpy.linalg import norm


class PageTransformGrid:
    """
    Holds grid of anchor points and applies transformation
    for intermediate points passed to transform grid
    """

    def __init__(self, anchor_points=None):
        self.anchor_points = anchor_points if anchor_points is not None else [[]]
        if not isinstance(self.anchor_points, list):
            raise ValueError("anchor points is not a list")

        self.metric_square = [[Point(0, 0), Point(1, 0)],
                              [Point(0, 1), Point(1, 1)]]

    def transform_point(self, point):
        # TODO finish transformations of page
        return Point(point.x, point.y)

    def set_metric_square(self, size):
        self.metric_square = [[Point(0, 0), Point(size, 0)],
                              [Point(0, size), Point(size, size)]]

    @staticmethod
    def normalize(vector):
        return vector / norm(vector)

    def get_square_vectors(self, row, col):
        point_lt = np.array([*self.anchor_points[row][col]])
        point_rt = np.array([*self.anchor_points[row][col + 1]])
        point_lb = np.array([*self.anchor_points[row + 1][col]])
        point_rb = np.array([*self.anchor_points[row + 1][col + 1]])

        vec_left = point_lt - point_lb
        vec_right = point_rt - point_rb
        vec_top = point_rt - point_lt
        vec_bottom = point_rb - point_lb

        return self.normalize(vec_left), self.normalize(vec_right), self.normalize(vec_top), self.normalize(vec_bottom)

    def add_anchor(self, point, line_index):
        self.anchor_points[line_index].append(point)
