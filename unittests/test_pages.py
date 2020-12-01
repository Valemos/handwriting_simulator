import unittest
from pathlib import Path

import sys
sys.path.append(r"D:\coding\Python_codes\Handwriting_extractor_project")

from handwriting.page_writing.page import Page

test_image_path = Path("test.jpg")

class TestPageLoading(unittest.TestCase):

    def test_page_loading(self):
        test_page = Page.from_image(test_image_path)

        test_page.set_name("page1")

        test_page.save_file()

        new_page = Page.from_file(test_page.save_path)

        self.assertEqual(test_page.image, new_page.image)
        self.assertEqual(test_page.name, new_page.name)
        self.assertEqual(test_page.save_path, new_page.save_path)

