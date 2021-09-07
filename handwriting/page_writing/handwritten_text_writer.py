from handwriting.misc.exceptions import ObjectNotFound
from handwriting.path.curve.curve import Curve
from handwriting.path.curve.point import Point
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.transform.dictionary_transformer import DictionaryTransformer
from handwriting.path.transform.path_shift_box import PathShiftBox
from handwriting.paths_dictionary.path_collection import PathsCollection
from handwriting.paths_dictionary.signature_dictionary import SignatureDictionary


class PathTextWriter:
    def __init__(self, dictionary, line_height, space_size=10):
        self.dictionary: SignatureDictionary = dictionary
        self.dict_transformer = DictionaryTransformer(dictionary)

        self.space_size = space_size
        self.line_height = line_height
        self.current_line = 1

    def write_text(self, text_input: str) -> PathsCollection:
        text_path = PathsCollection()

        self.dict_transformer.scale(0.5, 0.5)
        transformed_dict = self.dict_transformer.get_result()

        letter_size: list = transformed_dict.get_max_letter_size()
        cur_write_position = Point(0, self.line_height)

        for letter_index, char in enumerate(text_input):
            try:
                char_variants = transformed_dict[char]
                char_path = char_variants[0]

                boxed_path = PathShiftBox(char_path)
                boxed_path.extend_height(letter_size[1])
                boxed_path.set_position(cur_write_position)

                text_path.append(boxed_path)
                cur_write_position.x += boxed_path.box.get_size_x()
            except ObjectNotFound:
                if char == '\n':
                    self.current_line += 1
                    cur_write_position = Point(0, self.current_line * self.line_height)
                elif char == ' ':
                    cur_write_position.x += self.space_size
                else:
                    raise ObjectNotFound(f"'{repr(char)}' not found in dictionary")

        return text_path

    def set_space_size(self, space_size):
        self.space_size = Point(space_size, 0)

    def get_letter_position(self, text_index, size):
        return Point(text_index * size[0], 0)
