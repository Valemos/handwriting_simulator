import unittest

import numpy as np

from handwriting.page_writing.page_transform_grid import PageTransformGrid
from handwriting.path.curve.point import Point


class TestPageTransformation(unittest.TestCase):

    @staticmethod
    def create_square_transform():
        transform = PageTransformGrid([[Point(0, 0), Point(10, 0)],
                                       [Point(0, 10), Point(10, 10)]])
        return transform

    def setUp(self) -> None:
        self.square_transform = self.create_square_transform()

    def test_point_not_changed(self):
        self.square_transform.set_metric_square(10)
        self.assertEqual(self.square_transform.transform_point(Point(1, 1)), Point(1, 1))

    def test_metric_square(self):
        transform = PageTransformGrid()
        transform.set_metric_square(10)

        desired_square = [[Point(0, 0), Point(10, 0)],
                          [Point(0, 10), Point(10, 10)]]

        for r1, r2 in zip(transform.metric_square, desired_square):
            self.assertListEqual(r1, r2)

    def test_create_side_vectors(self):
        transform = PageTransformGrid([[Point(5, 0),  Point(15, 5)],
                                       [Point(0, 15), Point(20, 20)]])

        result = transform.get_square_vectors(0, 0)

        normalized_v = [np.array([5.0, -15.0]),
                        np.array([-5.0, -15.0]),
                        np.array([10.0, 5.0]),
                        np.array([20.0, 5.0])]

        for vec_i in range(len(normalized_v)):
            normalized_v[vec_i] /= np.linalg.norm(normalized_v[vec_i])

        for vec, desired in zip(result, normalized_v):
            self.assertTrue(np.allclose(vec, desired))

    def test_intermediate_vectors(self):
        pass
