from pathlib import Path
import pickle
from handwriting.path_management.handwritten_path import HandwrittenPath
from handwriting.path_management.curve import Curve
from handwriting.path_management.path_group import PathGroup
from handwriting.path_management.point import Point
from handwriting.path_management.signature_dictionary import SignatureDictionary

input_files = list(Path("../letters/").glob("*.dat"))

output_folder = Path("../my_letters")

# test_file = Path('test.dat')
# test_file.open('w+').close()

new_dictionary = SignatureDictionary("anton")

for file in input_files:
    with file.open('rb') as fin:
        letters_dict = pickle.load(fin)

        new_path_group = PathGroup(file.name[:file.name.index('.')])
        for letter, points in letters_dict.items():
            curves = [Curve()]
            last_curve_point = None
            for point in points:
                if point != (65535, 65535):
                    # first point must be shifted relative to previous curve if this curve is not the first
                    if last_curve_point is not None:
                        # calculate relative shift from last absolute point
                        curves[-1].last_absolute_point = last_curve_point
                        # must be called after last_curve_point assignment to avoid incorrect calculations
                        curves[-1].append_shift(Point(*point).get_shift(last_curve_point))
                        last_curve_point = None
                    else:
                        curves[-1].append_absolute(Point(*point))
                else:
                    if len(curves) > 0:
                        # create new curve and remember previous point
                        last_curve_point = curves[-1].last_absolute_point
                        curves.append(Curve())

            if len(curves[-1].components) == 0:
                curves.pop(len(curves) - 1)

            if sum((len(cr) for cr in curves)) > 10:
                new_path_group.append_path(HandwrittenPath(letter, curves))
        new_dictionary.append_group(new_path_group)

new_dictionary.save_file()
# print(new_dictionary == SignatureDictionary.from_file(Path("anton_rude_signature.dict")))
