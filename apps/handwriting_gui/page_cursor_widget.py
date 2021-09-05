import tkinter as tk
from tkinter.simpledialog import askstring

from gui import LeftRightButtons, MenuWithHandler
from gui.canvas_display import CanvasDisplay
from handwriting.page_writing.page_iterator import PageIterator


class PageCursorWidget(tk.Frame):
    def __init__(self,
                 root,
                 grid_width,
                 page_iterator: PageIterator,
                 callback_page_updated):
        tk.Frame.__init__(self, root)
        self.parent = root
        self.page_iterator = page_iterator
        self._callback_page_updated = callback_page_updated

        height = 4

        self.menu_pages = MenuWithHandler(self, grid_width, self.handle_page_chosen)
        self.update_page_name()

        buttons_page_controls = LeftRightButtons(self, grid_width, self.handle_prev_page, self.handle_next_page)

        btn_rename_page = tk.Button(self, text="Rename page", height=height,
                                    command=self.handle_rename_page)

        btn_remove_page = tk.Button(self, text="Remove page", height=height,
                                    command=self.handle_delete_page)

        tk.Label(self, text="Page: ").pack(side="left")
        self.menu_pages.pack(side="left")
        buttons_page_controls.pack(side="left")
        btn_rename_page.pack(side="left")
        btn_remove_page.pack(side="left")

    def handle_next_page(self, event=None):
        # TODO: stop anchor editing
        self.page_iterator.next_page()
        self.update_page_name()
        self._callback_page_updated()

    def handle_prev_page(self, event=None):
        # TODO: stop anchor editing
        self.page_iterator.previous_page()
        self._callback_page_updated()
        self.update_page_name()

    def handle_page_chosen(self, choice):
        # TODO: stop anchor editing
        self.page_iterator.select_page(choice)
        self._callback_page_updated()
        self.update_page_name()

    def handle_rename_page(self):
        if not self.page_iterator.page_exists(): return

        new_name = askstring("Rename", "Enter new page name")
        if new_name is not None:
            self.page_iterator.get_page().set_name(new_name)
            self.update_pages_menu()
            self.update_page_name()

    def handle_delete_page(self, event=None):
        self.page_iterator.delete_current_page()
        self._callback_page_updated()
        self.update_pages_menu()
        self.update_page_name()

    def update_pages_menu(self):
        choices = None
        if len(self.page_iterator.pages) > 0:
            choices = [self.page_iterator.pages[page_i].name for page_i, _ in enumerate(self.page_iterator.pages)]

        self.menu_pages.update_choices(choices)

    def update_page_name(self):
        if self.page_iterator.page_exists():
            self.menu_pages.set(self.page_iterator.get_page().name)

    def update_menus(self):
        self.update_page_name()
        self.update_pages_menu()
