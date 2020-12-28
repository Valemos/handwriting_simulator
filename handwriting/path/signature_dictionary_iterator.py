from handwriting.cyclic_iterator import CyclicIterator
from handwriting.empty_cyclic_iterator import EmptyCyclicIterator
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.path_group import PathGroup
from handwriting.updateable_iterator import UpdatableIterator


class SignatureDictionaryIterator:

    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.group_iter = CyclicIterator(self.dictionary.groups)
        self.variant_iter: CyclicIterator = None
        self.update_variant()

    def update_variant(self):
        current_group = self.group_iter.current()
        if current_group is not None:
            self.variant_iter = current_group.get_iterator()
        else:
            self.variant_iter = EmptyCyclicIterator()

    def next(self):
        if self.variant_iter.is_last():
            self.group_iter.next()
            self.update_variant()

        self.variant_iter.next()

    def prev(self):
        if self.variant_iter.is_first():
            self.group_iter.prev()
            self.update_variant()

        self.variant_iter.prev()

    def current(self) -> HandwrittenPath:
        return self.variant_iter.current()

    def current_group(self) -> PathGroup:
        return self.group_iter.current()

    def select_group(self, group_i: int):
        self.group_iter.select(group_i)
        self.update_variant()

    def select_variant(self, variant_i: int):
        self.variant_iter.select(variant_i)

    def delete_group(self):
        if self.group_iter.current() is not None:
            idx = self.dictionary.remove_group(self.group_iter.index)
            self.group_iter.select(idx)
            self.update_variant()

    def delete_current(self):
        if self.group_iter.current() is not None:
            if self.variant_iter.current() is not None:
                idx = self.dictionary.remove_variant(self.group_iter.index, self.variant_iter.index)
                self.group_iter.select(idx[0])
                self.update_variant()
                self.variant_iter.select(idx[1])
