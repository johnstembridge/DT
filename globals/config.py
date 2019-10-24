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


def full_url(url):
    return url_join(get('locations')['base_url'], url)