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

        def add_setting(self, key, value):
            if self._webview.get(key, None) is None:
                self._webview[key] = value

                full_key = self._parent._create_full_settings_key(self._webview_id, key)
                self._smng.add_setting(full_key, value)
            else:
                if self._debug:
                    print("Setting '{}' already exists!".format(key))
        
        def add_html_data_setting(
            self, 
            key, 
            value, 
            set_callback=None, 
            set_user_data=None,
            get_callback=None, 
            get_user_data=None,
        ):
            if self._webview['html_data'].get(key, None) is None:
                self._webview['html_data'][key] = value

                full_key = self._parent._create_full_html_data_key(self._webview_id, key)
                self._smng.add_setting(full_key, value)
                if set_callback:
                    self._smng.add_set_listener_for_setting(full_key, set_callback, set_user_data)
                if get_callback:
                    self._smng.add_get_listener_for_setting(full_key, get_callback, get_user_data)
            else:
                if self._debug:
                    print("HTML data setting '{}' already exists!".format(key))
        
        def set_html_data_setting(self, key, value):
            if self._webview['html_data'].get(key, None) is not None:
                self._webview['html_data'][key] = value
            else:
                if self._debug:
                    print("HTML data setting '{}' does not exists".format(key))


    def __init__(self, provider, settings_manager, debug=False):
        self._provider = provider
        self._smng     = settings_manager
        self._debug    = debug

        self._webviews = {}
        self._reset = True
        self._iter = None
        self._command = None
        self._return_data = True

    def _create_full_settings_key(self, webview_id, key):
        return ".".join(
            [
                self._provider.provider_id(),
                "webview",
                webview_id,
                key
            ]
        )

    def _create_full_html_data_key(self, webview_id, key):
        return ".".join(
            [
                self._provider.provider_id(),
                "webview",
                webview_id,
                "html_data",
                key
            ]
        )
        
    def add_webview(
        self,
        webview_id,
        window_title,
        html_callback,
        fullscreen=False,
        frameless=False,
        show=False,
        debug=False,
    ):
        if self._webviews.get(webview_id, None) is None:
            window_id = ".".join( [self._provider.provider_id(), webview_id])

            self._webviews[webview_id] = {
                'window_id': window_id,
                'window_title': window_title,
                'fullscreen': fullscreen,
                'frameless': frameless,
                'show': show,
                'debug': debug,
                'html_callback': html_callback, 
                'html_data': {},
            }

            # Add webview options to settings
            window_id_option    = self._create_full_settings_key(webview_id, "window_id")
            window_title_option = self._create_full_settings_key(webview_id, "window_title")
            fullscreen_option   = self._create_full_settings_key(webview_id, "fullscreen")
            frameless_option    = self._create_full_settings_key(webview_id, "frameless")
            show_option         = self._create_full_settings_key(webview_id, "show")
            debug_option         = self._create_full_settings_key(webview_id, "debug")

            self._smng.add_setting(window_id_option, window_id)
            self._smng.add_setting(window_title_option, window_title)
            self._smng.add_setting(fullscreen_option, fullscreen)
            self._smng.add_setting(frameless_option, frameless)
            self._smng.add_setting(show_option, show)
            self._smng.add_setting(debug_option, debug)

            self._smng.add_set_listener_for_setting(window_id_option,    self._window_settings_set_callback, self)
            self._smng.add_set_listener_for_setting(window_title_option, self._window_settings_set_callback, self)
            self._smng.add_set_listener_for_setting(fullscreen_option,   self._window_settings_set_callback, self)
            self._smng.add_set_listener_for_setting(frameless_option,    self._window_settings_set_callback, self)
            self._smng.add_set_listener_for_setting(show_option,         self._window_settings_set_callback, self)
            self._smng.add_set_listener_for_setting(debug_option,        self._window_settings_set_callback, self)

        else:
            raise Exception("Webview '{}' already exists!".format(webview_id))

    @staticmethod
    def _window_settings_set_callback(smng, setting_path, old_value, new_value, wctx):
        keys = setting_path.split(".")
        wctx_key = ".".join( [keys[2], keys[3]] )
        util.misc.DictUtil.set_by_path(wctx._webviews, wctx_key, new_value)
    
    @staticmethod
    def _window_settings_get_callback(smng, setting_path, old_value, new_value, wctx):
        pass

    def webview(self, webview_id):
        web_view = self._webviews.get(webview_id, None)
        if web_view:
            return self.__webview_proxy(self, webview_id)
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
            data = next(self._iter)

            # win_data = 
            # html_data = data['html_data']

            return {
                'command': self._command,
                'window_id': data['window_id'],
                'debug': data['debug'],
                'data': data if self._return_data else None
            }
        except StopIteration:
            self._reset = True
            raise StopIteration

class WebviewManager:
    def __init__(self, settings_manager, debug=False):
        self._smng = settings_manager,
        self._debug = debug
        self._q = Queue()
        self._p = None
        self._process_running  = False
        self._window = {}
        self._qdata = WebviewManager.generate_empty_qdata()

        atexit.register(self.__del__)

        if not self._process_running:
            self.start()
    
    def __del__(self):
        if self._process_running:
            self.stop()

    @staticmethod
    def generate_empty_qdata():
        return {
            'command': "",
            'window_id': "",
            'data': None,
        }

    @staticmethod
    def get_window_idx(window_dict, window_id, webview_windows):
        window = window_dict.get(window_id, None)
        if window:
            win_address = window_dict[window_id]
        else:
            return None

        win_idx = None
        for idx, win in enumerate(webview_windows):
            if win_address == re.split(".*0x", "{}".format(win))[1]:
                win_idx = idx
                break
        
        return win_idx

    @staticmethod
    def _webview_event_loop(q):
        _window = {}
        debug = False

        win_address = re.split(".*0x", "{}".format(webview.windows[0]))[1]
        _window["zero"] = win_address
        webview.windows[0].hide()

        # Start main event loop
        while True:
            # Get data from Queue
            webview_data = q.get()

            # Extract command and data
            command   = webview_data['command']
            window_id = webview_data['window_id']
            debug     = webview_data.get('debug', False)
            data      = webview_data['data']

            if debug:
                print("COMMAND  : {}".format(command))
                print("WINDOW_ID: {}".format(window_id))
                print("DATA     : {}".format(data))

            try:
                #======================================
                # Create
                #======================================
                if command == "create":
                    # win_title = data['window_title']
                    if _window.get(window_id, None) is None:
                        
                        # Create window data dictionary and copy data received from the queue
                        # _window[window_id] = copy.deepcopy(data)

                        # Get window options
                        win_title     = data['window_title']
                        fullscreen    = data['fullscreen']
                        frameless     = data['frameless']
                        show          = data['show']
                        html_callback = data['html_callback']
                        html_data     = data['html_data']

                        if debug:
                            print("HTML_DATA: {}".format(html_data))
                        if not html_callback:
                            raise Exception("Was expecting an html_callback")
                        
                        if html_data:
                            html = html_callback(**html_data)
                        else:
                            html = html_callback()
                        
                        if debug:
                            print("HTML_DATA: {}".format(html_data))

                        # Create window
                        win = webview.create_window(
                            win_title, 
                            html=html,
                            fullscreen=fullscreen, 
                            frameless=frameless)
                        
                        # Keep track of window addrees
                        win_address = re.split(".*0x", "{}".format(win))[1]
                        _window[window_id] = win_address
                    else:
                        print("Window '{}' already exists! Please choose another window id.".format(win_title))
                
                #======================================
                # Update
                #======================================
                if command == "update":                    
                    if _window.get(window_id, None):

                        # Update data of window from data received from the queue
                        # _window[win_title] = copy.deepcopy(data)

                        # Get window options
                        win_title     = data['window_title']
                        fullscreen    = data['fullscreen']
                        frameless     = data['frameless']
                        show          = data['show']
                        html_callback = data['html_callback']
                        html_data     = data['html_data']
                        
                        if not html_callback:
                            raise Exception("Was expecting an html_callback")

                        if debug:
                            print("HTML_DATA: {}".format(html_data))

                        if html_data:
                            html = html_callback(**html_data)
                        else:
                            html = html_callback()

                        if debug:
                            print("HTML_DATA: {}".format(html_data))

                        # Update window
                        win_idx = WebviewManager.get_window_idx(_window, window_id, webview.windows)

                        webview.windows[win_idx].set_title(win_title)

                        if fullscreen != webview.windows[win_idx].fullscreen:
                            webview.windows[win_idx].fullscreen = fullscreen
                            webview.windows[win_idx].toggle_fullscreen()
                        
                        # Load new HTML content
                        webview.windows[win_idx].load_html(html)

                        if show:
                            webview.windows[win_idx].show()
                        else:
                            webview.windows[win_idx].hide()
                        
                    else:
                        if debug:
                            print("Window '{}' doesn't exist!".format(window_id))

                #======================================
                # Destroy
                #======================================
                if command == "destroy":
                    win_idx    = WebviewManager.get_window_idx(_window, window_id, webview.windows)
                    if win_idx:
                        webview.windows[win_idx].destroy()
                        _window.pop(window_id, None)
                    else:
                        if debug:
                            print("Window '{}' does not exist!".format(title))

                #======================================
                # Hide
                #======================================
                if command == "hide":
                    win_idx    = WebviewManager.get_window_idx(_window, window_id, webview.windows)

                    if win_idx:
                        webview.windows[win_idx].hide()
                    else:
                        if debug:
                            print("Window '{}' does not exist!".format(window_id))
                
                #======================================
                # Show
                #======================================
                if command == "show":
                    win_idx    = WebviewManager.get_window_idx(_window, window_id, webview.windows)

                    if win_idx:
                        webview.windows[win_idx].show()
                    else:
                        if debug:
                            print("Window '{}' does not exist!".format(window_id))

                #======================================
                # Quit
                #======================================
                if command == "q" or command == "quit":
                    if debug:
                        print("Terminating event loop... ", end="")
                    try:
                        for win in webview.windows:
                            win.destroy()
                        
                        _window.clear()
                        if debug:
                            print("OK")
                        q.put(True)
                    except:
                        if debug:
                            print("ERROR")
                        q.put(False)
                    break
            
            except Exception as e:
                if debug:
                    print("Webview_event_loop ERROR: {}".format(e))
    
    @staticmethod
    def _webview_bootstrap(q):
        window = webview.create_window('zero')
        webview.start(WebviewManager._webview_event_loop, q)

    def start(self):
        try:
            if self._process_running:
                if self._debug:
                    print("Process is already running.")
                return None 

            if self._debug:
                print("Starting webview process... ", end="")
            
            self._p=Process(target=self._webview_bootstrap, args=(self._q,))
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
                self._qdata['command']  = "quit"
                self._q.put(self._qdata)
                res = self._q.get()
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

    def __call__(self, webview_data):
        return self.process(webview_data)

    def process(self, webview_data):
        if not self._process_running:
            return False

        # Send command and data to webview process
        self._q.put( webview_data )
        return True

    # def window_create(webview_data):
    #     if not self._process_running:
    #         return None

    #     # Send command and data to webview process
    #     self._q.put( ("create", webview_data ) )

    # def window_update(webview_data):
    #     if not self._process_running:
    #         return None

    #     # Send command and data to webview process
    #     self._q.put( ("update", webview_data ) )


    # def _window_exists(self, win_title):
    #     if self._window.get(win_title, None):
    #         return True
    #     else:
    #         return False

    # def window_create(
    #     self, 
    #     win_title, 
    #     html_callback, 
    #     html_data=None, 
    #     win_options={
    #         'fullscreen': False,
    #         'frameless': True
    #     }
    # ):
        
    #     if not self._process_running:
    #         return None
    
    #     if self._window_exists(win_title):
    #         if self._debug:
    #             print("WV: Window '{}' already exists. Please choose another title.".format(win_title))
    #     else:
    #         self._window[win_title] = WebviewManager.generate_empty_qdata()

    #         self._window[win_title]['command']       = "create"
    #         self._window[win_title]['win_title']     = win_title
    #         self._window[win_title]['win_options']   = win_options
    #         self._window[win_title]['html_callback'] = html_callback
    #         self._window[win_title]['html_data']     = html_data

    #         # Send command and data to webview process
    #         self._q.put(self._window[win_title])
    
    # def window_update(
    #     self, 
    #     win_title, 
    #     html_data, 
    #     html_callback=None, 
    #     win_options={
    #         'fullscreen': False,
    #         'frameless': True
    #     }):

    #     if not self._process_running:
    #         return None

    #     if self._window_exists(win_title):
    #         self._window[win_title]['command']       = "update"
    #         self._window[win_title]['win_options']   = win_options
    #         self._window[win_title]['html_callback'] = html_callback
    #         self._window[win_title]['html_data']     = html_data

    #         # Send command and data to webview process
    #         self._q.put(self._window[win_title])
    #     else:
    #         if self._debug:
    #             print("Window '{}' does not exist. Nothing to update.".format(win_title))
    
    # def window_destroy(self, win_title):
    #     if not self._process_running:
    #         return None
        
    #     if self._window_exists(win_title):
    #         self._window[win_title]['command']       = "destroy"

    #         # Send command and data to webview process
    #         self._q.put(self._window[win_title])

    #         # Remove window from internal dictionary
    #         self._window.pop(win_title, None)
    #     else:
    #         if self._debug:
    #             print("Window '{}' does not exist. Nothing to destroy.".format(win_title))
    
    # def window_hide(self, win_title):
    #     if not self._process_running:
    #         return None

    #     if self._window_exists(win_title):
    #         self._window[win_title]['command']       = "hide"

    #         # Send command and data to webview process
    #         self._q.put(self._window[win_title])
    #     else:
    #         if self._debug:
    #             print("Window '{}' does not exist. Nothing to hide.".format(win_title))

    # def window_show(self, win_title):
    #     if not self._process_running:
    #         return None
        
    #     if self._window_exists(win_title):
    #         self._window[win_title]['command']       = "show"

    #         # Send command and data to webview process
    #         self._q.put(self._window[win_title])
    #     else:
    #         if self._debug:
    #             print("Window '{}' does not exist. Nothing to show.".format(win_title))
    
    # def list_windows(self):
    #     if not self._process_running:
    #         return None

    #     self._qdata['command']       = "list"

    #     # Send command and data to webview process
    #     self._q.put(self._qdata)
