import tkinter as tk

from gui import EntryIntegerWithLabel


class TextWriterWidget(tk.Frame):
    def __init__(self, root, grid_width, page_manager):
        super().__init__(root)
        self.page_manager = page_manager
        self.parent = root

        # TODO pack all widgets
        btn_draw_text = tk.Button(self, text="Draw text", width=round(grid_width * 2 / 3),
                                  command=self.handle_draw_text)

        btn_reset_text = tk.Button(self, text="Reset text", width=round(grid_width * 2 / 3),
                                   command=self.handle_reset_text)

        self.entry_space_sz = EntryIntegerWithLabel(self, "Space size:", grid_width * 2, 1 / 2)
        self.entry_space_sz.set(50)

        self.entry_draw_text = tk.Text(self, height=20)

    def handle_reset_text(self, event=None):
        self.page_manager.get_page().reset()


    def handle_draw_text(self, event=None):
        text = self.entry_draw_text.get(1.0, tk.END)
        if self.page_manager.page_exists():
            current_page = self.page_manager.get_page()
        else:
            current_page = self.page_manager.create_empty_page()

        self.draw_text_on_page(text, current_page)
        self.update_current_page()

    def draw_text_on_page(self, text, page: Page):
        text_drawer = PathTextWriter(page, self.dictionary_manager.dictionary, space_size=50)

        page.reset_page()
        image_draw = ImageDraw.Draw(page.get_draw_image())
        text_drawer.write_text(text).draw(image_draw)
