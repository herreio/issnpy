from . import utils
from .record import ParserIssn, ParserIssnL

URL_BASE = "https://portal.issn.org/resource"
URL_BASE_ISSN = "{0}/ISSN".format(URL_BASE)
URL_BASE_ISSN_L = "{0}/ISSN-L".format(URL_BASE)

# Legacy portal data is still served by the publishers subdomain as
# graph-shaped JSON-LD via the old ?format=json query parameter.
URL_BASE_LEGACY = "https://publishers.issn.org/resource"
URL_BASE_LEGACY_ISSN = "{0}/ISSN".format(URL_BASE_LEGACY)
URL_BASE_LEGACY_ISSN_L = "{0}/ISSN-L".format(URL_BASE_LEGACY)


def _build_url(issn):
    return "{0}/{1}".format(URL_BASE_ISSN, issn)


def _build_url_l(issn_l):
    return "{0}/{1}".format(URL_BASE_ISSN_L, issn_l)


def _build_url_jsonld(issn):
    return "{0}.jsonld".format(_build_url(issn))


def _build_url_l_jsonld(issn_l):
    return "{0}.jsonld".format(_build_url_l(issn_l))


def _build_url_legacy(issn):
    return "{0}/{1}?format=json".format(URL_BASE_LEGACY_ISSN, issn)


def _build_url_l_legacy(issn_l):
    return "{0}/{1}?format=json".format(URL_BASE_LEGACY_ISSN_L, issn_l)


def _request_payload(url, url_jsonld):
    payload = utils.json_request(url_jsonld)
    if payload is not None:
        return payload
    # Fallback to content negotiation when direct JSON-LD URL is unavailable.
    return utils.json_request(url, headers={"Accept": "application/ld+json"})


def request(issn, link=False, parse=False, legacy=False):
    issn = utils.validate(issn)
    if issn is None:
        return None
    if legacy:
        if not link:
            payload = utils.json_request(_build_url_legacy(issn))
        else:
            payload = utils.json_request(_build_url_l_legacy(issn))
    else:
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
        issn_data = ParserIssn(payload, issn, legacy=legacy)
        if parse:
            return issn_data.parse()
        return issn_data


def record(issn, legacy=False):
    return request(issn, link=False, parse=True, legacy=legacy)


def record_link(issn, legacy=False):
    return request(issn, link=True, parse=True, legacy=legacy)


def find_link(issn, legacy=False):
    result = request(issn, link=False, parse=False, legacy=legacy)
    if result is not None:
        return result.get_issn_l()
