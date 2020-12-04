import os, sys, colorama
from colorama import Fore, Back, Style, Cursor
from .time import get_datetime_now_as_string
from .. import fonts
from .. import version

__all__ = [
    'pos', 'Fore', 'Back', 'Style', 'Cursor', 'app_welcome_message',
    'move_cursor', 'erase_screen', 'clear_screen', 'scroll_down',
    'hide_cursor', 'show_cursor',
]

pos = lambda x, y: Cursor.POS(x, y)

def app_welcome_message():
    format_welcome = Style.RESET_ALL + Style.BRIGHT  + Back.BLACK + Fore.YELLOW
    print(format_welcome + "==============================                                  ")
    print(format_welcome + " Welcome to Fini {:<6}                                         ".format(version.__version__))
    print(format_welcome + "==============================                                  ")
    print(format_welcome + " * Type a ticker symbol at the prompt and press enter to commit ")
    print(format_welcome + "   and get financial inforation about the company.              ")
    print(format_welcome + " * Type -h or --help to see what commands are available.        ")
    print(format_welcome + "                                                                ")
    print(format_welcome + " Enjoy using fini!                                              ")
    print(Style.RESET_ALL)
    print("Local time: {}".format(get_datetime_now_as_string()))
    print("")

def move_cursor(y):
    for yy in range(y):
        print(Style.RESET_ALL + Fore.BLACK + Back.BLACK + " ")

def erase_screen():
    print("\033[2J\033[3J\033[1;1H" + Style.RESET_ALL)

def clear_screen(): 
    term_x, term_y = os.get_terminal_size()
    for y in range(term_y):
        print(pos(0, y) + Fore.BLACK + Back.BLACK + " "*term_x)
    
    print(pos(0, 0) + Style.RESET_ALL)

def scroll_down(): 
    # for windows 
    if os.name == 'nt': 
        _ = os.system('cls') 

    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = os.system('clear') 
    
    print(pos(0, 0) + Style.RESET_ALL)


# Code taken from James's Spencer answer in StackOverflow:
# https://stackoverflow.com/questions/5174810/how-to-turn-off-blinking-cursor-in-command-window/10455937#10455937 
if os.name == 'nt':
    import msvcrt
    import ctypes

    class _CursorInfo(ctypes.Structure):
        _fields_ = [("size", ctypes.c_int),
                    ("visible", ctypes.c_byte)]
def hide_cursor():
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

def show_cursor():
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
