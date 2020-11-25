from pathlib import Path
import pickle
from handwriting.handwritten_path import HandwrittenPath
from handwriting.curve import Curve
from handwriting.path_group import PathGroup
from handwriting.point import Point

input_files = list(Path("../letters/").glob("*.dat"))

output_folder = Path("../my_letters")

# test_file = Path('test.dat')
# test_file.open('w+').close()

for file in input_files:
    with file.open('rb') as fin:
        letters_dict = pickle.load(fin)

        new_path_group = PathGroup(file.name[:file.name.index('.')])
        new_path_group.initialize_save_file(output_folder / file.name)

        for letter, points in letters_dict.items():
            curves = [Curve()]
            for point in points:
                if point != (65535, 65535):
                    curves[-1].append_shift(Point(*point))
                else:
                    curves.append(Curve())
            if len(curves[-1].components) == 0:
                curves.pop(len(curves) - 1)

            new_path_group.append_path(HandwrittenPath(letter, curves))

    # check if  object loads, and check if they are equal
    # check_group = PathGroup.from_file(new_path_group.save_file)
    #
    # print(check_group == new_path_group)
    # break
