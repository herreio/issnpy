# -*- coding: utf-8 -*-
"""
This package allows to access linked data from the ISSN Portal.
"""

__author__ = "Donatus Herre <donatus.herre@slub-dresden.de>"
__version__ = "0.2.0"

from .client import request as fetch
from .client import record, record_link, find_link

__all__ = ["fetch", "record", "record_link", "find_link"]
