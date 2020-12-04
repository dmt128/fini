import os, sys, json, appdirs, operator, ast, pkgutil
from functools import reduce  # forward compatibility for Python 3
from . import defaults

__all__ = [
    '__app_name', '__app_author',
    'get_setting', 'set_setting',
    'get_config_dir', 'get_settings_abs_path', 'get_cmd_history_abs_path', 
    'get_data_dir', 'get_cache_dir', 'get_stocks_dir', 'get_cache_abs_path', 
    'get_log_dir', 'create_directory', 'create_default_settings_file', 'initial_setup',
    ]

__app_name   = "Fini"
__app_author = "Dimitri Zantalis"

#================================================
# Functions to deal with nested dictionaries
#================================================
# As described in https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
def __get_by_path__(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)

def __set_by_path__(root, items, value):
    """Set a value in a nested object in root by item sequence."""
    __get_by_path__(root, items[:-1])[items[-1]] = value

def __del_by_path__(root, items):
    """Delete a key-value in a nested object in root by item sequence."""
    del __get_by_path__(root, items[:-1])[items[-1]]


#================================================
# Functions to deal with settings dictionary
#================================================
def get_setting(settings, path):
    try:
        value = __get_by_path__(settings, path.split("."))
    except:
        print("Setting '{}' does not exist".format(path) )
        return None
    
    return value

def __tryeval(val):
    try:
        val = ast.literal_eval(val)
    except ValueError:
        pass
    return val

def set_setting(settings, path, value):
    old_value = get_setting(settings, path)
    if old_value is None:
        return False
    else:
        if type(value) is str:
            __set_by_path__(settings, path.split("."), value)
        else:
            __set_by_path__(settings, path.split("."), __tryeval(value))
        
    return True
    

#================================================
# Path related getter functions
#================================================
def get_config_dir():
    return appdirs.user_config_dir(__app_name, __app_author)

def get_settings_abs_path():
    return os.path.join(get_config_dir(), "settings.json")

def get_cmd_history_abs_path():
    return os.path.join(get_config_dir(), "fini_cmd_history")

def get_data_dir():
    return os.path.join(appdirs.user_data_dir(__app_name, __app_author), "data")

def get_cache_dir():
    return appdirs.user_cache_dir(__app_name, __app_author)

def get_stocks_dir():
    return os.path.join(get_cache_dir(), "stocks")

def get_cache_abs_path():
    return os.path.join(get_cache_dir(), "cache.json")

def get_log_dir():
    return appdirs.user_log_dir(__app_name, __app_author)


#================================================
# Directory and file creation functions
#================================================
def ask_user_to_create_directory(directory, access_rights):
    dir_ = input("Create '{}' (leave empty to keep default or enter a new path): ".format(directory))
    try:
        if not dir_:
            dir_ = directory
        os.mkdir(dir_, access_rights)
    except OSError:
        print ("Creation of {} failed".format(dir_))
        return None
    else:
        print ("Successfully created {}".format(dir_))
        return dir_

def create_directory(directory, access_rights):
    try:
        os.mkdir(directory, access_rights)
    except OSError:
        print ("Creation of {} failed".format(directory))
        return None
    else:
        print ("Successfully created {}".format(directory))
        return directory

def create_default_settings_file(abs_path, base_config):
    settings = defaults.get_default_settings(base_config)
    with open(abs_path, 'w') as fp:
        json.dump(settings, fp, sort_keys=False, indent=4)
    return abs_path

def create_default_cache_file(abs_path):
    cache = defaults.get_default_cache()
    with open(abs_path, 'w') as fp:
        json.dump(cache, fp, sort_keys=False, indent=4)
    return abs_path

def get_base_config():
    base_config_dir = os.path.dirname(sys.modules["fini.settings"].__file__)
    base_config_abs_path = os.path.join(base_config_dir, "base_config.json")
    data = open(base_config_abs_path, 'rb').read()
    base_config = json.loads(data)

    return base_config, base_config_abs_path

#================================================
# Validation functions
#================================================
def initial_setup():
    pass
# def initial_setup():
#     access_rights = 0o755
#     rewrite_base_config = False
    
#     base_config, base_config_abs_path = get_base_config()

#     # Check to see if there is a dir_cache.json file. If not then this means that this 
#     # is the first time the user runs the app.

#     # Check config directory
#     if not base_config['config_dir']:
#         directory = appdirs.user_config_dir(__app_name, __app_author)
#     else:
#         directory = base_config['config_dir']
    
#     if not os.path.exists(directory):
#         res = ask_user_to_create_directory(directory, access_rights)
#         if res:
#             base_config['config_dir'] = res
#             rewrite_base_config = True
#         else:
#             return None
#     else:
#         if base_config['config_dir'] != directory:
#             base_config['config_dir'] = directory
#             rewrite_base_config = True
    
#     # Check data directory
#     if not base_config['data_dir']:
#         directory = os.path.join(appdirs.user_data_dir(__app_name, __app_author), "data")
#     else:
#         directory = base_config['data_dir']
    
#     if not os.path.exists(directory):
#         res = ask_user_to_create_directory(directory, access_rights)
#         if res:
#             base_config['data_dir'] = res
#             rewrite_base_config = True
#         else:
#             return None
#     else:
#         if base_config['data_dir'] != directory:
#             base_config['data_dir'] = directory
#             rewrite_base_config = True
    
#     # Check cache directory
#     if not base_config['cache_dir']:
#         directory = appdirs.user_cache_dir(__app_name, __app_author)
#     else:
#         directory = base_config['cache_dir']

#     if not os.path.exists(directory):
#         res = ask_user_to_create_directory(directory, access_rights)
#         if res:
#             base_config['cache_dir'] = res
#             rewrite_base_config = True
#         else:
#             return None
#     else:
#         if base_config['cache_dir'] != directory:
#             base_config['cache_dir'] = directory
#             rewrite_base_config = True
    
#     # Check stocks directory
#     if not base_config['stocks_dir']:
#         directory = os.path.join( base_config['cache_dir'], "stocks" )
#     else:
#         directory = base_config['stocks_dir']
    
#     if not os.path.exists(directory):
#         res = create_directory(directory, access_rights)
#         if res:
#             base_config['stocks_dir'] = res
#             rewrite_base_config = True
#         else:
#             return None
#     else:
#         if base_config['stocks_dir'] != directory:
#             base_config['stocks_dir'] = directory
#             rewrite_base_config = True
    
#     # Check log directory
#     if not base_config['log_dir']:
#         directory = appdirs.user_log_dir(__app_name, __app_author)
#     else:
#         directory = base_config['log_dir']
    
#     if not os.path.exists(directory):
#         res = ask_user_to_create_directory(directory, access_rights)
#         if res:
#             base_config['log_dir'] = res
#             rewrite_base_config = True
#         else:
#             return None
#     else:
#         if base_config['log_dir'] != directory:
#             base_config['log_dir'] = directory
#             rewrite_base_config = True
    
#     # Check cache file
#     if not base_config['cache_file']:
#         directory = os.path.join( base_config['cache_dir'], "cache.json" )
#     else:
#         directory = base_config['cache_file']

#     if not os.path.exists(directory):
#         res = create_default_cache_file(directory)
#         if res:
#             base_config['cache_file'] = res
#             rewrite_base_config = True
#         else:
#             return None
#     else:
#         if base_config['cache_file'] != directory:
#             base_config['cache_file'] = directory
#             rewrite_base_config = True
    
#     # Check settings file
#     if not base_config['settings_file']:
#         directory = os.path.join( base_config['config_dir'], "settings.json" )
#     else:
#         directory = base_config['settings_file']
    
#     if not os.path.exists(directory):
#         base_config['settings_file'] = directory
#         res = create_default_settings_file(directory, base_config)
#         if res:
#             base_config['settings_file'] = res
#             rewrite_base_config = True
#         else:
#             return None
#     else:
#         if base_config['settings_file'] != directory:
#             base_config['settings_file'] = directory
#             rewrite_base_config = True

#     # Overwrite base config file, since the user might have selected paths other than the defaults
#     if rewrite_base_config:
#         print("Rewriting base config file...")
#         with open(base_config_abs_path, 'w') as fp:
#             json.dump(base_config, fp, sort_keys=False, indent=4)

#     # Finally return the base config to signify success
#     return base_config


# def check_directories():
#     access_rights = 0o755

#     # Check config directory
#     directory = get_config_dir()
#     if not os.path.exists(directory):
#         create_directory(directory, access_rights)
    
#     # Check data directory
#     directory = get_data_dir()
#     if not os.path.exists(directory):
#         create_directory(directory, access_rights)
    
#     # Check cache directory
#     directory = get_cache_dir()
#     if not os.path.exists(directory):
#         create_directory(directory, access_rights)
    
#     # Check stocks directory
#     directory = get_stocks_dir()
#     if not os.path.exists(directory):
#         create_directory(directory, access_rights)
    
#     # Check log directory
#     directory = get_log_dir()
#     if not os.path.exists(directory):
#         create_directory(directory, access_rights)
    
#     # Check settings file
#     settings_file = get_settings_abs_path()
#     if not os.path.exists(settings_file):
#         create_default_settings_file(settings_file)
    
#     # Check cache file
#     cache_file = get_cache_abs_path()
#     if not os.path.exists(cache_file):
#         create_default_cache_file(cache_file)
    