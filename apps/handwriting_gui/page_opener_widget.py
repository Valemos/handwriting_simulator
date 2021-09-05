import tkinter as tk

from gui import EntryWithLabel
from handwriting.misc.exceptions import SavingException
from handwriting.page_writing.page_iterator import PageIterator
from gui.widget_positioning import put_objects_on_grid


class PageOpenerWidget(tk.Frame):
    def __init__(self, root, grid_width, page_iterator: PageIterator, callback_page_updated):
        tk.Frame.__init__(self, root)
        self.parent = root
        self.page_iterator = page_iterator
        self._callback_page_updated = callback_page_updated

        self.entry_pages_dir = EntryWithLabel(self, "Pages folder:", grid_width * 2, 1 / 2)

        btn_open_pages = tk.Button(self, text="Open pages", width=grid_width,
                                   command=self.open_pages_directory)

        btn_pages_from_images = tk.Button(self, text="Images to pages", width=grid_width,
                                          command=self.open_images_to_pages)

        btn_save_pages = tk.Button(self, text="Save pages", width=grid_width,
                                   command=self.save_pages_to_files)

        put_objects_on_grid(self, [[self.entry_pages_dir, btn_open_pages, btn_pages_from_images, btn_save_pages]])

        self.entry_pages_dir.bind("<KeyPress-Return>", self.update_pages_path)

    def open_pages_directory(self, event=None):
        file_path = self.get_pages_directory()
        self.entry_pages_dir.set(str(file_path))
        self.update_pages(file_path)
        self._callback_page_updated()

    def open_images_to_pages(self, event=None):
        file_path = self.get_pages_directory()
        self.entry_pages_dir.set(str(file_path))
        self.read_images_to_pages(file_path)
        self._callback_page_updated()

    def save_pages_to_files(self):
        for page in self.page_iterator.pages:
            try:
                page.save_file()
            except SavingException as exc:
                print(exc)

    def read_images_to_pages(self, file_path):
        self.page_iterator.pages = []
        self.page_iterator.read_images_to_pages(file_path)
        self._callback_page_updated()

    def update_pages(self, file_path):
        self.page_iterator.pages = []
        self.page_iterator.read_pages_from_dir(file_path)

    def get_pages_directory(self):
        directory = self.entry_pages_dir.get()
        # TODO write proper directory check and creation
        return directory

    def update_pages_path(self):
        # todo write directory path update
        # self.entry_pages_dir.set()
        pass
