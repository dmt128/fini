import json, pprint
from . import util
from .. util import screen

__all__ = [
    'load_cache', 'save_cache', 'display_cache',
    ]

def load_cache():
    cache_file = util.get_cache_abs_path()
    with open(cache_file , 'r') as fp:
        cache = json.load(fp)
    
    return cache

def save_cache(cache):
    cache_file = util.get_cache_abs_path()
    with open(cache_file, 'w') as fp:
        json.dump(cache, fp, sort_keys=False, indent=4)

def display_cache(cache):
    print(screen.Fore.CYAN + screen.Style.BRIGHT + "====================================")
    print("SETTINGS\n")
    pprint.pprint(settings, indent=4, width=80, depth=4, sort_dicts=False)
    print("====================================\n" + screen.Style.RESET_ALL)
