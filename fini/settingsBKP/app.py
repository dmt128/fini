import json, pprint
from . import util
from .. util import screen

__all__ = [
    'load_settings', 'save_settings', 'change_setting', 'display_settings',
    ]

def load_settings(base_config):
    # settings_file = util.get_settings_abs_path()
    settings_file = base_config['settings_file']
    with open(settings_file , 'r') as fp:
        settings = json.load(fp)
    
    return settings

def save_settings(settings):
    # settings_file = util.get_settings_abs_path()
    settings_file = settings['global']['dir']['settings_file']
    with open(settings_file, 'w') as fp:
        json.dump(settings, fp, sort_keys=False, indent=4)

def change_setting(settings, key, value):
    if key in settings:
        settings[key] = value
    
    save_settings(settings)

def display_settings(dictionary, parent=None):
    for key, value in dictionary.items():
        if type(value) is dict:
            if parent:
                display_settings(value, parent + "." + key)
            else:
                display_settings(value, key)
        else:
            # import ipdb; ipdb.set_trace()
            if parent:
                key = parent + "." + key
            print(screen.Style.RESET_ALL + screen.Fore.CYAN + screen.Style.BRIGHT + "{:>40}: {}". format(key, value))
