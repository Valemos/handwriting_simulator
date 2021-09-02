from abc import ABCMeta, abstractmethod

from handwriting.misc.exceptions import ObjectNotFound


class AContainerIterator(metaclass=ABCMeta):

    def __init__(self, objects):
        self.index = 0
        self.objects = objects

    def __contains__(self, i):
        return 0 <= i < len(self.objects)

    def __len__(self):
        return len(self.objects)

    def __getitem__(self, i):
        return self.objects[i]

    def __setitem__(self, i, val):
        self.objects[i] = val

    @abstractmethod
    def next(self):
        pass

    @abstractmethod
    def prev(self):
        pass

    def get_or_raise(self):
        """If current object is empty, raises ObjectNotFound"""
        if self.index in self:
            return self.objects[self.index]
        raise ObjectNotFound(f"current object not found in {repr(self)}")

    def get_or_none(self):
        if self.index in self:
            return self.objects[self.index]
        return None

    def append(self, item):
        self.objects.append(item)

    def select(self, index):
        if index in self:
            self.index = index
        else:
            self.index = 0

    def remove_current(self):
        if self.index in self:
            self.objects.pop(self.index)
            self.index = self.index - 1 if self.index > 0 else 0

    def is_first(self):
        return self.index == 0

    def is_last(self):
        return self.index == len(self.objects) - 1

    def empty(self):
        return len(self.objects) == 0
