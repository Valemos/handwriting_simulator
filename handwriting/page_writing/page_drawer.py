from PIL import ImageDraw

from handwriting.misc.i_lines_iterator import ILinesIterator
from handwriting.page_writing.page import Page
from handwriting.page_writing.page_iterator import PageIterator


class PageDrawer:
    def __init__(self, display, page_iterator: PageIterator):
        self.page_iterator = page_iterator
        self.display = display
        self.current_page_image = None

    def get_current_page(self) -> Page:
        return self.page_iterator.get_page()

    def draw_current_page(self):
        self.display.reset()
        if self.page_iterator.page_exists():
            page = self.page_iterator.get_page()
            self.current_page_image = self.display.get_resized_image(page.get_drawable_image())
            self.display.show_image(self.current_page_image)
        else:
            self.current_page_image = None

    def reset(self):
        self.page_iterator.get_page().reset()

    def draw_lines(self, lines: ILinesIterator):
        image_draw = ImageDraw.Draw(self.page_iterator.get_page().get_drawable_image())

        for p1, p2 in lines:
            image_draw.line((p1.x, p1.y, p2.x, p2.y), fill=0, width=3)
