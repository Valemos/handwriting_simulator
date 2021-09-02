from collections import Iterator

from handwriting.misc.container_iterator import AContainerIterator


class UpdatableIterator(Iterator, AContainerIterator):

    def __init__(self, objects):
        super().__init__(objects)

        # when next() first called on this object it must return first element
        self.index = -1

    def __len__(self):
        return len(self.objects)

    def __next__(self):
        if self.is_last():
            raise StopIteration

        self.next()
        return self.get_or_raise()

    def next(self):
        if self.index + 1 in self:
            self.index += 1
        else:
            self.index = len(self.objects) - 1

    def prev(self):
        if self.index - 1 in self:
            self.index -= 1
        else:
            self.index = 0
