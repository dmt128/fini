import argparse
from . import managers
from . import providers
from . import util
from . import fonts
from . import glossary

class FiniApp():
    def __init__(self):

        # Initialise colorama
        util.screen.colorama.init()

        # Clear screen
        util.screen.clear_screen()

        # Initialise cmd parser
        self._init_cmd_parser()

        # Create and initialise a SettingsManager object
        self._smng = managers.SettingsManager()
        self._smng.initial_setup()

        # # Create and initialise a ProvidersManager object
        # self._pmng = managers.ProvidersManager()
        # self._pmng.initial_setup()

        # Create a user prompt session. The following will keep the history of all user commands.
        self._cmd_session = util.prompt.PromptSession(
            history=util.prompt.FileHistory( self._smng.get_cmd_history_file() )
            )

        #Display the app's welcome message
        util.screen.app_welcome_message()

    def __del__(self):

        # De-initialise colorama
        util.screen.colorama.deinit()

        # The SettingsManager will self destroy here 
        # and will take care of any unsaved settings

    def _init_cmd_parser(self):
        self._cmd_parser = argparse.ArgumentParser(
            prog = "",
            description="Extract financial information from publicly available sources",
            add_help =False)

        self._cmd_parser.add_argument("-h", "--help", action="store_true", default=False, 
            help='print this help message')
        self._cmd_parser.add_argument("--version", action="store_true", default=False,
            help='display the app\'s version')
        self._cmd_parser.add_argument("-v", "--verbose", action="store_true", default=False,
            help="display verbose information during processing")
        self._cmd_parser.add_argument("-s", "--settings", nargs='+', metavar=('setting', 'value'),
            help="display the application's settings or set particular settings")
        self._cmd_parser.add_argument("-t", "--term", nargs='*', metavar=('list', 'TERM'),
            help="use '-t list' to display available terms;\nuse '-t TERM' to display the term's definition and other details")
        self._cmd_parser.add_argument("-c", "--cls", action="store_true", default=False, 
            help='clear screen')
        self._cmd_parser.add_argument("-q", "--quit", action="store_true", default=False,
            help='quit application')
        self._cmd_parser.add_argument('ticker_symbols', metavar='TICKER', type=str, nargs='*',
            help='One or more ticker symbols to get information for')
    
    
    def run(self):
        # Enter main event loop. Will only exit with the -q/--quit command.
        while True:
            try:
                # Get user input
                user_input = self._cmd_session.prompt(
                    util.prompt.get_prompt_message_from_settings(self._smng._settings) , 
                    style=util.prompt.get_prompt_style_from_settings(self._smng._settings)
                    )

                # Erase screen
                util.screen.erase_screen()

                # Parse user input
                args = self._cmd_parser.parse_args(user_input.split())

                # #======================================
                # # Ticker symbols
                # #======================================
                # if args.ticker_symbols:
                #     managers.provider.data_parser(args)
                #     self._pmng.process(args)

                #======================================
                # Settings
                #======================================
                if args.settings:
                    vv = vars(args)['settings']
                    if len(vv) == 1:
                        if vv[0] in ("d", "dis", "display"):
                            self._smng.display_settings()
                        elif vv[0] in ("reset"):
                            self._smng.reset_settings()
                        else:
                            pass

                    if len(vv) >=2:
                        val = self._smng.set_setting(vv[0], vv[1])

                #======================================
                # Term definitions
                #======================================
                if args.term:
                    terms = list(set(args.term))
                    if terms[0] == "list":
                        glossary.available_terms()
                    else:
                        for term in terms:
                            glossary.info(term)

                #======================================
                # Help
                #======================================
                if args.help:
                    print(util.screen.Fore.GREEN + "======================================================================")
                    self._cmd_parser.print_help()
                    print("======================================================================\n" + util.screen.Style.RESET_ALL)

                #======================================
                # Version
                #======================================
                if args.version:
                    print(util.screen.Fore.CYAN + "Fini {}".format(version.__version__) + util.screen.Style.RESET_ALL)

                #======================================
                # Clear screen
                #======================================
                if args.cls:
                    util.clear_screen()

                #======================================
                # Quit
                #======================================
                if args.quit:
                    break

            except:
                pass
