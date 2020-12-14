from handwriting.extending_iterator import ExtendingIterator
from handwriting.path_management.point import Point


class AnchorManager:

    """
    Iterates through anchor points lists, updates their positions
    and manages Tkinter canvas draw objects
    """

    def __init__(self, page):
        self.page = page

        # this function is passed as argument to AnchorManager with canvas object
        # it must return list of canvas objects that was drawn by it
        self.canvas_objects = {}
        self.temp_point = Point(0, 0)

        self.point_iterators = []
        for line in self.page.lines_points:
            self.point_iterators.append(ExtendingIterator(line))

        self.line_iterator = ExtendingIterator(self.point_iterators)

    def set_canvas_draw(self, canvas, draw_function):
        """
        Sets canvas to work with for next draw object manipulation
        :param canvas: tkinter canvas object
        :param draw_function: function, that takes as arguments (Canvas, Point) objects
        """
        self.canvas = canvas
        self.draw_function = draw_function

    def save_page_points(self):
        """
        Uses values from iterators and assigns them to current page object
        """

        if self.line_iterator is not None:
            self.page.lines_points = [it.object_list for it in self.point_iterators]
            self.point_iterators = None
            self.line_iterator = None

    def draw_all(self):
        """
        Draws all points on canvas
        stores canvas objects in internal map for future redraw updates of that point
        """
        for row in self.page.lines_points:
            for point in row:
                if point is not None:
                    self.canvas_objects[point] = self.draw_function(self.canvas, point)


    def delete_point_canvas_objects(self, point: Point):
        for obj in self.canvas_objects[point]:
            self.canvas.delete(obj)
        del self.canvas_objects[point]

    def redraw_pointer_point(self, new_position: Point):
        """
        Removes Canvas objects and draws them again on the new position
        :param new_position: new point position to update current point with
        """

        if self.line_iterator is not None:
            self.redraw_temp_point(new_position)
            cur_point = self.line_iterator.current().current()
            if cur_point is not None:
                self.redraw_point(cur_point, "blue")

    def redraw_temp_point(self, pos):
        self.temp_point.x = pos.x
        self.temp_point.y = pos.y
        self.redraw_point(self.temp_point, "red")

    def redraw_point(self, point, color="black"):
        if point in self.canvas_objects:
            self.delete_point_canvas_objects(point)
        self.canvas_objects[point] = self.draw_function(self.canvas, point, color)

    def redraw_previous_point(self):
        prev = self.line_iterator.current().current()
        if prev is not None:
            self.redraw_point(prev)

    def move_up(self):
        """Move up in points iterator"""

        if self.line_iterator is not None:
            self.redraw_previous_point()
            self.line_iterator.prev()
            if self.line_iterator.check_extended():
                self.line_iterator.set_current(ExtendingIterator([]))

    def move_down(self):
        """Move up in points iterators"""

        if self.line_iterator is not None:
            self.redraw_previous_point()
            self.line_iterator.next()
            if self.line_iterator.check_extended():
                self.line_iterator.set_current(ExtendingIterator([]))

    def move_left(self):
        """Move up in points iterators"""

        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                self.redraw_previous_point()
                self.line_iterator.current().prev()

    def move_right(self):
        """Move up in points iterators"""

        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                self.redraw_previous_point()
                self.line_iterator.current().next()


    def update_line_point(self, point: Point):
        """
        Updates or creates new position on this position in iterators
        :param point: Point object to update
        """
        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                self.redraw_previous_point()
                self.line_iterator.current().set_current(point)

    def get_current_point(self):
        """
        If line points setup started, returns current point
        else, returns None

        :return: Point object for given line index and point index in that line
        """
        if self.line_iterator is not None:
            return self.line_iterator.current().current()
        else:
            return None
