import urllib3

__all__ = [
    'get_URL_data'
]

http = urllib3.PoolManager()

def get_URL_data(
    URL,
    http_pool_manager=http,
    headers={'User-Agent': 'Mozilla/5.0'},
    verbose=False):
    """ Return data from URL
    """
    res = http_pool_manager.request('GET', URL, headers=headers)

    if res.status==200:
        return res.data.decode("utf-8")
    else:
        raise urllib3.exceptions.ResponseError