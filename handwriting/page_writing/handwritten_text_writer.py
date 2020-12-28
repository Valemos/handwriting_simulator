from handwriting.page_writing.page import Page
from handwriting.path.curve.spacer import Spacer
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.curve.point import Point
from handwriting.path.signature_dictionary import SignatureDictionary


class HandwrittenTextWriter:
    def __init__(self, page, dictionary, space_size=0):
        self.page: Page = page
        self.dictionary: SignatureDictionary = dictionary
        self.space_size = space_size

    def write_text(self, test_text: str):
        text_path = HandwrittenPath()

        space_shift = Point(self.space_size, 0)

        for char in test_text:
            if char == ' ':
                char_path = HandwrittenPath(curves=[Spacer(space_shift)])
            else:
                char_path = self.dictionary[char][0]

            text_path.append_path(char_path)

        return text_path

    def set_space_size(self, space_size):
        self.space_size = space_size


