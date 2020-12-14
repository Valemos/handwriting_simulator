
class CanvasObjectsManager:
    """
    This class controls canvas_objects, created on Tkinter canvas
    and allows to modify and delete them if needed
    """

    def __init__(self, initial_objects: list = None):
        self.canvas_objects = initial_objects if initial_objects is not None else []

    def append_canvas_objects(self, new_objects):
        """
        appends list of canvas_objects to self.canvas_objects,
        this allows user to delete different canvas_objects as if it was one object
        """
        self.canvas_objects.append(new_objects)

    def pop_last_canvas_objects(self):
        """Removes and returns last """
        if len(self.canvas_objects) > 0:
            return self.canvas_objects.pop()
        else:
            return None
