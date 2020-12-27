class PathLinesIterator:
    """
    this class returns pairs of points to properly draw lines on canvas
    """

    def __init__(self, obj):
        self.path = obj

        # cannot use list pages_iterator because it will not update on container change
        self.curve_index = 0
        self.point_iterator = None
        self.cur_curve = None
        self.prev_point = None
        self.cur_point = None

    def __next__(self):
        if self.cur_point is None:
            if self.curve_index >= len(self.path):
                raise StopIteration

            self.point_iterator = self.path[self.curve_index].get_shifted_iterator()
            self.prev_point = next(self.point_iterator)
            self.cur_point = next(self.point_iterator)
        else:
            try:
                # move to next line
                self.prev_point = self.cur_point
                self.cur_point = next(self.point_iterator)
            except StopIteration:  # if curve pages_iterator stopped, than it is the last point

                # go one step forward in curves list
                if self.curve_index < len(self.path) - 1:
                    self.curve_index += 1
                    self.start_iterating_next_line()
                else:
                    raise StopIteration

        return self.prev_point, self.cur_point

    def start_iterating_next_line(self):
        self.point_iterator = self.get_curve_iterator()
        if len(self.path[self.curve_index]) == 1:
            self.prev_point = next(self.point_iterator)
            self.cur_point = self.prev_point
        else:
            self.prev_point = next(self.point_iterator)
            self.cur_point = next(self.point_iterator)

    def get_curve_iterator(self):
        return self.path[self.curve_index].get_shifted_iterator(self.prev_point)

    def new_curve(self, point):
        self.path.new_curve(point)

    def append_absolute(self, point):
        self.path.append_absolute(point)