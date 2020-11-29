from pathlib import Path
from tkinter import messagebox

from handwriting.path_management.signature_dictionary import SignatureDictionary

class DictionaryManager:

    @staticmethod
    def open_dictionary_file(file_path):
        """
        Returns signature dictionary and dictionary irerator
        if cannot open file, returns (None, None)
        """
        dct = SignatureDictionary.from_file(file_path)
        it = None
        if dct is not None:
            it = dct.get_iterator()
        return dct, it

    @staticmethod
    def get_dictionary_file_path(field, path_str=None):
        file_path = Path(path_str) if path_str is not None else Path(field.get())

        sfx = SignatureDictionary.dictionary_suffix
        if file_path.suffix != sfx:
            file_path = file_path.with_suffix(sfx)

        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
            messagebox.showinfo('Message', 'Created new file\n' + str(file_path))

        field.set(str(file_path))
        return file_path

