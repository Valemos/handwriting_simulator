from gui.canvas_display import CanvasDisplay
from handwriting.misc.exceptions import ObjectNotFound
from handwriting.path.curve.point import Point
from handwriting.path.path_lines_iterator import PathLinesIterator
from handwriting.paths_dictionary.dictionary_manager import DictionaryManager


class PathDrawer:
    def __init__(self, dictionary_manager: DictionaryManager, display: CanvasDisplay):
        self.display = display
        self.dictionary_manager = dictionary_manager
        self.path_lines_iterator: PathLinesIterator = None
        self.shift_point = Point(0, 0)

    def set_global_shift(self, point):
        self.shift_point = point

    def redraw(self):

        try:
            self.reset()
            current_path = self.dictionary_manager.iterator.get_variant_or_raise()

            # place path at (0, 0) and shift according to entered shift point
            current_path.set_position(Point(0, 0))
            self.path_lines_iterator = current_path.get_iterator(self.shift_point)
            self.draw_lines_to_end(self.path_lines_iterator)
        except ObjectNotFound:
            pass

    def reset(self):
        self.display.reset()
        self.path_lines_iterator = None

    def update_path(self):

        path = self.dictionary_manager.iterator.get_variant_or_none()
        self.path_lines_iterator = path.get_lines() if path is not None else None

    def draw_lines_to_end(self, path_iterator):
        while True:
            try:
                p1, p2 = next(path_iterator)
                self.display.draw_line(p1, p2)
            except StopIteration:
                break

    def start_curve(self, point):
        if self.path_lines_iterator is None:
            path = self.dictionary_manager.iterator.get_variant_or_none()
            if path is not None:
                self.path_lines_iterator = path.get_lines()

        self.path_lines_iterator.new_curve(point)

    def continue_curve(self, point_absolute):
        self.path_lines_iterator.append_absolute(point_absolute)
        self.draw_lines_to_end(self.path_lines_iterator)

    def try_draw(self):
        if self.path_lines_iterator is None:
            self.update_path()

        return self.path_lines_iterator is not None
