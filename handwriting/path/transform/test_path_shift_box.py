from unittest import TestCase

from handwriting.path.curve.point import Point
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.transform.path_shift_box import PathShiftBox, Box


class TestPathShiftBox(TestCase):

    def setUp(self) -> None:
        self.path = HandwrittenPath()
        self.path.new_curve(Point(20, 20))
        self.path.append_absolute(Point(25, 30))  # (+5, +10)
        self.path.append_absolute(Point(28, 28))  # (+3, -2)

    def test_get_path_box(self):
        box = PathShiftBox.get_lines_box(self.path.get_lines())
        self.assertEqual(Box(min_x=20, max_x=28, min_y=20, max_y=30), box)

    def test_get_shifted_path_box(self):
        self.path.set_position(Point(0, 0))
        box = PathShiftBox.get_lines_box(self.path.get_lines())
        self.assertEqual(Box(min_x=0, max_x=8, min_y=0, max_y=10), box)

    def test_get_rectangle_shift(self):
        box = PathShiftBox.get_lines_box(self.path.get_lines())
        shift = PathShiftBox.get_rectangle_shift(box, (50, 50))
        self.assertEqual(Point(-20, 20), shift)
