from tkinter import messagebox
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw
import numpy as np

from handwriting.letter_processing import TextWriter
import path_manager as pm
from memory_limiter import limit_memory

class PhotoTextWriter(tk.Frame):

    def __init__(self, parent):
        limit_memory(1000)
        
        parent.geometry("800x650")
        tk.Frame.__init__(self, parent)
        self.parent = parent
        
        self.grid_width = 15
        self.grid_height = 1
        
        self.brush_size = 5
        self.brush_color = "black"
        
        self.last_draw_point = (None, None)
        self.cur_text_writer = None
        self.all_letters = {}
        self.all_pages = {}
        self.all_text_points = {} # format (left, top, right, bottom, line_x, line_y)
        self.all_fit_scales = {}
        
        self.text_image = None
        self.photoimage_page = None
        self.cur_page_number = 1
        
        self.points_counter = 0
        self.points_draw_objects = []
        self.points_colors = ['red', 'red', 'black']
        
        self.text_points_format = '({0}, {1})/({2}, {3})\n({4}, {5})'
        
        self.d_file_name = 'ant'
        self.d_path_name = 'path'
        self.d_page_name = 'page'
        self.d_file_suffix = '.hndw'
        self.d_shift_suffix = '.shift'
        self.image_suffix = '.png'
        self.msg_no_option = 'no options'
        self.msg_can_select = 'select'
        
        self.shift_paths_open_mode = tk.BooleanVar()
        self.shift_paths_open_mode.set(0)
        
        self.setUI()
        self.reset_canvas()
    
    def setUI(self):
 
        self.parent.title("Text writer")
        self.pack(fill = tk.BOTH, expand=1)
 
        self.columnconfigure(6, weight=1)
        self.rowconfigure(5, weight=1)
 
        self.canv = tk.Canvas(self, bg="white", height = 600)
        self.reset_canvas()
        self.canv.grid(row=5, column=0, columnspan=7,
                       padx=5, pady=5, sticky=tk.E+tk.W+tk.S+tk.N)
        
        color_lab = tk.Label(self, text="General: ")
        color_lab.grid(row=0, column=0, padx=6)
        
        draw_shift_chk = tk.Checkbutton(self, text="Shift mode", width=self.grid_width, height = self.grid_height, variable=self.shift_paths_open_mode, onvalue=1, offvalue=0)
        draw_shift_chk.grid(row=0, column=1, sticky=tk.W+ tk.E)
        
        clear_btn = tk.Button(self, text="Clear all", width=self.grid_width, height = self.grid_height, command = lambda: self.reset_canvas())
        clear_btn.grid(row=0, column=2, sticky=tk.W + tk.E)
        
        self.parent.bind('<Control-Key-d>', lambda e: self.reset_canvas())
        
        ch_file_path_label = tk.Label(self, text="Choose letters file: ")
        ch_file_path_label.grid(row=1, column=0, padx=5)
        
        self.file_path_var = tk.StringVar(self)
        letters_path_entry = tk.Entry(self, width=self.grid_width, textvariable = self.file_path_var)
        letters_path_entry.grid(row=1, column=1, sticky=tk.E+tk.W, padx=5)

        letters_path_entry.bind('<Return>', self.handle_enter_on_path)
        
        
        ch_pages_path_label = tk.Label(self, text="Choose pages folder: ")
        ch_pages_path_label.grid(row=2, column=0, padx=5)
        
        self.pages_path_var = tk.StringVar(self)
        pages_path_entry = tk.Entry(self, width=self.grid_width, textvariable = self.pages_path_var)
        pages_path_entry.grid(row=2, column=1, sticky=tk.E+tk.W, padx=5)
        pages_path_entry.bind('<Return>', self.handle_enter_on_dir)
        
        self.cur_page_name_var = tk.StringVar(self)
        self.cur_page_name_var.set(self.msg_no_option)
        self.ch_page_menu = tk.OptionMenu(self, self.cur_page_name_var, value = None)
        self.refresh_menu_choices()
        self.ch_page_menu.grid(row=1, column=2, sticky= tk.W)
        self.ch_page_menu.config(width=self.grid_width, height=self.grid_height)
        
        # enter press opens files
        
        control_btn_frame = tk.Frame(self)
        control_btn_frame.grid(row=2, column=2, sticky=tk.W+tk.E)
        control_btn_prev = tk.Button(control_btn_frame, text='<<', command = lambda: self.go_to_prev_page(), width=round(self.grid_width/2))
        control_btn_next = tk.Button(control_btn_frame, text='>>', command = lambda: self.go_to_next_page(), width=round(self.grid_width/2))
        control_btn_prev.pack(side=tk.LEFT)
        control_btn_next.pack(side=tk.RIGHT)
        
        self.parent.bind('<Left>', lambda e: self.go_to_prev_page())
        self.parent.bind('<Right>', lambda e: self.go_to_next_page())
        
        
        # save_letter_btn = tk.Button(self, text="Save page", width=self.grid_width, height=self.grid_height, command = lambda: self.handle_save_page())
        # save_letter_btn.grid(row=3, column=2, sticky=tk.W+tk.E)

        draw_text_btn = tk.Button(self, text="Remove image", width=round(self.grid_width/3*2), height=self.grid_height, command=lambda: self.handle_remove_image())
        draw_text_btn.grid(row=1, column=3, sticky=tk.W+tk.E)    

        draw_text_btn = tk.Button(self, text="Draw text", width=round(self.grid_width/3*2), height=self.grid_height, command=lambda: self.handle_draw_text())
        draw_text_btn.grid(row=2, column=3, sticky=tk.W+tk.E)
        
        reset_text_btn = tk.Button(self, text="Reset text", width=round(self.grid_width/3*2), command=lambda: self.handle_reset_text())
        reset_text_btn.grid(row=3, column=3, sticky=tk.W+tk.E)
        
        # text area abs_points
        points_btn = tk.Button(self, text="Points", width=self.grid_width, height=self.grid_height, command = lambda: self.handle_init_text_points())
        points_btn.grid(row=0, column=4, sticky=tk.W+tk.E)
        
        self.points_values_var = tk.StringVar(self)
        self.points_values_var.set(self.text_points_format.format(*[0]*6))
        points_values_str = tk.Label(self, width = self.grid_width, textvariable = self.points_values_var)#500,500,500,500,500,500))
        points_values_str.grid(row=1, column=4, padx=5)
        
        space_sz_label = tk.Label(self, text="Space size")
        space_sz_label.grid(row=0, column=6, padx=5)
        
        self.space_sz_var = tk.StringVar(self)
        self.space_sz_var.set(50)
        self.space_sz_var.trace('w', lambda *args: self.limit_var_int(self.space_sz_var))
        
        space_sz_entry = tk.Entry(self, width=self.grid_width, textvariable = self.space_sz_var)
        space_sz_entry.grid(row=1, column=6, padx=5)
        
        self.draw_text_var = tk.Text(self, width=self.grid_width*3, height=self.grid_height*3)
        self.draw_text_var.grid(row=2, column=4, rowspan=2, columnspan=3, sticky=tk.E+tk.W, padx=5)
            
    def reset_canvas(self):
        self.canv.delete("all")
        self.text_image = None
        self.photoimage_page = None
        
    def canvas_delete_points(self):
        for obj in self.points_draw_objects:
            self.canv.delete(obj)
        
        self.points_draw_objects = []

    def draw_page(self, page_name):
        
        img = self.all_pages.get(page_name)
        if img is None: return
        
        scale = self.get_cur_page_scale()
        img = img.resize((int(img.size[0]*scale), int(img.size[1]*scale)), Image.ANTIALIAS)
        
        img = ImageTk.PhotoImage(img)
        self.photoimage_page = img
        self.canv.create_image((0, 0), anchor= tk.NW, image = img)
        
        
    def handle_enter_on_path(self, event):
        file_path = self.handle_file_path(is_shift_file = self.shift_paths_open_mode.get())
        self.open_selected_letters_file(file_path, self.shift_paths_open_mode.get())
        
    def handle_enter_on_dir(self, event):
        file_path = self.handle_dir()
        self.init_page_images(file_path)
        
        if len(self.all_pages)>0:
            self.handle_page_chosen(self.cur_page_name_var, list(self.all_pages.keys())[0])
        
    def handle_draw_text(self):
        
        text = self.draw_text_var.get(1.0, tk.END)
        
        cur_page = self.get_cur_value(self.all_pages)[0] # copy image
        
        
        upper_letter = None
        for let in list(self.all_letters.keys()):
            if let.isupper():
                upper_letter = let
                break
        
        if upper_letter is None or cur_page is None:
            print('info not found')
            return
        
        cur_text_points = list(map(int, self.get_cur_value(self.all_text_points)[0]))
        line_height = np.sqrt((cur_text_points[4]-cur_text_points[0])**2 + (cur_text_points[5]-cur_text_points[1])**2)
        
        rect = pm.calc_path_rect(self.all_letters[upper_letter][0])
        scale_factor = (line_height-5)/(rect[3]-rect[1])
        
        pm.premodify_letters(self.all_letters, scale_factor)
        
        # pm.get_path_img(self.all_letters[upper_letter][0]).show()
        
        text_writer = TextWriter()
        text_writer.write_text(text, self.all_letters, int(self.space_sz_var.get()))
        
        
        # when first point on second place strange things happen
        
        sh_path = text_writer.get_text_path(line_height)
        # print(pm.calc_path_rect(sh_path))
        # print(sh_path.shifts)
        sh_path = pm.shift_path_rect(sh_path, (cur_text_points[0], cur_text_points[1]), False)
        
        pm.get_path_img(sh_path, ImageDraw.Draw(cur_page), draw_color = (0, 0, 48, 102), draw_w = 1)
        
        page_name = self.d_page_name + str(self.cur_page_number)
        self.cur_page_number += 1
        
        cur_page.save(page_name + self.image_suffix)
        self.all_pages[page_name] = cur_page
        self.handle_page_chosen(self.cur_page_name_var, page_name)
        self.refresh_menu_choices(page_name)
        
    def handle_reset_text(self):
        
        self.all_pages[self.cur_page_name_var.get()] = Image.open(self.handle_dir()/(self.cur_page_name_var.get()+self.image_suffix))
        self.handle_page_chosen(self.cur_page_name_var, self.cur_page_name_var.get())
    
    def handle_init_text_points(self):
        cur_page = self.get_cur_value()[1]
        
        
        if cur_page == self.msg_can_select or cur_page == self.msg_no_option:
            return
        
        self.canvas_delete_points()
        self.all_text_points[cur_page] = [0, 0, 0, 0, 0, 0]
        self.canv.bind('<Button-1>', self.handle_point_init_click)
        self.points_counter = 0
    
    def handle_point_init_click(self, event):
        
        real_point = self.get_real_point_coords((event.x, event.y))
        
        self.points_counter += 1
        
        if self.points_counter == 1:
            self.all_text_points[self.get_cur_value()[1]][0:2] = real_point
            self.draw_point_scope((event.x, event.y), self.points_colors[0])
            self.refresh_points_text()
            
        elif self.points_counter == 2:
            self.all_text_points[self.get_cur_value()[1]][2:4] = real_point
            self.draw_point_scope((event.x, event.y), self.points_colors[1])
            self.refresh_points_text()
            
        elif self.points_counter == 3:
            self.all_text_points[self.get_cur_value()[1]][4:6] = real_point
            self.draw_point_scope((event.x, event.y), self.points_colors[2])
            self.refresh_points_text()
            
        else:
            self.points_counter = 0
            self.canv.unbind('<Button-1>')

    def refresh_points_text(self, points = None):
        if points is None:
            points = tuple(map(int, self.get_cur_value(self.all_text_points)[0]))
            
        self.points_values_var.set(self.text_points_format.format(*points))

    def draw_point_scope(self, point, color):
        lst = []
        r = 10
        lst.append(self.canv.create_oval((point[0]-r, point[1]-r, point[0]+r, point[1]+r), outline=color))
        lst.append(self.canv.create_line(point[0], point[1]-r, point[0], point[1]+r, fill=color))
        lst.append(self.canv.create_line(point[0]-r, point[1], point[0]+r, point[1], fill=color))
        
        self.points_draw_objects.extend(lst)
        
    def handle_remove_image(self):
        remove_name = self.cur_page_name_var.get()
        
        if remove_name != self.msg_can_select and remove_name != self.msg_no_option:
            if len(self.all_pages) == 0:
                self.reset_canvas()
                self.cur_page_name_var.set(self.msg_no_option)
                self.refresh_menu_choices()
            elif len(self.all_pages) == 1:
                self.reset_canvas()
                self.cur_page_name_var.set(self.msg_no_option)
                del self.all_pages[remove_name]
            else:
                self.go_to_next_page()
                del self.all_pages[remove_name]    
                self.refresh_menu_choices(self.cur_page_name_var.get())
    
    def handle_page_chosen(self, label_var, choice):
        label_var.set(choice)
        self.reset_canvas()
        self.draw_page(choice)
        self.points_counter = 0
        self.canv.unbind('<Button-1>')
        
        cur_points = self.get_cur_value(self.all_text_points)[0]
        
        if not cur_points is None:
            self.points_draw_objects = []
            for p, color in zip([cur_points[0:2], cur_points[2:4], cur_points[4:6]], self.points_colors):
                self.draw_point_scope(self.get_canvas_point_coords(p), color)
            
            self.refresh_points_text()
        else:
            self.refresh_points_text([0]*6)
    
    def get_real_point_coords(self, point):
        scale = self.get_cur_page_scale()       
        return (point[0]/scale, point[1]/scale)
    
    def get_canvas_point_coords(self, point):
        scale = self.get_cur_page_scale()
        return (int(point[0]*scale), int(point[1]*scale))
    
    def get_cur_page_scale(self):
        cur_page = self.get_cur_value(self.all_pages)[0]
        
        max_img_side = max(*cur_page.size)
        max_canv_side = max(int(self.canv['width']), int(self.canv['height']))
        
        return max_canv_side/max_img_side
    
    def limit_var_int(self, var):
        if not self.str_is_int(var.get()):
            s = var.get()
            ns = ''
            for c in s:
                if c.isdigit():
                    ns += c
            var.set(ns)
    
    def str_is_int(self, s):
        try: 
            int(s)
            return True
        except ValueError:
            return False
    
    def get_cur_value(self, dct = None):
        if dct is None:
            return None, self.cur_page_name_var.get()
        else:
            return dct.get(self.cur_page_name_var.get()), self.cur_page_name_var.get()
    
    def go_to_next_page(self):
        cur_name = self.cur_page_name_var.get() 
        keys_list = list(self.all_pages.keys())
        
        if len(keys_list) == 0:
            self.reset_canvas()
            self.cur_page_name_var.set(self.msg_no_option)
            return None
        
        if cur_name not in keys_list:
            cur_name = keys_list[0]
            cur_idx = 0
        else:
            cur_idx = keys_list.index(cur_name)
            
        cur_idx = (cur_idx + 1) % len(keys_list)
        self.handle_page_chosen(self.cur_page_name_var, keys_list[cur_idx])
        return keys_list[cur_idx]
        
    def go_to_prev_page(self):
        cur_name = self.cur_page_name_var.get() 
        keys_list = list(self.all_pages.keys())
        
        if len(keys_list) == 0:
            self.reset_canvas()
            self.cur_page_name_var.set(self.msg_no_option)
            return None
            
        if cur_name in keys_list:
            cur_idx = keys_list.index(cur_name)
        else:
            cur_name = keys_list[0]
            cur_idx = 0
            
        cur_idx = (cur_idx-1)%len(keys_list)
        self.handle_page_chosen(self.cur_page_name_var, keys_list[cur_idx])
        return cur_name
    
    def set_menu_choices(self, option_menu, label_var, choices, default=None):
        if choices is not None:
            label_var.set(self.msg_can_select)
        else:
            label_var.set(self.msg_no_option)
            choices = []
        
        option_menu['menu'].delete(0, 'end')
        
        for choice in choices:
            option_menu['menu'].add_command(label = choice, command = lambda c = choice: self.handle_page_chosen(label_var,c))
        
        if default is not None:
            label_var.set(default)
       
    def refresh_menu_choices(self, default = None):
        self.set_menu_choices(self.ch_page_menu, self.cur_page_name_var, list(self.all_pages.keys()), default)
        
    def open_selected_letters_file(self, path = None, is_shift = False):
        self.all_letters = pm.load_paths_file(path, is_shift)
            
        
    def init_page_images(self, path = None):
        file_path = self.handle_dir()
        
        for path in file_path.glob('*'+self.image_suffix):
            self.all_pages[path.with_suffix('').name] = Image.open(path)
            
        if len(self.all_pages)>0:
            self.cur_page_name_var.set(self.msg_can_select)
            self.refresh_menu_choices()
        else:
            self.cur_page_name_var.set(self.msg_no_option)
            
    def make_unique_name(self, name, dct):
        if len(name) == 0: name = self.d_path_name
        count = 1
        new_name = name
        while new_name in dct:
            new_name = name + str(count)
            count+=1
        return new_name
        
    def handle_file_path(self, path_str = None, is_shift_file = False):
        if path_str is None:
            if len(self.file_path_var.get())==0:
                if is_shift_file:
                    file_path = Path(self.d_file_name + self.d_shift_suffix + self.d_file_suffix)
                else:
                    file_path = Path(self.d_file_name + self.d_file_suffix)
                self.file_path_var.set(str(file_path))
            else:
                file_path = Path(self.file_path_var.get())
        else:
            file_path = Path(path_str)
        

        if file_path.is_dir():
            if is_shift_file: def_file_path = file_path/(self.d_file_name + self.d_file_suffix)
            else:             def_file_path = file_path/(self.d_file_name + self.d_shift_suffix + self.d_file_suffix)
            
            if def_file_path.exists() and path_str is None:
                messagebox.showinfo('Handwriting manager','Found default file. Changing input path to\n'+str(def_file_path))
                
            file_path = def_file_path
            
        if is_shift_file:
            if file_path.suffixes != [self.d_shift_suffix, self.d_file_suffix]:
                file_path = file_path.with_suffix(self.d_shift_suffix + self.d_file_suffix)
                if path_str is None: self.file_path_var.set(str(file_path))
        else:
            file_path = file_path.with_suffix('').with_suffix(self.d_file_suffix)

        if not file_path.exists():
            file_path.parent.mkdir(parents = True, exist_ok = True)
            file_path.touch()
            messagebox.showinfo('Handwriting manager', 'Successfully created file\n'+str(file_path))
        
        self.file_path_var.set(str(file_path))
        return file_path

    def handle_dir(self, path_str = None):
        if path_str is None:
            if len(self.pages_path_var.get())==0:
                file_path = Path(self.d_page_name)
            else:
                file_path = Path(self.pages_path_var.get())
        else:
            file_path = Path(path_str)
        

        if not file_path.is_dir():
            
            while file_path.suffix != '':
                file_path = file_path.with_suffix('')
                
            
        if not file_path.exists():
            file_path.mkdir(parents = True, exist_ok = True)
            messagebox.showinfo('Handwriting manager', 'Successfully created folder')
        
        self.pages_path_var.set(str(file_path))
        return file_path
        
def main():
    root = tk.Tk()
    app = PhotoTextWriter(root)
    root.mainloop()

if __name__ == "__main__":
    main()

