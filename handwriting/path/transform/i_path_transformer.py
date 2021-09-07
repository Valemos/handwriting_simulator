from abc import ABCMeta, abstractmethod
from copy import deepcopy


class IPathTransformer(metaclass=ABCMeta):

    def __init__(self, original, inplace=False):
        # stores parameters and function pointer for previous transformations
        self.previous_transforms = {}

        # to allow transforming inplace need to implement init_path_copy accordingly
        self.inplace = inplace
        self.original = original
        self.transformed = None
        self.init_transformed()

    def is_repeated_transform(self, function, *params):
        previous_params = None
        if function in self.previous_transforms:
            previous_params = self.previous_transforms[function]

        # store current parameters for next check
        self.previous_transforms[function] = params

        return previous_params == params

    def transform_if_not_repeated(self, function, *params):
        """if transform is valid, initializes new transformed object"""
        if self.is_repeated_transform(function, *params):
            return True
        else:
            # new transformation must be applied to original path
            self.init_transformed()
            return False

    def init_transformed(self):
        self.transformed = self.get_original() if self.inplace else self.get_copy()

    def get_original(self):
        return self.original

    def get_copy(self):
        return deepcopy(self.original)

    def get_result(self):
        return self.transformed

    @abstractmethod
    def scale(self, x_scale, y_scale):
        pass
