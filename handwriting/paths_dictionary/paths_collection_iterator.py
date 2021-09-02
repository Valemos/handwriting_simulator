from typing import Iterator

from handwriting.misc.container_iterator import AContainerIterator
from handwriting.misc.updateable_iterator import UpdatableIterator


class PathsCollectionIterator(Iterator):

    def __init__(self, paths):
        self.paths = paths
        self.collection_iterator = UpdatableIterator(self.paths)
        self.cur_lines_iterator: AContainerIterator = None

    def __next__(self):
        if self.cur_lines_iterator is None:
            self.iterate_next_path()

        try:
            points = next(self.cur_lines_iterator)
        except StopIteration:
            # continue iterating next object without initial shift
            self.iterate_next_path()
            return self.__next__()
        
        return points

    def iterate_next_path(self):
        self.cur_lines_iterator = next(self.collection_iterator).get_lines()
