from handwriting.path.curve.point import Point


class PageLinesTransform:
    def __init__(self):
        self.top_left = Point()
        self.bottom_right = Point()
        self.top_right = Point()
        self.line_bottom_start = Point()

    def set_default(self):
        self.top_left = Point()
        self.bottom_right = Point()
        self.top_right = Point()
        self.line_bottom_start = Point()

    def get_line_height(self):
        height_vec = self.line_bottom_start - self.top_left
        return (height_vec.x**2 + height_vec.y**2)**(1/2)
