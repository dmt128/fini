import os, sys, re, json, operator, ast, inspect, pkgutil, appdirs, colorama
from functools import reduce  # forward compatibility for Python 3
from .. import util
from .. util import screen
from .. util.screen import Fore, Back, Style
from .. import version


__all__ = [
    'ask_user_to_create_directory', 'create_directory',
    'convert_value_str_to_type', 'SettingsManager',
]

def ask_user_to_create_directory(directory, access_rights):
    dir_ = input("Create '{}' (leave empty to keep default or enter a new path): ".format(directory))
    try:
        if not dir_:
            dir_ = directory
        os.mkdir(dir_, access_rights)
    except FileExistsError:
        # path already exists, so we are good to go
        return dir_
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


def convert_value_str_to_type(value):
    if value and value[0] == "#":
        value = "\"{}\"".format(value)
    try:
        value = ast.literal_eval(value)
    except Exception:
        value = "\"{}\"".format(value)
        try:
            value = ast.literal_eval(value)
        except Exception:
            return None
        return value
    return value

class settings_ctx:
    def __init__(self, provider, settings_manager, debug=False):
        self._provider = provider
        self._provider_id = provider.provider_id()
        self._smng = settings_manager
        self._settings  = {}
        self._condition = {}
        self._debug = debug

    def _create_color_setting_lambda(self, color_fmt):
        return lambda data: color_fmt
    
    def _create_color_setting_conditional_lambda(self, cond, fmt_option):
        if cond:
            return lambda data: self._settings[fmt_option[0]](None) if eval(cond[0].format(data=data)) else self._create_color_setting_conditional_lambda(cond[1:], fmt_option[1:])(data)
        else:
            return

    def _create_full_key(self, key):
        keys = key.split(".")
        if keys[0] not in self._smng.get_settings_parent_keys() and keys[0] != self._provider_id:
            return ".".join( [self._provider_id, key] )
        else:
            return key

    def _replace_ref_value(self, value):
        # Try to replace any refered value only if value is of string type
        if type(value) is str:
            ff = re.split("(?:{(.*)})",value)
            if len(ff) == 1:
                val     = ff[0]
                ref_val = ""
            elif len(ff) == 3:
                val     = ff[0]
                keys = ff[1].split(".")
                if keys[0] not in self._smng.get_settings_parent_keys() and keys[0] != self._provider_id:
                    ref_val = "{" + ".".join([self._provider_id, ff[1]]) + "}"
                else:
                    ref_val = "{" + ff[1] + "}"
            else:
                val     = value
                ref_val = ""

            # Check to see that ref val exists
            if ref_val:
                ref_val_exists = self._smng.get_setting(ref_val[1:-1])
                if not ref_val_exists:
                    raise Exception("Reference value '{}' does not exist!".format(ref_val[1:-1]))

            # Create and return full value name
            return val + ref_val, ref_val
        else:
            return value, None

    def add_setting(
        self, 
        key, 
        value, 
        set_callback=None, 
        set_user_data=None,
        get_callback=None, 
        get_user_data=None,
        ):
        # Create full settings path for this provider
        settings_path = self._create_full_key(key)

        # Add format setting to global settings manager
        self._smng.add_setting(settings_path, value)

        # Add set listener for this setting, if any
        if set_callback:
            self._smng.add_set_listener_for_setting(settings_path, set_callback, set_user_data)
        
        # Add get listener for this setting, if any
        if get_callback:
            self._smng.add_get_listener_for_setting(settings_path, get_callback, get_user_data)

    def add_fmt_setting(
        self, 
        key, 
        value, 
        set_callback=None, 
        set_user_data=None, 
        get_callback=None, 
        get_user_data=None):

        # Create full settings path for this provider
        settings_path = self._create_full_key(key)

        # Replace any refered value
        new_value, ref_value = self._replace_ref_value(value)
        
        # Add format setting to global settings manager
        self._smng.add_setting(settings_path, new_value)

        # Add listener for this setting.
        # In 'add_fmt_setting' we always add the base class supplied update_draw_ctx as
        # listener. This is a quick and dirty way to ensure graphics are updated when the
        # user makes a change on format settings.
        self._smng.add_set_listener_for_setting(settings_path, self._provider.update_draw_ctx, user_data=None)

        if ref_value:
            self._smng.add_set_listener_for_setting(ref_value[1:-1], self._provider.update_draw_ctx, user_data=None)

        # Add set listener for this setting, if any
        if set_callback:
            self._smng.add_set_listener_for_setting(settings_path, set_callback, set_user_data)
        
        # Add get listener for this setting, if any
        if get_callback:
            self._smng.add_get_listener_for_setting(settings_path, get_callback, get_user_data)

        # Evaluate the setting value and store in internal settings dictionary.
        evaluated_value = self._smng.get_setting(settings_path)
        # util.misc.DictUtil.add_by_path( self._settings, settings_path, self._create_color_setting_lambda(evaluated_value) )
        self._settings[settings_path] = self._create_color_setting_lambda(evaluated_value)

    def add_condition(self, key, condition, fmt_option):
        # Create full settings path for this provider
        settings_path = self._create_full_key(key)

        # Add provider id to settings path of format options, if necessary
        for idx, elem in enumerate(fmt_option):
            keys = fmt_option[idx].split(".")
            if keys[0] != self._provider_id:
                fmt_option[idx] = ".".join( [self._provider_id, fmt_option[idx]] )
        
        # Add condition to internal dictionary
        if not self._condition.get(settings_path):
            self._condition[settings_path] = {
                'condition': condition,
                'fmt_option': fmt_option,
            }

        # Add condition to internal settings dictionary
        if not self._settings.get(settings_path):
            self._settings[settings_path] = self._create_color_setting_conditional_lambda(self._condition[settings_path]['condition'], self._condition[settings_path]['fmt_option'])
        else:
            if self._debug:
                print("Condition '{}' already exists".format(name))

    def update_settings(self):
        for settings_path in self._settings:
            if "condition" in settings_path:
                self._settings[settings_path] = self._create_color_setting_conditional_lambda(self._condition[settings_path]['condition'], self._condition[settings_path]['fmt_option'])
            else:
                evaluated_value = self._smng.get_setting(settings_path)
                self._settings[settings_path] = self._create_color_setting_lambda(evaluated_value)


class SettingsManager:
    def __init__(
        self,
        app_name="Fini",
        app_author="Fini",
        config_path=None,
        base_config_module="fini.managers",
        debug=False
    ):
        self._app_name   = app_name
        self._app_author = app_author
        self._settings = {}
        self._set_listeners = {}
        self._get_listeners = {}
        self._initialised = False
        self._dirty = False
        self._base_config_module = base_config_module
        self._parent_settings_keys = []
        self._debug = debug

        if config_path:
            self.initial_setup(config_path, base_config_module)
    
    def __del__(self):
        if self._dirty:
            if self.get_setting("global.auto_save_on_exit"):
                print("SettingsManager INFO: settings have been modified. Auto saving on exit.")
                self.save_settings()
            else:
                user_input = input('SettingsManager INFO: settings have been modified. Would you like to save the new state? (Y/n): ')
                if not user_input or user_input in ("y", "Y", "yes", "Yes", "true"):
                    self.save_settings()

    @staticmethod
    def version():
        return version.__version__


    @staticmethod
    def generate_empty_base_config(module_name):
        base_config_dir = os.path.dirname(sys.modules[module_name].__file__)
        base_config_abs_path = os.path.join(base_config_dir, "base_config.json")
        base_config = {"settings_abs_path": ""}

        try:
            with open(base_config_abs_path, 'w') as fp:
                json.dump(base_config, fp, sort_keys=False, indent=4)
            return base_config_abs_path
        except Exception as e:
            return None
    

    @staticmethod
    def get_base_config(module_name):
        base_config_dir = os.path.dirname(sys.modules[module_name].__file__)
        base_config_abs_path = os.path.join(base_config_dir, "base_config.json")
        data = open(base_config_abs_path, 'rb').read()
        base_config = json.loads(data)

        return base_config, base_config_abs_path
    

    def initial_setup(self, config_path=None, base_config_module="fini.managers"):
        access_rights = 0o755

        # Get base config dictionry and its absolute path
        base_config, base_config_abs_path = SettingsManager.get_base_config(base_config_module)

        # If the base config's settings_abs_path is empty, then this means that
        # either the application is running for the first time or that there has
        # been some error. Whatever the case this means that we need to generate
        # a directory where the application can store its data.
        if not base_config['config_path']:

            # If user has not supplied any settings path, then suggest the default one
            if not config_path:
                config_path = appdirs.user_config_dir(self._app_name, self._app_author)
            
            print(" Welcome to Fini {}".format(version.__version__))
            print(" Fini needs a place on your system to store files and relevant data.")
            print(" You can either use the default suggested location or enter a new path.")
            print("")

            # Ask user to create directory
            config_path = ask_user_to_create_directory(config_path, access_rights)
            if not config_path:
                raise Exception("There was an error while creating the base config directory. Cannot proceed.")

            # Update the base config dictionary and save on disk. This will be checked 
            # next time the application starts and act as a reference for the settings file.
            base_config['config_path'] = config_path
            print("Rewriting base config file...")
            try:
                with open(base_config_abs_path, 'w') as fp:
                    json.dump(base_config, fp, sort_keys=False, indent=4)
            except:
                raise Exception("There was a problem writing the base config file on disk. Cannot proceed.")

            # # Once the base configuration directory is in place, we can then create 
            # # all other necessary directories and files.
            # self._settings = SettingsManager.get_default_settings(config_path)
        else:
            config_path = base_config['config_path']

            # If the base config exists, make sure that the corresponding path
            # is available on the system. If not, the ask the user to create it.
            if not os.path.exists(config_path):
                print(" The base configuration exists but the path is not set for some reason.")
                print(" Fini needs a place on your system to store files and relevant data.")
                print(" You can either use the default suggested location or enter a new path.")
                config_path = ask_user_to_create_directory(config_path, access_rights)
                if not config_path:
                    raise Exception("There was an error while creating the base config directory. Cannot proceed.")
        
        # At this stage the config_path is available. 
        # We can now check if all directories and files are in place
        # and if not we will create them.
        res = SettingsManager.check_directories_and_files(config_path, access_rights)
        if res != "OK":
            raise Exception("There was an error with {} during intial setup".format(res))
        
        # SettingsManager has been initialised at this point. We must do that here so that 
        # the load_settings call does not fail
        self._initialised = True

        # At this stage all necessary directories and files are in place.
        # We can finally proceed by loading the actual settings.
        settings_file = os.path.join(config_path, "settings.json")
        res = self.load_settings(settings_file)
        if not res:
            raise Exception("There was an error when loading settings from settings.json . Cannot proceed.")

        # Add the manager as listener to the global.config_path setting, so that
        # when and if the user changes the config path, we update the base config
        # accordingly.
        self.add_set_listener_for_setting("global.config_path", self._update_base_config)

        # Generate settings parent keys
        self.generate_settings_parent_keys()


    # Used in providers when generating settings
    def generate_settings_parent_keys(self):
        for key in self._settings.keys():
            if key not in self._parent_settings_keys:
                self._parent_settings_keys.append(key)
    
    def get_settings_parent_keys(self):
        return  self._parent_settings_keys
    
    @staticmethod
    def _update_base_config(smng, setting_path, new_value, old_value, user_data):
        # Get base config dictionary and its absolute path
        base_config, base_config_abs_path = SettingsManager.get_base_config(mng._base_config_module)
        base_config['config_path'] = new_value
        # Update the base config dictionary and save on disk. This will be checked 
        # next time the application starts and act as a reference for the settings file.
        print("Rewriting base config file...")
        try:
            with open(base_config_abs_path, 'w') as fp:
                json.dump(base_config, fp, sort_keys=False, indent=4)
        except:
            raise Exception("There was a problem writing the base config file on disk. Cannot proceed.")

        # We also copy any existing data from the old location to the new one.
        # This way the settings file will be found when the application runs next time.
        print("Copying data from '{}' to '{}' ".format(old_value, new_value))
        SettingsManager.copytree(old_value, new_value)

        # Since this is a big change, we can save the settings here
        # which will also update the manager's status to not dirty
        print("Saving new settings state...")
        smng.save_settings()


    @staticmethod
    def copytree(src, dest):
        import os, shutil
        try:
            shutil.copytree(src, dest)
        # Directories are the same
        except shutil.Error as e:
            print('Directory not copied. Error: %s' % e)
        # Any error saying that the directory doesn't exist
        except OSError as e:
            print('Directory not copied. Error: %s' % e)
    

    @staticmethod
    def check_directories_and_files(config_path, access_rights):
        # Check config directory
        directory = config_path
        if not os.path.exists(directory):
            res = create_directory(directory, access_rights)
            if not res:
                return "Err_ConfigDirectory"

        # Check log directory
        directory = os.path.join(config_path, "log")
        if not os.path.exists(directory):
            res = create_directory(directory, access_rights)
            if not res:
                return "Err_LogDirectory"
        
        # Check cache directory
        directory = os.path.join(config_path, "cache")
        if not os.path.exists(directory):
            res = create_directory(directory, access_rights)
            if not res:
                return "Err_CacheDirectory"
        
        # Check stocks directory
        directory = os.path.join(config_path, "cache", "stocks")
        if not os.path.exists(directory):
            res = create_directory(directory, access_rights)
            if not res:
                return "Err_StocksDirectory"
        
        # Check market directory
        directory = os.path.join(config_path, "cache", "market")
        if not os.path.exists(directory):
            res = create_directory(directory, access_rights)
            if not res:
                return "Err_MarketDirectory"

        # Check settings file
        settings_file = os.path.join(config_path, "settings.json")
        if not os.path.exists(settings_file):
            res = SettingsManager.create_default_settings_file(config_path)
            if not res:
                return "Err_SettingsFile"
        
        # Check stocks cache file
        stocks_file = os.path.join(config_path, "stocks.json")
        if not os.path.exists(stocks_file):
            res = SettingsManager.create_default_cache_stocks(config_path)
            if not res:
                return "Err_StocksFile"
        
        # Check market cache file
        market_file = os.path.join(config_path, "market.json")
        if not os.path.exists(market_file):
            res = SettingsManager.create_default_cache_market(config_path)
            if not res:
                return "Err_MarketFile"
        
        return "OK"


    def add_set_listener_for_setting(self, setting_path, listener, user_data=None):
        if not self._initialised:
            print("The SettingsManager is uninitialised!")
            print("You need to call 'initial_setup' before adding any listeners.")
            return None

        listener_num_args = len(inspect.signature(listener).parameters)
        if listener_num_args !=5:
            print("The supplied listener's funtion signature is wrong.")
            print("A function/method with five input arguments is required.")
            print("A listener function/method will be called as follows:")
            print("\tlistener_function(SettingsManager, setting_path, old_value, new_value, user_data)")
            return None
        
        # First check to see if the setting actually exists.
        current_value = self.get_setting(setting_path)
        if current_value is None:
            if self._debug:
                print("Cannot add set listener because setting '{}' does not exist.".format(setting_path))
            return None
        
        # Check if actual setting already exists as entry in the listeners dictionary.
        # If the entry does not exist, then add it and attach an empty list as value.
        if self._set_listeners.get(setting_path, None) is None:
            self._set_listeners[setting_path] = []
        
        # Finally append the listener to the appropriate setting entry in the
        # listener's dictionary
        self._set_listeners[setting_path].append( {'callback': listener, 'user_data':user_data} )
    

    def add_get_listener_for_setting(self, setting_path, listener, user_data=None):
        if not self._initialised:
            print("The SettingsManager is uninitialised!")
            print("You need to call 'initial_setup' before adding any listeners.")
            return None

        listener_num_args = len(inspect.signature(listener).parameters)
        if listener_num_args !=4 or listener_num_args !=5:
            print("The supplied listener's funtion signature is wrong.")
            print("A function/method with four or five input arguments is required.")
            print("A listener function/method will be called as follows:")
            print("\tlistener_function(SettingsManager, setting_path, current_value, user_data)")
            print("OR")
            print("\tlistener_function(SettingsManager, setting_path, current_value, None, user_data)")
            print("depending on the number of input arguments of the supplied listener function")
            return None
        
        # First check to see if the setting actually exists.
        current_value = self.get_setting(setting_path)
        if current_value is None:
            if self._debug:
                print("Cannot add get listener because setting '{}' does not exist.".format(setting_path))
            return None
        
        # Check if actual setting already exists as entry in the listeners dictionary.
        # If the entry does not exist, then add it and attach an empty list as value.
        if self._get_listeners.get(setting_path, None) is None:
            self._get_listeners[setting_path] = []
        
        # Finally append the listener to the appropriate setting entry in the
        # listener's dictionary
        self._get_listeners[setting_path].append( {'callback': listener, 'user_data':user_data} )


    def load_settings(self, settings_file=None):
        if not self._initialised:
            print("You need to initialise SettingsManager first before calling 'load_settings'")
            print("You can initialise SettingsManager by calling the 'initial_setup' method.")
            return None

        if not settings_file:
            settings_file = self.get_settings_file()

        if settings_file:
            try:
                with open(settings_file , 'r') as fp:
                    self._settings = json.load(fp)
                self._dirty = False
                return settings_file
            except:
                return None
        else:
            return None
    

    def save_settings(self):
        if not self._initialised:
            print("You need to initialise SettingsManager first before calling 'save_settings'")
            print("You can initialise SettingsManager by calling the 'initial_setup' method.")
            return None

        settings_file = self.get_settings_file()
        try:
            with open(settings_file, 'w') as fp:
                json.dump(self._settings, fp, sort_keys=False, indent=4)
        except:
            raise Exception("The was an error when saving settings to {}".format(settings_file))

        # Save the settings makes the file not dirty
        self._dirty = False

        return settings_file


    def reset_settings(self):
        if not self._initialised:
            print("You need to initialise SettingsManager first before calling 'reset_settings'")
            print("You can initialise SettingsManager by calling the 'initial_setup' method.")
            return None

        config_path = self.get_config_path()
        SettingsManager.create_default_settings_file(config_path)
        self.load_settings()
        

    def display_settings(self, root_path=None, style_title=None, style_key=None, style_val=None):
        
        if root_path:
            root_dict = util.misc.DictUtil.get_by_path(self._settings, root_path)
        else:
            root_dict = self._settings      
        
        max_key_length = util.misc.DictUtil.get_max_key_length(root_dict, parent=root_path)
        if not style_title:
            style_title = self.get_setting("global.settings.style_title")
        if not style_key:
            style_key = self.get_setting("global.settings.style_key")
        if not style_val:
            style_val = self.get_setting("global.settings.style_val")
        
        print(screen.Style.RESET_ALL + style_title + "==================================================================================")
        print("{key:^{l}} {val:^50}". format(key="SETTING NAME", l=max_key_length, val="VALUE"))
        print("")
        util.misc.DictUtil.display(
            root_dict, 
            parent=root_path,
            title_msg="SETTINGS", 
            max_key_len=max_key_length,
            style_title=style_title,
            style_key=style_key,
            style_val=style_val
            )
        print(screen.Style.RESET_ALL + style_title + "==================================================================================" + util.screen.Style.RESET_ALL)


    @staticmethod
    def create_default_settings_file(config_path):
        settings_abs_path = os.path.join(config_path, "settings.json")
        settings = SettingsManager.get_default_settings(config_path)
        try:
            with open(settings_abs_path, 'w') as fp:
                json.dump(settings, fp, sort_keys=False, indent=4)
            return settings_abs_path
        except:
            return None

    @staticmethod
    def create_default_cache_stocks(config_path):
        stocks_abs_path = os.path.join(config_path, "stocks.json")
        cache_stocks    = SettingsManager.get_default_cache_stocks()
        try:
            with open(stocks_abs_path, 'w') as fp:
                json.dump(cache_stocks, fp, sort_keys=False, indent=4)
            return stocks_abs_path
        except:
            return None
    
    @staticmethod
    def create_default_cache_market(config_path):
        market_abs_path = os.path.join(config_path, "market.json")
        cache_market    = SettingsManager.get_default_cache_market()
        try:
            with open(market_abs_path, 'w') as fp:
                json.dump(cache_market, fp, sort_keys=False, indent=4)
            return market_abs_path
        except:
            return None

    #================================================
    # Settings getters and setters
    #================================================
    def _reformat_value(self, value):
        ff = re.split("[!\{\}]", value)
        if len(ff) == 2:
            val = ff[1]
            setting_reference = None
        elif len(ff) == 4:
            val = ff[1]
            setting_reference = ff[2]
        else:
            raise Exception("_reformat_value failed with value: {}".format(value))

        if setting_reference:
            extra_value = self.get_raw_setting(setting_reference)
            if type(extra_value) is str:
                if extra_value[0] == "!":
                    extra_value = self._reformat_value(extra_value)
            if not extra_value:
                raise Exception("Setting '{}' does not exist!".format(setting_reference))
            value = "!" + val + extra_value[1:] if extra_value[0] == "!" else extra_value 
    
        return value

    def _evaluate_setting(self, value):
        if type(value) is str and value:
            if value[0] == "!":
                value = self._reformat_value(value)
                return (eval(value[1:]), True)
            else:
                return (value, False)
        else:
            return (value, False)

    def get_setting(self, setting_path, eval_out=False):
        current_value = util.misc.DictUtil.get_by_path(self._settings, setting_path)
        if current_value is None:
            if self._debug:
                print("Setting '{}' does not exist".format(setting_path) )
            return None

        # Notify all get listeners. Call each listener with this object,
        # the setting's path, and the current value
        if self._get_listeners.get(setting_path):
            for listener in self._get_listeners[setting_path]:
                listener_num_args = len(inspect.signature(listener['callback']).parameters)
                if listener_num_args == 5:
                    processed_value = listener['callback'](self, setting_path, current_value, None, listener['user_data'])
                elif listener_num_args == 4:
                    processed_value = listener['callback'](self, setting_path, current_value, listener['user_data'])
                else:
                    raise Exception("Don't know how to call listener")
        else:
            processed_value = None

        # The get listener callback might have processed the current value, 
        # so we need to update it here.
        if processed_value is not None:
            if processed_value != current_value:
                current_value = processed_value

        if eval_out:
            return self._evaluate_setting(current_value)
        else:
            return self._evaluate_setting(current_value)[0]

    def get_raw_setting(self, setting_path):
        try:
            value = util.misc.DictUtil.get_by_path(self._settings, setting_path)
            return value
        except:
            print("Setting '{}' does not exist".format(setting_path) )
            return None

    def set_setting(self, setting_path, value):
        if self.get_setting(setting_path) is None:
            if self._debug:
                print("'set_setting' ERROR: Could not find setting: {}".format(setting_path))
            return None
        
        # Make sure value is a string. If not, make it a string and hope for the best
        if type(value) is not str:
            value = str(value)
        
        old_value, eval_setting = self.get_setting(setting_path, eval_out=True)
        
        if old_value is not None:
            value = convert_value_str_to_type(value)
            if type(old_value) is not type(value):
                print("There is a value mismatch for setting '{}'. Was expecting value of type '{}' and got type '{}'".format(setting_path, type(old_value), type(value)) )
                return None
            if eval_setting:
                eval_value = self._reformat_value(value)
                # Try to evaluate the setting, see if it's correct
                try:
                    eval(eval_value[1:])
                except:
                    print("Setting '{}' is not valid!".format(value) )
                    return None
                if value[0] != "!":
                    value = "!" + value
            util.misc.DictUtil.set_by_path(self._settings, setting_path, value)
        else:
            return None
        
        # Mark settings as dirty. Will need to ask user to save on exit.
        # We mark it here and not at the end of this method, because a listener
        # can potentially perform a save operation, which will mark the state not dirty.
        if old_value != self._evaluate_setting(value)[0]:
            self._dirty = True

        # Notify all listeners. Call each listener with this object,
        # the setting's path, the new value and the old value
        if self._set_listeners.get(setting_path):
            for listener in self._set_listeners[setting_path]:
                if len(inspect.signature(listener['callback']).parameters) == 5:
                    listener['callback'](self, setting_path, old_value, value, listener['user_data'])
                elif len(inspect.signature(listener).parameters) == 4:
                    listener['callback'](self, setting_path, old_value, value)
                elif len(inspect.signature(listener).parameters) == 0:
                    listener['callback']()
                else:
                    raise Exception("Don't know how to call listener")

        return value
    
    def add_setting(self, setting_path, value):
        # First we need to check if the settign already exists.
        try:
            exists = util.misc.DictUtil.get_by_path(self._settings, setting_path)
        except:
            exists = None

        if not exists:
            util.misc.DictUtil.add_by_path(self._settings, setting_path, value)
            
            # Mark settings as dirty
            self._dirty = True

            return value
        else:
            if self._debug:
                print("Setting '{}' already exists!". format(setting_path))

            return None

    #================================================
    # Path related getter functions
    #================================================
    def get_config_path(self):
        return self.get_setting('global.config_path')

    def get_log_path(self):
        return os.path.join(self.get_config_path(), "log")

    def get_cache_path(self):
        return os.path.join(self.get_config_path(), "cache")

    def get_stocks_path(self):
        return os.path.join(self.get_config_path(), "cache", "stocks")
    
    def get_market_path(self):
        return os.path.join(self.get_config_path(), "cache", "market")

    def get_settings_file(self):
        return os.path.join(self.get_config_path(), "settings.json")

    def get_cache_stocks_file(self):
        return os.path.join(self.get_config_path(), "stocks.json")
    
    def get_cache_market_file(self):
        return os.path.join(self.get_config_path(), "market.json")

    def get_cmd_history_file(self):
        return os.path.join(self.get_config_path(), "fini_prompt_history")
    
    @staticmethod
    def get_default_settings(base_config=None):
        return {
            'version': version.__version__,
            #=====================================================
            # Global settings
            #=====================================================
            'global': {
                'prompt': {
                    'colour': "ff0000",
                    'cmd_colour': "ff8400",
                    'message': "fini >> ",
                },
                'settings': {
                    'style_title': "!Fore.BLUE + Style.BRIGHT",
                    'style_key': "!Fore.CYAN + Style.BRIGHT",
                    'style_val': "!Fore.GREEN + Style.BRIGHT",
                },
                'progressbar': {
                    'style': {
                        'bar': "!Fore.CYAN + Style.BRIGHT + {gfx.app_background}",
                        'desc': "!Fore.CYAN + Style.BRIGHT + {gfx.app_background}",
                        'uptick': "!Fore.GREEN + Style.BRIGHT + {gfx.app_background}",
                        'ticker': "!Fore.YELLOW + Style.BRIGHT + {gfx.app_background}",
                    },
                    'uptick_symbol': "\u2713",
                    'ascii': False,
                    'dynamic_ncols': True,
                },
                'config_path': base_config if base_config else "",
                'auto_save_on_exit': False, 
            },

            #=====================================================
            # Time settings
            #=====================================================
            'time' : {
                'timezone': util.time.get_local_timezone_as_string(),
                'datetime_format': "%b %d, %Y %I:%M %p %Z",
            },

            #=====================================================
            # Stock settings
            #=====================================================
            'stock' :{
                'cache_update_period_sec': 300, 
            },

            #=====================================================
            # Graphics settings
            #=====================================================
            'gfx' : {
                'app_background': "!Back.BLACK",
                'style': { 
                    'panel_background': "!Back.MAGENTA",
                    'empty_line':     "!{gfx.style.panel_background}",
                    'header':         "!Fore.YELLOW + Style.BRIGHT + Back.BLUE",
                    'header_light':   "!Fore.YELLOW + Style.NORMAL + Back.BLUE",
                    'key':            "!Fore.CYAN   + Style.NORMAL + {gfx.style.panel_background}",
                    'key_2':          "!Fore.CYAN   + Style.BRIGHT + {gfx.style.panel_background}",
                    'value':          "!Fore.WHITE  + Style.NORMAL + {gfx.style.panel_background}",
                    'value_positive': "!Fore.GREEN  + Style.BRIGHT + {gfx.style.panel_background}",
                    'value_negative': "!Fore.RED    + Style.NORMAL + {gfx.style.panel_background}",
                    'logo':           "!Fore.YELLOW + Style.BRIGHT + {gfx.style.panel_background}",
                },
            },
        }

    @staticmethod
    def get_default_cache_stocks():
        #=====================================================
        # Stocks cache
        #=====================================================
        return {
            'last_updated': util.time.get_datetime_now_as_string(),

            'qcom': {
                'zacks': {
                    'last_updated': "Nov 15, 2020 04:00 PM UTC",
                    'Nov 13, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 14, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 15, 2020 04:00 PM UTC': 'path/to/report',
                },
                'finviz': {
                    'last_updated': "Nov 15, 2020 04:00 PM UTC",
                    'Nov 13, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 14, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 15, 2020 04:00 PM UTC': 'path/to/report',
                },
                'marketbeat' : {
                    'last_updated': "Nov 15, 2020 04:00 PM UTC",
                    'Nov 13, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 14, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 15, 2020 04:00 PM UTC': 'path/to/report',
                },
                'earningswhispers' : {
                    'last_updated': "Nov 15, 2020 04:00 PM UTC",
                    'Nov 13, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 14, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 15, 2020 04:00 PM UTC': 'path/to/report',
                },
                'yahoo': {
                    'last_updated': "Nov 15, 2020 04:00 PM UTC",
                    'Nov 13, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 14, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 15, 2020 04:00 PM UTC': 'path/to/report',
                },
                'nasdaq': {
                    'last_updated': "Nov 15, 2020 04:00 PM UTC",
                    'Nov 13, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 14, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 15, 2020 04:00 PM UTC': 'path/to/report',
                },
                'seekingalpha' :{
                    'last_updated': "Nov 15, 2020 04:00 PM UTC",
                    'Nov 13, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 14, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 15, 2020 04:00 PM UTC': 'path/to/report',
                }
            },
            'amd': {
                'zacks': {
                    'last_updated': "Nov 15, 2020 04:00 PM UTC",
                    'Nov 13, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 14, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 15, 2020 04:00 PM UTC': 'path/to/report',
                },
                'finviz': {
                    'last_updated': "Nov 15, 2020 04:00 PM UTC",
                    'Nov 13, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 14, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 15, 2020 04:00 PM UTC': 'path/to/report',
                },
                'marketbeat' : {
                    'last_updated': "Nov 15, 2020 04:00 PM UTC",
                    'Nov 13, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 14, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 15, 2020 04:00 PM UTC': 'path/to/report',
                },
                'earningswhispers' : {
                    'last_updated': "Nov 15, 2020 04:00 PM UTC",
                    'Nov 13, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 14, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 15, 2020 04:00 PM UTC': 'path/to/report',
                },
                'yahoo': {
                    'last_updated': "Nov 15, 2020 04:00 PM UTC",
                    'Nov 13, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 14, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 15, 2020 04:00 PM UTC': 'path/to/report',
                },
                'nasdaq': {
                    'last_updated': "Nov 15, 2020 04:00 PM UTC",
                    'Nov 13, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 14, 2020 04:00 PM UTC': 'path/to/report',
                    'Nov 15, 2020 04:00 PM UTC': 'path/to/report',
                },
            },
        }

    @staticmethod
    def get_default_cache_market():
        return {
            'last_updated': util.time.get_datetime_now_as_string(),
            #=====================================================
            # Market cache
            #=====================================================
            'market': {
            }
        }