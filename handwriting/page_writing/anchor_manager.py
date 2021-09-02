from handwriting.misc.extending_iterator import ExtendingIterator
from handwriting.misc.exceptions import ObjectNotFound
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

        self.point_iterators: list = None
        self.line_iterator: ExtendingIterator = None
        # must be called to init iterators. or else will not work!
        self.reset_iterators(self.page)

    @staticmethod
    def create_empty_anchor():
        return Point()

    @staticmethod
    def create_empty_line():
        return ExtendingIterator([], AnchorManager.create_empty_anchor)

    def reset_iterators(self, page=None):
        self.point_iterators = []
        if page is not None:
            for line in page.lines_points:
                self.point_iterators.append(ExtendingIterator(line, AnchorManager.create_empty_anchor))
        self.line_iterator = ExtendingIterator(self.point_iterators, AnchorManager.create_empty_line)

    def save_page_points(self):
        self.page.lines_points = [it.objects for it in self.point_iterators]
        self.reset_iterators()

    def draw_all(self):
        self.delete_all_canvas_objects()
        self.redraw_all_points()

    def redraw_all_points(self):
        for row in self.line_iterator.objects:
            for point in row:
                if not point.is_empty():
                    self.redraw_point(point)

    def delete_point_canvas_objects(self, point: Point):
        for obj in self.canvas_objects[point]:
            self.canvas.delete(obj)
        del self.canvas_objects[point]

    def delete_all_canvas_objects(self):
        for point in list(self.canvas_objects.keys()):
            self.delete_point_canvas_objects(point)

    def delete_current_canvas_objects(self):
        try:
            current_point = self.line_iterator.get_or_raise().get_path_or_raise()
            self.delete_point_canvas_objects(current_point)
        except ObjectNotFound:
            pass

    def redraw_pointer_point(self, new_position: Point):
        self.redraw_temp_point(new_position)
        try:
            cur_point = self.line_iterator.get_or_raise().get_path_or_raise()
            self.redraw_point(cur_point, "blue")
        except ObjectNotFound:
            pass

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
        self.redraw_point(self.get_current_point())

    def get_current_indices(self):
        line_index = self.line_iterator.index
        point_index = self.line_iterator.get_or_raise().index if len(self.line_iterator) > 0 else 0

        return line_index, point_index

    def move_up(self):
        self.redraw_current_point_black()
        self.line_iterator.prev()

    def move_down(self):
        self.redraw_current_point_black()
        self.line_iterator.next()

    def move_left(self):
        self.redraw_current_point_black()
        self.line_iterator.get_or_raise().prev()

    def move_right(self):
        self.redraw_current_point_black()
        self.line_iterator.get_or_raise().next()

    def delete_current_point(self):
        self.delete_current_canvas_objects()
        self.line_iterator.get_or_raise().remove_current()

    def update_current(self, point: Point):
        self.delete_current_canvas_objects()
        self.line_iterator.get_or_raise().set_current(point)
        self.redraw_current_point_black()

    def get_current_point(self):
        return self.line_iterator.get_or_raise().get_path_or_raise()

    def add_intermediate_lines(self, top_index, bot_index, line_count):
        """Creates a grid of points between two selected lines"""

        if top_index == bot_index:
            return False

        self.remove_empty_points(self.line_iterator[top_index])
        self.remove_empty_points(self.line_iterator[bot_index])

        if not self.can_create_intermediate_lines(bot_index, top_index):
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
                cur_point.shift_inplace(step_point)
                self.line_iterator[row_iter].append(cur_point)

        self.draw_all()
        return True

    def can_create_intermediate_lines(self, bot_index, top_index):
        if top_index not in self.line_iterator or bot_index not in self.line_iterator:
            return False

        if len(self.line_iterator[top_index]) > len(self.line_iterator[bot_index]):
            return False

        return True

    def insert_empty_lines(self, start_index, line_count):
        for i in range(start_index + 1, start_index + line_count):
            self.line_iterator.objects.insert(i, AnchorManager.create_empty_line())

    @staticmethod
    def remove_empty_points(iterator: ExtendingIterator):
        i = 0
        while i < len(iterator):
            if iterator[i].is_empty():
                iterator.objects.pop(i)
            else:
                i += 1
