======
issnpy
======

``issnpy`` is a Python package and command line tool that allows to access
linked data from the `ISSN Portal <https://portal.issn.org>`_.

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

Command Line
~~~~~~~~~~~~

.. code-block:: shell

    # fetch ISSN data (JSON, fields: id, link, title, format, location, status, modified, url)
    ISSN "2151-2124"
    # fetch ISSN data (JSON-LD)
    ISSN "2151-2124" --ld
    # fetch ISSN-L data (JSON, fields: id, related, title)
    ISSN-L "0269-8803"
    # fetch ISSN-L data (JSON-LD)
    ISSN-L "0269-8803" --ld

Use the ``--pretty`` flag for formatted JSON output.

Interpreter
~~~~~~~~~~~

.. code-block:: python

    # import package issnpy
    import issnpy
    # select ISSN of record to fetch
    issn = "2767-3200"
    # fetch data of record identified by ISSN
    record = issnpy.fetch(issn)
    # get linked data graph
    record_graph = record.graph()
    # get linked data context
    record_context = record.context()
    # get parsed data of record (fields: id, link, title, format, location, status, modified, url)
    record_parsed = record.parse()
    # retrieve linking ISSN for given ISSN
    issn_l = issnpy.find_link(issn)
    # fetch data of record identified by ISSN-L
    record = issnpy.fetch(issn_l, link=True)
    # get parsed data of record (fields: id, related, title)
    record_parsed = record.parse()
    # fetch and parse in one go
    record_parsed = issnpy.record(issn)
    record_parsed = issnpy.record_link(issn_l)

Source Data
===========

    Identification and description data from the ISSN Register has been made
    available as linked data, in various RDF formats (RDF/XML, Turtle and JSON).
    This service shall foster the use, re-use, exchange and enrichment of ISSN data.

See the `linked data application profile <https://www.issn.org/understanding-the-issn/assignment-rules/issn-linked-data-application-profile/>`_
of the CIEPS/ISSN International Centre for further details.

Usage Terms
===========

CIEPS/ISSN International Centre
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DEFINITIONS

    ...

    *Released ISSN Data*: Part of the data extracted from the ISSN Register
    concerning a publication, selected by the CIEPS/ISSN International Centre
    and made available to users free of charge via the Free Access Portal.
    This Released ISSN Data is limited to:

    - ISSN
    - ISSN-L
    - Title proper
    - Key-title
    - Country
    - Medium
    - URL of the digital resource
    - Date of last update

    ...

See the `License contract of the ISSN Portal <https://portal.issn.org/content/license-contract>`_ for further details.
