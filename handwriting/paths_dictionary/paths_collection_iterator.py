from typing import Iterator

from handwriting.misc.container_iterator import AContainerIterator
from handwriting.misc.i_lines_iterator import ILinesIterator
from handwriting.misc.updateable_iterator import UpdatableIterator


class PathsCollectionIterator(ILinesIterator):

    # this iterator does not change paths

    def __init__(self, paths):
        self.paths = paths
        self.collection_iterator = UpdatableIterator(self.paths)
        self.cur_lines_iterator: AContainerIterator = None

    def __next__(self):
        if self.cur_lines_iterator is None:
            self._iterate_next_path()

        try:
            points = next(self.cur_lines_iterator)
        except StopIteration:
            # continue iterating next object without initial shift
            self._iterate_next_path()
            return self.__next__()
        
        return points

    def _iterate_next_path(self):
        self.cur_lines_iterator = next(self.collection_iterator).get_lines()
