from handwriting.step_functions import *


class CyclicIterator:
    """
    This class controls mechanisms of selecting and iterating in list of images back and forth
    if user iterates outside of bounds,
    iterator returns to first or last element of list to iterate in cycle
    """

    def __init__(self, object_list):
        self.object_list = object_list
        self.object_index = 0

    def get_max(self):
        return len(self.object_list)

    def next(self):
        if 0 <= self.object_index < len(self.object_list):
            self.object_index = step_forwards(self.object_index, len(self.object_list) - 1)
        else:
            self.object_index = 0

    def prev(self):
        if 0 <= self.object_index < len(self.object_list):
            self.object_index = step_backwards(self.object_index, len(self.object_list) - 1)
        else:
            self.object_index = 0

    def select(self, index):
        if 0 <= index < len(self.object_list):
            self.object_index = index

    def current(self):
        if 0 <= self.object_index < len(self.object_list):
            return self.object_list[self.object_index]
        return None
