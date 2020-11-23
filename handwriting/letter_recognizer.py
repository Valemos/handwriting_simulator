#%% Import cell
import numpy as np
from pathlib import Path
import path_manager as pm
from memory_limiter import limit_memory

limit_memory(1000)

def make_path_grid(path, size = (10, 10)):
    
    rect = pm.calc_path_rect(path)
     
    img_array = np.ones((rect[3]-rect[1]+1, rect[2]-rect[0]+1), dtype = np.bool)

    for p in path.shifts:
        if p != path.break_point:
            img_array[p[1], p[0]] =  0

    return img_array

# def make_empty_grid(rect, size = (10, 10)):
    
#     col_num = round((rect[2] - rect[0]) / size[0])
#     row_num = round((rect[3] - rect[1]) / size[1])
    
#     # every element contains rectangles
#     grid = np.zeros((col_num, row_num, 2), dtype = np.int32)
    
#     # we only need to store one point - (right, bottom)
#     # the second point is stored in previous cells
    
#     # grid starts on (0, 0)
    
#     # first one
#     grid[0, 0] = [*size]

#     # init first row
#     for c in range(1, col_num):
#         grid[c, 0] = [grid[c-1, 0, 0] + size[0], size[1]]
    
#     # init first column
#     for r in range(1, row_num):
#         grid[0, r] = [size[0], grid[0, r-1, 1]+size[1]]
    
    
#     for c in range(1, col_num):
#         for r in range(1, row_num):
#             grid[c, r] = [grid[c-1, r-1, 0] + size[0], grid[c-1, r-1, 1] + size[1]]
        
        
#     # last cells must finish at rectangle borders
    
#     for c in range(1, col_num):
#         grid[c, -1, 1] = rect[3] - rect[1]
    
#     for r in range(1, row_num):
#         grid[-1, r, 0] = rect[2] - rect[0]
        
# def draw_grid(grid):
    
#     im = Image.new('RGBA', (round(grid[-1, -1, 0]), round(grid[-1, -1, 1])), (255, 0, 0, 0))
#     dr = ImageDraw.Draw(im)
    
    
#     # first row
#     for c in range(1, grid.shape[0]):
#         pm.draw_rect((0, 0, *grid[c, 0]), dr)
    
#     # first column
#     for r in range(1, grid.shape[1]):
#         pm.draw_rect((0, 0, *grid[0, r]), dr)
        
#     # other cells
#     for c in range(1, grid.shape[0]):
#         for r in range(1, grid.shape[1]):
#             pm.draw_rect((*grid[c-1, r-1], *grid[c, r]), dr)
        
    
#     return im
    
#%% Make letters

letters = pm.load_paths_file(Path('ant2.hndw'))

#%% form arrays

letter_arr = {}

for let, paths_set in letters.items():
    
    for path in paths_set:
        if let in letter_arr:
            letter_arr[let].append(make_path_grid(path))
        else:
            letter_arr[let] = [make_path_grid(path)]
