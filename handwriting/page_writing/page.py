from PIL import Image
from PIL.ImageTk import PhotoImage

class Page:
    """
    class contains initial image and image with text of types ImageTk.PhotoImage
    also it contains letter transformations, needed to fit them on this specific page
    """

    def __init__(self, image: PhotoImage):
        self.image = image
        self.image_with_text = None
        self.anchor_points = []

    @classmethod
    def from_file(cls, path):
        try:
            return cls(PhotoImage(Image.open(path)))
        except Exception:
            return None
