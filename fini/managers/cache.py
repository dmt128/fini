import os, json

__all__ = [
    'CacheManager'    
]

class CacheManager:
    def __init__(self, settings_manager, debug=False):
        self._smng = settings_manager
        self._debug = debug
        self._cache = {}

    def load_stock_data(self, provider, ticker_symbol):
        # Check to see if the stock data for this ticker symbol and provider is available.
        # If it is, load it and return it. If not then create the data file first and 
        # then load it and return it
        dir_path, abs_path = self._get_stock_data_paths(provider, ticker_symbol)

        if os.path.exists(abs_path):
            return self._load_stock_data(abs_path)
        else:
            self._create_stock_data_file(provider, dir_path, abs_path)
            return self._load_stock_data(abs_path)

    def save_stock_data(self, provider, ticker_symbol):
        dir_path, abs_path = self._get_stock_data_paths(provider, ticker_symbol)

        if os.path.exists(abs_path):
            self._save_stock_data(abs_path, provider.stock_data_ref() )
        else:
            self._create_stock_data_file(provider, dir_path, abs_path)
            self._save_stock_data(abs_path, provider.stock_data_ref() )
    
    def save_stock_data_dict(self, provider, ticker_symbol):
        for ticker_symbol in provider._data_dict.keys():
            dir_path, abs_path = self._get_stock_data_paths(provider, ticker_symbol)

            if os.path.exists(abs_path):
                self._save_stock_data(abs_path, provider.stock_data_dict_ref(ticker_symbol) )
            else:
                self._create_stock_data_file(provider, dir_path, abs_path)
                self._save_stock_data(abs_path, provider.stock_data_dict_ref(ticker_symbol) )

    def _format_ticker_file(self, provider_id, ticker_symbol):
        return provider_id + "_" + ticker_symbol.upper() + ".json"

    def _create_stock_data_absolute_path(self, provider_id, ticker_symbol=None):
        stocks_dir = self._smng.get_stocks_path()
        if ticker_symbol:
            return os.path.join( stocks_dir, provider_id, self._format_ticker_file(provider_id, ticker_symbol) )
        else:
            return os.path.join( stocks_dir, provider_id)

    def _get_stock_data_paths(self, provider, ticker_symbol):
        dir_path = self._create_stock_data_absolute_path(provider.provider_id())
        abs_path = self._create_stock_data_absolute_path(provider.provider_id(), ticker_symbol)
        
        return dir_path, abs_path

    def _create_stock_data_file(self, provider, dir_path, abs_path):
        # Check if directory exists. If not create it.
        access_rights = 0o755
        if not os.path.exists(dir_path):
            try:
                os.mkdir(dir_path, access_rights)
            except OSError:
                raise Exception ("Creation of {} failed".format(dir_path))
                
            else:
                if self._debug:
                    print ("Successfully created {}".format(dir_path))
        
        # Check if file exists. If not create it.
        if not os.path.exists(abs_path):
            try:
                empty_data = provider.stock_data_copy()
                with open(abs_path, 'w') as json_file:
                    json.dump(empty_data, json_file)

            except:
                raise Exception ("Creation of {} failed".format(abs_path))
                
            else:
                if self._debug:
                    print ("Successfully created {}".format(abs_path))


    def _load_stock_data(self, abs_path):
        with open(abs_path, 'r') as json_file:
            return json.load(json_file)
    
    def _save_stock_data(self, abs_path, data):
        with open(abs_path, 'w') as json_file:
            json.dump(data, json_file)

