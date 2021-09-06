from pathlib import Path
from tkinter import messagebox, filedialog

from handwriting.paths_dictionary.path_group import PathGroup
from handwriting.paths_dictionary.signature_dictionary import SignatureDictionary
from handwriting.paths_dictionary.signature_dictionary_iterator import SignatureDictionaryIterator


class DictionaryManager:

    def __init__(self):
        self.dictionary: SignatureDictionary = SignatureDictionary()
        self.iterator: SignatureDictionaryIterator = self.dictionary.get_paths_iterator()

    @classmethod
    def get_or_create_path(cls, path_str):
        file_path = Path(path_str)
        if not cls.is_valid_dictionary_path(file_path):
            file_path = filedialog.askopenfilename()
            if file_path != '' and file_path != tuple():
                file_path = Path(file_path)
            else:
                file_path = SignatureDictionary.default_path

        file_path = DictionaryManager.create_if_not_exists(file_path)
        return file_path

    @staticmethod
    def is_valid_dictionary_path(path: Path):
        if path == "" or path is None:
            return False

        if path.suffix != SignatureDictionary.dictionary_suffix:
            return False

        return True

    @staticmethod
    def create_if_not_exists(file_path: Path):
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
            messagebox.showinfo('Message', 'Created new file\n' + str(file_path))
        return file_path

    def read_file(self, file_path: Path):
        self.dictionary = SignatureDictionary.from_file(file_path)
        self.iterator = self.dictionary.get_paths_iterator()

    def create_default(self):
        path = SignatureDictionary.default_path
        self.create_if_not_exists(path)
        self.save_file(path)

    def save_file(self, file_name):
        save_path = self.get_or_create_path(file_name)
        self.dictionary.save_file(save_path)

    def size(self):
        return len(self.dictionary)
