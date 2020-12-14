
class ExtendingIterator:
    """
    This class iterates through list and allows to add new items by iterating it's index outside of bounds
    """

    def __init__(self, object_list: list):
        self.object_list = object_list
        self.object_index = 0

    def get_max(self):
        return len(self.object_list)

    def next(self):
        if 0 <= self.object_index < len(self.object_list) - 1:
            self.object_index += 1
        elif self.object_index == len(self.object_list) - 1:
            if self.object_list[-1] is not None:
                self.object_list.append(None)
                self.object_index += 1
        else:
            self.object_index = 0

    def prev(self):
        if 0 < self.object_index < len(self.object_list):
            self.object_index -= 1
        elif self.object_index == 0:
            if self.object_list[0] is not None:
                self.object_list.insert(0, None)
        else:
            self.object_index = 0

    def set_current(self, new_object):
        if 0 <= self.object_index < len(self.object_list):
            self.object_list[self.object_index] = new_object
        else:
            self.object_list.append(new_object)
            self.object_index = len(self.object_list) - 1

    def select(self, index):
        if 0 <= index < len(self.object_list):
            self.object_index = index

    def current(self):
        if 0 <= self.object_index < len(self.object_list):
            return self.object_list[self.object_index]
        return None

    def delete_current(self):
        if 0 <= self.object_index < len(self.object_list):
            self.object_list.pop(self.object_index)
            self.object_index = self.object_index - 1 if self.object_index > 0 else 0


    def check_cell_empty(self):
        """
        Returns True, if current index is inside bounds, but current object is None
        That means, that current object was moved using next() or prev()
        and list was extended with None object
        :return: True if current object is None
        """

        if 0 <= self.object_index < len(self.object_list):
            return self.object_list[self.object_index] is None
