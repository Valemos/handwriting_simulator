from handwriting.misc.container_iterator import AContainerIterator


class ExtendingIterator(AContainerIterator):
    """
    This class iterates through list and allows to add new items by iterating it's variant_index outside of bounds
    runs extender_function to initialize new cells
    """

    def __init__(self, objects: list, empty_factory):
        super().__init__(objects)
        self.empty_factory = empty_factory

    def next(self):
        if self.index == len(self.objects) - 1:
            empty_element = self.empty_factory()
            if self.objects[-1] != empty_element:
                self.objects.append(empty_element)
                self.index += 1
        elif self.index in self:
            self.index += 1
        else:
            self.index = 0

    def prev(self):
        if self.index in self:
            self.index -= 1
        else:
            self.index = 0
            self.insert_empty(self.index)

    def insert_empty(self, index):
        self.objects.insert(index, self.empty_factory())

    def set_current(self, new_object):
        if self.index in self:
            self.objects[self.index] = new_object
        else:
            self.objects.append(new_object)
            self.index = len(self.objects) - 1
