import tkinter as tk

from gui import MenuWithHandler, MenuIndexedWithHandler, LeftRightButtons
from handwriting.misc.exceptions import ObjectNotFound
from handwriting.path.path_drawer import PathDrawer
from handwriting.paths_dictionary.dictionary_manager import DictionaryManager


class PathSelectorWidget(tk.Frame):
    def __init__(self, root, grid_width, path_drawer: PathDrawer):
        tk.Frame.__init__(self, root)
        self.parent = root
        self.path_drawer = path_drawer
        self.dictionary_manager = path_drawer.dictionary_manager

        label_path_gr = tk.Label(self, text="Path: ")
        self.menu_path_group = MenuWithHandler(self, grid_width, self.handle_group_chosen)
        self.menu_path_variant = MenuIndexedWithHandler(self, grid_width, self.handle_variant_chosen)
        buttons_move_paths = LeftRightButtons(self, grid_width, self.handle_prev_letter, self.handle_next_letter)

        label_path_gr.pack(side="left")
        self.menu_path_group.pack(side="left")
        self.menu_path_variant.pack(side="left")
        buttons_move_paths.pack(side="left")

    def handle_group_chosen(self, index):
        if not self.dictionary_manager.exists(): return

        self.dictionary_manager.iterator.select_group(index)
        self.path_drawer.redraw()
        self.update_menus()

    def handle_variant_chosen(self, variant_index):
        if not self.dictionary_manager.exists(): return

        group_index = self.dictionary_manager.iterator.group_iter.index
        self.dictionary_manager.iterator.select_group(group_index)
        self.dictionary_manager.iterator.select_variant(variant_index)
        self.update_menu_labels()

    def handle_next_letter(self, event=None):
        if not self.dictionary_manager.exists(): return

        prev_group = self.dictionary_manager.iterator.get_group_or_none()

        self.dictionary_manager.iterator.next()
        self.path_drawer.redraw()
        self.update_menu_labels()

        if self.dictionary_manager.iterator.get_group_or_none() != prev_group:
            self.update_menu_variants()

    def handle_prev_letter(self, event=None):
        if not self.dictionary_manager.exists(): return

        prev_group = self.dictionary_manager.iterator.get_group_or_none()

        self.dictionary_manager.iterator.prev()
        self.path_drawer.redraw()
        self.update_menu_labels()

        if self.dictionary_manager.iterator.get_group_or_none() != prev_group:
            self.update_menu_variants()

    def update_menu_groups(self):
        if not self.dictionary_manager.exists(): return

        all_groups = self.dictionary_manager.dictionary.groups
        choices = [all_groups[i].name for i, _ in enumerate(all_groups)]
        self.menu_path_group.update_choices(choices)

    def update_menu_variants(self):
        if not self.dictionary_manager.exists(): return

        group = self.dictionary_manager.iterator.get_group_or_none()
        if group is None: return

        choices = [group[i].name for i, _ in enumerate(group)]
        self.menu_path_variant.update_choices(choices)

    def update_menu_labels(self):
        if not self.dictionary_manager.exists():
            self.menu_path_group.set(None)
            self.menu_path_variant.set(None)
            return

        try:
            current_group = self.dictionary_manager.iterator.get_group_or_raise()
            self.menu_path_group.set(current_group.name)
            current_path = self.dictionary_manager.iterator.get_path_or_raise()
            self.update_menu_variant_name(current_path.name)
        except ObjectNotFound:
            self.menu_path_group.set(None)
            self.menu_path_variant.set(None)

    def update_menu_variant_name(self, new_name):
        variant_index = self.dictionary_manager.iterator.variant_iter.index + 1
        self.menu_path_variant.set_indexed_name(variant_index, new_name)

    def update_menus(self):
        self.update_menu_groups()
        self.update_menu_variants()
        self.update_menu_labels()
