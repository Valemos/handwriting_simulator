from handwriting.misc.cyclic_iterator import CyclicIterator
from handwriting.misc.exceptions import ObjectNotFound


class EmptyCyclicIterator(CyclicIterator):

    def __init__(self):
        super().__init__([])

    def __len__(self):
        return 0

    def next(self):
        pass

    def prev(self):
        pass

    def select(self, index):
        pass

    def append(self, new_object):
        pass

    def update_index(self):
        pass

    def get_or_raise(self):
        raise ObjectNotFound("no objects in empty iterator")

    def get_or_none(self):
        return None

    def empty(self):
        return True

    def is_first(self):
        return True

    def is_last(self):
        return True
