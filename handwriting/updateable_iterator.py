from collections import Iterator


class UpdatableIterator(Iterator):

    def __init__(self, objects):
        self.objects = objects
        self.index = -1

    def __len__(self):
        return len(self.objects)

    def __next__(self):
        if self.is_last():
            raise StopIteration

        self.next()
        return self.current()

    def next(self):
        if self.in_bounds(self.index + 1):
            self.index += 1
        else:
            self.index = len(self.objects) - 1

    def prev(self):
        if self.in_bounds(self.index - 1):
            self.index -= 1
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
