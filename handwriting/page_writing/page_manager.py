from pathlib import Path

from handwriting.extending_iterator import ExtendingIterator
from handwriting.path_management.point import Point
from handwriting.cyclic_iterator import CyclicIterator
from handwriting.page_writing.page import Page

class PageManager:
    """
    class allows to store pages and iterate through them

    Also this class supplies interface to interact with page lines anchor points
    """

    def __init__(self):
        self.pages = []
        self.pages_iterator = CyclicIterator(self.pages)
        self.line_iterator = None
        self.point_iterators = None

    def start_line_points_setup(self):
        """
        For current page creates updateable iterators to use move functions
        and update or add anchor points
        """
        self.point_iterators = []
        for line in self.pages_iterator.current().lines_points:
            self.point_iterators.append(ExtendingIterator(line))

        # iterator through all other iterator canvas_objects
        self.line_iterator = ExtendingIterator(self.point_iterators)

    def save_page_points(self):
        """
        Uses values from iterators and assigns them to current page object
        """

        if self.line_iterator is not None:
            self.pages_iterator.current().lines_points = [it.object_list for it in self.point_iterators]
            self.point_iterators = None
            self.line_iterator = None

    # set of functions to move between anchor points
    def move_up(self):
        """Move up in points iterator"""

        if self.line_iterator is not None:
            self.line_iterator.prev()
            if self.line_iterator.check_extended():
                self.line_iterator.set_current(ExtendingIterator([]))

    def move_down(self):
        """Move up in points iterators"""

        if self.line_iterator is not None:
            self.line_iterator.next()
            if self.line_iterator.check_extended():
                self.line_iterator.set_current(ExtendingIterator([]))

    def move_left(self):
        """Move up in points iterators"""

        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                self.line_iterator.current().prev()

    def move_right(self):
        """Move up in points iterators"""

        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                self.line_iterator.current().next()

    def update_line_point(self, point: Point):
        """
        Updates or creates new position on this position in iterators
        :param point: Point object to update
        """
        if self.line_iterator is not None:
            if self.line_iterator.current() is not None:
                self.line_iterator.current().set_current(point)

    def get_current_point(self):
        """
        If line points setup started, returns current point
        else, returns None

        :return: Point object for given line index and point index in that line
        """
        if self.line_iterator is not None:
            return self.line_iterator.current().current()
        else:
            return None

    # manage pages
    def current_page(self) -> Page:
        """
        Function ro query current page from iterator object
        :return: current Page object or None if noone present
        """
        return self.pages_iterator.current()

    def next_page(self):
        self.pages_iterator.next()

    def previous_page(self):
        self.pages_iterator.prev()

    def delete_current_page(self):
        if self.pages_iterator.current() is not None:
            self.pages.pop(self.pages_iterator.object_index)
            self.pages_iterator.prev()

    def select_page(self, index):
        self.pages_iterator.select(index)

    # read pages from files
    def read_pages_from_dir(self, directory_path: Path):
        """
        Reads all page data from binary files and after that, reads all images if they are present

        :param directory_path: directory with all images and pages data
        """
        # read all binary pages
        self.pages = Page.read_pages(directory_path)
        prev_i = self.pages_iterator.object_index
        self.pages_iterator = CyclicIterator(self.pages)
        self.pages_iterator.select(prev_i)

    def read_images_to_pages(self, directory_path: Path, glob_queries=None):
        """
        Reads all image_initial files using queries from glob_query list
        :param directory_path: directory to search images
        :param glob_queries: list of queries to glob function
        """

        if glob_queries is None:
            glob_queries = ["*.png", "*.jpg"]

        for query in glob_queries:
            for path in directory_path.glob(query):
                new_page = Page.from_image(path)
                if new_page is not None:
                    self.pages.append(new_page)

        prev_i = self.pages_iterator.object_index
        self.pages_iterator = CyclicIterator(self.pages)
        self.pages_iterator.select(prev_i)
