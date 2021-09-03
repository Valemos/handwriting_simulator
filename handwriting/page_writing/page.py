import pickle
from pickletools import optimize

from math import sqrt
from pathlib import Path

from PIL import Image
from handwriting.misc.stream_serialization import *
from handwriting.misc.exceptions import ObjectNotFound, SavingException, LoadingException
from handwriting.page_writing.page_transform_grid import PageTransformGrid


class Page:
    """
    class contains initial image_initial and image_initial with text of types ImageTk.PhotoImage
    also it contains letter transformations, needed to fit them on this specific page
    """

    default_file = Path("page_data")
    pages_data_suffix = ".page"

    # size as for A4 format scaled by 2
    default_size = (210 * 2, round(210 * 2 * sqrt(2)))

    def __init__(self, image: Image, name=None, path: Path = None):
        self.save_path = self.get_save_path(path)
        self.save_dir = None
        self.name = name if name is not None else ''

        # indicates to create new image on next request for image to draw
        self._image_initial = self.current_image = image
        self._image_text = None

        self.page_transform = PageTransformGrid([[]])

    @classmethod
    def empty(cls, page_size=None):
        page_size = page_size if page_size is not None else cls.default_size
        return Page(Image.new("RGB", page_size, (255, 255, 255)), "empty page")

    @classmethod
    def from_image(cls, path):
        if '.' in path.name:
            name = path.name[:path.name.index('.')]
        else:
            name = path.name

        return cls(Image.open(path), name, path)

    def get_save_path(self, file_path: Path = None):
        save_path = file_path if file_path is not None else Path(self.default_file)
        return save_path.with_suffix(self.pages_data_suffix)

    def set_name(self, name):
        self.name = name
        self.save_path = self.save_path.with_name(name).with_suffix(Page.pages_data_suffix)

    def save_file(self):
        if not self.save_path.exists():
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            self.save_path.touch()

        with self.save_path.open("wb+") as fout:
            try:
                page_name_bytes = str(self.name).encode("utf-8")
                write_length_object(fout, page_name_bytes)

                grid_bytes = pickle.dumps(self.page_transform)
                write_length_object(fout, optimize(grid_bytes), 4)

                pickle.dump(self._image_initial, fout)

            except pickle.PicklingError:
                raise SavingException(f"cannot save page to file {str(self.save_path)}")

    @staticmethod
    def from_file(file_path: Path):
        if not file_path.exists(): return

        with file_path.open("rb") as fin:
            try:
                page_name = read_length_object(fin).decode("utf-8")
                anchor_points = read_length_object(fin, 4)
                anchor_points = pickle.loads(anchor_points)
                image = pickle.load(fin)
                new_obj = Page(image, page_name, file_path)
                new_obj.lines_points = anchor_points
                return new_obj
            except pickle.UnpicklingError:
                raise LoadingException(f"cannot load page from file {str(file_path)}")

    def add_line_anchor_point(self, line_index, point):
        self.page_transform.add_anchor(point, line_index)

    @classmethod
    def read_pages(cls, directory_path):
        pages = []
        for page_file in directory_path.glob(f"*{Page.pages_data_suffix}"):
            try:
                pages.append(Page.from_file(page_file))
            except ObjectNotFound as exc:
                print(exc)

        return pages

    def reset(self):
        self._image_text = None
        self.current_image = self._image_initial

    def show_text(self):
        self.current_image = self._image_text

    def reset_page(self):
        self._image_text = self._image_initial.copy()

    def get_draw_image(self):
        if self._image_text is None:
            self.reset_page()

        return self._image_text
