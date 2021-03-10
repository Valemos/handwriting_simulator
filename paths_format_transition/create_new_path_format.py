from pathlib import Path
import pickle
from pickletools import optimize

from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.path_group import PathGroup
from handwriting.path.curve.point import Point
from handwriting.path.signature_dictionary import SignatureDictionary

input_files = list(Path("../letters/").glob("*.dat"))

output_folder = Path("../letters_updated")

# test_file = Path('test_dictionary.dat')
# test_file.open('w+').close()

new_dictionary = SignatureDictionary("anton")


def remove_empty_curves(path):
    i = 0
    while i < len(path.components):
        if len(path.components[i]) == 0:
            path.components.pop(i)
        else:
            i += 1


gap_point = Point(65535, 65535)

for file in input_files:
    with file.open('rb') as fin:
        letters_dict = pickle.load(fin)

        new_path_group = PathGroup(file.name[:file.name.index('.')])
        for letter, points in letters_dict.items():
            new_path = HandwrittenPath(letter)

            point = Point(0, 0)
            prev_point = Point(0, 0)
            is_first_point = True
            i = 0
            while i < len(points):
                prev_point = point
                point = Point(*points[i])
                i += 1

                if point == gap_point:
                    is_first_point = True
                    # take next point
                    if i < len(points):
                        point = Point(*points[i])
                        i += 1
                    else:
                        break

                if is_first_point:
                    new_path.new_curve(point, prev_point)
                    is_first_point = False
                else:
                    new_path.append_absolute(point)

            if new_path.points_count() > 10:
                remove_empty_curves(new_path)
                new_path_group.append_path(new_path)

        new_dictionary.append_group(new_path_group)

new_dictionary.save_file()
# print(new_dictionary == SignatureDictionary.from_file(Path("anton_rude_signature.dict")))
