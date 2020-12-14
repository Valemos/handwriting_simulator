from pathlib import Path

from handwriting.extending_iterator import ExtendingIterator
from handwriting.page_writing.anchor_manager import AnchorManager
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
        self.anchor_manager: AnchorManager = None

    def start_line_points_setup(self, canvas, draw_function):
        """
        For current page creates updateable iterators to use move functions
        and update or add anchor points
        """
        self.anchor_manager = AnchorManager(self.pages_iterator.current())
        self.anchor_manager.set_canvas_draw(canvas, draw_function)

    # manage pages
    def current_page(self) -> Page:
        """
        Function ro query current page from iterator object
        :return: current Page object or None if noone present
        """
        return self.pages_iterator.current()

    def next_page(self):
        if self.anchor_manager is not None:
            self.anchor_manager = None
        self.pages_iterator.next()

    def previous_page(self):
        if self.anchor_manager is not None:
            self.anchor_manager = None
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
