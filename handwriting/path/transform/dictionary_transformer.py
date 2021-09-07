from handwriting.paths_dictionary.signature_dictionary import SignatureDictionary
from handwriting.path.transform.i_path_transformer import IPathTransformer
from handwriting.path.transform.path_transformer import PathTransformer


class DictionaryTransformer(IPathTransformer):

    def __init__(self, dictionary: SignatureDictionary, inplace=False):
        super().__init__(dictionary, inplace)

    def scale(self, x_scale=1, y_scale=1):
        if self.transform_if_not_repeated(self.scale, x_scale, y_scale):
            return

        if x_scale == 1 and y_scale == 1:
            return

        for group in self.transformed:
            for letter in group:
                # always transform inplace because self.transformed_dict gets copied every time
                PathTransformer(letter, inplace=True).scale(x_scale, y_scale)
