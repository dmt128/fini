from .. managers import provider
from .. import util
import re, webview

__all__ = ['TradingViewProvider']
__docformat__ = 'restructuredtext'

# def on_closed():
#     print('pywebview window is closed')


# def on_closing():
#     print('pywebview window is closing')


# def on_shown():
#     print('pywebview window shown')


# def on_loaded():
#     print('DOM is ready')

#     # unsubscribe event listener
#     webview.windows[0].loaded -= on_loaded


# def load_window_html(q):
#     while True:
#         html_data = q.get()

#         if html_data['quit']:
#             break

#         # Get data from html_data dictionary
#         ticker              = html_data['ticker']
#         watchlist           = html_data['watchlist']
#         container_id        = html_data['container_id']
#         autosize            = html_data['autosize']
#         timezone            = html_data['timezone']
#         theme               = html_data['theme']
#         style               = html_data['style']
#         locale              = html_data['locale']
#         toolbar_bg          = html_data['toolbar_bg']
#         enable_publishing   = html_data['enable_publishing']
#         withdateranges      = html_data['withdateranges']
#         rangeo              = html_data['range']
#         hide_side_toolbar   = html_data['hide_side_toolbar']
#         allow_symbol_change = html_data['allow_symbol_change']
#         details             = html_data['details']
#         hotlist             = html_data['hotlist']
#         calendar            = html_data['calendar']
#         studies             = html_data['studies']

#         webview.windows[0].load_html( 
#             get_stock_chart_html(
#                 ticker,
#                 watchlist=watchlist, 
#                 container_id=container_id,
#                 autosize=autosize,
#                 timezone=timezone,
#                 theme=theme,
#                 style=style,
#                 locale=locale,
#                 toolbar_bg=toolbar_bg,
#                 enable_publishing=enable_publishing,
#                 withdateranges=withdateranges,
#                 rangeo=rangeo,
#                 hide_side_toolbar=hide_side_toolbar,
#                 allow_symbol_change=allow_symbol_change,
#                 details=details,
#                 hotlist=hotlist,
#                 calendar=calendar,
#                 studies=studies,
#             ) 
#         )
    
#     webview.windows[0].destroy()


# def create_stock_chart(q):
#     window = webview.create_window('Stock Chart', html=get_stock_chart_html("AAPL"), frameless=True)
#     window.closed  += on_closed
#     window.closing += on_closing
#     window.shown   += on_shown
#     window.loaded  +=on_loaded
#     webview.start(load_window_html, q)

class TradingViewProvider(provider.ProviderBase):
    def __init__(self, *args, **kwargs):
        # We need to call the superclass __init__ here.
        # The superclass __init__ calls some initialisation code that is 
        # necessary for the correct operation of this class
        super(TradingViewProvider, self).__init__(*args, **kwargs)

        # # studies=["CRSI@tv-basicstudies", "VolatilityIndex@tv-basicstudies"],
        # self._html_data = {
        #     'quit'               : False,
        #     'ticker'             : "",
        #     'watchlist'          : None,
        #     'container_id'       : "tradingview_60e16",
        #     'autosize'           : True,
        #     'timezone'           : "Europe/London",
        #     'theme'              : "light",
        #     'style'              : 2,
        #     'locale'             : "en",
        #     'toolbar_bg'         : "f1f3f6",
        #     'enable_publishing'  : False,
        #     'withdateranges'     : True,
        #     'range'              : "YTD",
        #     'hide_side_toolbar'  : False,
        #     'allow_symbol_change': True,
        #     'details'            : True,
        #     'hotlist'            : True,
        #     'calendar'           : True,
        #     'studies'            : None,
        # }

    @staticmethod
    def provider_id():
        return "tview"
    
    @staticmethod
    def generate_URL_ctx(uctx, provider):
        uctx.add_url("https://uk.tradingview.com/symbols/{ticker}", provider.data_parser_1)

    @staticmethod
    def generate_data(data):
        #===================================
        # Overview
        #===================================
        data.add_entry("overview.ticker",       "N/A")
        data.add_entry("overview.exchange",     "N/A")
        data.add_entry("overview.company",      "N/A")
        data.add_entry("overview.updated",      [""])
        data.add_entry("overview.requested",    "N/A")
        data.add_entry("overview.sector",       "N/A")
        data.add_entry("overview.industry",     "N/A")
        data.add_entry("overview.sub_industry", "N/A")
        data.add_entry("overview.country",      "N/A")
        data.add_entry("overview.url",          "N/A")

        #===================================
        # Stock Activity
        #===================================
        data.add_entry("stock_activity.time_recorded",    [])
        data.add_entry("stock_activity.stock_price",      [])
        data.add_entry("stock_activity.change_price",     [])
        data.add_entry("stock_activity.change_percent",   [])
        data.add_entry("stock_activity.stock_currency",   "N/A")
        data.add_entry("stock_activity.stock_open",       [])
        data.add_entry("stock_activity.stock_day_low",    [])
        data.add_entry("stock_activity.stock_day_high",   [])
        data.add_entry("stock_activity.stock_52_wk_low",  [])
        data.add_entry("stock_activity.stock_52_wk_high", [])
        data.add_entry("stock_activity.market_cap",       [])
        data.add_entry("stock_activity.market_cap_unit",  "N/A")
        data.add_entry("stock_activity.volume",           [])
        data.add_entry("stock_activity.avg_volume",       [])

        #===================================
        # Valuation
        #===================================

        #===================================
        # Financial
        #===================================

        #===================================
        # Technical
        #===================================
        # data.add_entry("technical.beta", [])

    
    @staticmethod
    def generate_settings(settings):
        #===================================
        # Create panels
        #===================================
        settings.add_setting("option1", 500)
        settings.add_setting("option2", True)
        settings.add_setting("option3", 3.4)
        settings.add_setting("option4", "Test Option")
        settings.add_fmt_setting("style.panel_background", "!{gfx.style.panel_background}")
        settings.add_fmt_setting("style.empty_line",       "!{gfx.style.empty_line}")
        settings.add_fmt_setting("style.header",           "!{gfx.style.header}")
        settings.add_fmt_setting("style.header_light",     "!{gfx.style.header_light}")
        settings.add_fmt_setting("style.key",              "!{gfx.style.key}")
        settings.add_fmt_setting("style.key_2",            "!{gfx.style.key_2}")
        settings.add_fmt_setting("style.value",            "!{gfx.style.value}")
        settings.add_fmt_setting("style.value_positive",   "!{gfx.style.value_positive}")
        settings.add_fmt_setting("style.value_negative",   "!{gfx.style.value_negative}")
        settings.add_fmt_setting("style.logo",             "!{gfx.style.logo}")
        settings.add_condition("condition_1", ["{data}>= 0", "{data}<0"] ,["style.value_positive", "style.value_negative"])

    @staticmethod
    def generate_draw_ctx(dctx):

        #===================================
        # Create panels
        #===================================

        # Create overview panel
        dctx.add_panel("overview", (52, 12), (0, 0))
        dctx.panel("overview").add_line("@style.header@ {overview.ticker:5s}!!@style.header_light@  [{overview.exchange:^10s}]") 
        dctx.panel("overview").add_line("@style.key@ {overview.company:<s}")
        dctx.panel("overview").add_line("@style.key@ Sec: !!@style.value@{overview.sector:<s}")
        dctx.panel("overview").add_line("@style.key@ Ind: !!@style.value@{overview.industry:<s}")
        dctx.panel("overview").add_line("@style.key@ Sub: !!@style.value@{overview.sub_industry:<s}")
        dctx.panel("overview").add_line("@style.key@ Cou: !!@style.value@{overview.country:<s}")
        dctx.panel("overview").add_line("@style.key@ Upd: !!@style.value@{overview.updated:<s}")
        dctx.panel("overview").add_line("@style.logo@  ______            ___          _   ___            ")
        dctx.panel("overview").add_line("@style.logo@ /_  __/______ ____/ (_)__  ___ | | / (_)__ _    __ ")
        dctx.panel("overview").add_line("@style.logo@  / / / __/ _ `/ _  / / _ \/ _ `/ |/ / / -_) |/|/ / ")
        dctx.panel("overview").add_line("@style.logo@ /_/ /_/  \_,_/\_,_/_/_//_/\_, /|___/_/\__/|__,__/  ")
        dctx.panel("overview").add_line("@style.logo@                          /___/                     ")
        # dctx.panel("overview").add_line("@style.logo@0123456789012345678901234567890123456789012345667890")

        # Create valuation panel
        dctx.add_panel("valuation", (30, 13), (53, 0))
        dctx.panel("valuation").add_line("@style.header@{:^s}", "Stock Activity")
        dctx.panel("valuation").add_line("@style.key@ Stock Price: !!@style.value@{stock_activity.stock_price:<7.2f} USD")
        dctx.panel("valuation").add_line("@style.empty_line@            !!@condition_1@ {stock_activity.change_price:<5.2f} !!@condition_1@ ({stock_activity.change_percent:<5.2f} %)!!@style.empty_line@")
        dctx.panel("valuation").add_line("@style.key@ Stock Open : !!@style.value@{stock_activity.stock_open:<7.2f}")
        dctx.panel("valuation").add_line("@style.key@ Day Low    : !!@style.value@{stock_activity.stock_day_low:<7.2f}")
        dctx.panel("valuation").add_line("@style.key@ Day High   : !!@style.value@{stock_activity.stock_day_high:<7.2f}")
        dctx.panel("valuation").add_line("@style.key@ 52 Wk Low  : !!@style.value@{stock_activity.stock_52_wk_low:<7.2f}")
        dctx.panel("valuation").add_line("@style.key@ 52 Wk High : !!@style.value@{stock_activity.stock_52_wk_high:<7.2f}")
        dctx.panel("valuation").add_line("@style.key@ Mkt Cap    : !!@style.value@{stock_activity.market_cap:<7.2f}!!@style.value@{stock_activity.market_cap_unit:<s}")
        dctx.panel("valuation").add_line("@style.key@ Volume     : !!@style.value@{stock_activity.volume:<12.0f}")
        dctx.panel("valuation").add_line("@style.key@ Avg Vol    : !!@style.value@{stock_activity.avg_volume:<12.0f}")
        # dctx.panel("valuation").add_line("@style.key@ Dividend   : !!@style.value@{financial.dividend:<5.2f} !!@style.value@({financial.dividend_percent:<5.2f} %)")
        # dctx.panel("valuation").add_line("@style.key@ Beta       : !!@style.value@{technical.beta:<5.2f}")
        dctx.panel("valuation").add_line("@style.empty_line@")
        dctx.panel("valuation").add_line("@style.empty_line@")

        # Create URL panel
        dctx.add_panel("url", (51, 1), (0, 12))
        dctx.panel("url").add_line("@style.logo@ {overview.url:<50s}")

        #===================================
        # Create views
        #===================================
        # Two ways to add view positions. Either using paths or using direct values

        dctx.add_view("main")
        dctx.view("main").add_panel("overview") # This will add the first panel at position (0, 0)
        dctx.view("main").add_panel("valuation", ["overview.width", "overview.pos_y"])
        dctx.view("main").add_panel("url", ["overview.pos_x", "overview.height"])

    @staticmethod
    def get_stock_chart_html(
        ticker="AAPL", 
        watchlist=["AAPL"], 
        container_id="tradingview_60e16",
        autosize=True,
        timezone="Europe/London",
        theme="light",
        style=2,
        locale="en",
        toolbar_bg="f1f3f6",
        enable_publishing=False,
        withdateranges=True,
        date_range="YTD",
        hide_side_toolbar=False,
        allow_symbol_change=True,
        details=True,
        hotlist=True,
        calendar=True,
        studies=["CRSI@tv-basicstudies", "VolatilityIndex@tv-basicstudies"],
        ):

        list_pattern = lambda tik: '"{}",'.format(tik)

        if not watchlist:
            watchlist = [ticker]
    
        watchlist_str = ""
        for t in watchlist:
            watchlist_str += list_pattern(t)
        watchlist_str = watchlist_str[:-1]

        studies_str = ""
        if studies:
            studies_msg = '    "studies": [{studies_list}],'
            studies_list = ""
            for s in studies:
                studies_list += list_pattern(s)
            studies_list = studies_list[:-1]
            studies_str = studies_msg.format(studies_list=studies_list) 

        ticker_str              = ticker
        container_id_str        = container_id
        autosize_str            = str(autosize).lower()
        timezone_str            = timezone
        theme_str               = theme
        style_str               = str(style)
        locale_str              = locale
        toolbar_bg_str          = toolbar_bg
        enable_publishing_str   = str(enable_publishing).lower()
        withdateranges_str      = str(withdateranges).lower()
        date_range_str          = date_range.upper()
        hide_side_toolbar_str   = str(hide_side_toolbar).lower()
        allow_symbol_change_str = str(allow_symbol_change).lower()
        details_str             = str(details).lower()
        hotlist_str             = str(hotlist).lower()
        calendar_str            = str(calendar).lower()

        html = (
            '<!-- TradingView Widget BEGIN -->'
            '<div class="tradingview-widget-container">'
            '    <div id="{container_id}"></div>'
            '    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>'
            '    <script type="text/javascript">'
            '    new TradingView.widget('
            '    {{'
            '    "autosize": {autosize},'
            '    "symbol": "{ticker}",'
            '    "timezone": "{timezone}",'
            '    "theme": "{theme}",'
            '    "style": "{style}",'
            '    "locale": "{locale}",'
            '    "toolbar_bg": "#{toolbar_bg}",'
            '    "enable_publishing": {enable_publishing},'
            '    "withdateranges": {withdateranges},'
            '    "range": "{date_range}",'
            '    "hide_side_toolbar": {hide_side_toolbar},'
            '    "allow_symbol_change": {allow_symbol_change},'
            '    "watchlist": ['
            '        {watchlist}'
            '    ],'
            '    "details": {details},'
            '    "hotlist": {hotlist},'
            '    "calendar": {calendar},'
            '    {studies}'
            '    "container_id": "{container_id}"'
            '    }}'
            '    );'
            '    </script>'
            '</div>'
            '<!-- TradingView Widget END -->'
        ).format(
            container_id=container_id_str,
            autosize=autosize_str,
            ticker=ticker_str,
            timezone=timezone_str,
            theme=theme_str,
            style=style_str,
            locale=locale_str,
            toolbar_bg=toolbar_bg_str,
            enable_publishing=enable_publishing_str,
            withdateranges=withdateranges_str,
            date_range=date_range_str,
            hide_side_toolbar=hide_side_toolbar_str,
            allow_symbol_change=allow_symbol_change_str,
            watchlist=watchlist_str,
            details=details_str,
            hotlist=hotlist_str,
            calendar=calendar_str,
            studies=studies_str
        )
        return html

    @staticmethod
    def _update_data_setting(smng, setting_path, old_value, new_value, wctx):
        pass
    
    @staticmethod
    def _update_html_data_setting(smng, setting_path, old_value, new_value, wctx):
        keys = setting_path.split(".")
        wctx_key = ".".join( [keys[2], keys[3], keys[4]] )
        util.misc.DictUtil.set_by_path(wctx._webviews, wctx_key, new_value)

    @staticmethod
    def generate_webview_ctx(wctx):
        wctx.add_webview(
            webview_id="window_1",
            window_title="Stock Chart", 
            html_callback=TradingViewProvider.get_stock_chart_html,
            fullscreen=False,
            frameless=False,
            show=True,
            debug=wctx._debug
        )

        wctx.webview("window_1").add_html_data_setting("ticker", "AAPL", set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("watchlist", ["AAPL", "AMD"], set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("container_id", "tradingview_60e16", set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("autosize", True, set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("timezone", "Europe/London", set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("theme", "light", set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("style", 2, set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("locale", "en", set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("toolbar_bg", "f1f3f6", set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("enable_publishing", False, set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("withdateranges", True, set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("date_range", "YTD", set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("hide_side_toolbar", False, set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("allow_symbol_change", True, set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("details", True, set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("hotlist", True, set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("calendar", True, set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)
        wctx.webview("window_1").add_html_data_setting("studies", ["CRSI@tv-basicstudies", "VolatilityIndex@tv-basicstudies"], set_callback=TradingViewProvider._update_html_data_setting, set_user_data=wctx)

    def _webview_process_impl(self, wctx, ticker_list):
        wctx.webview("window_1").set_html_data_setting("ticker", ticker_list[0])
        wctx.webview("window_1").set_html_data_setting("watchlist", ticker_list)

    def data_parser_1(self, URL, data, data_ctx):
        pass
