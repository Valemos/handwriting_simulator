from typing import Iterator

from handwriting.paths_dictionary.paths_collection_iterator import PathsCollectionIterator
from handwriting.path.curve.i_line_iterable import ILinesIterable
from handwriting.path.curve.point import Point


class PathsCollection(ILinesIterable):

    def __init__(self, paths: list = None):
        self.paths = paths if paths is not None else []

    def __iter__(self) -> PathsCollectionIterator:
        return self.get_lines()

    def get_lines(self, shift: Point = None) -> PathsCollectionIterator:
        return PathsCollectionIterator(self.paths)

    def append(self, path: ILinesIterable):
        self.paths.append(path)
