import unittest

import numpy as np
from PIL import Image

from handwriting.page_writing.handwritten_text_writer import HandwrittenTextWriter
from handwriting.page_writing.page import Page
from handwriting.path_management.curve import Curve
from handwriting.path_management.handwritten_path import HandwrittenPath
from handwriting.path_management.path_group import PathGroup
from handwriting.path_management.point import Point
from handwriting.path_management.signature_dictionary import SignatureDictionary


class TestTextWriter(unittest.TestCase):

    @staticmethod
    def init_test_path_group(name):
        curve = Curve([Point(0, 0), Point(-1, -1), Point(-1, 1), Point(0, -1)])
        path = HandwrittenPath('', [curve])
        path_group = PathGroup(name, [path])
        return path_group

    @staticmethod
    def init_page():
        page_image = Image.fromarray(np.zeros((10, 10)))
        page = Page(page_image, 'page')
        return page

    @staticmethod
    def init_dictionary(path_groups):
        dictionary = SignatureDictionary('test', path_groups)
        return dictionary

    def check_iterator_continues_with_other(self, parent_iter, child_iter):
        child_initialized = False
        try:
            while True:
                child_obj = next(child_iter)
                child_initialized = True
                parent_obj = next(parent_iter)

                self.assertTupleEqual(child_obj, parent_obj)

                child_initialized = False
        except StopIteration:
            if child_initialized:
                self.fail("parent finished before child object")
            return

    def setUp(self):
        self.path_group_a = self.init_test_path_group('a')
        self.path_group_b = self.init_test_path_group('b')
        self.page = self.init_page()
        self.dictionary = self.init_dictionary([self.path_group_a, self.path_group_b])

    def test_single_letter_written(self):

        test_letter = 'a'
        writer = HandwrittenTextWriter(self.page, self.dictionary)
        text_path = writer.write_text(test_letter)
        text_path_iter = iter(text_path)

        self.check_iterator_continues_with_other(text_path_iter, iter(self.path_group_a[0]))

    def test_multiple_letters_written(self):
        test_text = 'ab'

        writer = HandwrittenTextWriter(self.page, self.dictionary)
        text_path = writer.write_text(test_text)

        text_path_iter = iter(text_path)

        self.check_iterator_continues_with_other(text_path_iter, iter(self.path_group_a[0]))
        self.check_iterator_continues_with_other(text_path_iter, iter(self.path_group_b[0]))
