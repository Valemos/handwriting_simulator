from PIL import Image, ImageDraw
import numpy as np
from handwriting.path.handwritten_path import HandwrittenPath


def load_paths_file(file_path, is_shift=False):
    paths = {}

    for path in HandwrittenPath.from_file(file_path):
        path = shift_path_rect(let, (0, 0))
        if path.name[0] in paths:
            paths[path.name[0]].append(path)
        else:
            paths[path.name[0]] = [path]

    return paths


def draw_path(path, draw_obj, draw_color=(0, 0, 0), draw_w=4, shift=None):
    last_point = None
    for point in path.get_variant_or_raise(shift):
        if point != path.break_point:
            if last_point != None and last_point != path.break_point:
                draw_obj.line((*last_point, *point), fill=draw_color, width=draw_w)

        last_point = point
    return draw_obj


def draw_rect(borders, draw, accent_color=(255, 100, 100), draw_w=2):
    (left, top, right, bottom) = borders
    draw.line([left, top, right, top, right, bottom, left, bottom, left, top], fill=accent_color, width=draw_w)


def get_path_img(path, draw_obj=None, draw_color=(0, 0, 0), draw_w=4, img_size=None):
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


def premodify_letters(dct, scale_factor):
    for char, paths_set in dct.items():

        for path in paths_set:
            if len(path.shifts) < 2:
                continue

            first_p, last_p = path.shifts[0], path.shifts[-2]
            rotation = np.arctan((first_p[1] - last_p[1]) / (first_p[0] - last_p[0]))
            transform_path(path, rotation, (scale_factor, scale_factor))

    return dct


def transform_path(path, angle_rad=0, scale=(1, 1), inplace=True):
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
    scale = (new_size[0] / (rect[2] - rect[0]), new_size[1] / (rect[3] - rect[1]))

    return transform_path(path, 0, scale)
