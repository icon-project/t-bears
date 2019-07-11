import re


def uri_parser(uri : str) -> (str, int):
    uri = "http://127.0.0.1:9000"
    version = 3

    return uri, version


def tx_json_parser(conf: dict) -> dict:
    params = dict()

    params['to'] = conf['to']
    params['method'] = conf['data']['method']
    params['params'] = conf['data'].get('params', None)

    return params
