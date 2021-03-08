from handwriting.container_iterator import AContainerIterator
from handwriting.step_functions import *


class CyclicIterator(AContainerIterator):
    """
    This class controls mechanisms of selecting and iterating in list of images back and forth
    if user iterates outside of bounds,
    iterator returns to first or last element of list to iterate in cycle
    """

    def __init__(self, objects):
        super().__init__(objects)

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

    def append(self, new_object):
        self.objects.append(new_object)
        self.select(len(self.objects) - 1)
