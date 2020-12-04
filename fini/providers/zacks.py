from .. managers import provider
from .. import util
import re

__all__ = ['ZacksProvider']
__docformat__ = 'restructuredtext'

class ZacksProvider(provider.ProviderBase):
    def __init__(self, *args, **kwargs):
        # We need to call the superclass __init__ here.
        # The superclass __init__ calls some initialisation code that is 
        # necessary for the correct operation of this class
        super(ZacksProvider, self).__init__(*args, **kwargs)

    @staticmethod
    def provider_id():
        return "zacks"

    @staticmethod
    def generate_URL_ctx(uctx, provider):
        uctx.add_url("https://www.zacks.com/stock/quote/{ticker}?q={ticker}", provider.data_parser_1)
        uctx.add_url("https://www.zacks.com/stock/quote/{ticker}/detailed-estimates", provider.data_parser_2)
        uctx.add_url("https://www.zacks.com/stock/research/{ticker}/brokerage-recommendations", provider.data_parser_3)

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
        data.add_entry("valuation.date_current_qtr", [])
        data.add_entry("valuation.date_next_qtr", [])
        data.add_entry("valuation.date_current_yr", [])
        data.add_entry("valuation.date_next_yr", [])
        data.add_entry("valuation.eps_current_qtr", [])
        data.add_entry("valuation.eps_last_qtr", [])
        data.add_entry("valuation.eps_current_yr", [])
        data.add_entry("valuation.eps_last_yr", [])
        data.add_entry("valuation.eps_next_yr", [])
        data.add_entry("valuation.eps_diluted_ttm", [])

        data.add_entry("valuation.eps_growth_current_qtr", [])
        data.add_entry("valuation.eps_growth_next_qtr", [])
        data.add_entry("valuation.eps_growth_current_yr", [])
        data.add_entry("valuation.eps_growth_next_yr", [])
        data.add_entry("valuation.eps_growth_past_5_yr", [])
        data.add_entry("valuation.eps_growth_next_5_yr", [])

        data.add_entry("valuation.eps_growth_ind_current_qtr", [])
        data.add_entry("valuation.eps_growth_ind_next_qtr", [])
        data.add_entry("valuation.eps_growth_ind_current_yr", [])
        data.add_entry("valuation.eps_growth_ind_next_yr", [])
        data.add_entry("valuation.eps_growth_ind_past_5_yr", [])
        data.add_entry("valuation.eps_growth_ind_next_5_yr", [])

        data.add_entry("valuation.eps_growth_snp_current_qtr", [])
        data.add_entry("valuation.eps_growth_snp_next_qtr", [])
        data.add_entry("valuation.eps_growth_snp_current_yr", [])
        data.add_entry("valuation.eps_growth_snp_next_yr", [])
        data.add_entry("valuation.eps_growth_snp_past_5_yr", [])
        data.add_entry("valuation.eps_growth_snp_next_5_yr", [])

        data.add_entry("valuation.forward_pe_f1", [])
        data.add_entry("valuation.peg_ratio", [])

        #===================================
        # Financial
        #===================================
        data.add_entry("financial.dividend", [])
        data.add_entry("financial.dividend_percent", [])
        data.add_entry("financial.next_earnings_date", [])

        #===================================
        # Technical
        #===================================
        data.add_entry("technical.beta", [])

        #===================================
        # Zacks ESP
        #===================================
        data.add_entry("zacks_esp.earnings_esp", [])
        data.add_entry("zacks_esp.last_esp_surprise", [])
        data.add_entry("zacks_esp.esp_qtr_1_date", [])
        data.add_entry("zacks_esp.esp_qtr_1_reported", [])
        data.add_entry("zacks_esp.esp_qtr_1_estimate", [])
        data.add_entry("zacks_esp.esp_qtr_1_difference", [])
        data.add_entry("zacks_esp.esp_qtr_1_surprise", [])
        data.add_entry("zacks_esp.esp_qtr_2_date", [])
        data.add_entry("zacks_esp.esp_qtr_2_reported", [])
        data.add_entry("zacks_esp.esp_qtr_2_estimate", [])
        data.add_entry("zacks_esp.esp_qtr_2_difference", [])
        data.add_entry("zacks_esp.esp_qtr_2_surprise", [])
        data.add_entry("zacks_esp.esp_qtr_3_date", [])
        data.add_entry("zacks_esp.esp_qtr_3_reported", [])
        data.add_entry("zacks_esp.esp_qtr_3_estimate", [])
        data.add_entry("zacks_esp.esp_qtr_3_difference", [])
        data.add_entry("zacks_esp.esp_qtr_3_surprise", [])
        data.add_entry("zacks_esp.esp_qtr_4_date", [])
        data.add_entry("zacks_esp.esp_qtr_4_reported", [])
        data.add_entry("zacks_esp.esp_qtr_4_estimate", [])
        data.add_entry("zacks_esp.esp_qtr_4_difference", [])
        data.add_entry("zacks_esp.esp_qtr_4_surprise", [])

        #===================================
        # Zacks Rank
        #===================================
        data.add_entry("zacks_rank.zacks_rank", [])
        data.add_entry("zacks_rank.zacks_trend", [])
        data.add_entry("zacks_rank.zacks_score_value", [])
        data.add_entry("zacks_rank.zacks_score_growth", [])
        data.add_entry("zacks_rank.zacks_score_momentum", [])
        data.add_entry("zacks_rank.zacks_score_total", [])
        data.add_entry("zacks_rank.sector_rank", [])
        data.add_entry("zacks_rank.industry_rank", [])
    
    @staticmethod
    def generate_settings(settings):
        #===================================
        # Create panels
        #===================================
        settings.add_setting("option1", 500)
        settings.add_setting("option2", True)
        settings.add_setting("option3", 3.4)
        settings.add_setting("option4", "Test Option")
        # settings.add_fmt_setting("style.panel_background", "!Back.MAGENTA")
        # settings.add_fmt_setting("style.empty_line",       "!{style.panel_background}")
        # settings.add_fmt_setting("style.header",           "!Fore.YELLOW + Style.BRIGHT + Back.BLUE")
        # settings.add_fmt_setting("style.header_light",     "!Fore.YELLOW + Style.NORMAL + Back.BLUE")
        # settings.add_fmt_setting("style.key",              "!Fore.CYAN   + Style.NORMAL + {style.panel_background}")
        # settings.add_fmt_setting("style.key_2",            "!Fore.CYAN   + Style.BRIGHT + {style.panel_background}")
        # settings.add_fmt_setting("style.value",            "!Fore.WHITE  + Style.NORMAL + {style.panel_background}")
        # settings.add_fmt_setting("style.value_positive",   "!Fore.GREEN  + Style.BRIGHT + {style.panel_background}")
        # settings.add_fmt_setting("style.value_negative",   "!Fore.RED    + Style.NORMAL + {style.panel_background}")
        # settings.add_fmt_setting("style.logo",             "!Fore.YELLOW + Style.BRIGHT + {style.panel_background}")
        # settings.add_condition("condition_1", ["{data}>= 0", "{data}<0"] ,["style.value_positive", "style.value_negative"])
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
        dctx.add_panel("overview", (34, 13), (0, 0))
        dctx.panel("overview").add_line("@style.header@ {overview.ticker:5s}!!@style.header_light@  [{overview.exchange:^10s}]") 
        dctx.panel("overview").add_line("@style.key@ {overview.company:<s}")
        dctx.panel("overview").add_line("@style.key@ Sec: !!@style.value@{overview.sector:<s}")
        dctx.panel("overview").add_line("@style.key@ Ind: !!@style.value@{overview.industry:<s}")
        dctx.panel("overview").add_line("@style.key@ Sub: !!@style.value@{overview.sub_industry:<s}")
        dctx.panel("overview").add_line("@style.key@ Cou: !!@style.value@{overview.country:<s}")
        dctx.panel("overview").add_line("@style.key@ Upd: !!@style.value@{overview.updated:<s}")
        dctx.panel("overview").add_line("@style.logo@                   _              ")
        dctx.panel("overview").add_line("@style.logo@                  | |             ")
        dctx.panel("overview").add_line("@style.logo@  ____ __ _   ___ | | __ ___      ")
        dctx.panel("overview").add_line("@style.logo@ |_  // _` | / __|| |/ // __|     ")
        dctx.panel("overview").add_line("@style.logo@  / /| (_| || (__ |   < \__ \     ")
        dctx.panel("overview").add_line("@style.logo@ /___|\__,_| \___||_|\_\|___/     ")
        # dctx.panel("overview").add_line("@logo@0123456789012345678901234567890123")

        # Create valuation panel
        dctx.add_panel("valuation", (30, 14), (34, 0))
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
        dctx.panel("valuation").add_line("@style.key@ Dividend   : !!@style.value@{financial.dividend:<5.2f} !!@style.value@({financial.dividend_percent:<5.2f} %)")
        dctx.panel("valuation").add_line("@style.key@ Beta       : !!@style.value@{technical.beta:<5.2f}")
        dctx.panel("valuation").add_line("@style.empty_line@")

        # Create URL panel
        dctx.add_panel("url", (51, 1), (0, 13))
        dctx.panel("url").add_line("@style.logo@ {overview.url:<50s}")

        #===================================
        # Create views
        #===================================
        # Two ways to add view positions. Either using paths or using direct values

        dctx.add_view("main")
        dctx.view("main").add_panel("overview") # This will add the first panel at position (0, 0)
        dctx.view("main").add_panel("valuation", ["overview.width", "overview.pos_y"])
        dctx.view("main").add_panel("url", ["overview.pos_x", "overview.height"])

        # Silly test view
        dctx.add_view("big")
        dctx.view("big").add_panel("overview", [0, 0])
        dctx.view("big").add_panel("valuation", [85, 0])
        dctx.view("big").add_panel("url", [50, 22])
    
    def data_parser_1(self, URL, data, data_ctx):
        #====================================================
        # Ticker Symbol
        #====================================================
        m = re.search("<!--//www.zacks.com/stock/quote/(.*)\\?", data)
        if m:
            data_ctx.set_data( 'overview.ticker', m.group(1) )

        data_ctx.set_data( 'overview.url', URL )

        #====================================================
        # Exchange
        #====================================================
        # e.g. <h2>(Delayed Data from NSDQ)</h2>
        m = re.search("<h2>\\(Delayed Data from (.*)\\)</h2>", data)
        if m:
            data_ctx.set_data( 'overview.exchange', m.group(1) )
    
        #====================================================
        # Company
        #====================================================
        m = re.search("<a href=\"/stock/quote/(.*)\">(.*) \\((.*)\\)</a>", data)
        if m:
            data_ctx.set_data( 'overview.company', m.group(2).replace(',', '') ) # remove commas

        #====================================================
        # Updated
        #====================================================
        # e.g <span id="timestamp">Nov 13, 2020 12:45 PM</span>
        m = re.search("<span id=\"timestamp\">(.*)</span>", data)
        if m:
            data_ctx.set_data( 'overview.updated', m.group(1) + " ET" )
    
        #====================================================
        # Requested
        #====================================================
        data_ctx.set_data( 'overview.requested', util.time.get_datetime_now_as_string() )

        #====================================================
        # Sector
        #====================================================
        m = re.search("<a href=\"https://www.zacks.com/stocks/industry-rank/sector/(.*)\">(.*)</a><span", data)
        if m:
            data_ctx.set_data( 'overview.sector', m.group(2) )

        #====================================================
        # Industry
        #====================================================
        m = re.search("</span><a href=\"https://www.zacks.com/stocks/industry-rank/industry/(.*)\">(.*)</a>", data)
        if m:
            ind = m.group(2).split("-")
            if len(ind) == 1:
                data_ctx.set_data( 'overview.industry', ind[0] )
            if len(ind) == 2:
                data_ctx.set_data( 'overview.industry', ind[0].replace(" ", "") )
                data_ctx.set_data( 'overview.sub_industry', ind[1].replace(" ", "") )

        #====================================================
        # Country
        #====================================================
        m = re.search("<p class=\"last_price\">\$(.*)<span> (.*)</span></p>", data)
        if m:
            data_ctx.set_data( 'stock_activity.stock_price', float(m.group(1).replace(",", "").replace("NA", "0")) )
            data_ctx.set_data( 'stock_activity.stock_currency', m.group(2) )

        m = re.search("<div id=\"get_volume\" class=\"hide\">(.*)</div>", data)
        if m:
            data_ctx.set_data( 'stock_activity.volume', int(m.group(1).replace(",", "").replace("NA", "0")) )

        m = re.search("id=\"net_change\"> (.*) \((.*)%\)</p>", data)
        if m:
            pr = m.group(1)
            if pr[0] == "+":
                data_ctx.set_data( 'stock_activity.change_price', float(m.group(1).replace("+", "")) )
                data_ctx.set_data( 'stock_activity.change_percent', float(m.group(2).replace("+", "")) )
            elif pr[0] == "-":
                data_ctx.set_data( 'stock_activity.change_price', -1*float(m.group(1).replace("-", "")) )
                data_ctx.set_data( 'stock_activity.change_percent', -1*float(m.group(2).replace("-", "")) )

        m = re.search("<td class=\"alpha\">Open</td>\n                    <td>(.*)</td>", data)
        if m:
            data_ctx.set_data( 'stock_activity.stock_open', float(m.group(1).replace(",", "").replace("NA", "0")) )

        m = re.search("<td class=\"alpha\">Day Low</td>\n                    <td>(.*)</td>", data)
        if m:
            data_ctx.set_data( 'stock_activity.stock_day_low', float(m.group(1).replace(",", "").replace("NA", "0")) )

        m = re.search("<td class=\"alpha\">Day High</td>\n                    <td>(.*)</td>", data)
        if m:
            data_ctx.set_data( 'stock_activity.stock_day_high', float(m.group(1).replace(",", "").replace("NA", "0")) )

        m = re.search("<td class=\"alpha\">52 Wk Low</td>\n                    <td>(.*)</td>", data)
        if m:
            data_ctx.set_data( 'stock_activity.stock_52_wk_low', float(m.group(1).replace(",", "").replace("NA", "0")) )

        m = re.search("<td class=\"alpha\">52 Wk High</td>\n                    <td>(.*)</td>", data)
        if m:
            data_ctx.set_data( 'stock_activity.stock_52_wk_high', float(m.group(1).replace(",", "").replace("NA", "0")) )

        m = re.search("<td class=\"alpha\">Avg. Volume</td>\n                    <td><span>(.*)</span></td>", data)
        if m:
            data_ctx.set_data( 'stock_activity.avg_volume', int(m.group(1).replace(",", "").replace("NA", "0")) )

        m = re.search("<td class=\"alpha\">Market Cap</td>\n                    <td><span>(.*) (.*)</span></td>", data)
        if m:
            data_ctx.set_data( 'stock_activity.market_cap', float(m.group(1).replace(",", "").replace("NA", "0")) )
            data_ctx.set_data( 'stock_activity.market_cap_unit', m.group(2) )

        m = re.search("Dividend</a></td>\n                    <td><span>(.*) \( (.*)%\)</span>", data)
        if m:
            data_ctx.set_data( 'financial.dividend', float(m.group(1).replace(",", "").replace("NA", "0")) )
            data_ctx.set_data( 'financial.dividend_percent', float(m.group(2)) )

        m = re.search("Beta</a></td>\n                    <td><span>(.*)</span>", data)
        if m:
            data_ctx.set_data( 'technical.beta', float(m.group(1).replace(",", "").replace("NA", "0")) )

        m = re.search("<p class=\"premium\"><a href=\"//www.zacks.com/premium/esp-buy?adid=zp_esptooltip&icid=zpi_esptooltip\">See the Full List of Stocks To Beat Earnings</a></p><!--MSG:17305-->\n                        </div>\n                    </td>\n                    <td class="">(.*)%</td>\n                </tr>\n                <tr>\n", data)
        if m:
            data_ctx.set_data( 'zacks_esp.earnings_esp', float(m.group(1).replace(",", "").replace("NA", "0")) )

        # m = re.search("Most Accurate Est</a></td>\n                    <td>(.*)</td>", data)
        # if m:
        #     data_ctx.set_data( 'most_accurate_est', float(m.group(1).replace(",", "").replace("NA", "0")) )

        # m = re.search("Current Qtr Est</a></td>\n                    <td>(.*)</td>", data)
        # if m:
        #     data_ctx.set_data('current_qtr_est', float(m.group(1).replace(",", "").replace("NA", "0"))

        # m = re.search("Current Yr Est</a></td>\n                    <td>(.*)</td>", data)
        # if m:
        #     data_ctx.set_data('current_yr_est', float(m.group(1).replace(",", "").replace("NA", "0"))

        m = re.search("<td><sup class=\"spl_sup_text\">(.*)</sup>(.*)</td>", data)
        if m:
            if not m.group(1):
                data_ctx.set_data( 'financial.next_earnings_date', m.group(2) )
            else:
                data_ctx.set_data( 'financial.next_earnings_date', m.group(1).replace("*", "") + " " + m.group(2) )

        # m = re.search("Prior Year EPS</td>\n                    <td>(.*)</td>", data)
        # if m:
        #     data_ctx.set_data('prior_year_eps', float(m.group(1).replace(",", "").replace("NA", "0"))

        # m = re.search("Exp EPS Growth <span class=\"year\">\(3-5yr\)</span></a><p class=\"up float_right\">(.*)%</p></td>", data)
        # if m:
        #     data_ctx.set_data('exp_eps_growth_3_5_yr', float(m.group(1).replace(",", "").replace("NA", "0"))

        m = re.search("Forward PE</a></td>\n                    <td>(.*)</td>", data)
        if m:
            data_ctx.set_data( 'valuation.forward_pe_f1', float(m.group(1).replace(",", "").replace("NA", "0")) )

        m = re.search("PEG Ratio</a></td>\n                    <td>(.*)</td>", data)
        if m:
            data_ctx.set_data( 'valuation.peg_ratio', float(m.group(1).replace(",", "").replace("NA", "0")) )

        #====================================================
        # Zacks Rank
        #====================================================
        m = re.search("<p class=\"rank_view\">\n                       (.*)<span class=\"sr-only\"> of 5</span>", data)
        if m:
            data_ctx.set_data( 'zacks_rank.zacks_rank', m.group(1) )
    
        #====================================================
        # Zacks Trend
        #====================================================
        m = re.search("<img src=\"https://staticx.zacks.com/images/newzp_(.*).gif\" alt=\"(.*)\" border=\"0\" class=\"premium_resicon\"/>", data)
        if m:
            data_ctx.set_data( 'zacks_rank.zacks_trend', m.group(2).split(" ")[1] )

        #====================================================
        # Zacks Score Value
        #====================================================
        m = re.search("\"composite_val\">(.)</span> Value <span", data)
        if m:
            data_ctx.set_data( 'zacks_rank.zacks_score_value', m.group(1) )

        #====================================================
        # Zacks Score Growth
        #====================================================
        m = re.search("\"composite_val\">(.)</span> Growth <span", data)
        if m:
            data_ctx.set_data( 'zacks_rank.zacks_score_growth', m.group(1) )

        #====================================================
        # Zacks Score Momentum
        #====================================================
        m = re.search("\"composite_val\">(.)</span> Momentum <span", data)
        if m:
            data_ctx.set_data( 'zacks_rank.zacks_score_momentum', m.group(1) )

        #====================================================
        # Zacks Score Total
        #====================================================
        m = re.search("<span class=\"composite_val composite_val_vgm\">(.)</span> VGM</p>", data)
        if m:
            data_ctx.set_data( 'zacks_rank.zacks_score_total', m.group(1) )

        #====================================================
        # Sector Rank
        #====================================================
        m = re.search("<a href=\"/stocks/industry-rank/sector/(.*)\" ><span class=\"rank_direction\"> (.*)</span> (.*) </a>", data)
        if m:
            data_ctx.set_data( 'zacks_rank.sector_rank', m.group(2) + " " + m.group(3) )

        #====================================================
        # Industry Rank
        #====================================================
        m = re.search("<p class=\"rank_view\">\n<a href=\"/stocks/industry-rank/industry/(.*)\" class=\"status\">(.*)</a>                </p>", data)
        if m:
            data_ctx.set_data( 'zacks_rank.industry_rank', m.group(2) )
    

    def data_parser_2(self,  URL, website_data, data_ctx):
        pass
    

    def data_parser_3(self,  URL, website_data, data_ctx):
        pass
    













# def website_parser_stock(data):
#     result = {
#         "ticker": "N/A",
#         "exchange": "N/A",
#         "title": "N/A",
#         "updated": "N/A",
#         "requested": "N/A",
#         "sector": "N/A",
#         "industry": "N/A",
#         "sub_industry": "N/A",
#         "country": "N/A",
#         "stock_price": 0.0,
#         "change_price": 0.0,
#         "change_percent": 0.0,
#         "stock_open": 0.0,
#         "stock_day_low": 0.0,
#         "stock_day_high": 0.0,
#         "stock_52_wk_low": 0.0,
#         "stock_52_wk_high": 0.0,
#         "market_cap": 0.0,
#         "market_cap_unit": "B",
#         "volume": 0,
#         "avg_volume": 0,
#         "dividend": 0.0,
#         "dividend_percent": 0.0,
#         "beta": 0.0,
#         "earnings_esp": 0.0,
#         "most_accurate_est": 0.0,
#         "current_qtr_est": 0.0,
#         "current_yr_est": 0.0,
#         "exp_earnings_date": "-",
#         "prior_year_eps": 0.0,
#         "exp_eps_growth_3_5_yr": 0.0,
#         "forward_pe": 0.0,
#         "peg_ratio": 0.0,
#         "zacks_rank": "-",
#         "zacks_trend": "-",
#         "zacks_score_value": "-",
#         "zacks_score_growth": "-",
#         "zacks_score_momentum": "-",
#         "zacks_score_total": "-",
#         "sector_rank": "N/A",
#         "industry_rank": "N/A",
#     }

#     #====================================================
#     # Ticker Symbol
#     #====================================================
#     m = re.search("<!--//www.zacks.com/stock/quote/(.*)\\?", data)
#     if m:
#         data_ctx.set_data('ticker'] = m.group(1)

#     #====================================================
#     # Exchange
#     #====================================================
#     # e.g. <h2>(Delayed Data from NSDQ)</h2>
#     m = re.search("<h2>\\(Delayed Data from (.*)\\)</h2>", data)
#     if m:
#         data_ctx.set_data('exchange'] = m.group(1)
    
#     #====================================================
#     # Title
#     #====================================================
#     m = re.search("<a href=\"/stock/quote/(.*)\">(.*) \\((.*)\\)</a>", data)
#     if m:
#         data_ctx.set_data('title'] = m.group(2).replace(',', '') # remove commas

#     #====================================================
#     # Updated
#     #====================================================
#     # e.g <span id="timestamp">Nov 13, 2020 12:45 PM</span>
#     m = re.search("<span id=\"timestamp\">(.*)</span>", data)
#     if m:
#         data_ctx.set_data('updated'] = m.group(1) + " ET"
    
#     #====================================================
#     # Requested
#     #====================================================
#     data_ctx.set_data('requested'] = util.time.get_datetime_now_as_string()

#     #====================================================
#     # Sector
#     #====================================================
#     m = re.search("<a href=\"https://www.zacks.com/stocks/industry-rank/sector/(.*)\">(.*)</a><span", data)
#     if m:
#         data_ctx.set_data('sector'] = m.group(2)

#     #====================================================
#     # Industry
#     #====================================================
#     m = re.search("</span><a href=\"https://www.zacks.com/stocks/industry-rank/industry/(.*)\">(.*)</a>", data)
#     if m:
#         ind = m.group(2).split("-")
#         if len(ind) == 1:
#             data_ctx.set_data('industry'] = ind[0]
#         if len(ind) == 2:
#             data_ctx.set_data('industry'] = ind[0].replace(" ", "")
#             data_ctx.set_data('sub_industry'] = ind[1].replace(" ", "")

#     #====================================================
#     # Country
#     #====================================================
#     m = re.search("<p class=\"last_price\">\$(.*)<span> (.*)</span></p>", data)
#     if m:
#         data_ctx.set_data('stock_price'] = float(m.group(1).replace(",", "").replace("NA", "0"))
#         data_ctx.set_data('stock_currency'] = m.group(2)

#     m = re.search("<div id=\"get_volume\" class=\"hide\">(.*)</div>", data)
#     if m:
#         data_ctx.set_data('volume'] = int(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("id=\"net_change\"> (.*) \((.*)%\)</p>", data)
#     if m:
#         pr = m.group(1)
#         if pr[0] == "+":
#             data_ctx.set_data('change_price'] = float(m.group(1).replace("+", ""))
#             data_ctx.set_data('change_percent'] = float(m.group(2).replace("+", ""))
#         elif pr[0] == "-":
#             data_ctx.set_data('change_price'] = -1*float(m.group(1).replace("-", ""))
#             data_ctx.set_data('change_percent'] = -1*float(m.group(2).replace("-", ""))
        
#     m = re.search("<td class=\"alpha\">Open</td>\n                    <td>(.*)</td>", data)
#     if m:
#         data_ctx.set_data('stock_open'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("<td class=\"alpha\">Day Low</td>\n                    <td>(.*)</td>", data)
#     if m:
#         data_ctx.set_data('stock_day_low'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("<td class=\"alpha\">Day High</td>\n                    <td>(.*)</td>", data)
#     if m:
#         data_ctx.set_data('stock_day_high'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("<td class=\"alpha\">52 Wk Low</td>\n                    <td>(.*)</td>", data)
#     if m:
#         data_ctx.set_data('stock_52_wk_low'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("<td class=\"alpha\">52 Wk High</td>\n                    <td>(.*)</td>", data)
#     if m:
#         data_ctx.set_data('stock_52_wk_high'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("<td class=\"alpha\">Avg. Volume</td>\n                    <td><span>(.*)</span></td>", data)
#     if m:
#         data_ctx.set_data('avg_volume'] = int(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("<td class=\"alpha\">Market Cap</td>\n                    <td><span>(.*) (.*)</span></td>", data)
#     if m:
#         data_ctx.set_data('market_cap'] = float(m.group(1).replace(",", "").replace("NA", "0"))
#         data_ctx.set_data('market_cap_unit'] = m.group(2)

#     m = re.search("Dividend</a></td>\n                    <td><span>(.*) \( (.*)%\)</span>", data)
#     if m:
#         data_ctx.set_data('dividend'] = float(m.group(1).replace(",", "").replace("NA", "0"))
#         data_ctx.set_data('dividend_percent'] = float(m.group(2))

#     m = re.search("Beta</a></td>\n                    <td><span>(.*)</span>", data)
#     if m:
#         data_ctx.set_data('beta'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("<p class=\"premium\"><a href=\"//www.zacks.com/premium/esp-buy?adid=zp_esptooltip&icid=zpi_esptooltip\">See the Full List of Stocks To Beat Earnings</a></p><!--MSG:17305-->\n                        </div>\n                    </td>\n                    <td class="">(.*)%</td>\n                </tr>\n                <tr>\n", data)
#     if m:
#         data_ctx.set_data('earnings_esp'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("Most Accurate Est</a></td>\n                    <td>(.*)</td>", data)
#     if m:
#         data_ctx.set_data('most_accurate_est'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("Current Qtr Est</a></td>\n                    <td>(.*)</td>", data)
#     if m:
#         data_ctx.set_data('current_qtr_est'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("Current Yr Est</a></td>\n                    <td>(.*)</td>", data)
#     if m:
#         data_ctx.set_data('current_yr_est'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("<td><sup class=\"spl_sup_text\">(.*)</sup>(.*)</td>", data)
#     if m:
#         if not m.group(1):
#             data_ctx.set_data('exp_earnings_date'] = m.group(2)
#         else:
#             data_ctx.set_data('exp_earnings_date'] = m.group(1).replace("*", "") + " " + m.group(2)

#     m = re.search("Prior Year EPS</td>\n                    <td>(.*)</td>", data)
#     if m:
#         data_ctx.set_data('prior_year_eps'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("Exp EPS Growth <span class=\"year\">\(3-5yr\)</span></a><p class=\"up float_right\">(.*)%</p></td>", data)
#     if m:
#         data_ctx.set_data('exp_eps_growth_3_5_yr'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("Forward PE</a></td>\n                    <td>(.*)</td>", data)
#     if m:
#         data_ctx.set_data('forward_pe'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     m = re.search("PEG Ratio</a></td>\n                    <td>(.*)</td>", data)
#     if m:
#         data_ctx.set_data('peg_ratio'] = float(m.group(1).replace(",", "").replace("NA", "0"))

#     #====================================================
#     # Zacks Rank
#     #====================================================
#     m = re.search("<p class=\"rank_view\">\n                       (.*)<span class=\"sr-only\"> of 5</span>", data)
#     if m:
#         data_ctx.set_data('zacks_rank'] = m.group(1)
    
#     #====================================================
#     # Zacks Trend
#     #====================================================
#     m = re.search("<img src=\"https://staticx.zacks.com/images/newzp_(.*).gif\" alt=\"(.*)\" border=\"0\" class=\"premium_resicon\"/>", data)
#     if m:
#         data_ctx.set_data('zacks_trend'] = m.group(2).split(" ")[1]

#     #====================================================
#     # Zacks Score Value
#     #====================================================
#     m = re.search("\"composite_val\">(.)</span> Value <span", data)
#     if m:
#         data_ctx.set_data('zacks_score_value'] = m.group(1)

#     #====================================================
#     # Zacks Score Growth
#     #====================================================
#     m = re.search("\"composite_val\">(.)</span> Growth <span", data)
#     if m:
#         data_ctx.set_data('zacks_score_growth'] = m.group(1)

#     #====================================================
#     # Zacks Score Momentum
#     #====================================================
#     m = re.search("\"composite_val\">(.)</span> Momentum <span", data)
#     if m:
#         data_ctx.set_data('zacks_score_momentum'] = m.group(1)

#     #====================================================
#     # Zacks Score Total
#     #====================================================
#     m = re.search("<span class=\"composite_val composite_val_vgm\">(.)</span> VGM</p>", data)
#     if m:
#         data_ctx.set_data('zacks_score_total'] = m.group(1)

#     #====================================================
#     # Sector Rank
#     #====================================================
#     m = re.search("<a href=\"/stocks/industry-rank/sector/(.*)\" ><span class=\"rank_direction\"> (.*)</span> (.*) </a>", data)
#     if m:
#         data_ctx.set_data('sector_rank'] = m.group(2) + " " + m.group(3)

#     #====================================================
#     # Industry Rank
#     #====================================================
#     m = re.search("<p class=\"rank_view\">\n<a href=\"/stocks/industry-rank/industry/(.*)\" class=\"status\">(.*)</a>                </p>", data)
#     if m:
#         data_ctx.set_data('industry_rank'] = m.group(2)

#     return result

# def print_header(data, logo, x, y):
#     print(pos(x,y+0)  + format_header     + " {ticker:5s} [{exchange:^10s}]".format(**data) + " "*16 )
#     print(pos(x,y+1)  + format_section_1  + " {title:34s}".format(**data))
#     print(pos(x,y+2)  + format_section_2  + " Sec: {sector:29s}".format(**data))
#     print(pos(x,y+3)  + format_section_2  + " Ind: {industry:29s}".format(**data))
#     print(pos(x,y+4)  + format_section_2  + " Sub: {sub_industry:29s}".format(**data))
#     print(pos(x,y+5)  + format_section_2  + " Cou: {country:29s}".format(**data))
#     print(pos(x,y+6)  + format_section_3  + " Upd: {updated:29s}".format(**data))
#     print(pos(x,y+7)  + format_section_4  + logo["line_1"] )
#     print(pos(x,y+8)  + format_section_4  + logo["line_2"] )
#     print(pos(x,y+9)  + format_section_4  + logo["line_3"] )
#     print(pos(x,y+10) + format_section_4  + logo["line_4"] )
#     print(pos(x,y+11) + format_section_4  + logo["line_5"] )
#     print(pos(x,y+12) + format_section_4  + logo["line_6"] )

#     return 37 # Return width plus one


# def print_overview(data, x, y):
#     print(pos(x,y+0)  + format_header     + "{:^31s}".format("Stock Activity"))
#     print(pos(x,y+1)  + format_section_1  + " Stock Price: {stock_price:<7.2f} USD".format(**data) + "{:<6}".format(" ") )
#     if data["change_price"] > 0:
#         print(pos(x,y+2)  + format_section_1  + Fore.GREEN + "              {change_price:<5.2f} ({change_percent:<5.2f} %)".format(**data) + "{:<2}".format(" "))
#     elif data["change_price"] < 0:
#         print(pos(x,y+2)  + format_section_1  + Fore.RED   + "              {change_price:<5.2f} ({change_percent:<5.2f} %)".format(**data) + "{:<2}".format(" "))
#     else:
#         print(pos(x,y+2)  + format_section_1  + "              {change_price:<5.2f} ({change_percent:<5.2f} %)".format(**data) + "{:<2}".format(" "))
    
#     print(pos(x,y+3)  + format_section_1  + " Stock Open : {stock_open:<7.2f}".format(**data) + "{:<10}".format(" "))
#     print(pos(x,y+4)  + format_section_1  + " Day Low    : {stock_day_low:<7.2f}".format(**data) + "{:<10}".format(" "))
#     print(pos(x,y+5)  + format_section_1  + " Day High   : {stock_day_high:<7.2f}".format(**data) + "{:<10}".format(" "))
#     print(pos(x,y+6)  + format_section_1  + " 52 Wk Low  : {stock_52_wk_low:<7.2f}".format(**data) + "{:<10}".format(" "))
#     print(pos(x,y+7)  + format_section_1  + " 52 Wk High : {stock_52_wk_high:<7.2f}".format(**data) + "{:<10}".format(" "))
#     print(pos(x,y+8)  + format_section_2  + " Mkt Cap    : {market_cap:<7.2f} {market_cap_unit:<3}".format(**data) + "{:6}".format(" "))
#     print(pos(x,y+9)  + format_section_2  + " Volume     : {volume:<17}".format(**data))
#     print(pos(x,y+10) + format_section_2  + " Avg Vol    : {avg_volume:<17}".format(**data))
#     print(pos(x,y+11) + format_section_3  + " Dividend   : {dividend:<5.2f} ({dividend_percent:<5.2f} %)".format(**data) + "{:<2}".format(" "))
#     print(pos(x,y+12) + format_section_3  + " Beta       : {beta:<5.2f}".format(**data) + "{:<12}".format(" "))

#     return 32 # Return width plus one


# def print_earnings_data(data, x, y):
#     print(pos(x,y+0)  + format_header     + "{:^35s}".format("Key Earnings Data"))
#     print(pos(x,y+1)  + format_section_1  + " Earnings ESP   : {earnings_esp:<6.2f} %".format(**data) + "{:<9}".format(" "))
#     print(pos(x,y+2)  + format_section_2  + " Most Acc Est   : {most_accurate_est:<5.2f}".format(**data) + "{:<12}".format(" "))
#     print(pos(x,y+3)  + format_section_2  + " Current Qtr Est: {current_qtr_est:<7.2f}".format(**data) + "{:<10}".format(" "))
#     print(pos(x,y+4)  + format_section_2  + " Current Yr Est : {current_yr_est:<7.2f}".format(**data) + "{:<10}".format(" "))
#     print(pos(x,y+5)  + format_section_2  + " Exp Earnings D : {exp_earnings_date:<17s}".format(**data))
#     print(pos(x,y+6)  + format_section_2  + " Prior Year EPS : {prior_year_eps:<7.2f}".format(**data) + "{:<10}".format(" "))
#     print(pos(x,y+7)  + format_section_2  + " EPS Gr. (3-5yr): {exp_eps_growth_3_5_yr:<6.2f} %".format(**data) + "{:<9}".format(" "))
#     print(pos(x,y+8)  + format_section_2  + " Forward PE     : {forward_pe:<7.2f}".format(**data) + "[{:7.2f}] ".format(0.0))
#     print(pos(x,y+9)  + format_section_2  + " PEG Ratio      : {peg_ratio:<7.2f}".format(**data) + "[{:7.2f}] ".format(0.0))
#     print(pos(x,y+10) + format_empty_line + " "*35)
#     print(pos(x,y+11) + format_empty_line + " "*35)
#     print(pos(x,y+12) + format_empty_line + " "*35)

#     return 36 # Return width plus one


# def print_zacks_rank(data, x, y):
#     print(pos(x,y+0)  + format_header     + "{:^30s}".format("Zacks Rank"))
#     print(pos(x,y+1)  + format_section_1  + " Zacks Rank   : {zacks_rank:<14s}".format(**data) )
#     print(pos(x,y+2)  + format_section_1  + " Zacks Trend  : {zacks_trend:<14s}".format(**data) )
#     print(pos(x,y+3)  + format_section_2  + " Value        : {zacks_score_value:<14s}".format(**data) )
#     print(pos(x,y+4)  + format_section_2  + " Growth       : {zacks_score_growth:<14s}".format(**data) )
#     print(pos(x,y+5)  + format_section_2  + " Momentum     : {zacks_score_momentum:<14s}".format(**data) )
#     print(pos(x,y+6)  + format_section_2  + " Style Score  : {zacks_score_total:<14s}".format(**data))
#     print(pos(x,y+7)  + format_section_3  + " Sector Rank  : {:<14s}".format(" ") )
#     print(pos(x,y+8)  + format_section_3  + "  {sector_rank:<28s}".format(**data) )
#     print(pos(x,y+9)  + format_section_3  + " Industry Rank: {:<14s}".format(" ") )
#     print(pos(x,y+10) + format_section_3  + "  {industry_rank:<28s}".format(**data) )
#     print(pos(x,y+11) + format_empty_line + " "*30)
#     print(pos(x,y+12) + format_empty_line + " "*30)

#     return 31 # Return width plus one


# def print_zantalis_score(data, x, y):
#     print(pos(x,y+0)  + format_header     + "{:^30s}".format("Zantalis Score"))
#     print(pos(x,y+1)  + format_empty_line + " "*30)
#     print(pos(x,y+2)  + format_empty_line + " "*30)
#     print(pos(x,y+3)  + format_empty_line + " "*30)
#     print(pos(x,y+4)  + format_empty_line + " "*30)
#     print(pos(x,y+5)  + format_empty_line + " "*30)
#     print(pos(x,y+6)  + format_empty_line + " "*30)
#     print(pos(x,y+7)  + format_empty_line + " "*30)
#     print(pos(x,y+8)  + format_empty_line + " "*30)
#     print(pos(x,y+9)  + format_empty_line + " "*30)
#     print(pos(x,y+10) + format_empty_line + " "*30)
#     print(pos(x,y+11) + format_empty_line + " "*30)
#     print(pos(x,y+12) + format_empty_line + " "*30)

#     return 31


# def format_stock(data, logo, x, y):
#     x += print_header(data, logo, x, y)
#     x += print_overview(data, x, y)
#     x += print_earnings_data(data, x, y)
#     x += print_zacks_rank(data, x, y)
#     x += print_zantalis_score(data, x, y)
#     print(pos(0,y+13) + format_endline  + " {:66s}".format(create_URL_stock(data["ticker"])))

#     return 15 # Return height plus one
