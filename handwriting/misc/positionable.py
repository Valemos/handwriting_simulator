from abc import ABCMeta, abstractmethod


class IPositionable(metaclass=ABCMeta):
    @abstractmethod
    def set_position(self, point):
        pass

    @abstractmethod
    def get_position(self):
        pass
