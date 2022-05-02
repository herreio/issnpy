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

    def parse(self):
        return {
          "issn": self.id,
          "issn_l": self.get_issn_l(),
          "title": self.get_key_title(),
          "url": self.get_url()
        }
