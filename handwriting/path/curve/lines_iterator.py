from handwriting.path.curve.point import Point


class LinesIterator:

    def __init__(self, parent, shift: Point = None):
        self.parent = parent
        self.points_iterator = self.parent.get_iterator(shift)
        self.cur_point = self.points_iterator.cur_point
        self.prev_point = None
        self.finished = False

    def next(self):
        self.prev_point = self.cur_point

        try:
            self.cur_point = next(self.points_iterator)
        except StopIteration:
            self.finished = True
        finally:
            return self.prev_point, self.cur_point

    def is_finished(self):
        return self.finished
