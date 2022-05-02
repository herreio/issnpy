import datetime


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


def _get_issn_key_title(data, issn):
    response_graph = _get_graph(data)
    pattern = "resource/ISSN/{0}#KeyTitle".format(issn)
    for node in response_graph:
        nid = _get_field(node, "@id")
        if nid == pattern:
            if "value" in node:
                return node["value"]


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


def _get_title(data, issn):
    response_graph = _get_graph(data)
    response_graph_data = _get_issn_fields(response_graph, issn)
    if response_graph_data and "mainTitle" in response_graph_data:
        main_title = response_graph_data["mainTitle"]
        main_title = main_title.strip(".")
        main_title = main_title.strip()
        return main_title


def _get_format(data, issn):
    response_graph = _get_graph(data)
    response_graph_data = _get_issn_fields(response_graph, issn)
    if response_graph_data and "format" in response_graph_data:
        title_format = response_graph_data["format"]
        title_format = title_format.replace("vocabularies/medium#", "")
        return title_format


def _get_url(data, issn):
    response_graph = _get_graph(data)
    response_graph_data = _get_issn_fields(response_graph, issn)
    if response_graph_data and "url" in response_graph_data:
        return response_graph_data["url"]


class Parser:

    def __init__(self, data, issn):
        self.id = issn
        self.raw = data

    def graph(self):
        return _get_graph(self.raw)

    def context(self):
        return _get_context(self.raw)

    def get_title(self):
        return _get_title(self.raw, self.id)

    def get_key_title(self):
        return _get_issn_key_title(self.raw, self.id)

    def get_issn_l(self):
        return _get_issn_l(self.raw, self.id)

    def get_url(self):
        return _get_url(self.raw, self.id)

    def get_format(self):
        return _get_format(self.raw, self.id)

    def get_status(self):
        return _get_issn_record_status(self.raw, self.id)

    def get_modified(self):
        return _get_issn_record_modified_iso(self.raw, self.id)

    def parse(self):
        return {
          "issn": self.id,
          "issn_l": self.get_issn_l(),
          "title": self.get_key_title(),
          "format": self.get_format(),
          "status": self.get_status(),
          "modified": self.get_modified(),
          "url": self.get_url()
        }
