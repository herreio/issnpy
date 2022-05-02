from . import utils
from .record import Parser

URL_BASE = "https://portal.issn.org/resource"
URL_BASE_ISSN = "{0}/ISSN".format(URL_BASE)
URL_BASE_ISSN_L = "{0}/ISSN-L".format(URL_BASE)


def build_url(issn):
    return "{0}/{1}?format=json".format(URL_BASE_ISSN, issn)


def build_url_l(issn_l):
    return "{0}/{1}?format=json".format(URL_BASE_ISSN, issn_l)


def request(issn, linking=False):
    if not linking:
        url = build_url(issn)
    else:
        url = build_url_l(issn)
    payload = utils.json_request(url)
    if payload is not None:
        return Parser(payload, issn)
