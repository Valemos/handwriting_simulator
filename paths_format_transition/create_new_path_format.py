from pathlib import Path
import pickle
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.path_group import PathGroup
from handwriting.path.curve.point import Point
from handwriting.path.signature_dictionary import SignatureDictionary

input_files = list(Path("../letters/").glob("*.dat"))[:3]

output_folder = Path("../my_letters")

# test_file = Path('test_dictionary.dat')
# test_file.open('w+').close()

new_dictionary = SignatureDictionary("anton")

for file in input_files:
    with file.open('rb') as fin:
        letters_dict = pickle.load(fin)

        new_path_group = PathGroup(file.name[:file.name.index('.')])
        for letter, points in letters_dict.items():
            new_path = HandwrittenPath(letter)

            previous_point = None
            for point in points:
                if point != (65535, 65535):
                    # first point must be shifted relative to previous curve if this curve is not the first
                    if previous_point is not None:
                        new_path.new_curve(Point(*point), previous_point)
                        previous_point = None
                    else:
                        new_path.append_absolute(Point(*point))
                else:
                    if len(new_path) > 0:
                        # create new curve and remember previous point
                        previous_point = Point(*point)

            if sum((len(cr) for cr in new_path.components)) > 10:
                new_path_group.append_path(new_path)
        new_dictionary.append_group(new_path_group)

new_dictionary.save_file()
# print(new_dictionary == SignatureDictionary.from_file(Path("anton_rude_signature.dict")))
