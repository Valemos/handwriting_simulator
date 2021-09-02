from pathlib import Path

from handwriting.page_writing.anchor_manager import AnchorManager
from handwriting.misc.cyclic_iterator import CyclicIterator
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

    def start_anchor_editing(self, canvas):
        self.anchor_manager = AnchorManager(canvas, self.pages_iterator.get_or_raise())
        self.anchor_manager.draw_all()

    def stop_anchor_editing(self):
        if self.anchor_manager is None:
            return

        self.anchor_manager.save_page_points()
        self.anchor_manager.delete_all_canvas_objects()
        self.anchor_manager = None

    def is_started_anchor_editing(self):
        return self.anchor_manager is not None

    def get_page(self) -> Page:
        return self.pages_iterator.get_or_raise()

    def finish_anchor_editing(self):
        if self.anchor_manager is not None:
            self.anchor_manager.save_page_points()
            self.anchor_manager = None

    def next_page(self):
        self.finish_anchor_editing()
        self.pages_iterator.next()

    def previous_page(self):
        self.finish_anchor_editing()
        self.pages_iterator.prev()

    def delete_current_page(self):
        self.pages_iterator.remove_current()
        self.pages_iterator.update_index()

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
        prev_i = self.pages_iterator.index
        self.pages_iterator = CyclicIterator(self.pages)
        self.pages_iterator.select(prev_i)

    def read_images_to_pages(self, search_directory: Path, glob_queries=None):
        if glob_queries is None:
            glob_queries = ["*.png", "*.jpg"]

        for query in glob_queries:
            for path in search_directory.glob(query):
                try:
                    new_page = Page.from_image(path)
                    self.pages.append(new_page)
                except Exception as exc:
                    print(f"cannot open file {str(exc)}")

        prev_i = self.pages_iterator.index
        self.pages_iterator = CyclicIterator(self.pages)
        self.pages_iterator.select(prev_i)

    def page_exists(self):
        return len(self.pages_iterator) > 0

    def create_empty_page(self):
        self.pages_iterator.append(Page.empty())
        return self.pages_iterator.get_or_raise()

    def get_anchor_indices(self):
        if self.is_started_anchor_editing():
            return self.anchor_manager.get_current_indices()
