from typing import Iterator

from handwriting.paths_dictionary.paths_collection_iterator import PathsCollectionIterator
from handwriting.path.curve.i_line_iterable import ILineIterable
from handwriting.path.curve.point import Point


class PathDrawableCollection(ILineIterable):

    def __init__(self, paths: list = None):
        self.paths = paths if paths is not None else []

    def __iter__(self):
        return iter(self.paths)

    def get_iterator(self, shift: Point = None) -> Iterator:
        return iter(self.paths)

    def get_lines(self, shift: Point = None):
        # this iterator do not changes settings in paths
        return PathsCollectionIterator(self.paths)

    def append(self, path: ILineIterable):
        self.paths.append(path)

    def draw(self, image_draw):
        for p1, p2 in self.get_lines():
            image_draw.line((p1.x, p1.y, p2.x, p2.y), fill=0, width=3)
