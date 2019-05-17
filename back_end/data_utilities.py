import calendar
import datetime
import time
import math
import re


# region dates
def decode_date(wdm, y):
    # wdm is in the form Friday 28 April, y is year
    if wdm:
        try:
            a = wdm.strip().split(' ')
            d = int(re.findall(r'\d+', a[1])[0])
            m = calendar.month_name[0:13].index(a[-1])
            return datetime.date(y, m, d)
        except:
            return datetime.date.today()
    else:
        return None


def encode_date(date):
    # result is in the form Friday 28 April
    if date is None:
        return ''
    return date.strftime('%A %d %B')


def encode_date_short(date):
    # result is in the form Fri 28 Apr
    if date is None:
        return ''
    return date.strftime('%a %d %b')


def decode_date_formal(wdm):
    # wdm is in the form 8th September 2013
    if wdm is not None:
        try:
            a = wdm.split(' ')
            d = int(re.findall(r'\d+', a[0])[0])
            m = calendar.month_name[0:13].index(a[1])
            y = int(a[2])
            return datetime.date(y, m, d)
        except:
            return datetime.date.today()
    else:
        return None


def encode_date_formal(date):
    # result is in the form 8th September 2013
    if date is None:
        return ''
    de = {1: 'st', 2: 'nd', 3: 'rd', 21: 'st', 22: 'nd', 23: 'rd', 31: 'st'}

    def custom_strftime(format, t):
        return time.strftime(format, t).replace('{TH}', str(t[2]) + de.get(t[2], 'th'))

    if isinstance(date, str):
        date = datetime.datetime.strptime(date, '%Y/%m/%d')

    return custom_strftime('{TH} %B %Y', date.timetuple())


def decode_date_range(dr, year):
    # dr is in the form Friday 22 - Sunday 24 April, y is year
    dr = dr.split('-')
    month = (dr[1].split(' '))[-1]
    dr[0] = dr[0] + ' ' + month
    return [decode_date(d, year) for d in dr]


def coerce_fmt_date(x):
    if type(x) == datetime.date:
        x = fmt_date(x)
    return x


def fmt_date(date, fmt=None):
    if not fmt:
        fmt = '%d/%m/%Y'
    return date.strftime(fmt)


def parse_date(ymd, sep='/', reverse=False):

    if type(ymd) is datetime.date:
        return ymd
    else:
        if len(ymd) > 0:
            date = ymd.split(sep)
            if reverse:
                date = date[::-1]
            return datetime.date(int(date[0]), int(date[1]), int(date[2]))
        else:
            return datetime.datetime.now().date()


def in_date_range(date, date_from, date_to):
    if date and date_from and date_to:
        return date_from <= date <= date_to
    else:
        return False


def current_year():
    return datetime.datetime.now().year

# endregion


def normalise_name(all_names, name):
    i = lookup(all_names, name, case_sensitive=False)
    if i == -1:
        return name.title(), i
    else:
        return all_names[i], i


def sort_name_list(names):
    fl = [v.split(' ', 2) for v in names]
    fl.sort(key=lambda tup: (tup[1], tup[0]))
    return [n[0] + ' ' + n[1] for n in fl]


def lookup(item_list, items, index_origin=0, case_sensitive=None):
    res = []
    lower = case_sensitive is False
    if lower:
        item_list = [item.lower() for item in item_list]
    for item in force_list(items):
        if lower:
            item = item.lower()
        if item in item_list:
            i = index_origin + item_list.index(item)
        else:
            i = -1
        res.append(i)
    if type(items) is not list:
        res = res[0]
    return res


def force_list(x):
    if type(x) is tuple:
        x = list(x)
    if type(x) is not list:
        x = [x]
    return x


def force_lower(x):
    if type(x) is list:
        return [y.lower() for y in x]
    else:
        return x.lower()


def coerce(x, required_type):
    if x is not None and type(x) != required_type:
        x = required_type(x)
    return x


def fmt_num(num):
    return str(int(num) if num == math.floor(num) else num)


def parse_float(num, default=None):
    try:
        return float(num)
    except:
        return default


def fmt_curr(num):
    if num:
        res = '£{:,.2f}'.format(abs(num))
        if num < 0:
            res = '({})'.format(res)
    else:
        res = ''
    return res


def first_or_default(list, default):
    if len(list) > 0:
        return list[0]
    else:
        return default


def is_num(s):
    return isinstance(s, str) and s.replace('.', '', 1).isdigit()


def to_float(s):
    if is_num(s):
        return float(s)
    else:
        return 0


def to_bool(s):
    if s is None:
        return True
    if type(s) is bool:
        return s
    return s == 'True'


def dequote(string):
    if string:
        if string.startswith('"') and string.endswith('"'):
            string = string[1:-1]
    return string


def enquote(string):
    return string if len(string) == 0 else '"' + string + '"'


def my_round(float_num, dp=0):
    if dp == 0:
        return math.floor(float(float_num) + 0.5)
    else:
        return (math.floor(float(float_num * 10 ** dp) + 0.5)) / 10 ** dp


def mean(values):
    if type(first_or_default(values, 0)) == str:
        values = [float(v) for v in values]
    return sum(values)/max(len(values), 1)


def gen_to_list(gen):
    # force evaluation of a generator
    return [x for x in gen]


def html_escape(text):
    return text.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')


def html_unescape(text):
    return text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
