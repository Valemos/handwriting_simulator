from handwriting.handwritten_path import HandwrittenPath, Curve, Point


a = HandwrittenPath('hello',
                    [
                        Curve([Point(1, 100), Point(50, 50), Point(20, 111), Point(50, 66)]),
                        Curve([Point(50, 56), Point(10, 70)])
                    ])
b = HandwrittenPath('out', [])

bt = a.get_bytes()

c = HandwrittenPath.from_bytes(bt)
print(b == c)
