from abc import ABCMeta, abstractmethod


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

    def current(self):
        if self.index in self:
            return self.objects[self.index]
        return None

    def append(self, item):
        self.objects.append(item)

    def select(self, index):
        if index in self:
            self.index = index

    def is_first(self):
        return self.index == 0

    def is_last(self):
        return self.index == len(self.objects) - 1
