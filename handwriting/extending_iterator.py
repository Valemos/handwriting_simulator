
class ExtendingIterator:
    """
    This class iterates through list and allows to add new items by iterating it's variant_index outside of bounds
    """

    def __init__(self, object_list: list):
        self.object_list = object_list
        self.object_index = 0

    def __contains__(self, i):
        return 0 <= i < len(self.object_list)

    def __getitem__(self, i):
        return self.object_list[i]

    def __setitem__(self, i, val):
        self.object_list[i] = val

    def __len__(self):
        return len(self.object_list)

    def append(self, item):
        self.object_list.append(item)

    def next(self):
        if len(self) == 0:
            self.create_first_empty()
        elif self.object_index == len(self.object_list) - 1:
            if self.object_list[-1] is not None:
                self.object_list.append(None)
                self.object_index += 1
        elif self.object_index in self:
            self.object_index += 1
        else:
            self.object_index = 0

    def create_first_empty(self):
        self.object_list.append(None)
        self.object_index = 0

    def prev(self):
        if self.object_index in self:
            self.object_index -= 1
        else:
            self.object_index = 0
            self.insert_empty(self.object_index)

    def insert_empty(self, index):
        if self.object_list[index] is not None:
            self.object_list.insert(index, None)
            return True
        return False

    def set_current(self, new_object):
        if self.object_index in self:
            self.object_list[self.object_index] = new_object
        else:
            self.object_list.append(new_object)
            self.object_index = len(self.object_list) - 1

    def select(self, index):
        if index in self:
            self.object_index = index

    def current(self):
        if self.object_index in self:
            return self.object_list[self.object_index]
        return None

    def delete_current(self):
        if self.object_index in self:
            self.object_list.pop(self.object_index)
            self.object_index = self.object_index - 1 if self.object_index > 0 else 0

    def check_cell_empty(self):
        """
        Returns True, if current variant_index is inside bounds, but current object is None
        That means, that current object was moved using next() or prev()
        and list was extended with None object
        :return: True if current object is None, or object list is empty, False otherwise
        """

        if self.object_index in self:
            return self.object_list[self.object_index] is None
        return True