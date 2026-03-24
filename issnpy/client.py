from . import utils
from .record import ParserIssn, ParserIssnL

URL_BASE = "https://portal.issn.org/resource"
URL_BASE_ISSN = "{0}/ISSN".format(URL_BASE)
URL_BASE_ISSN_L = "{0}/ISSN-L".format(URL_BASE)


def _build_url(issn):
    return "{0}/{1}".format(URL_BASE_ISSN, issn)


def _build_url_l(issn_l):
    return "{0}/{1}".format(URL_BASE_ISSN_L, issn_l)


def _build_url_jsonld(issn):
    return "{0}.jsonld".format(_build_url(issn))


def _build_url_l_jsonld(issn_l):
    return "{0}.jsonld".format(_build_url_l(issn_l))


def _request_payload(url, url_jsonld):
    payload = utils.json_request(url_jsonld)
    if payload is not None:
        return payload
    # Fallback to content negotiation when direct JSON-LD URL is unavailable.
    return utils.json_request(url, headers={"Accept": "application/ld+json"})


def request(issn, link=False, parse=False):
    issn = utils.validate(issn)
    if issn is None:
        return None
    if not link:
        url = _build_url(issn)
        url_jsonld = _build_url_jsonld(issn)
    else:
        url = _build_url_l(issn)
        url_jsonld = _build_url_l_jsonld(issn)
    payload = _request_payload(url, url_jsonld)
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
