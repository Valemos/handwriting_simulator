from handwriting.extending_iterator import ExtendingIterator
from handwriting.path_management.point import Point


class AnchorManager:

    """
    Iterates through anchor points lists, updates their positions
    and manages Tkinter canvas draw objects

    Anchor lines must be created as grid, where the top line used to guide letters? sitting on bottom line
    Ideally, all anchor points must outline the shape of page,
    defining required transformations to fit letters on this page
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

        self.delete_all_canvas_objects()
        for row in self.line_iterator.object_list:
            for point in row:
                if point is not None:
                    self.redraw_point(point)

    def delete_current_canvas_objects(self):
        """
        this function assumes, that self.line_iterator and self.line_iterator.current() is not None
        Deletes current point canvas objects from canvas
        """
        cur = self.line_iterator.current().current()
        if cur is not None:
            for obj in self.canvas_objects[cur]:
                self.canvas.delete(obj)
            del self.canvas_objects[cur]

    def delete_all_canvas_objects(self):
        for point in list(self.canvas_objects.keys()):
            self.delete_point_canvas_objects(point)

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

    def delete_temp_point(self):
        self.delete_point_canvas_objects(self.temp_point)

    def redraw_temp_point(self, pos):
        self.temp_point.x = pos.x
        self.temp_point.y = pos.y
        self.redraw_point(self.temp_point, "red")

    def redraw_point(self, point, color="black"):
        if point in self.canvas_objects:
            self.delete_point_canvas_objects(point)
        self.canvas_objects[point] = self.draw_function(self.canvas, point, color)

    def redraw_current_point_black(self):
        cur = self.line_iterator.current().current()
        if cur is not None:
            self.redraw_point(cur)

    def move_up(self):
        """Move up in points iterator"""

        if self.line_iterator is not None:
            self.redraw_current_point_black()
            self.line_iterator.prev()
            if self.line_iterator.check_cell_empty():
                self.line_iterator.set_current(ExtendingIterator([]))

    def move_down(self):
        """Move up in points iterators"""

        if self.line_iterator is not None:
            self.redraw_current_point_black()
            self.line_iterator.next()
            if self.line_iterator.check_cell_empty():
                self.line_iterator.set_current(ExtendingIterator([]))

    def move_left(self):
        """Move up in points iterators"""

        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                self.redraw_current_point_black()
                self.line_iterator.current().prev()

    def move_right(self):
        """Move up in points iterators"""

        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                self.redraw_current_point_black()
                self.line_iterator.current().next()

    def delete_current_point(self):
        """
        Removes current point from sequence if it exists
        updates all necessary objects
        """
        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                cur_point = self.line_iterator.current().current()
                if cur_point is not None:
                    self.delete_point_canvas_objects(cur_point)
                self.line_iterator.current().delete_current()

    def update_current_point(self, point: Point):
        """
        Updates or creates new position on this position in iterators
        :param point: Point object to update
        """
        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                self.delete_current_canvas_objects()
                self.line_iterator.current().set_current(point)
                self.redraw_current_point_black()

    def get_current_point(self):
        """
        If line points setup started, returns current point
        else, returns None

        :return: Point object for given line index and point index in that line
        """
        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                return self.line_iterator.current().current()
        return None

    # line modification
    def add_intermediate_lines(self, top_index, bot_index, line_count):
        """
        Top line is taken as guide for letters from next line
        Every next line uses previous line to guide letters in right way

        :param top_index: index of top line to take points from
        :param bot_index: index of bottom line to take points from
        :param line_count: number of total lines to end up with
        :return: True if lines were added, False otherwise
        """

        if self.line_iterator is None or top_index == bot_index:
            return False

        self.remove_empty_points(self.line_iterator[top_index])
        self.remove_empty_points(self.line_iterator[bot_index])

        if top_index not in self.line_iterator or bot_index not in self.line_iterator:
            return False

        if len(self.line_iterator[top_index]) > len(self.line_iterator[bot_index]):
            return False

        first_line = self.line_iterator[top_index]
        last_line = self.line_iterator[bot_index]
        for i in range(top_index + 1, top_index + line_count):
            self.line_iterator.object_list.insert(i, ExtendingIterator([]))


        for point_i in range(len(first_line)):
            # create intermediate points
            step_point = last_line[point_i].get_shift(first_line[point_i])
            step_point.x /= line_count
            step_point.y /= line_count
            cur_point = Point(*first_line[point_i])
            for row_iter in range(top_index + 1, top_index + line_count):
                cur_point = cur_point.shift(step_point)
                self.line_iterator[row_iter].append(cur_point)

        self.draw_all()
        return True

    @staticmethod
    def remove_empty_points(iterator: ExtendingIterator):
        i = 0
        while i < len(iterator):
            if iterator[i] is None:
                iterator.object_list.pop(i)
            else:
                i += 1
