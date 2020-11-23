from pathlib import Path
import pickle
from handwriting.handwritten_path import HandwrittenPath
from handwriting.curve import Curve

input_files = list(Path("../letters/").glob("*.dat"))

output_folder = Path("../my_letters")

test_file = Path('test.dat')
test_file.open('w').close()

for file in input_files:
    with file.open('rb') as fin:
        letters_dict = pickle.load(fin)

        for letter, points in letters_dict.items():
            curves = [Curve()]
            for point in points:
                if point != (65535, 65535):
                    curves[-1].append_shift(*point)
                else:
                    curves.append(Curve())
            if len(curves[-1].shifts) == 0:
                curves.pop(len(curves) - 1)

            HandwrittenPath(letter, curves).append_to_file(test_file)
    break

paths_list = HandwrittenPath.read_file(test_file)
pass
