import tkinter as tk
from tkinter.simpledialog import askstring

from gui import LeftRightButtons, MenuWithHandler
from gui.canvas_display import CanvasDisplay
from handwriting.page_writing.page_manager import PagesIterator


class PageCursorWidget(tk.Frame):
    def __init__(self,
                 root,
                 grid_width,
                 page_manager: PagesIterator,
                 display: CanvasDisplay,
                 callback_page_selected):
        super().__init__(root)
        self.parent = root
        self.page_manager = page_manager
        self.display = display
        self._callback_page_selected = callback_page_selected

        self.current_page_image = None

        self.menu_pages = MenuWithHandler(root, grid_width, self.handle_page_chosen)
        self.update_page_name()

        self.menu_pages.config(width=grid_width)

        buttons_page_controls = LeftRightButtons(root, grid_width, self.handle_prev_page, self.handle_next_page)

        btn_rename_page = tk.Button(root, text="Rename page", width=round(grid_width * 2 / 3),
                                    command=self.handle_rename_page)

        btn_remove_page = tk.Button(root, text="Remove page", width=round(grid_width * 2 / 3),
                                    command=self.handle_delete_page)

    def handle_next_page(self, event=None):
        # TODO: stop anchor editing
        self.page_manager.next_page()
        self.update_current_page()
        self.update_page_name()

    def handle_prev_page(self, event=None):
        # TODO: stop anchor editing
        self.page_manager.previous_page()
        self.update_current_page()
        self.update_page_name()

    def handle_page_chosen(self, choice):
        # TODO: stop anchor editing
        self.page_manager.select_page(choice)
        self.update_current_page()
        self.update_page_name()

    def handle_rename_page(self):
        if not self.page_manager.page_exists(): return

        new_name = askstring("Rename", "Enter new page name")
        if new_name is not None:
            self.page_manager.get_page().set_name(new_name)
            self.update_pages_menu()
            self.update_page_name()

    def handle_delete_page(self, event=None):
        self.page_manager.delete_current_page()
        self.update_current_page()
        self.update_pages_menu()
        self.update_page_name()

    def update_current_page(self):
        self.display.reset()
        if self.page_manager.page_exists():
            page = self.page_manager.get_page()
            self.current_page_image = self.display.get_cropped_image(page.get_draw_image())
            self.display.show_image(self.current_page_image)
        else:
            self.current_page_image = None

    def update_pages_menu(self):
        choices = None
        if len(self.page_manager.pages) > 0:
            choices = [self.page_manager.pages[page_i].name for page_i, _ in enumerate(self.page_manager.pages)]

        self.menu_pages.update_choices(choices)

    def update_page_name(self):
        if self.page_manager.page_exists():
            self.menu_pages.set(self.page_manager.get_page().name)
