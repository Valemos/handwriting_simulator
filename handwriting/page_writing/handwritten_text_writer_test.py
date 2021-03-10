import unittest

import numpy as np
from PIL import Image, ImageDraw

from handwriting.page_writing.handwritten_text_writer import PathTextWriter
from handwriting.page_writing.page import Page
from handwriting.path.curve.curve import Curve
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.path_group import PathGroup
from handwriting.path.curve.point import Point
from handwriting.path.signature_dictionary import SignatureDictionary


class TestTextWriter(unittest.TestCase):

    @staticmethod
    def init_test_path_group(name):
        curve = Curve([Point(0, 0), Point(2, 2), Point(1, -1), Point(1, 0)])
        path = HandwrittenPath(curves=[curve])
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

    @unittest.skip("image show do not needed")
    def test_show_image(self):
        test_text = 'a b'

        writer = PathTextWriter(self.page, self.dictionary)
        text_path = writer.write_text(test_text)

        image = Image.fromarray(np.full((20, 20), 255))
        draw = ImageDraw.Draw(image)

        it = text_path.get_iterator(Point(5, 5))
        try:
            while True:
                p1, p2 = next(it)
                draw.line((*p1, *p2), 0)
        except StopIteration:
            image.resize((100, 100)).show()

    @staticmethod
    def init_path_plus_5():
        return HandwrittenPath(curves=[Curve([Point(1, 0), Point(1, 0), Point(1, 0), Point(1, 0), Point(1, 0)])])

    def setUp(self):
        self.path_group_a: PathGroup = self.init_test_path_group('a')
        self.path_group_b: PathGroup = self.init_test_path_group('b')
        self.path_plus_5: HandwrittenPath = self.init_path_plus_5()
        self.page: Page = self.init_page()
        self.dictionary: SignatureDictionary = self.init_dictionary([self.path_group_a, self.path_group_b])

    def test_single_letter_written(self):

        test_letter = 'a'
        writer = PathTextWriter(self.page, self.dictionary)
        text_path = writer.write_text(test_letter)
        text_path_iter = iter(text_path)

        self.check_iterator_continues_with_other(text_path_iter, iter(self.path_group_a[0]))

    def test_multiple_letters_written(self):
        test_text = 'ab'

        writer = PathTextWriter(self.page, self.dictionary)
        text_path = writer.write_text(test_text)
        text_path_iter = iter(text_path)

        last_point = self.path_group_a[0].get_last_point()
        b_iter = self.path_group_b[0].get_iterator(last_point)

        self.check_iterator_continues_with_other(text_path_iter, iter(self.path_group_a[0]))
        self.check_iterator_continues_with_other(text_path_iter, b_iter)

    def test_space_written(self):
        test_text = 'a a'

        writer = PathTextWriter(self.page, self.dictionary)
        writer.set_space_size(5)
        text_path_iter = iter(writer.write_text(test_text))

        self.path_group_a[0].set_position(Point(0, 0))
        last_point = self.path_group_a[0].get_last_point()

        self.check_iterator_continues_with_other(text_path_iter, iter(self.path_group_a[0]))

        a_iter_shifted = self.path_group_a[0].get_iterator(last_point.shift(Point(5, 0)))
        self.check_iterator_continues_with_other(text_path_iter, a_iter_shifted)

    def test_save_and_load_dictionary(self):
        self.dictionary.save_file()

        d2 = SignatureDictionary.from_file(self.dictionary.get_save_path())

        self.assertEquals(self.dictionary, d2)
