import pickle
from pathlib import Path

from PIL import Image
from handwriting.length_object_serializer import LengthObjectSerializer
from handwriting.page_writing.page_transform_grid import PageTransformGrid


class Page(LengthObjectSerializer):
    """
    class contains initial image_initial and image_initial with text of types ImageTk.PhotoImage
    also it contains letter transformations, needed to fit them on this specific page
    """

    default_file = Path("page_data")
    pages_data_suffix = ".page"

    def __init__(self, image: Image, name=None, path=None):
        self.save_path = self.get_save_path(path)
        self.save_dir = None
        self.current_image = image
        self.image_initial = image
        self.image_text = None
        self.name = name if name is not None else ''

        self.page_transform = PageTransformGrid([[]])

    @classmethod
    def from_image(cls, path):
        try:
            name = path.name[:path.name.index('.')] if '.' in path.name else path.name
            return cls(Image.open(path), name, path)
        except Exception as exc:
            print(exc)
            return None

    def get_save_path(self, file_path: Path = None):
        save_path = (file_path
                     if file_path is not None else
                     Path(self.default_file)) \
            .with_suffix(self.pages_data_suffix)

        return save_path

    def set_name(self, name):
        if self.save_path is not None:
            self.save_path = self.save_path.with_name(name).with_suffix(Page.pages_data_suffix)
        else:
            self.name = name
        pass

    def save_file(self):
        if self.save_path is not None:
            if not self.save_path.exists():
                self.save_path.parent.mkdir(parents=True, exist_ok=True)
                self.save_path.touch()

            with self.save_path.open("wb+") as fout:
                try:
                    page_name_bytes = str(self.name).encode("utf-8")
                    self.write_length_object(fout, page_name_bytes)

                    grid_bytes = pickle.dumps(self.page_transform)
                    self.write_length_object(fout, grid_bytes, 4)

                    pickle.dump(self.image_initial, fout)

                except pickle.PicklingError:
                    print(f"cannot save page to file {str(self.save_path)}")

    @staticmethod
    def from_file(file_path):
        if file_path.exists():
            with file_path.open("rb") as fin:
                try:
                    page_name = LengthObjectSerializer.read_length_object(fin).decode("utf-8")
                    anchor_points = LengthObjectSerializer.read_length_object(fin, 4)
                    anchor_points = pickle.loads(anchor_points)
                    image = pickle.load(fin)
                    new_obj = Page(image, page_name, file_path)
                    new_obj.lines_points = anchor_points
                    return new_obj
                except pickle.UnpicklingError:
                    print(f"cannot load page from file {str(file_path)}")

    def add_line_anchor_point(self, line_index, point):
        self.page_transform.add_anchor(point, line_index)

    @classmethod
    def read_pages(cls, directory_path):
        pages = []
        for page_file in directory_path.glob(f"*{Page.pages_data_suffix}"):
            pages.append(Page.from_file(page_file))

        return pages

    def set_current_image_initial(self):
        self.current_image = self.image_initial

    def set_current_image_text(self):
        self.current_image = self.image_text

    def get_new_text_image(self):
        self.current_image = self.image_initial.copy()
        return self.current_image
