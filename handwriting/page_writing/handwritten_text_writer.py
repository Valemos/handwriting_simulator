from handwriting.path.transform.dictionary_transformer import DictionaryTransformer
from handwriting.path.path_collection import PathDrawableCollection
from handwriting.path.curve.curve import Curve
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.signature_dictionary import SignatureDictionary
from handwriting.page_writing.page import Page
from handwriting.path.curve.point import Point
from handwriting.path.transform.path_collection_transformer import PathCollectionTransformer
from handwriting.path.transform.path_shift_box import PathShiftBox


class HandwrittenTextWriter:
    def __init__(self, page, dictionary, space_size=0):
        self.page: Page = page
        self.dictionary: SignatureDictionary = dictionary
        self.dict_transformer = DictionaryTransformer(dictionary)

        self.space_shift: Point = self.get_space_shift(space_size)

    def write_text(self, text_input: str):
        text_path = PathDrawableCollection()
        borders_path = PathDrawableCollection()

        self.dict_transformer.scale(0.5, 0.5)

        letter_size: list = self.dict_transformer.get_result().get_max_letter_size()

        for letter_index, char in enumerate(text_input):
            char_variants = self.dictionary[char]

            if char_variants is not None:
                char_path = char_variants[0]
            else:
                char_path = self.get_special_character_path(char)

            if char_path is not None:
                boxed_path = PathShiftBox(char_path, letter_size)
                boxed_path.set_position(self.get_letter_position(letter_index, letter_size))
                text_path.append(boxed_path)
                borders_path.append(boxed_path.get_border_path())

        # test path transform
        path_collection = PathCollectionTransformer(text_path)
        return path_collection.get_result()

    def get_special_character_path(self, char):
        if char == ' ':
            return self.space_path()
        elif char == '\n':
            return self.new_line_path()
        else:
            print(f"'{repr(char)}' not found in dictionary")
            return None

    @staticmethod
    def get_space_shift(space_size):
        return Point(space_size, 0)

    def set_space_size(self, space_size):
        self.space_shift = self.get_space_shift(space_size)

    def space_path(self):
        return HandwrittenPath(curves=[Curve(start_shift=self.space_shift)])

    def new_line_path(self):
        return self.space_path()

    def get_letter_position(self, text_index, size):
        return Point(text_index * size[0], 0)
