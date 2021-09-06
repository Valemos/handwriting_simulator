from tkinter import Canvas

from gui.canvas_display import CanvasDisplay


class DrawTransaction:
    def __init__(self, canvas: Canvas, objects=None):
        if objects is None: objects = []

        self.canvas = canvas
        self.objects = objects

    def delete(self):
        for obj in self.objects:
            self.canvas.delete(obj)

    def create_oval(self, *args, **kwargs):
        self.objects.append(self.canvas.create_oval(*args, **kwargs))

    def create_line(self, *args, **kwargs):
        self.objects.append(self.canvas.create_line(*args, **kwargs))


class DisplayDrawHistory:
    """manages Tkinter canvas draw objects"""

    def __init__(self, display: CanvasDisplay):
        self.display = display
        self.transactions = []

    def draw(self, draw_function, *args):
        """

        Parameters
        ----------
        draw_function : callable
        must have one parameter - transaction object where to draw
        canvas will be supplied from internal drawer display

        Returns
        -------
        transaction object of current draw operation
        """
        new_transaction = DrawTransaction(self.display.get_canvas())
        draw_function(new_transaction, *args)
        self.transactions.append(new_transaction)
        return new_transaction

    def delete(self, transaction: DrawTransaction):
        try:
            transaction.delete()
            self.transactions.remove(transaction)
        except ValueError:
            pass

    def delete_all(self):
        for transaction in self.transactions:
            transaction.delete()
        self.transactions = []
