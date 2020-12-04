import os
from . screen import pos
from .. import fonts

__all__ = [
    'find_starting_pos_for_ticker_title',
    'print_using_font', 'print_using_font2',
]

def find_starting_pos_for_ticker_title(tik, font=fonts.small_slant):
    term_x, term_y = os.get_terminal_size()
    max_width = 0
    for c in list(tik):
        f = font[c]
        width  = len(f["line_1"])
        max_width += width
    
    return int( (term_x/2) - (max_width/2) )

def print_using_font(msg, x, y, format_font, font=fonts.small_slant):
    term_x, term_y = os.get_terminal_size()
    cur_x = x   
    for c in list(msg):
        cur_y = y
        f = font[c]
        width  = len(f["line_1"])
        height = len(f) 

        i = 0
        for v in f.values():
            print(pos(cur_x, cur_y)  + format_font[i] + v )
            cur_y += 1
            i += 1
        
        cur_x += width
    
    return cur_x, y + height

def print_using_font2(msg, x, y, format_font, font=fonts.small_slant):
    term_x, term_y = os.get_terminal_size()
    f_list = []
    for c in list(msg):
        f_list.append(font[c])

    num_lines = len(f_list[0])
    lines = []
    cur_y = y
    for l in range(num_lines):
        line = ""
        for f in f_list:
            line += f["line_{}".format(l+1)]
        print(format_font[l] + "{:^{term_x}}".format(line, term_x=term_x ))

    return 0, y + num_lines + 1