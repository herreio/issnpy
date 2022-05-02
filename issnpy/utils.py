import json
import logging
import requests
import stdnum.issn
import stdnum.exceptions

from . import __version__


def get_logger(name="issnpy", loglevel=None):
    logger = logging.getLogger(name)
    if not logger.handlers:
        stream = logging.StreamHandler()
        if loglevel is not None and loglevel != stream.level:
            stream.setLevel(loglevel)
        stream.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(stream)
        if loglevel is not None and loglevel != logger.level:
            logger.setLevel(loglevel)
    else:
        if loglevel is not None and logger.level != loglevel:
            logger.setLevel(loglevel)
    return logger


def validate(issn):
    issnf = stdnum.issn.format(issn)
    try:
        issnf = stdnum.issn.validate(issnf)
        return stdnum.issn.format(issnf)
    except stdnum.exceptions.ValidationError:
        logger = get_logger()
        logger.error("Saw invalid ISSN {0}!".format(issn))
        return None


def get_request(url, params={}, headers={}):
    if "User-Agent" not in headers:
        headers["User-Agent"] = "issnpy {0}".format(__version__)
    try:
        return requests.get(url, params=params, headers=headers)
    except requests.exceptions.RequestException as err:
        logger = get_logger()
        logger.error(err.__class__.__name__)
        return None


def response_ok(response, loglevel=None):
    if response is None:
        return False
    if response.status_code == 200:
        return True
    else:
        logger = get_logger(loglevel=loglevel)
        logger.error("HTTP request to {0} failed!".format(response.url))
        logger.error("HTTP response code is {0}.".format(response.status_code))
        return False


def response_json(response):
    if response_ok(response):
        try:
            payload = response.json()
            if payload:
                return payload
        except requests.exceptions.JSONDecodeError:
            logger = get_logger()
            logger.error(
                "Failed to parse JSON data retrieved from URL {0}".format(response.url))


def json_request(url, headers={}):
    response = get_request(url, headers=headers)
    return response_json(response)


def json_str(data):
    return json.dumps(data, ensure_ascii=False, separators=(',', ':'))


def json_str_pretty(data):
    return json.dumps(data, ensure_ascii=False, indent=2)
