from handwriting.extending_iterator import ExtendingIterator
from handwriting.path.curve.point import Point


class AnchorManager:

    """
    Iterates through anchor points lists, updates their positions
    and manages Tkinter canvas draw objects

    Anchor lines must be created as grid, where the top line used to guide letters? sitting on bottom line
    Ideally, all anchor points must outline the shape of page,
    defining required transformations to fit letters on this page
    """

    def __init__(self, canvas, page):
        self.page = page

        self.canvas = canvas
        self.canvas_objects = {}
        self.temp_point = Point(0, 0)

        self.point_iterators = []
        for line in self.page.lines_points:
            self.point_iterators.append(ExtendingIterator(line))

        self.line_iterator = ExtendingIterator(self.point_iterators)

    def save_page_points(self):
        if self.line_iterator is not None:
            self.page.lines_points = [it.objects for it in self.point_iterators]
            self.point_iterators = None
            self.line_iterator = None

    def draw_all(self):
        self.delete_all_canvas_objects()
        self.redraw_all_points()

    def redraw_all_points(self):
        for row in self.line_iterator.objects:
            for point in row:
                if point is not None:
                    self.redraw_point(point)

    def delete_point_canvas_objects(self, point: Point):
        for obj in self.canvas_objects[point]:
            self.canvas.delete(obj)
        del self.canvas_objects[point]

    def delete_all_canvas_objects(self):
        for point in list(self.canvas_objects.keys()):
            self.delete_point_canvas_objects(point)

    def delete_current_canvas_objects(self):
        current_point = self.line_iterator.current().current()
        if current_point is not None:
            self.delete_point_canvas_objects(current_point)

    def redraw_pointer_point(self, new_position: Point):
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

    @staticmethod
    def draw_point_scope(canvas, point, color="black"):
        lst = []
        r = 10
        lst.append(canvas.create_oval((point.x - r, point.y - r, point.x + r, point.y + r), outline=color))
        lst.append(canvas.create_line(point.x, point.y - r, point.x, point.y + r, fill=color))
        lst.append(canvas.create_line(point.x - r, point.y, point.x + r, point.y, fill=color))
        return lst

    def redraw_point(self, point, color="black"):
        if point in self.canvas_objects:
            self.delete_point_canvas_objects(point)
        self.canvas_objects[point] = self.draw_point_scope(self.canvas, point, color)

    def redraw_current_point_black(self):
        cur = self.line_iterator.current().current()
        if cur is not None:
            self.redraw_point(cur)

    def get_current_indices(self):
        line_i, point_i = None, None
        line_iter = self.line_iterator
        if line_iter is not None:
            line_i = line_iter.index
            point_i = line_iter.current().index if line_iter.current() is not None else 0

        return line_i, point_i

    def move_up(self):
        if self.line_iterator is not None:
            self.redraw_current_point_black()
            self.line_iterator.prev()
            if self.line_iterator.check_cell_empty():
                self.line_iterator.set_current(ExtendingIterator([]))

    def move_down(self):
        if self.line_iterator is not None:
            self.redraw_current_point_black()
            self.line_iterator.next()
            if self.line_iterator.check_cell_empty():
                self.line_iterator.set_current(ExtendingIterator([]))

    def move_left(self):
        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                self.redraw_current_point_black()
                self.line_iterator.current().prev()

    def move_right(self):
        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                self.redraw_current_point_black()
                self.line_iterator.current().next()

    def delete_current_point(self):
        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                self.delete_current_canvas_objects()
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

        :return: Point object for given line variant_index and point variant_index in that line
        """
        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                return self.line_iterator.current().current()
        return None

    def add_intermediate_lines(self, top_index, bot_index, line_count):
        """
        Top line is taken as guide for letters from next line
        Every next line uses previous line to guide letters in right way
        """

        if self.line_iterator is None or top_index == bot_index:
            return False

        self.remove_empty_points(self.line_iterator[top_index])
        self.remove_empty_points(self.line_iterator[bot_index])

        if not self.check_can_create_intermediate_lines(bot_index, top_index):
            return False

        first_line = self.line_iterator[top_index]
        last_line = self.line_iterator[bot_index]
        self.insert_empty_lines(top_index, line_count)

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

    def check_can_create_intermediate_lines(self, bot_index, top_index):
        if top_index not in self.line_iterator or bot_index not in self.line_iterator:
            return False

        if len(self.line_iterator[top_index]) > len(self.line_iterator[bot_index]):
            return False

        return True

    def insert_empty_lines(self, start_index, line_count):
        for i in range(start_index + 1, start_index + line_count):
            self.line_iterator.objects.insert(i, ExtendingIterator([]))

    @staticmethod
    def remove_empty_points(iterator: ExtendingIterator):
        i = 0
        while i < len(iterator):
            if iterator[i] is None:
                iterator.objects.pop(i)
            else:
                i += 1
