from pathlib import Path

from handwriting.misc.exceptions import ObjectNotFound
from handwriting.page_writing.anchor_manager import AnchorManager
from handwriting.misc.cyclic_iterator import CyclicIterator
from handwriting.page_writing.page import Page


class PageIterator:
    """
    class allows to store pages and iterate through them
    """

    def __init__(self):
        self.pages = CyclicIterator([])

    def get_page(self) -> Page:
        try:
            return self.pages.get_or_raise()
        except ObjectNotFound:
            return self.create_empty_page()

    def next_page(self):
        self.pages.next()

    def previous_page(self):
        self.pages.prev()

    def delete_current_page(self):
        self.pages.remove_current()
        self.pages.update_index()

    def select_page(self, index):
        self.pages.select(index)

    # read pages from files
    def read_pages_from_dir(self, directory_path: Path):
        """
        Reads all page data from binary files and after that, reads all images if they are present

        :param directory_path: directory with all images and pages data
        """
        # read all binary pages
        self.pages = Page.read_pages(directory_path)
        prev_i = self.pages.index
        self.pages = CyclicIterator(self.pages)
        self.pages.select(prev_i)

    def read_images_to_pages(self, search_directory: Path, image_patterns=None):
        if image_patterns is None:
            image_patterns = ["*.png", "*.jpg"]

        for query in image_patterns:
            for path in search_directory.glob(query):
                try:
                    new_page = Page.from_image(path)
                    self.pages.append(new_page)
                except Exception as exc:
                    print(f"cannot open file {str(exc)}")

        prev_i = self.pages.index
        self.pages = CyclicIterator(self.pages)
        self.pages.select(prev_i)

    def page_exists(self):
        return len(self.pages) > 0

    def create_empty_page(self):
        page = Page.empty()
        self.pages.append(page)
        return page
