import os, operator, json, copy
from abc import ABC, abstractmethod
from functools import reduce  # forward compatibility for Python 3
from tqdm import tqdm
from . import pprinter
from . import settings
from . import wview
from .. import util

__all__ = ['ProviderManager']

class url_ctx:
    def __init__(self, provider):
        self._provider = provider
        self._debug    = provider._debug
        self._url      = []
        self._num_urls = 0
        self._count    = 0
        self._ticker   = ""

    def add_url(self, url, parser_callback):
        exists = False
        for eurl in self._url:
            if url == eurl[0]:
                exists = True
        
        if not exists:
            self._url.append( (url, parser_callback) )
            self._num_urls += 1

    def __call__(self, ticker):
        self._ticker = ticker
        return self

    def __iter__(self):
        return self 

    def __next__(self):
        if not self._ticker:
            print("You need to call the iterator using a ticker symbol!")
            raise StopIteration
        if self._count == self._num_urls:
            self._count = 0
            raise StopIteration
        
        url    = self._url[self._count][0].format(ticker=self._ticker)
        parser = self._url[self._count][1]
        self._count += 1

        return url, parser

class provider_data_ctx:
    def __init__(self, debug=False):
        self._debug    = debug
        self._data     = {
            "num_records": 0,
            "active_record": 0,
        }

    def add_entry(self, path, value):
        util.misc.DictUtil.add_by_path(self._data, path, value)
    
    def get_data(self, path):
        return util.misc.DictUtil.get_by_path(self._data, path)
    
    def set_data(self, path, new_value):
        dict_value = util.misc.DictUtil.get_by_path(self._data, path)
        if dict_value is not None:
            if type(dict_value) is list:
                dict_value.append(new_value)
            elif type(dict_value) is dict:
                raise Exception("Cannot deal with dictionary values yet!")
            else:
                util.misc.DictUtil.set_by_path(self._data, path, new_value)
        else:
            raise Exception("Key '{}' does not exist!". format(path))

    def data_ref(self):
        return self._data
    
    def data_copy(self):
        return json.loads( json.dumps(self._data) )

    def load_data(self, data):
        # Thread safe alternative to copy.deepcopy
        self._data = json.loads( json.dumps(data) )


class ProviderBase(ABC):
    def __init__(self, settings_manager, cache_manager, webview_manager, debug=False):
        # Managers
        self._smng = settings_manager
        self._cmng = cache_manager
        self._wmng = webview_manager

        # Internal variables
        self._provider_id = self.provider_id()
        self._ticker_data = {}
        self._cmd = {}
        self._pos_x = 0
        self._pos_y = 1
        self._debug = debug

        # Context data structures
        self._uctx = url_ctx(provider=self)
        self._data = provider_data_ctx(debug=debug)
        self._opts = settings.settings_ctx(provider=self)
        self._dctx = pprinter.draw_ctx(provider=self, dims=(None, None))
        self._wctx = wview.webview_ctx(provider=self)

        # Populate context data structures
        self.generate_URL_ctx(self._uctx, self)
        self.generate_data(self._data)
        self.generate_settings(self._opts)
        self.generate_draw_ctx(self._dctx)
        self.generate_webview_ctx(self._wctx)
        
        # Validate panels
        self._validate_panels()
        
        # Validate views
        self._validate_views()

        # Create webviews for this provider
        self._create_webviews()

    def _validate_panels(self):
        for panel_name, panel in self._dctx._panels.items():
            pprinter.validate_panel(panel_name, panel, debug=self._debug)
            self._cmd[panel_name] = pprinter.generate_draw_commands(self.provider_id(), panel, self._opts,  debug=self._debug)

    def _validate_views(self):
        for view_name, view in self._dctx._views.items():
            pprinter.validate_view(view_name, view, debug=self._debug) 

    def update_draw_ctx(self, smng, setting_path, new_value, old_value, user_data=None):
        self._opts.update_settings()
        self._validate_panels()
        self._validate_views()
        return new_value

    def _create_webviews(self):
        for webview_data in self._wctx("create"):
            self._wmng.process(webview_data)

    def debug(self, debug=True):
        self._debug       = debug
        self._uctx._debug = debug 
        self._data._debug = debug 
        self._opts._debug = debug 
        self._dctx._debug = debug 
        self._wctx._debug = debug 

    @staticmethod
    @abstractmethod
    def provider_id():
        return ""

    @staticmethod
    @abstractmethod
    def generate_URL_ctx(uctx, provider):
        pass

    @staticmethod
    @abstractmethod
    def generate_data():
        return {}
    
    @staticmethod
    @abstractmethod
    def generate_settings(settings):
        pass

    @staticmethod
    @abstractmethod
    def generate_draw_ctx(ctx):
        pass
    
    @staticmethod
    @abstractmethod
    def generate_webview_ctx(ctx):
        pass

    def stock_data_ref(self):
        return self._data.data_ref()

    def stock_data_copy(self):
        return self._data.data_copy()
    
    def stock_data_dict_ref(self, ticker):
        return self._ticker_data[ticker].data_ref()

    def stock_data_dict_copy(self, ticker):
        return self._ticker_data[ticker].data_copy()
        
    def get_panel_data(self, item):
        return util.misc.DictUtil.get_by_path(self._dctx._panels, item)
    
    def set_panel_data(self, item, value):
        return util.misc.DictUtil.set_by_path(self._dctx._panels, item, value)
    
    def get_view_data(self, item):
        return util.misc.DictUtil.get_by_path(self._dctx._views, item)
    
    def set_view_data(self, item, value):
        return util.misc.DictUtil.set_by_path(self._dctx._views, item, value)

    def get_terminal_size(self):
        x, y = os.get_terminal_size()
        return x, y

    def reset_pos(self):
        self._pos_x = 0
        self._pos_y = 0

    def draw_view(self, view_name=None, pos_x=None, pos_y=None):
        # Get first view in dictionary if no view_name is provided
        if not view_name:
            view_name = next( iter( self._dctx._views.keys() ) )

        # Check to see if view exists
        if not self._dctx._views.get(view_name, None):
            raise Exception("View {} does not exist!".format(view_name))
        
        # Get terminal size
        term_x, term_y = os.get_terminal_size()

        # Get view
        view = self._dctx._views[view_name]

        # Get current x,y position
        cpos_x = pos_x if pos_x else self._pos_x
        cpos_y = pos_y if pos_y else self._pos_y

        # If next view draw exceeds the terminal height
        # then make some space by scrolling down, before drawing
        if cpos_y + view["height"]  > term_y:
            util.screen.move_cursor( term_y - 4 )
            print(util.screen.Style.RESET_ALL + util.screen.pos(0, 0))
            cpos_y = 1

        # Draw each panel in the view
        for panel_name, panel in view["panels"].items():
            width  = panel["width"]
            height = panel["height"]
            ppos_x  = panel["pos_x"]
            ppos_y  = panel["pos_y"]
            self.draw_panel(panel_name, width, height, cpos_x + ppos_x, cpos_y + ppos_y)

        cpos_x = 0
        cpos_y += view["height"]

        self._pos_x = cpos_x
        self._pos_y = cpos_y

        return cpos_x, cpos_y
    
    def draw_panel(self, panel_name, width, height, pos_x, pos_y):
        # Check to see if panel exists
        if not self._dctx._panels.get(panel_name, None):
            raise Exception("Panel {} does not exist!".format(panel_name))

        # Get drawing commands for this panel
        draw_cmds = self._cmd[panel_name]

        # Draw panel
        for cmd in draw_cmds:
            cmd(pos_x, pos_y, self._data._data)

    def _webview_process_impl(self, wctx, ticker_list):
        pass
    
    def webview_process(self, command="update", ticker="AMD"):
        ticker_list = []
        return_data = True

        if type(ticker) is str:
            ticker_list.append(ticker)
        elif type(ticker) is list:
            ticker_list = ticker
        elif type(ticker) is None:
            return_data = False
        else:
            raise Exception("'ticker' input must be either of type 'str' or 'list'. Type {} was given".format(type(ticker))) 

        # Update the html data dictionary as necessary
        self._webview_process_impl(self._wctx, ticker_list)

        # Update webviews for this provider
        for webview_data in self._wctx(command, data=return_data):
            self._wmng.process(webview_data)

    def process(self, ticker):
        # This method processes a list of ticker symbols in one go. We keep all 
        # the extracted data in an internal dictionary, which is cleared next
        # time this method is processed.
        
        ticker_list = []

        if type(ticker) is str:
            ticker_list.append(ticker)
        elif type(ticker) is list:
            ticker_list = ticker
        else:
            raise Exception("'ticker' input must be either of type 'str' or 'list'. Type {} was given".format(type(ticker))) 

        # # Check to see if internal cache is large. If that is the case, 
        # # clear it before continuing.
            # if get_size(self._ticker_data) > self._smng._get_setting("global.cache_max_size"):
            #     self._ticker_data.clear()

        uptick_symbol       = self._smng.get_setting("global.progressbar.uptick_symbol")
        ascii_              = self._smng.get_setting("global.progressbar.ascii")
        dynamic_ncols       = self._smng.get_setting("global.progressbar.dynamic_ncols")
        bar_style           = pprinter.Style.RESET_ALL + self._smng.get_setting("global.progressbar.style.bar")
        desc_style          = pprinter.Style.RESET_ALL + self._smng.get_setting("global.progressbar.style.desc")
        uptick_symbol_style = pprinter.Style.RESET_ALL + self._smng.get_setting("global.progressbar.style.uptick") 
        ticker_style        = pprinter.Style.RESET_ALL + self._smng.get_setting("global.progressbar.style.ticker")
        
        if len(uptick_symbol) > 1 :
            uptick_symbol = uptick_symbol[0]
        
        #================================================================
        # Deal with webviews
        #================================================================
        # Update the html data dictionary as necessary
        self._webview_process_impl(self._wctx, ticker_list)

        # # Update webviews for this provider
        for webview_data in self._wctx("load_html"):
            self._wmng.process(webview_data)

        # Deal with CLI views
        util.screen.hide_cursor()
        for ticker_symbol in tqdm(
            ticker_list, 
            # desc=tick_symbol_style + "\u2713 " + desc_style + "Downloaded data from '{}' provider".format(self._provider_id) + bar_style,
            desc=uptick_symbol_style + uptick_symbol + " " + desc_style + "Downloaded data from '{}' provider".format(self._provider_id) + bar_style,
            ascii=ascii_,
            dynamic_ncols=dynamic_ncols,
            ):
            if ticker_symbol not in self._ticker_data:
                # Load stock data for this provider and ticker_symbol
                cached_data = self._cmng.load_stock_data( self, ticker_symbol)

                # Copy cached data to internal data dictionary
                # self._ticker_data[ticker_symbol] = copy.deepcopy(self._data)
                self._ticker_data[ticker_symbol] = self._data
                self._ticker_data[ticker_symbol].load_data(cached_data)

            # Get website data, parse it and store it in internal data dictionary
            print("\r" + desc_style + "Downloading" + ticker_style + "{:^7s}".format(ticker_symbol) + desc_style, end="")
            res = None
            for URL, parser in self._uctx(ticker_symbol):
                website_data = util.web.get_URL_data(URL)
                res = parser(URL, website_data, self._ticker_data[ticker_symbol])

            # Increase number of records and active record entries in data
            if res is not None:
                self._ticker_data[ticker_symbol]._data["num_records"] += 1
                self._ticker_data[ticker_symbol]._data["active_record"] = self._ticker_data[ticker_symbol]._data["num_records"] - 1

            # Save new extracted data
            self._cmng.save_stock_data_dict( self, ticker_symbol)
        
        print(pprinter.Style.RESET_ALL, end="")
        util.screen.show_cursor()


class ProviderManager:
    def __init__(self, settings_manager, debug=False):
        self._smng  = settings_manager
        self._providers = {}
        self._debug = debug
        
        # Check external providers directory
        self._check_external_providers()

        # Add available providers to internal dictionary
        self.instantiate_all_providers()

    def instantiate_all_providers(self):
        from .. import get_providers
        providers_temp = get_providers( self._smng.get_setting("global.external_providers_directory") )
        for provider_name, provider in providers_temp.items():
            if not self._providers.get(provider_name):
                if self._debug:
                    print("Registering provider {}".format(provider_name))
                self._providers[provider_name] = provider[1]( settings_manager=self._smng )
                self.register_with_all_style_settings( self._providers[provider_name] )

    def register_with_all_style_settings(self, provider):
        for key in self._smng._settings["gfx"]["style"].keys():
            setting_path = ".".join( ["gfx", "style", key] )
            self._smng.add_set_listener_for_setting(setting_path, provider.update_draw_ctx, user_data=None)

    def _check_external_providers(self):
        # First check to see if the setting is available already. If not, create it and 
        # save the new settings state.
        if not self._smng.get_setting("global.external_providers_directory"):
            # Add the default directory as new setting in settings manager.
            self._smng.add_setting(
                "global.external_providers_directory",
                os.path.join(self._smng.get_config_path(), "providers")
            )

            # Save settings state
            self._smng.save_settings()
        
        # At this stage the external providers directory exists as a setting, so now
        # we need to make sure that the physical directory exists. If not we need to
        # create it here.
        directory = self._smng.get_setting("global.external_providers_directory")
        access_rights = 0o755
        try:
            if not os.path.exists(directory):
                res = create_directory(directory, access_rights)
        except:
            print("There was an error while creating '{}'".format(directory))
            directory = None
        
        # Add listener for 'global.external_providers_directory' setting
        if directory:
            self._smng.add_set_listener_for_setting("global.external_providers_directory", self._update_external_providers_directory, self)
        else:
            # If there was an error creating the directory in the previous step, 
            # then set the value of the setting to an empty string (i.e None)
            self._smng.set_setting("global.external_providers_directory", "")
    

    @staticmethod
    def _update_external_providers_directory(smng, setting_path, new_value, old_value, user_data):
        if smng._debug:
            print("User updated the external providers path")

        # Create the new directory
        access_rights = 0o755
        directory = new_value
        try:
            if not os.path.exists(directory):
                res = create_directory(directory, access_rights)
        except:
            raise Exception("There was an error while creating '{}'".format(directory))

        try:
            # Copy any existing data from the old location to the new one.
            print("Copying data from '{}' to '{}' ".format(old_value, new_value))
            smng.copytree(old_value, new_value)

            # Since this is a big change, we can save the settings here
            # which will also update the manager's status to not dirty
            print("Saving new settings state...")
            smng.save_settings()
        except:
            raise Exception("There was an error while copying from '{}' to '{}'".format(old_value, directory))

    def display_providers(self):
        print("=================================================================")
        print("Number of available providers: {}\n".format(len(self._providers)))
        for idx, provider in enumerate(self._providers.values()):
            print("\tProvider {:<3}: {}".format(idx+1, provider[0]) )
        print("\n=================================================================\n")


def data_parser(args):
    import ipdb; ipdb.set_trace()
    #=========================================
    # Get list of data providers
    #=========================================
    # At this stage the user has requested to get information for, potentally,
    # several companies and from several data providers.

    # First of all, we need to get a list of all the data providers that the user 
    # has requested.
    data_providers = get_list_of_data_providers(args)

    #=========================================
    # For each ticker symbol
    #=========================================
    # Then ,for each ticker symbol we need to do the following:
    cur_i = 0
    cur_y = 1
    for tik in args.ticker_symbols:
        
        #=========================================
        # For each data provider
        #=========================================
        for provider in data_providers:
            # First check if the information requested by a particular provider is in the cache. 
            #
            # 1.) If the information is in the cache, then do the following:
            #     * check to see if the cache report is outdated:
            #       - If the cached report is outdated, retrieve a new report from the provider
            #       - If the cached report is not outdated, then show that to the user.
            # If the information requested is not in the cache, retrieve a new report from the provider.

            #=========================================
            # Check if report is in cache
            #=========================================
            

            #=========================================
            # Retrieve report
            #=========================================
            # Get URL of ticker
            # URL = zacks.create_URL_stock(tik)
            URL = provider.create_URL_stock(tik)

            # Get data from URL
            web_data = util.web.get_URL_data(URL)

            # Parse website data
            # parsed_data = zacks.website_parser_stock(web_data)
            stock_data = provider.website_parser_stock(web_data)

            #=========================================
            # Save report into cache
            #=========================================

            #=========================================
            # Print report to screen
            #=========================================
            # Once a report has been generated (either by retrieving it from the provider or the cache)
            # we need to print it on screen.

            # Print main title using ticker symbol
            start_x  = util.font.find_starting_pos_for_ticker_title(tik.upper())
            _, cur_y = util.font.print_using_font(tik.upper(), start_x, cur_y, data_formatter.format_tik_font)

            # Print data and get height of row
            # row_y = zacks.format_stock(parsed_data, zacks.logo, 0, cur_y)
            row_y = provider.format_stock(stock_data, provider.logo, 0, cur_y)
            cur_y += row_y

            #=========================================
            # Update screen to make room if necessary
            #=========================================
            # Check to see if next row exceeds the terminals height. If that is the case, 
            # we make sure to make some room before printing the next row
            if (cur_y + row_y) > term_y:
                util.screen.move_cursor(term_y)
                print(util.screen.pos(0, 0) + util.screen.Style.RESET_ALL)
                cur_y = 1
