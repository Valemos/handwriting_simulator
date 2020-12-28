from handwriting.length_object_serializer import LengthObjectSerializer
from handwriting.path.curve.point import Point

import numpy as np
from numpy.linalg import norm


class PageTransformGrid(LengthObjectSerializer):
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
        pointLT = np.array([*self.anchor_points[row][col]])
        pointRT = np.array([*self.anchor_points[row][col + 1]])
        pointLB = np.array([*self.anchor_points[row + 1][col]])
        pointRB = np.array([*self.anchor_points[row + 1][col + 1]])

        vec_left = pointLT - pointLB
        vec_right = pointRT - pointRB
        vec_top = pointRT - pointLT
        vec_bottom = pointRB - pointLB

        return self.normalize(vec_left), self.normalize(vec_right), self.normalize(vec_top), self.normalize(vec_bottom)

    def add_anchor(self, point, line_index):
        self.anchor_points[line_index].append(point)
