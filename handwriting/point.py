class Point:

    byte_len = 2
    coord_shift = 2 ** (byte_len * 8 - 1)

    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def get_shift(self, prev):
        return Point(self.x - prev.x, self.y - prev.y)

    def shift(self, amount):
        return Point(self.x + amount.x, self.y + amount.y)

    @staticmethod
    def from_byte(data, byte_len=2):
        return Point(int.from_bytes(data[:byte_len], 'big'), int.from_bytes(data[byte_len:], 'big'))
