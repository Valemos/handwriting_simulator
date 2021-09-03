from abc import ABC


class ICollection(ABC):

    def __init__(self, components) -> None:
        self.components = components if components is not None else []

    def __len__(self):
        return len(self.components)

    def __getitem__(self, i):
        return self.components[i]

    def __iter__(self):
        return iter(self.components)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, ICollection):
            return self.components == o.components
        return False

    def empty(self):
        return len(self.components) == 0
