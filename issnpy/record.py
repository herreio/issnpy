import datetime
from . import utils


class Parser:

    def __init__(self, data, issn):
        self.id = issn
        self.raw = data

    @staticmethod
    def _clean_str(char):
        if isinstance(char, str):
            char = char.strip(".")
            char = char.strip()
        return char

    @staticmethod
    def _get_field(data, name):
        if data and name in data:
            if data[name]:
                return data[name]

    def _get_graph(self):
        return self._get_field(self.raw, "@graph")

    def _get_context(self):
        return self._get_field(self.raw, "@context")

    def _get_issn_l(self):
        response_graph = self._get_graph()
        if response_graph is None:
            return None
        pattern = "resource/ISSN-L/"
        for node in response_graph:
            nid = self._get_field(node, "@id")
            if pattern in nid:
                issn_l = nid.replace(pattern, "")
                issn_l = utils.validate(issn_l)
                if issn_l is not None:
                    return issn_l

    def graph(self):
        return self._get_graph()

    def context(self):
        return self._get_context()

    def get_issn_l(self):
        return self._get_issn_l()


class ParserIssn(Parser):

    def __init__(self, data, issn):
        super().__init__(data, issn)

    def _get_issn_fields(self):
        data = self._get_graph()
        if data is None:
            return None
        pattern = "resource/ISSN/{0}".format(self.id)
        for d in data:
            did = self._get_field(d, "@id")
            if did == pattern:
                return d

    def _get_main_title(self):
        response_graph = self._get_graph()
        if response_graph is None:
            return None
        node = self._get_issn_fields()
        if node and "mainTitle" in node:
            main_title = node["mainTitle"]
            return self._clean_str(main_title)

    def _get_format(self):
        response_graph = self._get_graph()
        if response_graph is None:
            return None
        node = self._get_issn_fields()
        if node and "format" in node:
            title_format = node["format"]
            if isinstance(title_format, str):
                title_format = title_format.replace("vocabularies/medium#", "")
                return title_format
            elif isinstance(title_format, list):
                return [tf.replace("vocabularies/medium#", "")
                        for tf in title_format]

    def _get_url(self):
        response_graph = self._get_graph()
        if response_graph is None:
            return None
        node = self._get_issn_fields()
        if node and "url" in node:
            return node["url"]

    def _get_name(self):
        response_graph = self._get_graph()
        if response_graph is None:
            return None
        node = self._get_issn_fields()
        if node and "name" in node:
            return node["name"]

    def _get_issn_reference_publication_event(self):
        response_graph = self._get_graph()
        if response_graph is None:
            return None
        pattern = "resource/ISSN/{0}#ReferencePublicationEvent".format(self.id)
        for node in response_graph:
            nid = self._get_field(node, "@id")
            if nid == pattern:
                if "location" in node:
                    return node["location"]

    def _get_location(self):
        response_graph = self._get_graph()
        if response_graph is None:
            return None
        pattern = self._get_issn_reference_publication_event()
        for node in response_graph:
            nid = self._get_field(node, "@id")
            if nid == pattern:
                if "label" in node:
                    return node["label"]

    def _get_publisher(self):
        response_graph = self._get_graph()
        if response_graph is None:
            return None
        publishers = []
        for node in response_graph:
            if "publisher" in node and node["publisher"] not in publishers:
                publishers.append(node["publisher"])
        if len(publishers) > 0:
            publishers.sort()
            return "|".join(publishers)

    def _get_issn_key_title(self):
        response_graph = self._get_graph()
        if response_graph is None:
            return None
        pattern = "resource/ISSN/{0}#KeyTitle".format(self.id)
        for node in response_graph:
            nid = self._get_field(node, "@id")
            if nid == pattern:
                if "value" in node:
                    value = node["value"]
                    if isinstance(value, str):
                        return self._clean_str(value)
                    elif isinstance(value, list):
                        values = [self._clean_str(v) for v in value]
                        return values

    def _get_issn_record_field(self, field):
        response_graph = self._get_graph()
        if response_graph is None:
            return None
        pattern = "resource/ISSN/{0}#Record".format(self.id)
        for node in response_graph:
            nid = self._get_field(node, "@id")
            if nid == pattern:
                if field in node:
                    return node[field]

    def _get_issn_record_modified(self):
        return self._get_issn_record_field("modified")

    def _get_issn_record_modified_iso(self):
        record_modified = self._get_issn_record_modified()
        if record_modified is not None:
            try:
                dt = datetime.datetime.strptime(record_modified, "%Y%m%d%H%M%S.0")
            except ValueError:
                try:
                    dt = datetime.datetime.strptime(record_modified, "%Y%m%d%H%M%S.%f")
                except ValueError:
                    dt = None
            if isinstance(dt, datetime.datetime):
                return dt.isoformat()

    def _get_issn_record_status(self):
        record_status = self._get_issn_record_field("status")
        if record_status is not None:
            record_status = record_status.replace("vocabularies/RecordStatus#", "")
            return record_status

    def get_main_title(self):
        return self._get_main_title()

    def get_key_title(self):
        return self._get_issn_key_title()

    def get_url(self):
        return self._get_url()

    def get_name(self):
        """str OR list"""
        return self._get_name()

    def get_location(self):
        return self._get_location()

    def get_publisher(self):
        return self._get_publisher()

    def get_format(self):
        return self._get_format()

    def get_status(self):
        return self._get_issn_record_status()

    def get_modified(self):
        return self._get_issn_record_modified_iso()

    def parse(self):
        if not self.raw:
            return None
        return {
          "id": self.id,
          "link": self.get_issn_l(),
          "title": self.get_key_title(),
          "format": self.get_format(),
          "location": self.get_location(),
          "status": self.get_status(),
          "modified": self.get_modified(),
          "url": self.get_url()
          }

    def to_csv(self, header=False):
        csv_data = []
        parsed = self.parse()
        if parsed is not None:
            if header:
                csv_data.append(list(parsed.keys()))
            row = list(v if v else "" for v in parsed.values())
            row = ["|".join(r) if isinstance(r, list) else r for r in row]
            csv_data.append(row)
        if len(csv_data) > 0:
            return csv_data


class ParserIssnL(Parser):

    def __init__(self, data, issn):
        super().__init__(data, issn)

    def _get_issns(self):
        issns = []
        response_graph = self._get_graph()
        if response_graph is None:
            return None
        pattern = "resource/ISSN/"
        for node in response_graph:
            nid = self._get_field(node, "@id")
            if pattern in nid and len(nid.replace(pattern, "")) == 9:
                title_issn = nid.replace(pattern, "")
                title_format = None
                if "format" in node:
                    title_format = node["format"]
                    if isinstance(title_format, str):
                        title_format = title_format.replace("vocabularies/medium#", "")
                    elif isinstance(title_format, list):
                        title_format = [tf.replace("vocabularies/medium#", "")
                                        for tf in title_format]
                issns.append({"id": title_issn, "format": title_format})
        if len(issns) > 0:
            return issns

    def _get_issn_l_name(self):
        response_graph = self._get_graph()
        if response_graph is None:
            return None
        pattern = "resource/ISSN-L/{0}".format(self.id)
        for node in response_graph:
            nid = self._get_field(node, "@id")
            if nid == pattern:
                if "name" in node:
                    name = node["name"]
                    return self._clean_str(name)

    def get_name(self):
        return self._get_issn_l_name()

    def get_issns(self):
        return self._get_issns()

    def parse(self):
        if not self.raw:
            return None
        return {
          "id": self.get_issn_l(),
          "related": self.get_issns(),
          "title": self.get_name()
          }
