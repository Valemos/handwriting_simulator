from typing import List, Dict

from gui.canvas_display import CanvasDisplay
from handwriting.misc.cyclic_iterator import CyclicIterator
from handwriting.misc.extending_iterator import ExtendingIterator
from handwriting.misc.exceptions import ObjectNotFound
from handwriting.page_writing.display_draw_history import DisplayDrawHistory, DrawTransaction
from handwriting.page_writing.page import Page
from handwriting.path.curve.point import Point


class PointCollectionRedactor:

    """
    Iterates through list of points, updates their positions using input from
    """

    def __init__(self, display: CanvasDisplay, page: Page):
        self.display = DisplayDrawHistory(display)
        self.page = page
        self.point_draw_objects: Dict[Point, DrawTransaction] = {}
        self.temp_point = Point(0, 0)

        self.points_iterator = CyclicIterator(self.page.get_line_transform().anchors)
        # must be called to init iterators. or else will not work!
        self.reset_iterator()

    def reset_iterator(self):
        self.points_iterator = CyclicIterator(self.page.get_line_transform().anchors)

    def save_page_points(self):
        self.page.lines_points = [it.objects for it in self.points_iterator]
        self.reset_iterator()

    def draw_all(self):
        self.display.delete_all()
        self.redraw_all_points()

    def redraw_all_points(self):
        for point in self.points_iterator.objects:
            if not point.empty():
                self.redraw_point(point)

    def delete_current_canvas_objects(self):
        try:
            current_point = self.line_iterator.get_or_raise().get_variant_or_raise()
            self.delete_point_canvas_objects(current_point)
        except ObjectNotFound:
            pass

    def redraw_pointer_point(self, new_position: Point):
        self.redraw_temp_point(new_position)
        try:
            cur_point = self.line_iterator.get_or_raise().get_variant_or_raise()
            self.redraw_point(cur_point, "blue")
        except ObjectNotFound:
            pass

    def redraw_temp_point(self, pos: Point):
        self.temp_point.x = pos.x
        self.temp_point.y = pos.y
        self.redraw_point(self.temp_point, "red")

    @staticmethod
    def draw_point_scope(draw: DrawTransaction, point: Point, color="black"):
        r = 10
        draw.create_oval((point.x - r, point.y - r, point.x + r, point.y + r), outline=color)
        draw.create_line(point.x, point.y - r, point.x, point.y + r, fill=color)
        draw.create_line(point.x - r, point.y, point.x + r, point.y, fill=color)

    def redraw_point(self, point: Point, color="black"):
        last_draw = self.point_draw_objects.get(point)
        if last_draw is not None: self.display.delete(last_draw)
        self.point_draw_objects[point] = self.display.draw(self.draw_point_scope, point, color)

    def redraw_current_point_black(self):
        self.redraw_point(self.get_current_point())

    def move_up(self):
        self.redraw_current_point_black()
        self.points_iterator.prev()

    def move_down(self):
        self.redraw_current_point_black()
        self.points_iterator.next()

    def move_left(self):
        self.redraw_current_point_black()
        self.points_iterator.get_or_raise().prev()

    def move_right(self):
        self.redraw_current_point_black()
        self.points_iterator.get_or_raise().next()

    def update_current(self, point: Point):
        self.delete_current_canvas_objects()
        self.points_iterator.get_or_raise().set_current(point)
        self.redraw_current_point_black()

    def get_current_point(self):
        return self.points_iterator.get_or_raise().get_variant_or_raise()
