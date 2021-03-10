from handwriting.path.path_collection import PathDrawableCollection
from handwriting.path.transform.i_path_transformer import IPathTransformer
from handwriting.path.transform.path_transformer import PathTransformer


class PathCollectionTransformer(IPathTransformer):

    def __init__(self, collection: PathDrawableCollection, inplace=False):
        super().__init__(collection, inplace)
        self.collection = collection

    def scale(self, x_scale=1, y_scale=1):
        if self.transform_invalid(self.scale, x_scale, y_scale):
            return

        for path in self.transformed:
            PathTransformer(path, inplace=True).scale(x_scale, y_scale)
