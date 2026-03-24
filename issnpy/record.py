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

    @staticmethod
    def _issn_from_node(node):
        if not isinstance(node, dict):
            return None
        value = node.get("value")
        if isinstance(value, str):
            return utils.validate(value)
        identifier = node.get("identifier")
        if isinstance(identifier, str):
            return utils.validate(identifier)

    @staticmethod
    def _clean_medium(value):
        if isinstance(value, str):
            value = value.replace("vocabularies/medium#", "")
            value = value.replace("medium:", "")
            return value

    @staticmethod
    def _clean_record_status(value):
        if isinstance(value, str):
            value = value.replace("vocabularies/RecordStatus#", "")
            value = value.replace("recordStatus:", "")
            return value

    def _get_issn_l(self):
        response_graph = self._get_graph()
        if response_graph is not None:
            pattern = "resource/ISSN-L/"
            for node in response_graph:
                nid = self._get_field(node, "@id")
                if isinstance(nid, str) and pattern in nid:
                    issn_l = nid.replace(pattern, "")
                    issn_l = utils.validate(issn_l)
                    if issn_l is not None:
                        return issn_l

        identified_by = self._get_field(self.raw, "identifiedBy")
        if isinstance(identified_by, dict):
            issn_l = self._issn_from_node(identified_by)
            if issn_l is not None:
                return issn_l
            for key, value in identified_by.items():
                if "ISSN-L" in key:
                    issn_l = self._issn_from_node(value)
                    if issn_l is not None:
                        return issn_l

        is_part_of = self._get_field(self.raw, "isPartOf")
        if isinstance(is_part_of, dict):
            is_part_of_identified_by = self._get_field(is_part_of, "identifiedBy")
            if isinstance(is_part_of_identified_by, dict):
                for key, value in is_part_of_identified_by.items():
                    if "ISSN-L" in key:
                        issn_l = self._issn_from_node(value)
                        if issn_l is not None:
                            return issn_l
            issn_l = self._issn_from_node(is_part_of)
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
        if data is not None:
            pattern = "resource/ISSN/{0}".format(self.id)
            for d in data:
                did = self._get_field(d, "@id")
                if did == pattern:
                    return d
        if isinstance(self.raw, dict):
            return self.raw

    def _get_main_title(self):
        node = self._get_issn_fields()
        if node and "mainTitle" in node:
            main_title = node["mainTitle"]
            if isinstance(main_title, dict):
                main_title = main_title.get("@value")
            return self._clean_str(main_title)

    def _get_format(self):
        node = self._get_issn_fields()
        if node and "format" in node:
            title_format = node["format"]
            if isinstance(title_format, str):
                return self._clean_medium(title_format)
            elif isinstance(title_format, list):
                return [self._clean_medium(tf) for tf in title_format]

    def _get_url(self):
        node = self._get_issn_fields()
        if node and "url" in node:
            return node["url"]

    def _get_name(self):
        node = self._get_issn_fields()
        if node and "name" in node:
            return node["name"]

    def _get_issn_reference_publication_event(self):
        response_graph = self._get_graph()
        if response_graph is not None:
            pattern = "resource/ISSN/{0}#ReferencePublicationEvent".format(self.id)
            for node in response_graph:
                nid = self._get_field(node, "@id")
                if nid == pattern:
                    if "location" in node:
                        return node["location"]
            return None
        publication = self._get_field(self.raw, "publication")
        if isinstance(publication, list) and len(publication) > 0:
            event = publication[0]
            if isinstance(event, dict) and "location" in event:
                return event["location"]

    def _get_location(self):
        response_graph = self._get_graph()
        pattern = self._get_issn_reference_publication_event()
        if pattern is None:
            return None
        if response_graph is not None:
            for node in response_graph:
                nid = self._get_field(node, "@id")
                if nid == pattern:
                    if "label" in node:
                        return node["label"]
        elif isinstance(pattern, list):
            for location in pattern:
                if isinstance(location, dict) and "label" in location:
                    return location["label"]
        elif isinstance(pattern, dict) and "label" in pattern:
            return pattern["label"]

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
        if response_graph is not None:
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
            return None

        identified_by = self._get_field(self.raw, "identifiedBy")
        if isinstance(identified_by, dict):
            key_title = identified_by.get("#KeyTitle")
            if isinstance(key_title, dict):
                value = key_title.get("value")
                if isinstance(value, str):
                    return self._clean_str(value)
                elif isinstance(value, list):
                    return [self._clean_str(v) for v in value]
                main_title = key_title.get("mainTitle")
                if isinstance(main_title, dict):
                    value = main_title.get("@value")
                    if isinstance(value, str):
                        return self._clean_str(value)

    def _get_issn_record_field(self, field):
        response_graph = self._get_graph()
        if response_graph is not None:
            pattern = "resource/ISSN/{0}#Record".format(self.id)
            for node in response_graph:
                nid = self._get_field(node, "@id")
                if nid == pattern:
                    if field in node:
                        return node[field]
            return None

        main_entity_of = self._get_field(self.raw, "mainEntityOf")
        if isinstance(main_entity_of, dict) and field in main_entity_of:
            return main_entity_of[field]

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
                    try:
                        dt = datetime.datetime.fromisoformat(record_modified)
                    except ValueError:
                        dt = None
            if isinstance(dt, datetime.datetime):
                return dt.isoformat()
            try:
                dt = datetime.date.fromisoformat(record_modified)
            except ValueError:
                dt = None
            if isinstance(dt, datetime.date):
                return dt.isoformat()

    def _get_issn_record_status(self):
        record_status = self._get_issn_record_field("status")
        if record_status is not None:
            return self._clean_record_status(record_status)

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
        if response_graph is not None:
            pattern = "resource/ISSN/"
            for node in response_graph:
                nid = self._get_field(node, "@id")
                if isinstance(nid, str) and pattern in nid and len(nid.replace(pattern, "")) == 9:
                    title_issn = nid.replace(pattern, "")
                    title_format = None
                    if "format" in node:
                        title_format = node["format"]
                        if isinstance(title_format, str):
                            title_format = self._clean_medium(title_format)
                        elif isinstance(title_format, list):
                            title_format = [self._clean_medium(tf)
                                            for tf in title_format]
                    issns.append({"id": title_issn, "format": title_format})
        else:
            has_part = self._get_field(self.raw, "hasPart")
            if isinstance(has_part, list):
                for part in has_part:
                    if not isinstance(part, dict):
                        continue
                    title_issn = part.get("identifier")
                    title_issn = utils.validate(title_issn) if isinstance(title_issn, str) else None
                    if title_issn is None:
                        continue
                    title_format = part.get("format")
                    if isinstance(title_format, str):
                        title_format = self._clean_medium(title_format)
                    elif isinstance(title_format, list):
                        title_format = [self._clean_medium(tf)
                                        for tf in title_format]
                    issns.append({"id": title_issn, "format": title_format})
        if len(issns) > 0:
            return issns

    def _get_issn_l_name(self):
        response_graph = self._get_graph()
        if response_graph is not None:
            pattern = "resource/ISSN-L/{0}".format(self.id)
            for node in response_graph:
                nid = self._get_field(node, "@id")
                if nid == pattern:
                    if "name" in node:
                        name = node["name"]
                        return self._clean_str(name)
            return None
        name = self._get_field(self.raw, "name")
        if isinstance(name, str):
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
