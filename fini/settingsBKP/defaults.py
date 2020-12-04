from .. import util

__all__ = [
    'get_default_settings', 'get_default_cache',
]

def get_default_settings(base_config=None):
    return {
        'version': 1,

        #=====================================================
        # Global settings
        #=====================================================
        'global': {
            'prompt': {
                'colour': "#ff0000",
                'cmd_colour': "#ff8400",
                'message': "fini >> ",
            },
            'auto_save_on_exit': False,   
            'path' : {
                'config': base_config if base_config else "",
                'data': os.path.join(base_config, "data") if base_config else "",
                'cache': os.path.join(base_config, "cache") if base_config else "",
                'stocks': os.path.join(base_config, "cache", "stocks") if base_config else "",
                'log': os.path.join(base_config, "log") if base_config else "",
                'cache_file': os.path.join(base_config, "cache", "stocks_cache.json") if base_config else "",
                'settings_file': os.path.join(base_config, "settings.json") if base_config else "",
            },
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
        # Theme settings
        #=====================================================
        'theme' : {

        }
    }

def get_default_cache():
    return {
        'version': 1,
        # 'last_updated': util.time.get_datetime_now_as_string(),

        #=====================================================
        # Stocks cache
        #=====================================================
        'stocks': {
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
        },

        #=====================================================
        # Market cache
        #=====================================================
        'market': {

        }
    }