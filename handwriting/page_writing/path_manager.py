from PIL import Image, ImageDraw
import numpy as np
from handwriting.path_management.handwritten_path import HandwrittenPath



def load_paths_file(file_path, is_shift = False):
    paths = {}

    for path in HandwrittenPath.from_file(file_path):
        path = shift_path_rect(let, (0, 0))
        if path.name[0] in paths:
            paths[path.name[0]].append(path)
        else:
            paths[path.name[0]] = [path]

    return paths

def draw_path(path, draw_obj, draw_color = (0, 0, 0), draw_w = 4, shift = None):

    last_point = None
    for point in path.get_path(shift):
        if point != path.break_point:
            if last_point != None and last_point != path.break_point:
                draw_obj.line((*last_point, *point), fill = draw_color, width = draw_w)

        last_point = point
    return draw_obj

def draw_rect(borders, draw, accent_color = (255, 100, 100), draw_w = 2):
    (left, top, right, bottom) = borders
    draw.line([left, top, right, top, right, bottom, left, bottom, left, top], fill = accent_color, width = draw_w)

def calc_path_rect(path, shift = None):
    points = path.get_path(shift)
    
    not_br = 0
    while points[not_br] == path.break_point: not_br+=1
    
    left, top, right, bottom = points[not_br][0], points[not_br][1], points[not_br][0], points[not_br][1]

    for p in points:
        if p != path.break_point:
            if p[0] > right:
                right = p[0]
            elif p[0] < left:
                left = p[0]

            if p[1] > bottom:
                bottom = p[1]
            elif p[1] < top:
                top = p[1]

    return (left, top, right, bottom)

def get_path_img(path, draw_obj = None, draw_color = (0, 0, 0), draw_w = 4, img_size = None):

    im = None
    
    if draw_obj is None:
        if img_size is None:
            rect = calc_path_rect(path)
            im = Image.new('RGBA', (int(rect[2]), int(rect[3])), (0, 0, 0, 255))
        else:
            im = Image.new('RGBA', img_size, (0, 0, 0, 255))
        
        draw_obj = ImageDraw.Draw(im)
        
    draw_path(path, draw_obj, draw_color, draw_w)
    return im

def shift_path_rect(path, shift_p, inplace = True):
    new_path = path if inplace else path.copy()
    rect = calc_path_rect(new_path)
    shift = (shift_p[0] - rect[0], shift_p[1] - rect[1])
    new_path.shifts[0] = (new_path.shifts[0][0] + shift[0], new_path.shifts[0][1] + shift[1])
    for i in range(len(path.shifts)):
        if new_path.points[i] != new_path.break_point:
            new_path.points[i] = (new_path.points[i][0] + shift[0], new_path.points[i][1] + shift[1])
    return new_path

def premodify_letters(dct, scale_factor):
    
    for char, paths_set in dct.items():
        
        for path in paths_set:
            if len(path.shifts) < 2:
                continue
            
            first_p, last_p = path.shifts[0], path.shifts[-2]
            rotation = np.arctan((first_p[1]-last_p[1])/(first_p[0]-last_p[0]));
            transform_path(path, rotation, (scale_factor, scale_factor))
            shift_path_rect(path, (0, 0))
            
    return dct
    

def transform_path(path, angle_rad = 0, scale = (1, 1), inplace = True):
   
    new_points = list(path.shifts)
        
    r = np.matrix([[np.cos(angle_rad), np.sin(angle_rad)], [-np.sin(angle_rad), np.cos(angle_rad)]])
    r = r.dot(np.matrix([[scale[0], 0], [0, scale[1]]]))
    r = r.round(5)
    
    for i in range(len(new_points)):
        if new_points[i] != path.break_point:
            lst = np.dot(r, path.shifts[i]).tolist()
            
            new_points[i] = (round(lst[0]), round(lst[1]))
    
    if inplace:
        path.set_points(new_points)
        return path
    else:
        return HandwrittenPath(path.name, new_points)

def rescale_path(path, new_size):
    rect = calc_path_rect(path)
    scale = (new_size[0]/(rect[2]-rect[0]), new_size[1]/(rect[3]-rect[1]))

    return transform_path(path, 0, scale)

