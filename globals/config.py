import os
import json
from flask import url_for
from flask import request
from werkzeug.urls import url_parse, url_unparse, url_join


def read():
    file_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(file_path) as json_data_file:
        de_commented = ''.join(line for line in json_data_file if not line.strip().startswith('//'))
        cfg = json.loads(de_commented)
    return cfg


def get(key):
    return read()[key]


# def url_for_admin(endpoint, **values):
#     return url_for_app('admin', endpoint, **values)


# def url_for_user(endpoint, **values):
#     return url_for_app('user', endpoint, **values)


def full_url_for(endpoint, **values):
    ref_url = url_parse(get('locations')['base_url'])
    url = url_for(endpoint, _scheme=ref_url.scheme, _external=True, **values)
    url_ = url_parse(url)
    new = url_unparse(
        (ref_url.scheme,
         url_.netloc,
         url_.path,
         url_.query,
         url_.fragment
         )
    )
    return new


# def url_for_html(*paths):
#     return os.path.join(get('locations')['base_url'], *paths)


# def path_for_app(app, path):
#     prefix = get('url_prefix')[app]
#     url = (prefix + '/' + path).replace('//', '/')
#     return url


# def full_url_for_app(app, url):
#     prefix = get('url_prefix')[app]
#     path = (prefix + '/' + url).replace('//', '/')
#     url = url_join(get('locations')['base_url'], path)
#     return url


# def adjust_url_for_https(app, url=None):
#     if url:
#         url_ = url_parse(url)
#         ref_url = url_parse(get('locations')['base_url'])
#
#         new = url_unparse(
#             (ref_url.scheme,
#              url_.netloc or ref_url.netloc,
#              path_for_app(app, url_.path),
#              url_.query,
#              url_.fragment
#              )
#         )
#     else:
#         new = full_url_for_app(app, 'index')
#     return new


# def url_for_index(app):
#     if app == 'user':
#         return os.path.join(get('locations')['base_url'], 'index.html')
#     else:
#         return adjust_url_for_https(app, '')


# def is_safe_url(target):
#     ref_url = url_parse(request.host_url)
#     test_url = url_parse(url_join(request.host_url, target))
#     return test_url.scheme in ('http', 'https') and \
#         ref_url.netloc.replace('www.', '') == test_url.netloc.replace('www.', '')


# def url_path_etc(endpoint):
#     if endpoint:
#         url = url_parse(endpoint)
#         return url.path + (('?' + url.query) if len(url.query) > 0 else '')
#     else:
#         return ''


def full_url(url):
    return url_join(get('locations')['base_url'], url)