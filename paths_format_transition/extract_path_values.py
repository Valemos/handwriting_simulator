from pathlib import Path
import pickle

input_files = list(Path("../letters/").glob("*.hndw"))
output_files = [file.with_name(file.name).with_suffix('.dat') for file in input_files]

for input_file, output_file in zip(input_files, output_files):
    with input_file.open('rb') as fin, output_file.open('wb+') as fout:

        letters_dict = {}

        first_byte = '1'
        while first_byte != b'':
            first_byte = fin.read(1)
            name_len = int.from_bytes(first_byte, byteorder='big')
            name = fin.read(name_len).decode('utf-8')
            letters_dict[name] = []

            cur_bytes = fin.read(4)
            escape_bytes = (0).to_bytes(4, byteorder='big')

            while True:
                x, y = int.from_bytes(cur_bytes[0: 2], byteorder='big'), int.from_bytes(cur_bytes[2: 4], byteorder='big')
                letters_dict[name].append((x, y))

                cur_bytes = fin.read(4)
                if cur_bytes == escape_bytes or cur_bytes == b'':
                    break

        pickle.dump(letters_dict, fout)
