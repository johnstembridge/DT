import calendar
import datetime
import time
import math
import re
import os
from email.utils import parseaddr
import globals.config as config


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


def encode_date_formal(date, cert=False):
    # result is in the form 8th September 2013
    if date is None:
        return ''
    de = {1: 'st', 2: 'nd', 3: 'rd', 21: 'st', 22: 'nd', 23: 'rd', 31: 'st'}

    def custom_strftime(format, t):
        return time.strftime(format, t).replace('{TH}', str(t[2]) + de.get(t[2], 'th'))

    if isinstance(date, str):
        date = datetime.datetime.strptime(date, '%Y/%m/%d')
    if cert:
        return custom_strftime('{TH} day of %B %Y', date.timetuple())
    else:
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


def fmt_date(date, fmt='%d/%m/%Y'):
    if not date:
        return ''
    return date.strftime(fmt)


def sql_fmt_date(date):
    return '"' + fmt_date(date,'%Y-%m-%d') + '"'


def parse_date(ymd, sep='/', reverse=False, default=datetime.datetime.now().date()):
    if type(ymd) is datetime.date:
        return ymd
    else:
        if len(ymd) > 0:
            date = ymd.split(sep)
            if reverse:
                date = date[::-1]
            return datetime.date(int(date[0]), int(date[1]), int(date[2]))
        else:
            return default


def valid_date(date, fmt='%d/%m/%Y'):
    try:
        d = datetime.datetime.strptime(date, fmt)
    except ValueError:
        return False
    else:
        return True


def in_date_range(date, date_from, date_to):
    if date and date_from and date_to:
        return date_from <= date <= date_to
    else:
        return False


def current_year():
    return datetime.datetime.now().year


def current_year_end():
    date = config.get('next_renewal_date')
    return parse_date(date, reverse=True)

# endregion


# region lists

def unique(item_list):
    # retains order
    res = []
    for item in item_list:
        if item not in res:
            res.append(item)
    return res


def take(n, item_list):
    l = len(item_list)
    if l < n:
        return item_list + [None] * (n - l)
    elif l == n:
        return item_list
    elif l > n:
        return item_list[:n]


def pop_next(str, sep):
    i = str.find(sep)
    if i == -1:
        return str, None
    else:
        head = str[:i]
        tail = str[i + 1:]
        return head, tail


def force_list(x):
    if type(x) is tuple:
        x = list(x)
    if type(x) is not list:
        x = [x]
    return x


def gen_to_list(gen):
    # force evaluation of a generator
    return [x for x in gen]


def first_or_default(list, default):
    if len(list) > 0:
        return list[0]
    else:
        return default


def last_or_default(list, default):
    if len(list) > 0:
        return list[-1]
    else:
        return default


def list_from_dict(dict, keys):
    return [dict.get(item, None) for item in keys]

# endregion


# region files

def file_delimiter(filename):
    file_type = (filename.split('.'))[-1]
    if file_type == 'csv':
        delimiter = ','
    elif file_type == 'tab':
        delimiter = ':'
    elif file_type == 'txt':
        delimiter = '\t'
    else:
        delimiter = ' '
    return delimiter


def delete_file(file):
    if os.path.isfile(file):
        os.remove(file)
# endregion


def get_digits(text):
    return ''.join(list(filter(str.isdigit, text)))


def is_valid_email(email):
    res = parseaddr(email)
    return len(res[1]) > 0


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


def remove(string, chars):
    return ''.join([c for c in string if c not in chars])


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
    return sum(values) / max(len(values), 1)


def html_escape(text):
    return text.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')


def html_unescape(text):
    return text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')


def yes_no(true_false):
    return 'yes' if true_false else 'no'


def match_string(a, b):
    a = remove(a.lower(), ' ')
    b = remove(b.lower(), ' ')
    return a == b