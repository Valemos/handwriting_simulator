from tkinter import *
from tkinter import messagebox
from pathlib import Path
import copy

from handwriting.handwritten_path import HandwrittenPath
from handwriting.path_group import PathGroup
from handwriting.point import Point


class HandwritingShiftModifyer(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        self.grid_width = 15

        self.brush_size = 5
        self.brush_color = "black"

        # set default current path
        self.set_current_path()

        # dict of PathGroup objects
        self.all_path_groups = {}

        self.background_image = None

        self.default_bg_path = 'default_bg.gif'

        self.d_file_suffix = '.hndw'
        self.no_file_message = 'no files'
        self.can_select_message = 'select'

        self.setup_UI()
        self.reset_canvas()

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
                "Left": lambda e: self.go_to_prev_letter(),
                "Right": lambda e: self.go_to_next_letter(),
                "KeyRelease": {
                    "Return": [
                        (self.shift_x_entry, self.handle_draw_path),
                        (self.shift_y_entry, self.handle_draw_path),
                        (self.file_entry, self.handle_enter_on_path),
                        (self.new_char_entry, lambda e: self.handle_save_new_letter())
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

        self.canvas = Canvas(root, bg="white")
        self.reset_canvas()
        general_lab = Label(root, text="General: ")
        # ?
        clear_btn = Button(root, text="Clear all", width=self.grid_width, command=lambda: self.reset_canvas())

        shift_x_label = Label(root, text="Shift X: ")
        self.shift_x_field = StringVar(root)
        self.shift_x_field.set('100')
        self.shift_x_field.trace('w', self.limit_is_int_shx)
        self.shift_x_entry = Entry(root, width=self.grid_width, textvariable=self.shift_x_field)

        shift_y_label = Label(root, text="Shift Y: ")
        self.shift_y_field = StringVar(root)
        self.shift_y_field.set('100')
        self.shift_y_field.trace('w', self.limit_is_int_shy)
        self.shift_y_entry = Entry(root, width=self.grid_width, textvariable=self.shift_y_field)

        ch_file_lab = Label(root, text="Choose file path: ")
        ch_let_lab = Label(root, text="Choose file letter: ")
        open_file_btn = Button(root, text="Open file", width=self.grid_width, command=lambda: self.open_selected_file())
        save_file_btn = Button(root, text="Save file", width=self.grid_width, command=lambda: self.save_selected_file())

        self.file_path_field = StringVar(self)
        self.file_entry = Entry(root, width=self.grid_width, textvariable=self.file_path_field)

        # enter press opens files
        self.cur_path_name_field = StringVar(self)
        self.cur_path_name_field.set(self.no_file_message)
        self.ch_letter_menu = OptionMenu(root, self.cur_path_name_field, value=None)
        self.ch_letter_menu.configure(width=self.grid_width)
        self.set_field_choices(self.ch_letter_menu, self.cur_path_name_field, None)

        control_btn_frame = Frame(root)
        control_btn_frame.grid(row=2, column=2, sticky=W + E)
        control_btn_prev = Button(control_btn_frame, text='<<', command=lambda: self.go_to_prev_letter(),
                                  width=round(self.grid_width / 2))
        control_btn_next = Button(control_btn_frame, text='>>', command=lambda: self.go_to_next_letter(),
                                  width=round(self.grid_width / 2))
        control_btn_prev.pack(side=LEFT)
        control_btn_next.pack(side=RIGHT)

        # ?
        draw_curve_btn = Button(root, text="Draw path", command=lambda: self.handle_draw_path(self.current_path))

        edit_btn = Button(root, text="Edit path", width=self.grid_width, command=lambda: self.handle_edit_letter())
        del_btn = Button(root, text="Delete path", width=self.grid_width, command=lambda: self.handle_delete_letter())
        create_let_lab = Label(root, text="Create new path: ")
        new_char_frame = Frame(root)
        new_char_label = Label(new_char_frame, text='New name:', width=round(self.grid_width / 2))
        new_char_label.pack(side=LEFT)

        self.new_char_field = StringVar(self)
        self.new_char_entry = Entry(new_char_frame, width=10, textvariable=self.new_char_field)
        self.new_char_entry.pack(side=RIGHT)

        save_let_btn = Button(root, text="Save and continue", width=self.grid_width,
                              command=lambda e: self.handle_save_new_letter())
        detect_let_btn = Button(root, text="Detect current letter", width=self.grid_width,
                                command=lambda e: self.handle_detect_letter())

        # list of rows with widget objects, representing grid of corresponding widgets
        # to specify parameters for .grid function object is wrapped into dict with all it's parameters

        widgets_table_rows = [
            [general_lab,    clear_btn,              shift_x_label,  self.shift_x_entry,     shift_y_label,  self.shift_y_entry],
            [ch_file_lab,    self.file_entry,        open_file_btn,  save_file_btn],
            [ch_let_lab,     self.ch_letter_menu,    None,           draw_curve_btn,         edit_btn,       del_btn],
            [],
            [create_let_lab, new_char_frame,         save_let_btn,   detect_let_btn],
            [(self.canvas, {"columnspan": 6, "sticky": NSEW})]
        ]
        # if argument not specifyed explicitly, take it from global arguments
        global_arguments = {"padx": 5, "pady": 5, "sticky": EW}

        root.columnconfigure(max(len(row) for row in widgets_table_rows), weight=1)
        root.rowconfigure(len(widgets_table_rows), weight=1)

        return widgets_table_rows, global_arguments

    def dummy(self, event):
        print(event)

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
        self.pack(fill=BOTH, expand=1)

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
            self.background_image = PhotoImage(file=str(Path(self.default_bg_path).resolve()))
            self.canvas.create_image(
                (
                    int(self.background_image.width() / 2),
                    int(self.background_image.height() / 2)
                ),
                image=self.background_image)

    def set_current_path(self, path: HandwrittenPath = None):
        """
        Sets current draw path to given path and draws it on canvas
        :param path: path to set, if Path is None, sets default empty path as current
        """
        self.current_path = HandwrittenPath('', []) if path is None else path
        self.draw_current_path(self.current_path.get_position())

    def handle_mouse_press(self, event):
        print("press", event.state)

    def handle_motion_draw(self, event):
        # self.current_path.append_absolute(Point(event.x, event.y))
        print('move', event.state)

    def handle_mouse_release(self, event):
        print('release', event.state)

    def draw_line(self, point1: Point, point2: Point):
        self.canvas.create_line(point1.x, point1.y, point2.x, point2.y, fill=self.brush_color, width=self.brush_size)

    def draw_current_path(self, anchor_point=None):
        """
        Draws current path lines using HandwrittenPath iterator

        :param anchor_point: if anchor_point is not None,
                            updates absolute position of current path
        """
        self.reset_canvas()
        for p1, p2 in self.current_path:
            self.draw_line(p1, p2)

    def handle_detect_letter(self):
        pass

    def handle_letter_chosen(self, label_var, choice):
        label_var.set(choice)
        choice = label_var.get()
        if choice in self.all_paths_dict:
            self.handle_draw_path(self.all_paths_dict[choice])

    def handle_enter_on_path(self, event):
        file_path = self.handle_file_path()
        new_group = PathGroup.read_next(file_path)
        self.all_path_groups[new_group.name] = new_group

    def handle_save_new_letter(self, clear=True):
        name = self.make_unique_name(self.new_char_field.get(), self.all_paths_dict)
        self.current_path.name = name
        self.all_paths_dict[name] = copy.deepcopy(self.current_path)
        self.refresh_letter_choices(self.all_paths_dict)
        if clear:
            self.reset_canvas()

    def handle_draw_path(self, event):
        pass

    def handle_edit_letter(self):
        if self.cur_path_name_field.get() in self.all_paths_dict:
            self.all_paths_dict[self.cur_path_name_field.get()] = copy.deepcopy(self.current_path)
        else:
            self.handle_save_new_letter(clear=False)

    def handle_delete_letter(self):
        if self.cur_path_name_field.get() in self.all_paths_dict:
            if self.cur_path_name_field.get() in self.all_paths_dict:
                to_delete = self.cur_path_name_field.get()

                cur_name = self.go_to_next_letter()  # it goes next and sets current name to next in dict
                if len(self.all_paths_dict) == 1:
                    cur_name = None

                del self.all_paths_dict[to_delete]
                self.refresh_letter_choices(self.all_paths_dict, cur_name)  # uses current name to set
        else:
            self.refresh_letter_choices(self.all_paths_dict)

    def go_to_next_letter(self):
        cur_name = self.cur_path_name_field.get()
        keys_list = list(self.all_paths_dict.keys())

        if len(keys_list) == 0:
            self.reset_canvas()
            return None

        if cur_name not in keys_list:
            cur_name = keys_list[0]
            cur_idx = 0
        else:
            cur_idx = keys_list.index(cur_name)

        cur_idx = (cur_idx + 1) % len(keys_list)
        self.handle_letter_chosen(self.cur_path_name_field, keys_list[cur_idx])
        return keys_list[cur_idx]

    def go_to_prev_letter(self):
        cur_name = self.cur_path_name_field.get()
        keys_list = list(self.all_paths_dict.keys())

        if len(keys_list) == 0:
            self.reset_canvas()
            return None

        if cur_name in keys_list:
            cur_idx = keys_list.index(cur_name)
        else:
            cur_name = keys_list[0]
            cur_idx = 0

        cur_idx = (cur_idx - 1) % len(keys_list)
        self.handle_letter_chosen(self.cur_path_name_field, keys_list[cur_idx])
        return cur_name

    def limit_is_int_shx(self, *args):
        value = self.shift_x_field.get()
        if not self.str_is_int(value):
            self.shift_x_field.set(''.join([i for i in value if i.isdigit()]))

    def limit_is_int_shy(self, *args):
        value = self.shift_y_field.get()
        if not self.str_is_int(value):
            self.shift_y_field.set(''.join([i for i in value if i.isdigit()]))

    def str_is_int(self, s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    def set_field_choices(self, option_menu, label_var, choices, default=None):
        if choices is not None:
            label_var.set(self.can_select_message)
        else:
            label_var.set(self.no_file_message)
            choices = [self.no_file_message]

        option_menu['menu'].delete(0, 'end')

        for choice in choices:
            option_menu['menu'].add_command(label=choice,
                                            command=lambda c=choice: self.handle_letter_chosen(label_var, c))

        if default is not None:
            label_var.set(default)

    def open_selected_file(self, path=None):
        # if path is None:
        #     file_path = self.handle_file_path(is_shift_file=self.shift_mode.get())
        # else:
        #     file_path = path
        #
        # if self.shift_mode.get() and not str(file_path.with_suffix('')).endswith(self.d_shift_suffix):
        #     file_path = self.handle_file_path(str(file_path.with_suffix('')) + self.d_shift_suffix + self.d_file_suffix)
        #     self.file_path_field.set(str(file_path))
        #
        # if file_path.exists():
        #     temp_paths = HandwrittenPath.from_file(self.shift_mode.get())
        #     temp_dict = {}
        #     for path in temp_paths:
        #         path.name = self.make_unique_name(path.name, temp_dict)
        #         temp_dict[path.name] = path
        #
        #     self.all_paths_dict = temp_dict
        #     self.refresh_letter_choices(temp_dict)
        #     if len(self.all_paths_dict) > 0:
        #         self.handle_letter_chosen(self.cur_path_name_field, list(self.all_paths_dict.keys())[0])
        #         self.new_char_field.set(list(self.all_paths_dict.values())[0].name)
        #     else:
        #         self.new_char_field.set('')
        return None

    def save_selected_file(self):
        file_path = self.handle_file_path()
        if file_path.exists():
            with file_path.open('wb') as save_file:
                for letter in self.all_paths_dict.values():
                    save_file.write(letter.get_bytes(self.shift_mode.get()))
                    save_file.write((0).to_bytes(4, 'big'))

    def refresh_letter_choices(self, choices_dict, default=None):
        self.set_field_choices(self.ch_letter_menu, self.cur_path_name_field, list(choices_dict.keys()), default)

    def handle_file_path(self, path_str=None):
        # todo: rewrite this handler
        # if path_str is None:
        #     if len(self.file_path_field.get()) == 0:
        #         if is_shift_file:
        #             file_path = Path(self.d_file_name + self.d_shift_suffix + self.d_file_suffix)
        #         else:
        #             file_path = Path(self.d_file_name + self.d_file_suffix)
        #         self.file_path_field.set(str(file_path))
        #     else:
        #         file_path = Path(self.file_path_field.get())
        # else:
        #     file_path = Path(path_str)
        #
        # if file_path.is_dir():
        #     if is_shift_file:
        #         def_file_path = file_path / (self.d_file_name + self.d_file_suffix)
        #     else:
        #         def_file_path = file_path / (self.d_file_name + self.d_shift_suffix + self.d_file_suffix)
        #
        #     if def_file_path.exists() and path_str is None:
        #         messagebox.showinfo('Handwriting manager',
        #                             'Found default file. Changing input path to\n' + str(def_file_path))
        #
        #     file_path = def_file_path
        #
        # if is_shift_file:
        #     if file_path.suffixes != [self.d_shift_suffix, self.d_file_suffix]:
        #         file_path = file_path.with_suffix(self.d_shift_suffix + self.d_file_suffix)
        #         if path_str is None: self.file_path_field.set(str(file_path))
        # else:
        #     file_path = file_path.with_suffix('').with_suffix(self.d_file_suffix)
        #
        # if not file_path.exists():
        #     file_path.parent.mkdir(parents=True, exist_ok=True)
        #     file_path.touch()
        #     messagebox.showinfo('Handwriting manager', 'Successfully created file\n' + str(file_path))
        #
        # self.file_path_field.set(str(file_path))
        # return file_path
        return Path(path_str)

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        self.grid_width = 15

        self.brush_size = 5
        self.brush_color = "black"

        # dictionary of

        self.background_image = None

        self.default_bg_path = 'default_bg.gif'

        self.d_file_suffix = '.hndw'
        self.no_file_message = 'no files'
        self.can_select_message = 'select'

        self.setup_UI()
        self.reset_canvas()
        # set default current path
        self.set_current_path()

def main():
    root = Tk()
    root.geometry("800x700")
    app = HandwritingShiftModifyer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
