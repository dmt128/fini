import os, sys, json, operator, ast, inspect, pkgutil, appdirs, colorama
from functools import reduce  # forward compatibility for Python 3
from .. import util
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


class SettingsManager:
    def __init__(self,
        app_name="Fini",
        app_author="Fini",
        settings_abs_path=None,
        base_config_module="fini.settings",
    ):
        self._app_name   = app_name
        self._app_author = app_author
        self._settings = {}
        self._listeners = {}
        self._initialised = False
        self._dirty = False

        if settings_abs_path:
            self.initial_setup(settings_abs_path, base_config_module)
    
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
    

    def initial_setup(self, config_path=None, base_config_module="fini.settings"):
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
            import ipdb; ipdb.set_trace()
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
        
        # At this stage all necessary directories and files are in place.
        # We can finally proceed by loading the actual settings.
        
        settings_file = os.path.join(config_path, "settings.json")
        res = self.load_settings(settings_file)
        if not res:
            raise Exception("There was an error when loading settings from settings.json . Cannot proceed.")

        self._initialised = True

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


    def add_listener_for_setting(self, setting_path, listener):
        if not self._initialised:
            print("The SettingsManager is uninitialised!")
            print("You need to call 'initial_setup' before adding any listeners.")
            return None

        if len(inspect.signature(listener).parameters) !=4:
            print("The supplied listener's funtion signature is wrong.")
            print("A function/method with four input arguments is required.")
            print("A listener function/method will be called as follows:")
            print("\tlistener_function(SettingsManager, setting_path, new_value, old_value)")
            return None
        
        # First check to see if the setting actually exists.
        old_value = self.get_setting(setting_path)
        if old_value is None:
            return None
        
        # Check if actual setting already exists as entry in the listeners dictionary.
        # If the entry does not exist, then add it and attach an empty list as value.
        if not self._listeners.get(setting_path):
            self._listeners[setting_path] = []
        
        # Finally append the listener to the appropriate setting entry in the
        # listener's dictionary
        self._listeners[setting_path].append(listener)
            


    def load_settings(self, settings_file=None):
        try:
            with open(settings_file , 'r') as fp:
                self._settings = json.load(fp)
            return settings_file
        except:
            return None
    

    def save_settings(self):
        if not self._initialised:
            print("You need to initialise SettingsManager first before calling 'save_settings'")
            print("You can initialise SettingsManager by calling the 'initial_setup' method.")
            return None

        settings_file = self.get_setting("global.path.settings_file")
        try:
            with open(settings_file, 'w') as fp:
                json.dump(self._settings, fp, sort_keys=False, indent=4)
        except:
            raise Exception("The was an error when saving settings to {}".format(settings_file))
        
        return settings_file


    def display_settings(self):
        print(util.screen.Style.RESET_ALL + util.screen.Fore.CYAN + util.screen.Style.BRIGHT + "==================================================================================")
        print("{:^30} {:^50}". format("SETTING", "VALUE"))
        print("")
        SettingsManager._display_settings(self._settings)
        print("==================================================================================" + util.screen.Style.RESET_ALL)


    @staticmethod
    def _display_settings(dictionary, parent=None):
        for key, value in dictionary.items():
            if type(value) is dict:
                if parent:
                    SettingsManager._display_settings(value, parent + "." + key)
                else:
                    SettingsManager._display_settings(value, key)
            else:
                # import ipdb; ipdb.set_trace()
                if parent:
                    key = parent + "." + key
                print(util.screen.Style.RESET_ALL + util.screen.Fore.CYAN + util.screen.Style.BRIGHT + "{:<30}: {}". format(key, value))


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
    def get_setting(self, setting_path):
        try:
            value = SettingsManager._get_by_path(self._settings, setting_path.split("."))
        except:
            print("Setting '{}' does not exist".format(setting_path) )
            return None
        
        return value

    def set_setting(self, setting_path, value):
        old_value = self.get_setting(setting_path)
        if old_value is None:
            return None
        else:
            value = convert_value_str_to_type(value)
            SettingsManager._set_by_path(self._settings, setting_path.split("."), value)
        
        # Notify all listeners. Call each listener with this object,
        # the setting's path, the new value and the old value
        if self._listeners.get(setting_path):
            for listener in self._listeners[setting_path]:
                listener(self, setting_path, value, old_value)

        # Mark settings as dirty. Will need to ask user to save on exit
        self._dirty = True

        return value
    
    #================================================
    # Functions to deal with nested dictionaries
    #================================================
    # As described in https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
    @staticmethod
    def _get_by_path(root, items):
        """Access a nested object in root by item sequence."""
        return reduce(operator.getitem, items, root)

    @staticmethod
    def _set_by_path(root, items, value):
        """Set a value in a nested object in root by item sequence."""
        SettingsManager._get_by_path(root, items[:-1])[items[-1]] = value

    @staticmethod
    def _del_by_path(root, items):
        """Delete a key-value in a nested object in root by item sequence."""
        del SettingsManager._get_by_path(root, items[:-1])[items[-1]]

    #================================================
    # Path related getter functions
    #================================================
    def get_config_path(self):
        return self.get_setting('global.path.config')

    def get_log_path(self):
        return self.get_setting('global.path.log')

    def get_cache_path(self):
        return self.get_setting('global.path.cache')

    def get_stocks_path(self):
        return self.get_setting('global.path.stocks')
    
    def get_market_path(self):
        return self.get_setting('global.path.market')

    def get_settings_file(self):
        return self.get_setting('global.path.settings_file')

    def get_cache_stocks_file(self):
        return self.get_setting('global.path.stocks_file')
    
    def get_cache_market_file(self):
        return self.get_setting('global.path.market_file')

    def get_cmd_history_abs_path(self):
        return self.get_setting('global.path.prompt_history')
    
    @staticmethod
    def get_default_settings(base_config=None):
        return {
            'version': version.__version__,
            #=====================================================
            # Global settings
            #=====================================================
            'global': {
                'prompt': {
                    'colour': "#ff0000",
                    'cmd_colour': "#ff8400",
                    'message': "fini >> ",
                }, 
                'path' : {
                    'config': base_config if base_config else "",
                    'log': os.path.join(base_config, "log") if base_config else "",
                    'cache': os.path.join(base_config, "cache") if base_config else "",
                    'stocks': os.path.join(base_config, "cache", "stocks") if base_config else "",
                    'market': os.path.join(base_config, "cache", "market") if base_config else "",
                    'settings_file': os.path.join(base_config, "settings.json") if base_config else "",
                    'stocks_file': os.path.join(base_config, "stocks.json") if base_config else "",
                    'market_file': os.path.join(base_config, "market.json") if base_config else "",
                    'prompt_history': os.path.join(base_config, "fini_prompt_history") if base_config else "",
                },
                'auto_save_on_exit': False,  
            },

            #=====================================================
            # Time settings
            #=====================================================
            'time' : {
                "timezone": util.time.get_local_timezone_as_string(),
                "datetime_format": "%b %d, %Y %I:%M %p %Z",
            },

            #=====================================================
            # Stock settings
            #=====================================================
            'stock' :{
                "cache_update_period_sec": 300, 
            },

            #=====================================================
            # Graphics settings
            #=====================================================
            'gfx' : {

            }
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