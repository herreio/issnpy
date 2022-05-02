from . import utils
from .record import ParserIssn, ParserIssnL

URL_BASE = "https://portal.issn.org/resource"
URL_BASE_ISSN = "{0}/ISSN".format(URL_BASE)
URL_BASE_ISSN_L = "{0}/ISSN-L".format(URL_BASE)


def _build_url(issn):
    return "{0}/{1}?format=json".format(URL_BASE_ISSN, issn)


def _build_url_l(issn_l):
    return "{0}/{1}?format=json".format(URL_BASE_ISSN_L, issn_l)


def request(issn, link=False, parse=False):
    issn = utils.validate(issn)
    if issn is None:
        return None
    if not link:
        url = _build_url(issn)
    else:
        url = _build_url_l(issn)
    payload = utils.json_request(url)
    if payload is not None:
        if link:
            issn_l_data = ParserIssnL(payload, issn)
            if parse:
                return issn_l_data.parse()
            return issn_l_data
        issn_data = ParserIssn(payload, issn)
        if parse:
            return issn_data.parse()
        return issn_data


def record(issn):
    return request(issn, link=False, parse=True)


def record_link(issn):
    return request(issn, link=True, parse=True)


def find_link(issn):
    result = request(issn, link=False, parse=False)
    if result is not None:
        return result.get_issn_l()
