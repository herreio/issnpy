# -*- coding: utf-8 -*-
"""
This package allows to access linked open data from the ISSN Portal.
"""

__author__ = "Donatus Herre <donatus.herre@slub-dresden.de>"
__version__ = "0.0.0"

from .client import request as fetch
from .client import record, link, find_link
