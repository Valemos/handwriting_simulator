from pathlib import Path

from handwriting.path_management.path_group import PathGroup

inp_file = next(Path("../letters/").glob("*.dat"))

test_file = Path('test.dat')
test_file.open('w').close()

with inp_file.open('rb') as fin:

    path_group = PathGroup.read_next(fin)

pass
