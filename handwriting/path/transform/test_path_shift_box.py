from unittest import TestCase

from handwriting.path.curve.point import Point
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.transform.path_shift_box import PathShiftBox


class TestPathShiftBox(TestCase):

    def setUp(self) -> None:
        self.path = HandwrittenPath()
        self.path.new_curve(Point(20, 20))
        self.path.append_absolute(Point(25, 30))  # (+5, +10)
        self.path.append_absolute(Point(28, 28))  # (+3, -2)

    def test_get_path_box(self):
        box = PathShiftBox.get_path_box(self.path)
        self.assertEqual([20, 28, 20, 30], box)

    def test_get_shifted_path_box(self):
        self.path.set_position(Point(0, 0))
        box = PathShiftBox.get_path_box(self.path)
        self.assertEqual([0, 8, 0, 10], box)

    def test_get_rectangle_shift(self):
        box = PathShiftBox.get_path_box(self.path)
        shift = PathShiftBox.get_rectangle_shift(box, (50, 50))
        self.assertEqual(Point(-20, 20), shift)
