from abc import ABC

from handwriting.path.stream_savable import IStreamSavable


class IStreamSavableCollection(IStreamSavable, ABC):

    def __init__(self, components) -> None:
        self.components = components if components is not None else []

    def __len__(self):
        return len(self.components)

    def __getitem__(self, i):
        return self.components[i]

    def __iter__(self):
        return iter(self.components)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, IStreamSavableCollection):
            return self.components == o.components
        return False
