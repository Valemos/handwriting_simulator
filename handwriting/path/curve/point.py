class Point:

    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return id(self)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __lt__(self, other: float):
        """coordinate-wise comparison"""
        return (self.x < other) or (self.y < other)

    def __gt__(self, other: float):
        """coordinate-wise comparison"""
        return (self.x > other) or (self.y > other)

    def get_shift(self, prev):
        """Returns shift from previous point to current"""
        return Point(self.x - prev.x, self.y - prev.y)

    def shift(self, amount):
        return Point(self.x + amount.x, self.y + amount.y)

    def in_range(self, mn, mx):
        return not (self < mn or self > mx)

    def shift_inplace(self, amount):
        self.x += amount.x
        self.y += amount.y

    def copy(self):
        return Point(self.x, self.y)

    @staticmethod
    def from_byte(data, byte_len=2):
        return Point(int.from_bytes(data[:byte_len], 'big'), int.from_bytes(data[byte_len:], 'big'))

    def empty(self):
        return self.x is None or self.y is None
