from handwriting.cyclic_iterator import CyclicIterator


class EmptyCyclicIterator(CyclicIterator):

    def __init__(self):
        super().__init__(None)

    def get_max(self):
        return 0

    def next(self):
        pass

    def prev(self):
        pass

    def select(self, index):
        pass

    def current(self):
        return None