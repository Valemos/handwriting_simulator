from handwriting.path.path_collection import PathDrawableCollection
from handwriting.path.transform.i_path_transformer import IPathTransformer
from handwriting.path.transform.path_transformer import PathTransformer


class PathCollectionTransformer(IPathTransformer):

    def __init__(self, collection: PathDrawableCollection):
        super().__init__()
        self.collection = collection
        self.transformed = [PathTransformer(path) for path in collection.paths]

    def get_result(self):
        return PathDrawableCollection([path.get_result() for path in self.transformed])

    def scale(self, x_scale=1, y_scale=1):
        if self.is_repeated_transform(self.scale, x_scale, y_scale):
            return

        for path_transformed in self.transformed:
            path_transformed.scale(x_scale, y_scale)
