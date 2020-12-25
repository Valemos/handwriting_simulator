from handwriting.cyclic_iterator import CyclicIterator
from handwriting.empty_cyclic_iterator import EmptyCyclicIterator
from handwriting.path_management.handwritten_path import HandwrittenPath
from handwriting.path_management.path_group import PathGroup


class SignatureDictionaryIterator:

    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.group_iter = CyclicIterator(self.dictionary.path_groups)
        self._update_variant()

    def _update_variant(self):
        if self.group_iter.current() is not None:
            self.variant_iter = self.group_iter.current().get_iterator()
        else:
            self.variant_iter = EmptyCyclicIterator()

    def next(self) -> HandwrittenPath:
        """Iterates one step forward"""

        self.variant_iter.next()
        if self.variant_iter.object_index == 0:
            # pages_iterator jumped to next loop
            self.group_iter.next()
            self._update_variant()

    def prev(self) -> HandwrittenPath:
        """Iterates step backwards and returns current element"""

        self.variant_iter.prev()
        if self.variant_iter.object_index == self.variant_iter.get_max():
            # pages_iterator jumped to next loop
            self.group_iter.prev()
            self._update_variant()

    def current(self) -> HandwrittenPath:
        return self.variant_iter.current()

    def current_group(self) -> PathGroup:
        return self.group_iter.current()

    def select(self, group_i: int, variant_i: int = None):
        """Assignes indices according to arguments if they are in allowed range"""
        self.group_iter.select(group_i)
        self._update_variant()
        self.variant_iter.select(variant_i if variant_i is not None else 0)

    def delete_group(self):
        if self.group_iter.current() is not None:
            idx = self.dictionary.remove_group(self.group_iter.object_index)
            self.group_iter.select(idx)
            self._update_variant()

    def delete_current(self):
        if self.group_iter.current() is not None:
            if self.variant_iter.current() is not None:
                idx = self.dictionary.remove_variant(self.group_iter.object_index, self.variant_iter.object_index)
                self.group_iter.select(idx[0])
                self._update_variant()
                self.variant_iter.select(idx[1])