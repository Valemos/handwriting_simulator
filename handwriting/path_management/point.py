class Point:

    byte_len = 2
    coord_shift = 2 ** (byte_len * 8 - 1)

    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __iter__(self):
        return (i for i in (self.x, self.y))

    def get_shift(self, prev):
        """Returns Point which was added to previous point to get this one"""
        return Point(self.x - prev.x, self.y - prev.y)

    def shift(self, amount):
        return Point(self.x + amount.x, self.y + amount.y)

    @staticmethod
    def from_byte(data, byte_len=2):
        return Point(int.from_bytes(data[:byte_len], 'big'), int.from_bytes(data[byte_len:], 'big'))
