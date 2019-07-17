import re
from urllib import parse


def uri_parser(uri: str) -> (str, int):

    uri = parse.urlparse(uri)
    _uri = uri.scheme + '://' + uri.netloc
    _version = re.search(r'(?<=\bv)\d+', uri.path).group(0)

    return _uri, int(_version)


