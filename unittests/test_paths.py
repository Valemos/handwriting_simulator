import sys
sys.path.append(r"D:\coding\Python_codes\Handwriting_extractor_project")

from handwriting.path.curve import Curve
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.curve.point import Point

test_path = HandwrittenPath('hello',
                            [
                                Curve([Point(1, 10), Point(1, 10), Point(1, 10), Point(1, 10)]),
                                Curve([Point(10, 100), Point(10, 100)])
                            ])



