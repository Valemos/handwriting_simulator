from handwriting.step_functions import *


class CyclicIterator:
    """
    This class controls mechanisms of selecting and iterating in list of images back and forth
    if user iterates outside of bounds,
    iterator returns to first or last element of list to iterate in cycle
    """

    def __init__(self, object_list):
        self.objects = object_list
        self.index = 0

    def get_max(self):
        return len(self.objects)

    def next(self):
        if len(self.objects) > 0:
            self.index = step_forwards(self.index, len(self.objects) - 1)
        else:
            self.index = 0

    def prev(self):
        if len(self.objects) > 0:
            self.index = step_backwards(self.index, len(self.objects) - 1)
        else:
            self.index = 0

    def select(self, index):
        if self.in_bounds(index):
            self.index = index

    def current(self):
        if self.in_bounds(self.index):
            return self.objects[self.index]
        return None

    def in_bounds(self, index):
        return 0 <= index < len(self.objects)

    def is_first(self):
        return self.index == 0

    def is_last(self):
        return self.index == len(self.objects) - 1
