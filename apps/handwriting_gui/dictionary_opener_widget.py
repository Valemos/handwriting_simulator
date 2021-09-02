import tkinter as tk

from handwriting.misc.exceptions import SavingException
from gui import EntryWithLabel
from handwriting.path.path_drawer import PathDrawer
from handwriting.paths_dictionary.dictionary_manager import DictionaryManager


class DictionaryOpenerWidget(tk.Frame):

    def __init__(self, root, grid_width, path_drawer: PathDrawer):
        tk.Frame.__init__(self, root)
        self.parent = root
        self.path_drawer = path_drawer

        self.entry_dict_path = EntryWithLabel(self, "File path:", grid_width * 2, 1 / 3)
        self.btn_save_file = tk.Button(self, text="Save file", command=self.save_to_file, width=grid_width)
        self.btn_open_file = tk.Button(self, text="Open file", command=self.open_from_entry_path, width=grid_width)

        self.entry_dict_path.pack(side="left")
        self.btn_open_file.pack(side="left")
        self.btn_save_file.pack(side="left")

        self.entry_dict_path.bind("<KeyPress-Return>", self.open_from_entry_path)

    def open_from_entry_path(self, event=None):
        dictionary_path = DictionaryManager.get_or_create_path(self.entry_dict_path.get())
        self.entry_dict_path.set(dictionary_path)

        self.path_drawer.dictionary_manager.read_file(dictionary_path)

    def save_to_file(self):
        if self.path_drawer.dictionary_manager.exists():
            try:
                self.path_drawer.dictionary_manager.save_file(self.entry_dict_path.get())
            except SavingException as exc:
                print(exc)
        else:
            self.path_drawer.dictionary_manager.create_default()

    def set_entry(self, path):
        self.entry_dict_path.set(str(path))
