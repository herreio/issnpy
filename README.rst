======
issnpy
======

``issnpy`` is a Python package that allows to access linked open data from the ISSN Portal.

Installation
============

... via SSH
~~~~~~~~~~~

.. code-block:: bash

   pip install -e git+ssh://git@github.com/herreio/issnpy.git#egg=issnpy

... or via HTTPS
~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -e git+https://github.com/herreio/issnpy.git#egg=issnpy

Usage Example
=============

.. code-block:: python

    # import package issnpy
    import issnpy
    # select ISSN of record to fetch
    issn = "2767-3200"
    # fetch data of record identified by ISSN
    record = issnpy.fetch(issn)
    # get linked open data graph
    record_graph = record.graph()
    # get linked open data context
    record_context = record.context()
    # get parsed data of record (issn, issn_l, title, format, location, status, modified, url)
    record_parsed = record.parse()
    # retrieve linking ISSN for given ISSN
    issn_l = issnpy.link(issn)
    # fetch data of record identified by ISSN-L
    record = issnpy.fetch(issn_l, linking=True)
    # get parsed data of record (issn, issn_l, title, format)
    record_parsed = record.parse()

Usage Terms
===========

ISSN International Centre
~~~~~~~~~~~~~~~~~~~~~~~~~

    The CIEPS/ISSN International Centre grants the Licensee the non-exclusive,
    personal, non-assignable and non-transferable right to view, extract and
    reuse the ISSN Data subject to the conditions and restrictions below.

    The use rights granted under the Agreement do not imply any transfer of the
    intellectual property rights over all or part of the ISSN Data or of rights
    other than those expressly referred to in this Agreement:

    Consultation and viewing of ISSN Data;

    Extraction and reuse under the following cumulative conditions:

    ISSN Data may be copied.

    ISSN Data must necessarily be modified in such a way that the informational
    value added to the ISSN Data by the Licensee corresponds to at least the
    addition of a holdings statement, a call number or URL of the Publisher
    or provider of access to the resource.

    ISSN Data thus modified can be reused in a catalogue or database.

    ISSN Data thus modified must mention the CIEPS/ISSN International Centre
    as a source.

    https://portal.issn.org/content/license-contract
