# -*- coding: utf-8 -*-
"""
This package allows to access linked data from the ISSN Portal.
"""

__author__ = "Donatus Herre <donatus.herre@slub-dresden.de>"
__version__ = "0.1.3"

from .client import request as fetch
from .client import record, record_link, find_link
