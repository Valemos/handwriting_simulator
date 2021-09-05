import tkinter as tk

from gui import EntryIntegerWithLabel
from gui.widget_positioning import put_objects_on_grid
from handwriting.page_writing.handwritten_text_writer import PathTextWriter
from handwriting.page_writing.page import Page
from handwriting.page_writing.page_drawer import PageDrawer
from handwriting.paths_dictionary.dictionary_manager import DictionaryManager


class TextWriterWidget(tk.Frame):
    def __init__(self, root, grid_width, page_drawer: PageDrawer, dictionary_manager: DictionaryManager):
        tk.Frame.__init__(self, root)
        self.parent = root
        self.page_drawer = page_drawer
        self.dictionary_manager = dictionary_manager

        btn_draw_text = tk.Button(self, text="Draw text", width=round(grid_width * 2 / 3),
                                  command=self.handle_draw_text)

        btn_reset_page = tk.Button(self, text="Reset page", width=round(grid_width * 2 / 3),
                                   command=self.page_drawer.reset)

        self.entry_space_sz = EntryIntegerWithLabel(self, "Space size:", grid_width * 2, 1 / 2)
        self.entry_space_sz.set(50)

        self.entry_draw_text = tk.Text(self, height=20)

        put_objects_on_grid(self, [
            [self.entry_space_sz, btn_draw_text, btn_reset_page],
            [(self.entry_draw_text, {"columnspan": 3})],
        ])

    def handle_draw_text(self, event=None):
        text = self.entry_draw_text.get(1.0, tk.END)

        text_drawer = PathTextWriter(self.dictionary_manager.dictionary, space_size=self.entry_space_sz.get())
        paths_collection = text_drawer.write_text(text)

        self.page_drawer.draw_lines(paths_collection.get_lines())
