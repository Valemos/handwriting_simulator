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

        self.d_path_name = 'path'
        self.d_file_suffix = '.hndw'
        self.no_file_message = 'no files'
        self.can_select_message = 'select'

        self.shift_mode = BooleanVar()
        self.shift_mode.set(0)

        self.setup_UI()
        self.reset_canvas()

    def setup_UI(self):

        self.parent.title("Handwriting manager")
        self.pack(fill=BOTH, expand=1)

        self.columnconfigure(6, weight=1)
        self.rowconfigure(5, weight=1)

        self.canvas = Canvas(self, bg="white")
        self.reset_canvas()
        self.canvas.grid(row=5, column=0, columnspan=7,
                         padx=5, pady=5, sticky=E + W + S + N)

        self.canvas.bind('<B1-Motion>', self.draw)
        self.canvas.bind('<Button-1>', self.draw)
        self.canvas.bind('<ButtonRelease-1>', self.handle_mouse_release)

        color_lab = Label(self, text="General: ")
        color_lab.grid(row=0, column=0, padx=6)

        clear_btn = Button(self, text="Clear all", width=self.grid_width, command=lambda: self.reset_canvas())
        clear_btn.grid(row=0, column=1, sticky=W + E)

        self.parent.bind('<Control-Key-d>', lambda e: self.reset_canvas())

        shift_x_label = Label(self, text="Shift X: ")
        shift_x_label.grid(row=0, column=2, padx=5)

        self.shift_x_field = StringVar(self)
        self.shift_x_field.set('100')
        self.shift_x_field.trace('w', self.limit_is_int_shx)
        shift_x_entry = Entry(self, width=self.grid_width, textvariable=self.shift_x_field)
        shift_x_entry.grid(row=0, column=3, sticky=E + W, padx=5)

        shift_y_label = Label(self, text="Shift Y: ")
        shift_y_label.grid(row=0, column=4, padx=5)

        self.shift_y_field = StringVar(self)
        self.shift_y_field.set('100')
        self.shift_y_field.trace('w', self.limit_is_int_shy)
        shift_y_entry = Entry(self, width=self.grid_width, textvariable=self.shift_y_field)
        shift_y_entry.grid(row=0, column=5, sticky=E + W, padx=5)

        shift_x_entry.bind('<Return>', lambda e: self.handle_draw_path(self.current_path))
        shift_y_entry.bind('<Return>', lambda e: self.handle_draw_path(self.current_path))

        ch_file_path_label = Label(self, text="Choose file path: ")
        ch_file_path_label.grid(row=1, column=0, padx=5)

        self.file_path_field = StringVar(self)
        file_path_entry = Entry(self, width=self.grid_width, textvariable=self.file_path_field)
        file_path_entry.grid(row=1, column=1, sticky=E + W, padx=5)

        open_file_btn = Button(self, text="Open file", width=self.grid_width, command=lambda: self.open_selected_file())
        open_file_btn.grid(row=1, column=2, sticky=W + E)
        save_file_btn = Button(self, text="Save file", width=self.grid_width, command=lambda: self.save_selected_file())
        save_file_btn.grid(row=1, column=3, sticky=W + E)
        draw_shift_chk = Checkbutton(self, text="Shift mode", width=self.grid_width, variable=self.shift_mode,
                                     onvalue=1, offvalue=0)
        draw_shift_chk.grid(row=1, column=4, sticky=W + E)

        ch_file_label = Label(self, text="Choose file letter: ")
        ch_file_label.grid(row=2, column=0, padx=5)

        self.cur_path_name_field = StringVar(self)
        self.cur_path_name_field.set(self.no_file_message)
        self.ch_letter_menu = OptionMenu(self, self.cur_path_name_field, value=None)
        self.set_field_choices(self.ch_letter_menu, self.cur_path_name_field, None)
        self.ch_letter_menu.grid(row=2, column=1, sticky=W)
        self.ch_letter_menu.config(width=self.grid_width)

        # enter press opens files
        file_path_entry.bind('<Return>', self.handle_enter_on_path)

        control_btn_frame = Frame(self)
        control_btn_frame.grid(row=2, column=2, sticky=W + E)
        control_btn_prev = Button(control_btn_frame, text='<<', command=lambda: self.go_to_prev_letter(),
                                  width=round(self.grid_width / 2))
        control_btn_next = Button(control_btn_frame, text='>>', command=lambda: self.go_to_next_letter(),
                                  width=round(self.grid_width / 2))
        control_btn_prev.pack(side=LEFT)
        control_btn_next.pack(side=RIGHT)

        self.parent.bind('<Left>', lambda e: self.go_to_prev_letter())
        self.parent.bind('<Right>', lambda e: self.go_to_next_letter())

        draw_curve_btn = Button(self, text="Draw path", command=lambda: self.handle_draw_path(self.current_path))
        draw_curve_btn.grid(row=2, column=3, sticky=W + E)

        edit_btn = Button(self, text="Edit path", width=self.grid_width, command=lambda: self.handle_edit_letter())
        edit_btn.grid(row=2, column=4, sticky=W + E)

        del_btn = Button(self, text="Delete path", width=self.grid_width, command=lambda: self.handle_delete_letter())
        del_btn.grid(row=2, column=5, sticky=W + E)

        create_letter_label = Label(self, text="Create new path: ")
        create_letter_label.grid(row=4, column=0, padx=5)

        new_char_frame = Frame(self)
        new_char_frame.grid(row=4, column=1, sticky=W + E, padx=5)

        new_char_label = Label(new_char_frame, text='New name:', width=round(self.grid_width / 2))
        new_char_label.pack(side=LEFT)

        self.new_char_field = StringVar(self)
        new_char_entry = Entry(new_char_frame, width=10, textvariable=self.new_char_field)
        new_char_entry.pack(side=RIGHT)
        new_char_entry.bind('<KeyPress-Return>', lambda e: self.handle_save_new_letter())

        save_letter_btn = Button(self, text="Save and continue", width=self.grid_width,
                                 command=lambda e: self.handle_save_new_letter())
        save_letter_btn.grid(row=4, column=2, sticky=W + E)
        save_letter_btn = Button(self, text="Detect current letter", width=self.grid_width,
                                 command=lambda e: self.handle_detect_letter())
        save_letter_btn.grid(row=4, column=3, sticky=W + E)

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
        self.current_path = path if path is not None else HandwrittenPath('', [])
        self.draw_current_path(path.get_position())

    def draw(self, event):
        self.current_path.append_absolute(Point(event.x, event.y))

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

    def handle_mouse_release(self, event):
        pass

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
        if clear: self.reset_canvas()

    def handle_draw_path(self, path):
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
        if path is None:
            file_path = self.handle_file_path(is_shift_file=self.shift_mode.get())
        else:
            file_path = path

        if self.shift_mode.get() and not str(file_path.with_suffix('')).endswith(self.d_shift_suffix):
            file_path = self.handle_file_path(str(file_path.with_suffix('')) + self.d_shift_suffix + self.d_file_suffix)
            self.file_path_field.set(str(file_path))

        if file_path.exists():
            temp_paths = HandwrittenPath.from_file(self.shift_mode.get())
            temp_dict = {}
            for path in temp_paths:
                path.name = self.make_unique_name(path.name, temp_dict)
                temp_dict[path.name] = path

            self.all_paths_dict = temp_dict
            self.refresh_letter_choices(temp_dict)
            if len(self.all_paths_dict) > 0:
                self.handle_letter_chosen(self.cur_path_name_field, list(self.all_paths_dict.keys())[0])
                self.new_char_field.set(list(self.all_paths_dict.values())[0].name)
            else:
                self.new_char_field.set('')

    def save_selected_file(self):
        file_path = self.handle_file_path(is_shift_file=self.shift_mode.get())
        if file_path.exists():
            with file_path.open('wb') as save_file:
                for letter in self.all_paths_dict.values():
                    save_file.write(letter.get_bytes(self.shift_mode.get()))
                    save_file.write((0).to_bytes(4, 'big'))

    def make_unique_name(self, name, dct):
        if len(name) == 0:
            name = self.d_path_name
        count = 1
        new_name = name
        while new_name in dct:
            new_name = name + str(count)
            count += 1
        return new_name

    def refresh_letter_choices(self, choices_dict, default=None):
        self.set_field_choices(self.ch_letter_menu, self.cur_path_name_field, list(choices_dict.keys()), default)

    def handle_file_path(self, path_str=None):
        # todo: rewrite this function
        if path_str is None:
            if len(self.file_path_field.get()) == 0:
                if is_shift_file:
                    file_path = Path(self.d_file_name + self.d_shift_suffix + self.d_file_suffix)
                else:
                    file_path = Path(self.d_file_name + self.d_file_suffix)
                self.file_path_field.set(str(file_path))
            else:
                file_path = Path(self.file_path_field.get())
        else:
            file_path = Path(path_str)

        if file_path.is_dir():
            if is_shift_file:
                def_file_path = file_path / (self.d_file_name + self.d_file_suffix)
            else:
                def_file_path = file_path / (self.d_file_name + self.d_shift_suffix + self.d_file_suffix)

            if def_file_path.exists() and path_str is None:
                messagebox.showinfo('Handwriting manager',
                                    'Found default file. Changing input path to\n' + str(def_file_path))

            file_path = def_file_path

        if is_shift_file:
            if file_path.suffixes != [self.d_shift_suffix, self.d_file_suffix]:
                file_path = file_path.with_suffix(self.d_shift_suffix + self.d_file_suffix)
                if path_str is None: self.file_path_field.set(str(file_path))
        else:
            file_path = file_path.with_suffix('').with_suffix(self.d_file_suffix)

        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
            messagebox.showinfo('Handwriting manager', 'Successfully created file\n' + str(file_path))

        self.file_path_field.set(str(file_path))
        return file_path


def main():
    root = Tk()
    root.geometry("800x700")
    app = HandwritingShiftModifyer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
