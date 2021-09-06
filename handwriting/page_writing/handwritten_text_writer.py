from handwriting.misc.exceptions import ObjectNotFound
from handwriting.path.transform.dictionary_transformer import DictionaryTransformer
from handwriting.paths_dictionary.path_collection import PathsCollection
from handwriting.path.curve.curve import Curve
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.paths_dictionary.signature_dictionary import SignatureDictionary
from handwriting.page_writing.page import Page
from handwriting.path.curve.point import Point
from handwriting.path.transform.path_shift_box import PathShiftBox


class PathTextWriter:
    def __init__(self, dictionary, line_height, space_size=10):
        self.dictionary: SignatureDictionary = dictionary
        self.dict_transformer = DictionaryTransformer(dictionary)

        self.space_shift: Point = self.get_space_shift(space_size)

    def write_text(self, text_input: str) -> PathsCollection:
        text_path = PathsCollection()
        borders_path = PathsCollection()

        self.dict_transformer.scale(0.5, 0.5)
        transformed_dict = self.dict_transformer.get_result()

        letter_size: list = transformed_dict.get_max_letter_size()
        cur_write_position = self.get_letter_position(0, )

        for letter_index, char in enumerate(text_input):
            char_variants = transformed_dict[char]

            if char_variants is not None:
                char_path = char_variants[0]
            else:
                char_path = self.get_special_character_path(char)

            if char_path is not None:
                boxed_path = PathShiftBox(char_path)
                boxed_path.extend_height(letter_size[1])
                boxed_path.set_position(self.get_letter_position(letter_index, letter_size))
                text_path.append(boxed_path)
                borders_path.append(boxed_path.get_border_path())

        return text_path

    def get_special_character_path(self, char):
        if char == ' ':
            return self.space_path()
        elif char == '\n':
            return self.new_line_path()
        else:
            raise ObjectNotFound(f"'{repr(char)}' not found in dictionary")

    @staticmethod
    def get_space_shift(space_size):
        return Point(space_size, 0)

    def set_space_size(self, space_size):
        self.space_shift = self.get_space_shift(space_size)

    def space_path(self):
        return HandwrittenPath(curves=[Curve(start=self.space_shift)])

    def new_line_path(self):
        return self.space_path()

    def get_letter_position(self, text_index, size):
        return Point(text_index * size[0], 0)
