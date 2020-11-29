from pathlib import Path

from handwriting.updateable_iterator import UpdateableIterator
from handwriting.page_writing.page import Page

class PageManager:
    """class allows to store pages and iterate through them"""

    def __init__(self):
        self.pages = []


    def read_pages_from_dir(self, directory_path: Path, glob_query="*.png"):
        for path in directory_path.glob(glob_query):
            new_page = Page.from_file(path)
            if new_page is not None:
                self.pages.append(new_page)

    def get_iterator(self):
        """Iterator for all pages"""
        return UpdateableIterator(self.pages)
