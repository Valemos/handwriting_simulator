#%% First cell

from pathlib import Path
from handwriting.handwritten_path import HandwrittenPath
import path_manager as pm
import random as rnd
from memory_limiter import limit_memory


class TextWriter:
    
    def __init__(self):
        self.line_paths = [HandwrittenPath('', [])] # this contains paths for every line
    
    # text work functions
    def reset(self):
        self.line_paths = [HandwrittenPath('', [])] # set first line    
    
    def append(self, path):
        if len(path.shifts)>1:
            self.line_paths[-1].append_shift_list(path.shifts[1:-1])
            
        self.line_paths[-1].name += path.name[0]
        # print(self.line_paths[-1].name, pm.calc_path_rect(self.line_paths[-1]))
            
    def add_space(self, space_size):
        self.line_paths[-1].append(self.line_paths[-1].break_point)
        self.line_paths[-1].append_shift((space_size, 0))
        self.line_paths[-1].name += ' '
    
    def new_line(self):
        self.line_paths.append(HandwrittenPath('', []))
        
    def get_text_path(self, line_height = 100):
    
        fin_path = HandwrittenPath('', [])
        
        for l in range(len(self.line_paths)):
            fin_path.append_shift_list(self.line_paths[l].shifts[1:-1])
            fin_path.append(fin_path.break_point)
            fin_path.append((0, line_height*(l+1)))
        
        
        return fin_path

        
    def write_text(self, text, paths_dict, space_size, line_let_count = 10):
    
        self.reset()
        
        c = 0
        for let in text:
            
            if c >= line_let_count or let == '\n':
                c=0
                self.new_line()
            
            if let == ' ':
                self.add_space(space_size)
                
            elif let in paths_dict:
                self.append(rnd.choice(paths_dict[let]))
                
            c+=1
    

#%% Init letters

if __name__ == '__main__':

    # print text to image    
    
    limit_memory(1200)
    
    m_let_size = 50
    
    letters_dict = pm.load_paths_file(Path('ant2.hndw'))
    
    rect = pm.calc_path_rect(letters_dict['А'][0])
    scale_factor = (m_let_size)/(rect[3]-rect[1])
    
    letters_dict = pm.premodify_letters(letters_dict, scale_factor)
    
    #%% Write text
        
    m_writer = TextWriter()
    
    m_line_height = m_let_size+20
    
    text = 'Для каждого исконного закона познания очень рано должно было быть найдено' #' более или менее точное определение его абстрактного выражения, поэтому трудно, да и не особенно интересно, установить, где оно впервые встречается. Платон и Аристотель еще не устанавливают его по всей форме как главный основной закон, но часто говорят о нем как о самоочевидной истине. Так, Платон с наивностью, которая относится к критическим исследованиям нового времени, как состояние невинности к состоянию после познания добра и зла, говорит:'
    
    m_writer.write_text(text, letters_dict, round(m_line_height/2), 35)
    
    text_path = m_writer.get_text_path(m_line_height)
    
    pm.shift_path_rect(text_path, (0, 0))
    
    print(pm.calc_path_rect(text_path))
    
    img_text = pm.get_path_img(text_path, (0, 0, 0), 2)
    
    # img_text.save('test.png', 'PNG')
    
    img_text.show()