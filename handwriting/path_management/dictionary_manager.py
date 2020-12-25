from pathlib import Path
from tkinter import messagebox, filedialog

from handwriting.path_management.signature_dictionary import SignatureDictionary

class DictionaryManager:

    def __init__(self):
        self.dictionary_groups = None
        self.iterator = None

    @staticmethod
    def read_dictionary_file(file_path):
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
    def get_dictionary_file_path(path_str=None):

        file_path = Path(path_str if path_str is not None else '')
        if not file_path.exists():
            file_path = filedialog.askopenfilename()

        file_path = Path(file_path) if file_path != '' else SignatureDictionary.default_path

        file_path = DictionaryManager.create_dictionary_file_if_needed(file_path)

        return file_path

    @staticmethod
    def create_dictionary_file_if_needed(file_path):
        required_suffix = SignatureDictionary.dictionary_suffix
        if file_path.suffix != required_suffix:
            file_path = file_path.with_suffix(required_suffix)
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
            messagebox.showinfo('Message', 'Created new file\n' + str(file_path))
        return file_path

    def read_from_file(self, file_string):
        dict_file = self.get_dictionary_file_path(file_string)
        self.dictionary_groups, self.paths_iterator = self.read_dictionary_file(dict_file)

    def exists(self):
        return self.iterator is not None
