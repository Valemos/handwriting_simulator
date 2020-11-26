import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from handwriting.handwritten_path import HandwrittenPath, HandwrittenPathIterator
from handwriting.point import Point
from handwriting.signature_dictionary import SignatureDictionary, SignatureDictionaryIterator


def str_is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class HandwritingShiftModifyer(tk.Frame):
    default_bg_path = 'default_bg.gif'

    no_choices_message = 'no options'
    can_select_message = 'select'

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.brush_size = 5
        self.brush_color = "black"

        # dictionary of path groups
        self.dictionary_paths: SignatureDictionary = None

        # iterator inside dictionary through all groups and path variants
        self.paths_iterator: SignatureDictionaryIterator = None

        # current path from self.paths_iterator
        self.current_path: HandwrittenPath = None
        # iterator inside path to draw lines
        self.current_path_iterator: HandwrittenPathIterator = None

        self._mouse_released = True

        self.background_image = None
        self.setup_UI()
        self.reset_canvas()

        test_path = Path("paths_format_transition/anton_test.dict")
        self.file_path_field.set(str(test_path))
        self.open_selected_file()

    def create_events_dict(self):
        """
        dictionary with keys as events and handler functions as values
        format as follows <modifier-type-first_part>, handler at the end of the chain
        handler handler can be a tuple of Tkinter object and handler handler to bind to it
        if bind object is not specifyed, event will be bound to root
        """

        return \
            {
                # event type
                "B1": {
                    "ButtonPress": (self.canvas, self.handle_mouse_press),
                    "ButtonRelease": (self.canvas, self.handle_mouse_release),
                    "Motion": (self.canvas, self.handle_motion_draw)
                },
                "Control-Key": {
                    "d": lambda e: self.reset_canvas()
                },
                "KeyRelease": {
                    "Left": self.go_to_prev_letter,
                    "Right": self.go_to_next_letter,
                    "Return": [
                        (self.shift_x_entry, self.handle_draw_path),
                        (self.shift_y_entry, self.handle_draw_path),
                        (self.file_entry, self.handle_enter_on_path),
                        (self.new_char_entry, self.handle_save_new_letter)
                    ],
                }
            }

    def _bind_function(self, handler, first_part, second_part=None):
        if isinstance(handler, dict):
            for second_part, func in handler.items():
                self._bind_function(func, first_part, second_part)
            return

        if isinstance(handler, list):
            for func in handler:
                self._bind_function(func, first_part, second_part)
            return

        if isinstance(handler, tuple):
            bind_object, handler = handler
            bind_object.bind(f"<{first_part}>"
                             if second_part is None else
                             f"<{first_part}-{second_part}>",
                             handler)
        else:
            self.bind(f"<{first_part}>"
                      if second_part is None else
                      f"<{first_part}-{second_part}>",
                      handler)

    def bind_window_events(self, events_dict):
        for first_part, function in events_dict.items():
            self._bind_function(function, first_part)

    def create_grid(self, root):
        """
        Grid must be created before event binding
        :return: grid of objects
        """

        grid_width = 15

        self.canvas = tk.Canvas(root, bg="white")
        self.reset_canvas()
        general_lab = tk.Label(root, text="General: ")
        # ?
        clear_btn = tk.Button(root, text="Clear all", width=grid_width, command=lambda: self.reset_canvas())

        shift_x_label = tk.Label(root, text="Shift X: ")
        self.shift_x_field = tk.StringVar(root)
        self.shift_x_field.set('100')
        self.shift_x_entry = tk.Entry(root, width=grid_width, textvariable=self.shift_x_field)

        shift_y_label = tk.Label(root, text="Shift Y: ")
        self.shift_y_field = tk.StringVar(root)
        self.shift_y_field.set('100')
        self.shift_y_entry = tk.Entry(root, width=grid_width, textvariable=self.shift_y_field)

        ch_file_lab = tk.Label(root, text="Choose file path: ")
        ch_let_lab = tk.Label(root, text="Choose file letter: ")
        open_file_btn = tk.Button(root, text="Open file", width=grid_width,
                                  command=self.open_selected_file)
        save_file_btn = tk.Button(root, text="Save file", width=grid_width,
                                  command=self.save_selected_file)

        self.file_path_field = tk.StringVar(self)
        self.file_entry = tk.Entry(root, width=grid_width, textvariable=self.file_path_field)

        # enter press opens files
        self.group_name_field = tk.StringVar(self)
        self.group_name_field.set(self.no_choices_message)
        self.dictionary_menu = tk.OptionMenu(root, self.group_name_field, value=None)
        self.dictionary_menu.configure(width=grid_width)
        self.update_dictionary_menu()

        control_btn_frame = tk.Frame(root)
        control_btn_frame.grid(row=2, column=2, sticky=tk.EW)
        control_btn_prev = tk.Button(control_btn_frame, text='<<', command=self.go_to_prev_letter,
                                     width=round(grid_width / 2))
        control_btn_next = tk.Button(control_btn_frame, text='>>', command=self.go_to_next_letter,
                                     width=round(grid_width / 2))
        control_btn_prev.pack(side=tk.LEFT)
        control_btn_next.pack(side=tk.RIGHT)

        # ?
        draw_curve_btn = tk.Button(root, text="Draw path", command=self.handle_draw_path)

        edit_btn = tk.Button(root, text="Edit path", width=grid_width, command=self.handle_edit_letter)
        del_btn = tk.Button(root, text="Delete path", width=grid_width, command=self.handle_delete_letter)
        create_let_lab = tk.Label(root, text="Create new path: ")
        new_char_frame = tk.Frame(root)
        new_char_label = tk.Label(new_char_frame, text='New name:', width=round(grid_width / 2))
        new_char_label.pack(side=tk.LEFT)

        self.new_char_field = tk.StringVar(self)
        self.new_char_entry = tk.Entry(new_char_frame, width=10, textvariable=self.new_char_field)
        self.new_char_entry.pack(side=tk.RIGHT)

        save_let_btn = tk.Button(root, text="Save and continue", width=grid_width,
                                 command=self.handle_save_new_letter)

        detect_let_btn = tk.Button(root, text="Detect current letter", width=grid_width,
                                   command=self.handle_detect_letter)

        """
        list of rows with widget objects, representing grid of corresponding widgets
        to specify parameters for .grid function object is wrapped into dict with all it's parameters
        """

        widgets_table_rows = [
            [general_lab, clear_btn, shift_x_label, self.shift_x_entry, shift_y_label, self.shift_y_entry],
            [ch_file_lab, self.file_entry, open_file_btn, save_file_btn],
            [ch_let_lab, self.dictionary_menu, None, draw_curve_btn, edit_btn, del_btn],
            [],
            [create_let_lab, new_char_frame, save_let_btn],  # detect_let_btn
            [(self.canvas, {"columnspan": 6, "sticky": tk.NSEW})]
        ]
        # if argument not specifyed explicitly, take it from global arguments
        global_arguments = {"padx": 5, "pady": 5, "sticky": tk.EW}

        root.columnconfigure(max(len(row) for row in widgets_table_rows), weight=1)
        root.rowconfigure(len(widgets_table_rows), weight=1)

        return widgets_table_rows, global_arguments

    @staticmethod
    def put_objects_on_grid(grid_rows, arguments):
        for row in range(len(grid_rows)):
            for col in range(len(grid_rows[row])):
                if grid_rows[row][col] is None:
                    continue
                elif isinstance(grid_rows[row][col], tuple):
                    obj, args = grid_rows[row][col]
                    for arg_name, value in arguments.items():
                        if arg_name not in args:
                            args[arg_name] = value

                    obj.grid(row=row, column=col, **args)
                else:
                    grid_rows[row][col].grid(row=row, column=col, **arguments)

    def setup_UI(self):

        self.parent.title("Handwriting manager")
        self.pack(fill=tk.BOTH, expand=1)

        grid, arguments = self.create_grid(self)
        self.put_objects_on_grid(grid, arguments)

        self.bind_window_events(self.create_events_dict())

    def reset_canvas(self):

        self.canvas.delete("all")
        if self.background_image is not None:
            self.canvas.create_image((int(self.background_image.width() / 2), int(self.background_image.height() / 2)),
                                     image=self.background_image)
        else:
            self.update_background_image()

    def update_background_image(self):
        if Path(self.default_bg_path).exists():
            self.background_image = tk.PhotoImage(file=str(Path(self.default_bg_path).resolve()))
            self.canvas.create_image(
                (
                    int(self.background_image.width() / 2),
                    int(self.background_image.height() / 2)
                ),
                image=self.background_image)

    def handle_mouse_press(self, event):
        pass

    def handle_motion_draw(self, event):
        """
        After new point is appended, iterator will be updated and will be able to give another line
        If this event begins new curve (mouse was previously released and now it was pressed)
        New_curve is created for path and first point is appended to it

        Only one point is not enough for line, so, for this iteration self.current_path_iterator
        must not return anything, but point must be appended
        :param event: tkinter Event object
        """
        if self._mouse_released:
            self._mouse_released = False
            self.current_path.new_curve(Point(event.x, event.y))
        else:
            self.current_path.append_absolute(Point(event.x, event.y))
            self.draw_iterator(self.current_path_iterator)

    def handle_mouse_release(self, event):
        self._mouse_released = True

    def draw_line(self, point1: Point, point2: Point):
        self.canvas.create_line(point1.x, point1.y, point2.x, point2.y, fill=self.brush_color, width=self.brush_size)

    def draw_iterator(self, path_iterator):
        """
        Draws current path lines using HandwrittenPath iterator

        :param path_iterator: iterator for current path
        """
        while True:
            try:
                p1, p2 = next(path_iterator)
                self.draw_line(p1, p2)
            except StopIteration:
                break

    def handle_detect_letter(self, event):
        pass

    def handle_letter_chosen(self, choice_index):
        self.select_group_by_index(choice_index)
        self.update_current_path()
        self.update_dictionary_menu_names()

    def handle_enter_on_path(self, event):
        self.open_selected_file()

    def save_selected_file(self):
        self.dictionary_paths.save_file()

    def open_selected_file(self):
        file_path = self.handle_file_path(self.file_path_field.get())
        self.dictionary_paths = SignatureDictionary.from_file(file_path)
        self.update_dictionary_menu()
        self.update_dictionary_menu_names()
        self.reset_current_group()

    def reset_current_group(self):
        """
        Function resets iterator inside dictionary and resets current group
        """
        if self.dictionary_paths is not None:
            self.paths_iterator = self.dictionary_paths.get_iterator()
            self.update_current_path()

    def update_current_path(self, anchor_point: Point = None):
        """
        Function assumes, that self.paths_iterator is not None

        Updates current path variables and applies shift to new path
        Draws current iterator lines

        :param anchor_point: if anchor_point is not None,
                            updates absolute position of current path
        """
        if self.paths_iterator.current() is not None:
            self.current_path = self.paths_iterator.current()
            if self.current_path is not None:
                if anchor_point is not None:
                    self.current_path.set_position(anchor_point)
                self.current_path_iterator = iter(self.current_path)

                self.reset_canvas()
                self.draw_iterator(self.current_path_iterator)

    def select_group_by_index(self, choice_index):
        if self.paths_iterator is not None:
            self.paths_iterator.select(choice_index)

    def handle_save_new_letter(self, event):
        """Saves letter to path group using default (or specifyed) additional name"""
        self.paths_iterator.current()

    def handle_draw_path(self, event):
        self.update_current_path(self.get_shift_point())

    def handle_edit_letter(self, event):
        """Sets new path instead of current chosen letter"""
        pass

    def handle_delete_letter(self):
        """Removes current letter from selected path group"""
        self.paths_iterator.delete_current()
        self.update_current_path(self.get_shift_point())
        self.update_dictionary_menu_names()

    def go_to_next_letter(self):
        if self.paths_iterator is not None:
            self.paths_iterator.next()
            self.update_current_path(self.get_shift_point())
            self.update_dictionary_menu_names()

    def go_to_prev_letter(self):
        if self.paths_iterator is not None:
            self.paths_iterator.prev()
            self.update_current_path(self.get_shift_point())
            self.update_dictionary_menu_names()

    @staticmethod
    def update_integer_field(field):
        if not str_is_int(field.get()):
            field.set(str(int('0' + ''.join((i for i in field.get() if i.isdigit())))))

    def update_dictionary_menu(self):
        """
        If self.dictionary_paths is None, than sets default name for list and clears all previous options
        """
        if self.dictionary_paths is not None:
            choices = {self.dictionary_paths[i].name: i for i in range(len(self.dictionary_paths))}
        else:
            choices = None


        self.group_name_field.set(self.no_choices_message if choices is None else self.can_select_message)

        if choices is None:
            self.dictionary_menu['menu'].delete(0, 'end')
            return

        for choice_name, choice_object in choices.items():
            self.dictionary_menu['menu'].add_command(
                label=choice_name,
                command=lambda c=choice_object: self.handle_letter_chosen(c))

    def update_dictionary_menu_names(self):
        if self.paths_iterator is not None:
            path = self.paths_iterator.current()
            if path is not None:
                self.group_name_field.set(path.name)

    def handle_file_path(self, path_str=None):
        file_path = Path(path_str) if path_str is not None else Path(self.file_path_field.get())

        sfx = SignatureDictionary.dictionary_suffix
        if file_path.suffix != sfx:
            file_path = file_path.with_suffix(sfx)

        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
            messagebox.showinfo('Handwriting manager', 'Successfully created file\n' + str(file_path))

        self.file_path_field.set(str(file_path))
        return file_path

    def get_shift_point(self):
        """Reads values of two corresponding fields and returns Point object"""
        self.update_integer_field(self.shift_x_field)
        self.update_integer_field(self.shift_y_field)

        return Point(int(self.shift_x_field.get()), int(self.shift_y_field.get()))


def main():
    root = tk.Tk()
    root.geometry("800x700")
    app = HandwritingShiftModifyer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
