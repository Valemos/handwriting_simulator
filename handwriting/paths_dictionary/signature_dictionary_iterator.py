from typing import Union

from handwriting.misc.cyclic_iterator import CyclicIterator
from handwriting.misc.empty_cyclic_iterator import EmptyCyclicIterator
from handwriting.misc.exceptions import ObjectNotFound
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.paths_dictionary.path_group import PathGroup


class SignatureDictionaryIterator:

    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.group_iter = CyclicIterator(self.dictionary.groups)
        self.variant_iter: CyclicIterator = None
        self.update_variant()

    def update_variant(self):
        try:
            self.variant_iter = self.group_iter.get_or_raise().get_paths_iterator()
        except ObjectNotFound:
            self.variant_iter = EmptyCyclicIterator()

    def next(self):
        if self.variant_iter.is_last():
            # select next group and first variant
            self.group_iter.next()
            self.update_variant()
            self.variant_iter.select(0)
        else:
            self.variant_iter.next()

    def prev(self):
        if self.variant_iter.is_first():
            # select previous group and last variant
            self.group_iter.prev()
            self.update_variant()
            self.variant_iter.select_last()
        else:
            self.variant_iter.prev()

    def get_variant_or_raise(self) -> HandwrittenPath:
        return self.variant_iter.get_or_raise()

    def get_group_or_raise(self) -> PathGroup:
        return self.group_iter.get_or_raise()

    def get_variant_or_none(self) -> Union[HandwrittenPath, None]:
        return self.variant_iter.get_or_none()

    def get_group_or_none(self) -> Union[PathGroup, None]:
        return self.group_iter.get_or_none()

    def select_group(self, group_i: int):
        self.group_iter.select(group_i)
        self.update_variant()

    def select_variant(self, variant_i: int):
        self.variant_iter.select(variant_i)

    def delete_group(self):
        if self.group_iter.empty(): return

        self.dictionary.remove_group(self.group_iter.index)
        self.group_iter.update_index()
        self.update_variant()

    def delete_current_variant(self):
        if self.group_iter.empty(): return
        if self.variant_iter.empty(): return

        new_group, new_variant = self.dictionary.remove_variant(self.group_iter.index, self.variant_iter.index)

        # must be called in this order or variants will be taken from previous group
        self.group_iter.select(new_group)
        self.update_variant()
        self.variant_iter.select(new_variant)

    def get_current_labels(self):
        group = self.get_group_or_none()
        variant = self.get_variant_or_none()

        return group.name if group is not None else None, \
                variant.name if variant is not None else None
