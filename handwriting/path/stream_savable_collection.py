from abc import ABC

from handwriting.path.stream_savable import IStreamSavable


class IStreamSavableCollection(IStreamSavable, ABC):

    def __init__(self, components) -> None:
        self.components = components if components is not None else []

    def __len__(self):
        return len(self.components)

    def __getitem__(self, i):
        return self.components[i]

    def __eq__(self, o: object) -> bool:
        if isinstance(o, IStreamSavableCollection):
            return self.components == o.components
        return False

    def inner_elements_count(self):
        total = 0
        for component in self.components:
            if isinstance(component, IStreamSavableCollection):
                total += component.inner_elements_count()
            else:
                total += len(component)

        return total
