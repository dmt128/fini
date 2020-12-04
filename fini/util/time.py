import os, time, datetime, pytz

__all__ = [
    'get_local_timezone_as_string', 'get_datetime_now_as_string', 'get_datetime_from_string',
    'datetime_diff_from_strings',
]

def get_local_timezone_as_string():
    return time.strftime("%Z", time.gmtime())

def get_datetime_now_as_string(timezone=get_local_timezone_as_string(), format="%b %d, %Y %I:%M %p %Z"):
    tz = pytz.timezone(timezone) 
    dt = datetime.datetime.now(tz)
    return dt.strftime(format)

def get_datetime_from_string(datetime_str, timezone=get_local_timezone_as_string(), format="%b %d, %Y %I:%M %p %Z"):
    os.environ['TZ'] = timezone
    time.tzset()
    datetime_str = datetime_str.replace("ET", "EST")
    dt = datetime.datetime.strptime(datetime_str, format)
    os.environ['TZ'] = ""
    time.tzset()
    return dt

def datetime_diff_from_strings(datetime_t0, datetime_t1, 
    tz_t0 = get_local_timezone_as_string(), 
    tz_t1 = get_local_timezone_as_string(), 
    format="%b %d, %Y %I:%M %p %Z"):
    t0 = get_datetime_from_string(datetime_t0, tz_t0, format)  
    t1 = get_datetime_from_string(datetime_t1, tz_t1, format)
    return t1 - t0    


