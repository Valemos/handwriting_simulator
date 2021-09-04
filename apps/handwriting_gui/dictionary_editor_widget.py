import tkinter as tk
from tkinter import messagebox

from gui import EntryWithLabel
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.path_drawer import PathDrawer
from handwriting.paths_dictionary.dictionary_manager import DictionaryManager
from handwriting.paths_dictionary.path_group import PathGroup


class DictionaryEditorWidget(tk.Frame):
    message_path_name_invalid = "name must be a single line\nwith length no more than 128"

    def __init__(self,
                 root,
                 grid_width,
                 path_drawer: PathDrawer,
                 dictionary_manager: DictionaryManager,
                 update_menus_callback):
        super().__init__(self, root)
        self.parent = root
        self.path_drawer = path_drawer
        self.dictionary_manager = dictionary_manager
        self._update_menus_callback = update_menus_callback

        label_new_names = tk.Label(self, text="New names")
        self.entry_new_group = EntryWithLabel(self, 'Group:', grid_width, 1 / 6)
        self.entry_new_variant = EntryWithLabel(self, 'Variant:', grid_width, 1 / 6)
        new_path_btn = tk.Button(self, text="New path", width=grid_width, command=self.handle_create_path)
        btn_clear = tk.Button(self, text="\u239A", width=grid_width, command=self.handle_clear_path)
        btn_del = tk.Button(self, text="\U0001F5D1", width=grid_width, command=self.handle_delete_path)

        label_new_names.grid(row=1, column=1)
        self.entry_new_group.grid(row=1, column=2)
        self.entry_new_variant.grid(row=1, column=3)
        new_path_btn.grid(row=1, column=4)
        btn_clear.grid(row=2, column=3)
        btn_del.grid(row=2, column=4)

        self.entry_new_group.bind("<KeyPress-Return>", self.handle_create_path)
        self.entry_new_variant.bind("<KeyPress-Return>", self.handle_create_path)

    def handle_clear_path(self, event=None):
        if self.dictionary_manager.iterator.get_variant_or_raise() is not None:
            self.dictionary_manager.iterator.get_variant_or_raise().components = []
            self.path_drawer.redraw()

    def handle_create_path(self, event=None):
        group_name = self.entry_new_group.get()
        if not self.check_name_valid(group_name):
            messagebox.showinfo("Group name invalid", self.message_path_name_invalid)
            return

        path_name = self.entry_new_variant.get()
        if not self.check_name_valid(path_name):
            messagebox.showinfo("Path name invalid", self.message_path_name_invalid)
            return

        if not self.dictionary_manager.dictionary.is_group_exists(group_name):
            self.create_group(group_name)
        self.create_path_variant(path_name)

        self.path_drawer.reset()
        self._update_menus_callback()
        self.parent.focus()

    def handle_delete_group(self):
        self.dictionary_manager.iterator.delete_group()
        self.path_drawer.redraw()
        self._update_menus_callback()

    def handle_delete_path(self, event=None):
        group = self.dictionary_manager.iterator.get_group_or_none()
        if group is None: return
        if group.empty():
            self.handle_delete_group()
            return

        self.dictionary_manager.iterator.delete_current_variant()
        self.path_drawer.redraw()
        self._update_menus_callback()

    def create_group(self, group_name):
        self.dictionary_manager.dictionary.append_group(PathGroup(group_name))
        self.dictionary_manager.iterator.select_group(len(self.dictionary_manager.dictionary) - 1)
        self._update_menus_callback()

    def create_path_variant(self, path_name):
        """must be called only if group exists"""
        current_group = self.dictionary_manager.iterator.get_group_or_raise()
        current_group.append_path(HandwrittenPath(path_name))
        self.dictionary_manager.iterator.select_variant(len(current_group) - 1)

        self.path_drawer.redraw()
        self._update_menus_callback()

    @staticmethod
    def check_name_valid(name):
        """Checks if name for HandwrittenPath or SignatureDictionary can be written to file and is one line"""
        return all((i not in name for i in '\t\n')) and len(name) <= 128
