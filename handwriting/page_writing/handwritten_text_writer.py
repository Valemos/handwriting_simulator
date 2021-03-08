from handwriting.path.curve.curve import Curve
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.signature_dictionary import SignatureDictionary
from handwriting.page_writing.page import Page
from handwriting.path.curve.point import Point
from handwriting.path.transform.path_transformer import PathTransformer


class HandwrittenTextWriter:
    def __init__(self, page, dictionary, space_size=0):
        self.page: Page = page
        self.dictionary: SignatureDictionary = dictionary

        self.space_shift = None
        self.set_space_size(space_size)

    def write_text(self, test_text: str):
        text_path = HandwrittenPath()

        for char in test_text:
            char_variants = self.dictionary[char]

            if char_variants is not None:
                char_path = char_variants[0]
            else:
                char_path = self.get_special_character_path(char)

            text_path.append_path(char_path)

        # test path transform
        output_path = PathTransformer(text_path)

        return output_path.transform(0.5, 0.5)

    def get_special_character_path(self, char):
        # TODO move special characters to separate class
        if char == ' ':
            return self.space_path()
        if char == '\n':
            return self.space_path()
        else:
            print(f"'{char}' not found in dictionary")
            return self.space_path()

    def set_space_size(self, space_size):
        self.space_shift = Point(space_size, 0)

    def space_path(self):
        return HandwrittenPath(curves=[Curve(start_shift=self.space_shift)])


