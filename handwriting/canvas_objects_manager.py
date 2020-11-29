
class CanvasObjectsManager:
    """
    This class controls objects, created on Tkinter canvas
    and allows to modify and delete them if needed
    """

    def __init__(self, initial_objects: list = None):
        self.objects = initial_objects if initial_objects is not None else []

    def append_canvas_objects(self, new_objects):
        """
        appends list of objects to self.objects,
        this allows user to delete different objects as if it was one object
        """
        self.objects.append(new_objects)
