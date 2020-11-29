from PIL import Image
from PIL.ImageTk import PhotoImage

class Page:
    """
    class contains initial image and image with text of types ImageTk.PhotoImage
    also it contains letter transformations, needed to fit them on this specific page
    """

    def __init__(self, image: PhotoImage, name=None, path=None):
        self.image = image
        self.image_with_text = None
        self.anchor_points = []
        self.name = name if name is not None else ''
        self.page_path = path

    @classmethod
    def from_file(cls, path):
        try:
            name = path.name[:path.name.index('.')] if '.' in path.name else path.name
            return cls(PhotoImage(Image.open(path)), name, path)
        except Exception:
            return None
