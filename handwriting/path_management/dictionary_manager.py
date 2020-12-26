from pathlib import Path
from tkinter import messagebox, filedialog

from handwriting.path_management.signature_dictionary import SignatureDictionary
from handwriting.path_management.signature_dictionary_iterator import SignatureDictionaryIterator


class DictionaryManager:

    def __init__(self):
        self.dictionary: SignatureDictionary = None
        self.iterator: SignatureDictionaryIterator = None

    @staticmethod
    def read_dictionary_file(file_path):
        """
        Returns signature dict_manager and dict_manager irerator
        if cannot open file, returns (None, None)
        """
        dct = SignatureDictionary.from_file(file_path)
        it = None
        if dct is not None:
            it = dct.get_iterator()
        return dct, it

    @classmethod
    def get_dictionary_file_path(cls, path_str=None):
        file_path = Path(path_str)
        if not cls.is_valid_dictionary_path(file_path):
            file_path = filedialog.askopenfilename()
            file_path = Path(file_path) if file_path != "" else SignatureDictionary.default_path

        file_path = DictionaryManager.create_file_if_needed(file_path)
        return file_path

    @staticmethod
    def is_valid_dictionary_path(path):
        if path == "" or path is None:
            return False

        if path.suffix != SignatureDictionary.dictionary_suffix:
            return False

        return True

    @staticmethod
    def create_file_if_needed(file_path):
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
            messagebox.showinfo('Message', 'Created new file\n' + str(file_path))
        return file_path

    def read_from_file(self, file_string):
        dict_file = self.get_dictionary_file_path(file_string)
        self.dictionary, self.iterator = self.read_dictionary_file(dict_file)
        return dict_file

    def save_file(self, file_name):
        save_path = self.get_dictionary_file_path(file_name)
        self.dictionary.save_file(save_path)

    def exists(self):
        return self.iterator is not None

    def size(self):
        if self.dictionary is not None:
            return len(self.dictionary)
        else:
            return 0
