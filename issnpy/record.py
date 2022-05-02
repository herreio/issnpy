import datetime


def _clean_up(char):
    char = char.strip(".")
    char = char.strip()
    return char


def _get_field(data, name):
    if name in data:
        if data[name]:
            return data[name]


def _get_graph(data):
    return _get_field(data, "@graph")


def _get_context(data):
    return _get_field(data, "@context")


def _get_issn_l(data, issn):
    response_graph = _get_graph(data)
    pattern = "resource/ISSN-L/"
    for node in response_graph:
        nid = _get_field(node, "@id")
        if pattern in nid:
            return nid.replace(pattern, "")


def _get_issn_l_name(data, issn):
    response_graph = _get_graph(data)
    pattern = "resource/ISSN-L/{0}".format(issn)
    for node in response_graph:
        nid = _get_field(node, "@id")
        if nid == pattern:
            if "name" in node:
                name = node["name"]
                return _clean_up(name)


def _get_issn_reference_publication_event(data, issn):
    response_graph = _get_graph(data)
    pattern = "resource/ISSN/{0}#ReferencePublicationEvent".format(issn)
    for node in response_graph:
        nid = _get_field(node, "@id")
        if nid == pattern:
            if "location" in node:
                return node["location"]


def _get_location(data, issn):
    response_graph = _get_graph(data)
    pattern = _get_issn_reference_publication_event(data, issn)
    for node in response_graph:
        nid = _get_field(node, "@id")
        if nid == pattern:
            if "label" in node:
                return node["label"]


def _get_issn_key_title(data, issn):
    response_graph = _get_graph(data)
    pattern = "resource/ISSN/{0}#KeyTitle".format(issn)
    for node in response_graph:
        nid = _get_field(node, "@id")
        if nid == pattern:
            if "value" in node:
                value = node["value"]
                return _clean_up(value)


def _get_issn_record_field(data, issn, field):
    response_graph = _get_graph(data)
    pattern = "resource/ISSN/{0}#Record".format(issn)
    for node in response_graph:
        nid = _get_field(node, "@id")
        if nid == pattern:
            if field in node:
                return node[field]


def _get_issn_record_modified(data, issn):
    return _get_issn_record_field(data, issn, "modified")


def _get_issn_record_modified_iso(data, issn):
    record_modified = _get_issn_record_modified(data, issn)
    if record_modified is not None:
        dt = datetime.datetime.strptime(record_modified, "%Y%m%d%H%M%S.0")
        return dt.isoformat()


def _get_issn_record_status(data, issn):
    record_status = _get_issn_record_field(data, issn, "status")
    if record_status is not None:
        record_status = record_status.replace("vocabularies/RecordStatus#", "")
        return record_status


def _get_issn_fields(data, issn):
    pattern = "resource/ISSN/{0}".format(issn)
    for d in data:
        did = _get_field(d, "@id")
        if did == pattern:
            return d


def _get_issns(data):
    issns = []
    response_graph = _get_graph(data)
    pattern = "resource/ISSN/"
    for node in response_graph:
        nid = _get_field(node, "@id")
        if pattern in nid and len(nid.replace(pattern, "")) == 9:
            title_issn = nid.replace(pattern, "")
            title_format = None
            if "format" in node:
                title_format = node["format"]
                title_format = title_format.replace("vocabularies/medium#", "")
            issns.append({"issn": title_issn, "format": title_format})
    if len(issns) > 0:
        return issns


def _get_title(data, issn):
    response_graph = _get_graph(data)
    node = _get_issn_fields(response_graph, issn)
    if node and "mainTitle" in node:
        main_title = node["mainTitle"]
        return _clean_up(main_title)


def _get_format(data, issn):
    response_graph = _get_graph(data)
    node = _get_issn_fields(response_graph, issn)
    if node and "format" in node:
        title_format = node["format"]
        title_format = title_format.replace("vocabularies/medium#", "")
        return title_format


def _get_url(data, issn):
    response_graph = _get_graph(data)
    node = _get_issn_fields(response_graph, issn)
    if node and "url" in node:
        return node["url"]


class Parser:

    def __init__(self, data, issn, linking=False):
        self.id = issn
        self.raw = data
        self.linking = linking

    def graph(self):
        return _get_graph(self.raw)

    def context(self):
        return _get_context(self.raw)

    def get_name(self):
        if self.linking:
            return _get_issn_l_name(self.raw, self.id)

    def get_issns(self):
        if self.linking:
            return _get_issns(self.raw)

    def get_title(self):
        if not self.linking:
            return _get_title(self.raw, self.id)

    def get_key_title(self):
        if not self.linking:
            return _get_issn_key_title(self.raw, self.id)

    def get_issn_l(self):
        return _get_issn_l(self.raw, self.id)

    def get_url(self):
        if not self.linking:
            return _get_url(self.raw, self.id)

    def get_location(self):
        if not self.linking:
            return _get_location(self.raw, self.id)

    def get_format(self):
        if not self.linking:
            return _get_format(self.raw, self.id)

    def get_status(self):
        if not self.linking:
            return _get_issn_record_status(self.raw, self.id)

    def get_modified(self):
        if not self.linking:
            return _get_issn_record_modified_iso(self.raw, self.id)

    def parse(self):
        if self.linking:
            return {
              "issn_l": self.get_issn_l(),
              "related": self.get_issns(),
              "title": self.get_name()
            }
        else:
            return {
              "issn": self.id,
              "issn_l": self.get_issn_l(),
              "title": self.get_title(),
              "format": self.get_format(),
              "location": self.get_location(),
              "status": self.get_status(),
              "modified": self.get_modified(),
              "url": self.get_url()
            }
