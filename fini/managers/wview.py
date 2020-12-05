import atexit, argparse, re, webview, copy
from multiprocessing import Process, Queue
from .. import util

__all__ = [
    'WebviewManager'
]

class webview_ctx:
    class __webview_proxy:
        def __init__(self, parent, webview_id):
            self._parent     = parent
            self._webview_id = webview_id
            self._webview    = parent._webviews[webview_id]
            self._provider   = parent._provider
            self._smng       = parent._smng
            self._debug      = parent._debug

        def add_setting(
            self, 
            key, 
            value,
            set_callback=None, 
            set_user_data=None,
            get_callback=None, 
            get_user_data=None,
        ):
            full_key = self._parent._create_full_settings_key(self._webview_id, key)
            self._smng.add_setting(
                full_key, 
                value,
                set_callback=set_callback, 
                set_user_data=set_user_data,
                get_callback=get_callback, 
                get_user_data=get_user_data,
            )
        
        def add_html_data_setting(
            self, 
            key, 
            value, 
            set_callback=None, 
            set_user_data=None,
            get_callback=None, 
            get_user_data=None,
        ):
            full_key = self._parent._create_full_html_data_key(self._webview_id, key)
            
            # if not set_callback:
            #     set_callback  = self._update_html_data_setting
            #     set_user_data = self

            self._smng.add_setting(
                full_key, 
                value,
                set_callback=set_callback, 
                set_user_data=set_user_data,
                get_callback=get_callback, 
                get_user_data=get_user_data,
            )

        def _update_html_data_setting(self, smng, setting_path, old_value, new_value, wctx):
            keys = setting_path.split(".")
            wctx_key = ".".join( [keys[2], keys[3], keys[4]] )
            util.misc.DictUtil.set_by_path(wctx._webviews, wctx_key, new_value)

        def set_html_data_setting(self, key, value):
            full_key = self._parent._create_full_html_data_key(self._webview_id, key)
            self._smng.set_setting(full_key, value)

    def __init__(self, provider):
        self._provider    = provider
        self._smng        = provider._smng
        self._wmng        = provider._wmng
        self._debug       = provider._debug
        self._webviews    = {}
        self._reset       = True
        self._iter        = None
        self._command     = None
        self._return_data = True

    def _create_full_settings_key(self, window_id, key):
        return ".".join(
            [
                self._provider.provider_id(),
                "webview",
                window_id,
                key
            ]
        )

    def _create_full_html_data_key(self, window_id, key):
        return ".".join(
            [
                self._provider.provider_id(),
                "webview",
                window_id,
                "html_data",
                key
            ]
        )
    
    def _create_root_provider_webview_path(self, window_id):
        return ".".join(
            [
                self._provider.provider_id(),
                "webview",
                window_id
            ]
        )
        
    def add_webview(
        self,
        window_id,
        window_title, 
        url="",
        html="",
        url_callback=None,
        html_callback=None,
        js_api=None,
        size=(600, 500),
        position=(0, 0),
        min_size=(200, 100),
        resizable=True,
        fullscreen=False,
        hidden=False,
        frameless=False,
        easy_drag=True,
        minimized=False,
        on_top=False,
        confirm_close=False,
        background_color='#FFFFFF',
        transparent=False, 
        text_select=False,
        debug=False,
    ):
        if self._webviews.get(window_id, None) is None:
            self._webviews[window_id] = {}
            self._webviews[window_id]['window_id']     = self._create_root_provider_webview_path(window_id)
            self._webviews[window_id]['url_callback']  = url_callback
            self._webviews[window_id]['html_callback'] = html_callback
            
            # Add webview options to global settings
            webview_id_key       = self._create_full_settings_key(window_id, "webview_id")
            window_title_key     = self._create_full_settings_key(window_id, "window_title")
            url_key              = self._create_full_settings_key(window_id, "url") 
            html_key             = self._create_full_settings_key(window_id, "html")
            js_api_key           = self._create_full_settings_key(window_id, "js_api")
            size_key             = self._create_full_settings_key(window_id, "size")
            position_key         = self._create_full_settings_key(window_id, "position")
            min_size_key         = self._create_full_settings_key(window_id, "min_size")
            resizable_key        = self._create_full_settings_key(window_id, "resizable")
            fullscreen_key       = self._create_full_settings_key(window_id, "fullscreen")
            hidden_key           = self._create_full_settings_key(window_id, "hidden")
            frameless_key        = self._create_full_settings_key(window_id, "frameless")
            easy_drag_key        = self._create_full_settings_key(window_id, "easy_drag")
            minimized_key        = self._create_full_settings_key(window_id, "minimized")
            on_top_key           = self._create_full_settings_key(window_id, "on_top")
            confirm_close_key    = self._create_full_settings_key(window_id, "confirm_close")
            background_color_key = self._create_full_settings_key(window_id, "background_color")
            transparent_key      = self._create_full_settings_key(window_id, "transparent") 
            text_select_key      = self._create_full_settings_key(window_id, "text_select")
            debug_key            = self._create_full_settings_key(window_id, "debug")

            self._smng.add_setting( webview_id_key, ".".join( [self._provider.provider_id(), window_id]), set_callback=self._webview_id_set_callback )        
            self._smng.add_setting( window_title_key, window_title )  
            self._smng.add_setting( url_key, url)     
            self._smng.add_setting( html_key, html )   
            self._smng.add_setting( js_api_key, js_api )
            self._smng.add_setting( size_key, size )
            self._smng.add_setting( position_key, position ) 
            self._smng.add_setting( min_size_key, min_size )             
            self._smng.add_setting( resizable_key, resizable )        
            self._smng.add_setting( fullscreen_key, fullscreen )       
            self._smng.add_setting( hidden_key, hidden )           
            self._smng.add_setting( frameless_key, frameless )        
            self._smng.add_setting( easy_drag_key, easy_drag )        
            self._smng.add_setting( minimized_key, minimized )        
            self._smng.add_setting( on_top_key, on_top )           
            self._smng.add_setting( confirm_close_key, confirm_close )    
            self._smng.add_setting( background_color_key, background_color ) 
            self._smng.add_setting( transparent_key, transparent )      
            self._smng.add_setting( text_select_key, text_select )      
            self._smng.add_setting( debug_key, debug )            

        else:
            raise Exception("Window id '{}' already exists! Please select a different window id".format(window_id))
    
    def _webview_id_set_callback(self, smng, setting_path, old_value, new_value, wctx):
        print("Cannot change 'webview_id' as it's a fixed value. Might be able to change this setting in a future version of the software.")
        return None

    def webview(self, window_id):
        web_view = self._webviews.get(window_id, None)
        if web_view:
            return self.__webview_proxy(self, window_id)
        else:
            raise Exception("Webview '{}' does not exist. Make sure you have created it first using the 'add_webview' method.".format(webview_id))
    
    def __call__(self, command, data=True):
        self._command = command
        self._return_data = data

        return self

    def __iter__(self):
        return self
    
    def __next__(self):

        if self._reset:
            self._iter = iter(self._webviews.values())
            self._reset = False
        
        try:
            webview_data = next(self._iter)
            webview_data_settings_path = webview_data['window_id']
            data = copy.deepcopy(self._smng.get_setting(webview_data_settings_path))
            if not data:
                raise Exception("Could not get data using settings path: {}".format(webview_data_settings_path))

            # Add callbacks to data
            data['url_callback']  = webview_data['url_callback']
            data['html_callback'] = webview_data['html_callback']

            return {
                'command': self._command,
                'window_id': data['webview_id'],
                'debug': data['debug'],
                'data': data if self._return_data else None
            }
        except StopIteration:
            self._reset = True
            raise StopIteration
        except Exception as e:
            print("ERROR while iterating wctx: {}".format(e))


class WebviewProcess:
    def __init__(self, from_main, to_main):
        self._from_main = from_main
        self._to_main   = to_main
        self._window    = {}
        self._cmds      = {}
        self._debug     = False 
        self._webview   = webview
        self._running   = True

        # Get address of first window and update the internal dictionary
        win_address = self.get_window_address(0)
        self._window["zero"] = win_address
        self._webview.windows[0].hide()

        # Add command callbacks
        self.add_command("create",     self._cmd_create)
        self.add_command("update",     self._cmd_update)
        self.add_command("load_url",   self._cmd_load_url)
        self.add_command("load_html",  self._cmd_load_html)
        self.add_command("get_url",    self._cmd_get_url)
        self.add_command("get_dom",    self._cmd_get_dom)
        # self.add_command("eval_js",    self._cmd_eval_js)
        self.add_command("destroy",    self._cmd_destroy)
        self.add_command("title",      self._cmd_set_title)
        self.add_command("show",       self._cmd_show)
        self.add_command("hide",       self._cmd_hide)
        self.add_command("fullscreen", self._cmd_fullscreen)
        self.add_command("resize",     self._cmd_resize)
        self.add_command("move",       self._cmd_move)
        self.add_command("get_size",   self._cmd_get_size)
        self.add_command("get_pos",    self._cmd_get_pos)
        self.add_command("list",       self._cmd_list)
        self.add_command("quit",       self._cmd_quit)

    def __del__(self):
        pass

    def get_window_address(self, widx):
        return re.split(".*0x", "{}".format(self._webview.windows[widx]))[1][:-1]
    
    def extract_window_address(self, win):
        return re.split(".*0x", "{}".format(win))[1][:-1]

    def get_window_idx(self, window_id):
        window = self._window.get(window_id, None)
        if window:
            win_address = self._window[window_id]
        else:
            return None

        win_idx = None
        for idx, win in enumerate(self._webview.windows):
            if win_address == re.split(".*0x", "{}".format(win))[1][:-1]:
                win_idx = idx
                break
        
        return win_idx

    def add_command(self, command, callback):
        if not self._cmds.get(command, False):
            self._cmds[command] = callback
    
    #====================================================================
    # Command implementations
    #====================================================================

    #================================
    # Create window
    #================================
    def _dummy_html_callback(self):
        return "<h1>No data supplied. Make sure you create command is complete</h1>"

    def _get_webview_content(self, data):
        url           = data.get('url', None)
        html          = data.get('html', None)
        url_callback  = data.get('url_callback', None)
        html_callback = data.get('html_callback', None)
        url_data      = data.get('url_data', None)
        html_data     = data.get('html_data', None)
        js_api        = None

        if not url:
            if url_callback:
                if url_data:
                    url = url_callback(**url_data)
                else:
                    url = url_callback()

        if not html:
            if html_callback:
                if html_data:
                    html = html_callback(**html_data)
                else:
                    html = html_callback()

        if not url and not html:
            print("Was expecting either a URL ot HTML content. Neither was provided")
            raise Exception("Was expecting either a URL ot HTML content. Neither was provided")

        # We can only set either the url or the html content.
        # URL takes precedence
        if url and html:
            html = None
        
        return url, html, js_api

    def _format_background_colour(self, colour):
        if type(colour) is not str:
            raise Exception("Colour should be a string. Type '{}' was received.".format(type(colour)))
        
        if not colour:
            colour = "#FFFFFF"
        
        if colour[0] != "#":
            coclour = "#"+colour
        
        return colour

    def _generate_create_data(self, data):
        create_data = {}
        width, height     = data['size']
        x, y              = data['position']
        url, html, js_api = self._get_webview_content(data)
        colour            = data["background_color"]
        colour            = self._format_background_colour(colour)

        create_data["title"]            = data["window_title"] 
        create_data["url"]              = url
        create_data["html"]             = html 
        create_data["js_api"]           = js_api 
        create_data["width"]            = width     
        create_data["height"]           = height 
        create_data["x"]                = x 
        create_data["y"]                = y 
        create_data["resizable"]        = data["resizable"] 
        create_data["fullscreen"]       = data["fullscreen"]  
        create_data["min_size"]         = data["min_size"]  
        create_data["hidden"]           = data["hidden"] 
        create_data["frameless"]        = data["frameless"] 
        create_data["easy_drag"]        = data["easy_drag"]
        create_data["minimized"]        = data["minimized"] 
        create_data["on_top"]           = data["on_top"]
        create_data["confirm_close"]    = data["confirm_close"]
        create_data["background_color"] = colour
        create_data["transparent"]      = data["transparent"] 
        create_data["text_select"]      = data["text_select"]

        return create_data

    def _cmd_create(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if not win_idx:
            # Create window
            window_create_data = self._generate_create_data(data)
            win = self._webview.create_window(**window_create_data)
            
            # Keep track of window address
            self._window[window_id] = self.extract_window_address(win)

            self._to_main.put( 
                {
                    'command': "create", 
                    'result': {
                        'window_id':window_id,
                        'window_address': self._window[window_id],
                    } 
                } 
            )
        else:
            print("Window '{}' already exists! Please choose another window id.".format(window_id))
            self._to_main.put( 
                {
                    'command': "create", 
                    'result': False
                } 
            )

    #================================
    # Update window
    #================================
    def _cmd_update(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            # Get window options
            win_title     = data['window_title']
            fullscreen    = data['fullscreen']
            frameless     = data['frameless']
            hidden        = data['hidden']
            size          = data['size']
            position      = data['position']

            # Get window
            url, html, js_api = self._get_webview_content(data)

            # Update window title
            self._webview.windows[win_idx].set_title(win_title)

            # Update fullscreen status
            if fullscreen != self._webview.windows[win_idx].fullscreen:
                self._webview.windows[win_idx].toggle_fullscreen()
                self._webview.windows[win_idx].fullscreen = fullscreen

            # Load new content
            if url:
                self._webview.windows[win_idx].load_url(url)
            if html:
                self._webview.windows[win_idx].load_html(html)

            # Update size
            self._webview.windows[win_idx].resize(size[0], size[1])
            
            # Update position:
            self._webview.windows[win_idx].move(position[0], position[1])

            # Update hidden status
            if hidden:
                self._webview.windows[win_idx].hide()
            else:
                self._webview.windows[win_idx].show()
            
            # Send back response
            self._to_main.put( 
                {
                    'command': "update", 
                    'result': True
                } 
            )
        else:
            if debug:
                print("Window '{}' doesn't exist!".format(window_id))
            self._to_main.put( 
                {
                    'command': "update", 
                    'result': False
                } 
            )

    #================================
    # Load HTML
    #================================
    def _cmd_load_html(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            # Get window options
            win_title     = data.get('window_title', None)
            html          = data.get('html', None)
            html_callback = data.get('html_callback', None)
            html_data     = data.get('html_data', None)
            html_cmd      = data.get("cmd_data", None)

            if not html_cmd:
                if not html:
                    if not html_callback:
                        raise Exception("Was expecting either HTML content or an html_callback")
                    else:
                        if html_data:
                            html = html_callback(**html_data)
                        else:
                            html = html_callback()
            else:
                html = html_cmd

            if debug:
                print("HTML DATA     : {}".format(html_data))
                print("GENERATED HTML: {}".format(html))

            # Load new HTML content
            self._webview.windows[win_idx].load_html(html)

            self._to_main.put( 
                {
                    'command': "load_html", 
                    'result': True
                } 
            )
        else:
            if debug:
                print("Window '{}' doesn't exist!".format(window_id))
            self._to_main.put( 
                {
                    'command': "load_html", 
                    'result': False
                } 
            )
    
    #================================
    # Load URL
    #================================
    def _cmd_load_url(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            # Get window options
            url          = data.get('url', None)
            url_callback = data.get('url_callback', None)
            url_data     = data.get('url_data', None)
            url_cmd      = data.get("cmd_data", None)

            if not url_cmd:
                if not url:
                    if not url_callback:
                        raise Exception("Was expecting either a URL, a url_callback or url command data")
                    else:
                        if url_data:
                            url = url_callback(**url_data)
                        else:
                            url = url_callback()
            else:
                url = url_cmd

            if debug:
                print("URL DATA     : {}".format(url_data))
                print("GENERATED URL: {}".format(url))

            # Load new URL
            self._webview.windows[win_idx].load_url(url)

            self._to_main.put( 
                {
                    'command': "load_url", 
                    'result': True
                } 
            )
        else:
            if debug:
                print("Window '{}' doesn't exist!".format(window_id))
            self._to_main.put( 
                {
                    'command': "load_url", 
                    'result': False
                } 
            )

    #================================
    # Destroy window
    #================================
    def _cmd_destroy(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            self._webview.windows[win_idx].destroy()
            self._window.pop(window_id, None)
            self._to_main.put( 
                {
                    'command': "destroy", 
                    'result': {
                        "window_id": window_id,
                        "window_idx": win_idx,
                    }
                } 
            )
        else:
            if debug:
                print("Window '{}' does not exist!".format(title))
            self._to_main.put( 
                {
                    'command': "destroy", 
                    'result': False,
                } 
            )

    #================================
    # Get current URL
    #================================
    def _cmd_get_url(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            url = self._webview.windows[win_idx].get_current_url()
            self._to_main.put( 
                {
                    'command': "get_url", 
                    'result': url 
                } 
            )
        else:
            if debug:
                print("Window '{}' doesn't exist!".format(window_id))
            self._to_main.put( 
                {
                    'command': "get_url", 
                    'result': False 
                } 
            )
    
    #================================
    # Get DOM
    #================================
    def _cmd_get_dom(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            element = data.get("cmd_data", None)
            if element is None:
                element=".*"
            DOM = self._webview.windows[win_idx].get_elements(element)
            self._to_main.put( 
                {
                    'command': "get_dom", 
                    'result': DOM 
                } 
            )
        else:
            if debug:
                print("Window '{}' doesn't exist!".format(window_id))
            self._to_main.put( 
                {
                    'command': "get_dom", 
                    'result': False 
                } 
            )

    #================================
    # Set window title
    #================================
    def _cmd_set_title(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            win_title = data['window_title']
            self._webview.windows[win_idx].set_title(win_title)
            self._to_main.put( 
                {
                    'command': "title", 
                    'result': True,
                } 
            )
        else:
            if debug:
                print("Window '{}' doesn't exist!".format(window_id))
            self._to_main.put( 
                {
                    'command': "title", 
                    'result': False,
                } 
            )


    #================================
    # Show window
    #================================
    def _cmd_show(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            self._webview.windows[win_idx].show()
            self._to_main.put( 
                {
                    'command': "show", 
                    'result': True,
                } 
            )
        else:
            if debug:
                print("Window '{}' doesn't exist!".format(window_id))
            self._to_main.put( 
                {
                    'command': "show", 
                    'result': False,
                } 
            )


    #================================
    # Hide window
    #================================
    def _cmd_hide(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            self._webview.windows[win_idx].hide()
            self._to_main.put( 
                {
                    'command': "hide", 
                    'result': True,
                } 
            )
        else:
            if debug:
                print("Window '{}' doesn't exist!".format(window_id))
            self._to_main.put( 
                {
                    'command': "hide", 
                    'result': False,
                } 
            )


    #================================
    # Fullscreen window
    #================================
    def _cmd_fullscreen(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            fullscreen_status = self._webview.windows[win_idx].fullscreen
            self._webview.windows[win_idx].toggle_fullscreen()
            self._webview.windows[win_idx].show()
            new_fullscreen_status = not fullscreen_status
            self._webview.windows[win_idx].fullscreen = new_fullscreen_status
            self._to_main.put( 
                {
                    'command': "fullscreen", 
                    'result': new_fullscreen_status,
                } 
            ) 
        else:
            self._to_main.put( 
                {
                    'command': "fullscreen", 
                    'result': None,
                } 
            ) 


    #================================
    # Resize window
    #================================
    def _cmd_resize(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            new_dims = data.get("cmd_data", None)
            if new_dims:
                if type(new_dims) is tuple and len(new_dims) == 2:
                    width, height = new_dims
                    self._webview.windows[win_idx].resize(width, height)

                    self._to_main.put( 
                        {
                            'command': "resize", 
                            'result': True,
                        } 
                    )
                else:
                    raise Exception("CMD Resize: Was expecting a tuple of two elements as cmd_data")
            else:
                raise Exception("CMD Resize: Was expecting a tuple of two elements as cmd_data")
        else:
            if debug:
                print("Window '{}' doesn't exist!".format(window_id))
            self._to_main.put( 
                {
                    'command': "resize", 
                    'result': False,
                } 
            )


    #================================
    # Move window
    #================================
    def _cmd_move(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            new_pos = data.get("cmd_data", None)
            if new_pos:
                if type(new_pos) is tuple and len(new_pos) == 2:
                    pos_x, pos_y = new_pos
                    self._webview.windows[win_idx].move(pos_x, pos_y)
                    self._to_main.put( 
                        {
                            'command': "move", 
                            'result': True,
                        } 
                    )
                else:
                    raise Exception("CMD Move: Was expecting a tuple of two elements as cmd_data")
            else:
                raise Exception("CMD Move: Was expecting a tuple of two elements as cmd_data")
        else:
            if debug:
                print("Window '{}' doesn't exist!".format(window_id))
            self._to_main.put( 
                {
                    'command': "move", 
                    'result': False,
                } 
            )


    #================================
    # Get window size
    #================================
    def _cmd_get_size(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            width  = self._webview.windows[win_idx].width
            height = self._webview.windows[win_idx].height
            self._to_main.put( 
                {
                    'command': "get_size", 
                    'result': (width, height) 
                } 
            )
        else:
            if debug:
                print("Window '{}' doesn't exist!".format(window_id))
            self._to_main.put( 
                {
                    'command': "get_size", 
                    'result': False 
                } 
            )


    #================================
    # Get window position
    #================================
    def _cmd_get_pos(self, window_id, data, debug):
        win_idx = self.get_window_idx(window_id)
        if win_idx or win_idx==0:
            win   = self._webview.windows[win_idx]
            pos_x = win.x
            pos_y = win.y
            self._to_main.put( 
                {
                    'command': "get_pos", 
                    'result': (pos_x, pos_y) 
                } 
            )
        else:
            if debug:
                print("Window '{}' doesn't exist!".format(window_id))
            self._to_main.put( 
                {
                    'command': "get_pos", 
                    'result': False 
                } 
            )


    #================================
    # Get list of windows
    #================================
    def _cmd_list(self, window_id, data, debug):
        self._to_main.put( 
            {
                'command': "list", 
                'result': self._window 
            } 
        )


    #================================
    # Quit event loop
    #================================
    def _cmd_quit(self, window_id=None, data=None, debug=True):
        if debug:
            print("Terminating event loop... ", end="")
        try:
            for win in self._webview.windows:
                win.destroy()
            
            self._window.clear()
            if debug:
                print("OK")
            self._running = False
            self._to_main.put( 
                {
                    'command': "quit", 
                    'result': True 
                } 
            )
        except:
            if debug:
                print("ERROR while quitting WebviewProcess")
            self._to_main.put( {'command': "quit", 'result': False } )


    #====================================================================
    # Main event loop
    #====================================================================
    def run(self):
        while self._running:
            # Get data from Queue
            webview_data = self._from_main.get()

            # Extract command and data
            commands  = re.split('\W+', webview_data['command'])
            window_id = webview_data.get('window_id', "no window")
            data      = webview_data.get('data', None)
            debug     = webview_data.get('debug', False)

            if debug:
                print("COMMAND  : {}".format(commands))
                print("WINDOW_ID: {}".format(window_id))
                print("DATA     : {}".format(data))

            try:
                for cmd in commands:
                    cmd_callback = self._cmds.get(cmd, None)
                    if cmd_callback:
                        res = cmd_callback(window_id, data, debug)

            except Exception as e:
                if debug:
                    print("WebviewProcess 'run' method ERROR: {}".format(e))


class WebviewManager:
    def __init__(self, settings_manager, debug=False):
        self._smng = settings_manager,
        self._debug = debug
        self._to_wv   = Queue()
        self._from_wv = Queue()
        self._p = None
        self._process_running  = False
        self._window = {}

        atexit.register(self.__del__)

        if not self._process_running:
            self.start()
    
    def __del__(self):
        if self._process_running:
            self.stop()

    @staticmethod
    def _webview_event_loop(from_main, to_main):

        wv_proc = WebviewProcess(from_main, to_main)
        wv_proc.run()
    
    @staticmethod
    def _webview_bootstrap(from_main, to_main):
        window = webview.create_window('zero')
        webview.start(WebviewManager._webview_event_loop, (from_main, to_main) )

    def start(self):
        try:
            if self._process_running:
                if self._debug:
                    print("Process is already running.")
                return None 

            if self._debug:
                print("Starting webview process... ", end="")
            
            self._p=Process(target=self._webview_bootstrap, args=(self._to_wv, self._from_wv))
            self._p.start()
            self._process_running = True

            if self._debug:
                print("OK")
        except Exception as e:
            if self._debug:
                print("ERROR while staring webview process: {}".format(e))
            raise Exception(e)
    
    def stop(self):
        # Send command and data to webview process
        try:
            if self._process_running:
                webview_data = self._create_webview_data(
                    command="quit", 
                    cmd_data=None,
                    window_id=None,
                    debug=self._debug,
                    data=None
                )
                self._to_wv.put( webview_data )
                res = self._from_wv.get()
                if res:
                    print("Successfully terminated event loop!")
                else:
                    print("ERROR while terminating event loop!")
                
                self._window.clear()

                if self._debug:
                    print("Stopping webview process... ", end="")

                self._p.terminate()
                self._p.join()
                self._p.close()
                self._process_running = False
                if self._debug:
                    print("OK")
            else:
                if self._debug:
                    print("Process is already stopped.")
                return None 

        except Exception as e:
            if self._debug:
                print("ERROR while stopping webview process: {}".format(e))
            raise Exception(e)

    def _create_webview_data(
        self,
        command,
        cmd_data,
        window_id,
        debug,
        data
    ):
        webview_data = {
            "command": command,
            "window_id": window_id,
            "debug": debug,
            "data": data,
        }
        if webview_data.get("data", None):
            webview_data['data']['cmd_data'] = cmd_data
        else:
            webview_data['data'] = {}
            webview_data['data']['cmd_data'] = cmd_data
            
        return webview_data

    def __call__(self, command, cmd_data=None, window_id=None, debug=False, data=None):
        if not self._process_running:
            return False
        
        if type(command) is tuple and len(command) == 2:
            command_ = command[0]
            cmd_data_ = command[1]
        else:
            command_  = command
            cmd_data_ = cmd_data

        webview_data = self._create_webview_data(
            command_,
            cmd_data_,
            window_id,
            debug,
            data
        )

        # Send command and data to webview process
        self._to_wv.put( webview_data )

        # Wait for result from webview process
        result = self._from_wv.get()    

        ret_cmd = result.get("command", None)
        if not ret_cmd:
            print("ERROR! Was expecting answer for '{}' received answer for '{}'".format(command, ret_cmd))
            return None

        return result

    def process(self, webview_data):
        if not self._process_running:
            return False

        # Send command and data to webview process
        self._to_wv.put( webview_data, timeout=3 )
        return self._from_wv.get(timeout=5)
