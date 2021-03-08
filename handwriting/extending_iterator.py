from handwriting.container_iterator import AContainerIterator


class ExtendingIterator(AContainerIterator):
    """
    This class iterates through list and allows to add new items by iterating it's variant_index outside of bounds
    """

    def __init__(self, objects: list):
        super().__init__(objects)

    def next(self):
        if self.index == len(self.objects) - 1:
            if self.objects[-1] is not None:
                self.objects.append(None)
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
        if self.objects[index] is not None:
            self.objects.insert(index, None)
            return True
        return False

    def set_current(self, new_object):
        if self.index in self:
            self.objects[self.index] = new_object
        else:
            self.objects.append(new_object)
            self.index = len(self.objects) - 1

    def delete_current(self):
        if self.index in self:
            self.objects.pop(self.index)
            self.index = self.index - 1 if self.index > 0 else 0

    def check_cell_empty(self):
        """
        Returns True, if current variant_index is inside bounds, but current object is None
        That means, that current object was moved using next() or prev()
        and list was extended with None object
        :return: True if current object is None, or object list is empty, False otherwise
        """

        if self.index in self:
            return self.objects[self.index] is None
        return True