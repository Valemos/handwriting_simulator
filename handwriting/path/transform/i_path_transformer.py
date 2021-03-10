from abc import ABCMeta, abstractmethod


class IPathTransformer(metaclass=ABCMeta):

    def __init__(self):
        self.previous_transforms = {}  # stores parameters for previous transformations

    def is_repeated_transform(self, function, *params):
        previous_params = None
        if function in self.previous_transforms:
            previous_params = self.previous_transforms[function]

        # store current parameters for next check
        self.previous_transforms[function] = params

        return previous_params == params

    @abstractmethod
    def scale(self, x_scale, y_scale):
        pass

    @abstractmethod
    def get_result(self):
        pass
