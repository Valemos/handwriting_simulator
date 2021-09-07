from handwriting.path.curve.point import Point


class PageLinesTransform:
    def __init__(self, width=100, height=200, line_height=50):
        self.set_parameters(width, height, line_height)

    def set_parameters(self, width, height, line_height):
        self.top_left = Point(0, 0)
        self.bottom_right = Point(0, height)
        self.top_right = Point(width, 0)
        self.line_bottom_start = Point(0, line_height)

    def get_line_height(self):
        height_vec = self.line_bottom_start - self.top_left
        return (height_vec.x**2 + height_vec.y**2)**(1/2)
