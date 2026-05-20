import unittest
from unittest import mock

from issnpy import client
from issnpy.record import ParserIssn, ParserIssnL


ISSN_COMPACT = {
    "@context": {},
    "format": "medium:Online",
    "identifiedBy": {
        "#ISSN": {"value": "2151-2124"},
        "#ISSN-L": {"value": "0269-8803"},
        "#KeyTitle": {"value": "Journal of psychophysiology (Online)"},
    },
    "mainEntityOf": {"modified": "2025-12-13", "status": "recordStatus:Register"},
    "publication": [{"location": [{"label": "GERMANY"}, {"label": "Germany"}]}],
    "url": ["http://example.invalid/journal"],
}

ISSN_L_COMPACT = {
    "@context": {},
    "identifiedBy": {"type": "bf:IssnL", "value": "0269-8803"},
    "hasPart": [
        {"format": "medium:Online", "identifier": "2151-2124"},
        {"format": "medium:Print", "identifier": "0269-8803"},
    ],
}

# Current portal compact ISSN-L JSON-LD no longer exposes a name/title field.
ISSN_L_COMPACT_NO_TITLE = {
    "@context": {},
    "identifiedBy": {"type": "bf:IssnL", "value": "2767-3200"},
    "hasPart": [
        {"format": "medium:Online", "identifier": "2767-3200"},
    ],
}

# Legacy graph-shaped JSON-LD as served by publishers.issn.org for 2943-0070.
ISSN_LEGACY_GRAPH = {
    "@graph": [
        {
            "@id": "_:b0",
            "issn": "2943-0070",
            "name": "AI-Linguistica. Linguistic Studies on AI-Generated Texts and Discourses",
            "publisher": "PUBLIA – SLUB Open Publishing",
        },
        {
            "@id": "http://id.loc.gov/vocabulary/countries/gw",
            "label": "Germany",
        },
        {
            "@id": "resource/ISSN-L/2943-0070",
            "identifiedBy": "resource/ISSN/2943-0070#ISSN-L",
        },
        {
            "@id": "resource/ISSN/2943-0070",
            "identifiedBy": [
                "resource/ISSN/2943-0070#ISSN-L",
                "resource/ISSN/2943-0070#KeyTitle",
            ],
            "mainTitle": "AI-Linguistica",
            "title": "resource/ISSN/2943-0070#KeyTitle",
            "format": "vocabularies/medium#Online",
            "isPartOf": "resource/ISSN-L/2943-0070",
            "name": "AI-Linguistica",
            "publication": "resource/ISSN/2943-0070#ReferencePublicationEvent",
            "url": [
                "https://ai-ling.publia.org",
                "https://doi.org/10.62408/ai-ling",
                "https://ezb.ur.de/?3178164-0",
            ],
        },
        {
            "@id": "resource/ISSN/2943-0070#ISSN-L",
            "status": "vocabularies/IdentifierStatus#Valid",
            "value": "2943-0070",
        },
        {
            "@id": "resource/ISSN/2943-0070#KeyTitle",
            "value": "AI-Linguistica",
        },
        {
            "@id": "resource/ISSN/2943-0070#Record",
            "modified": "20260506070724.741482",
            "mainEntity": "resource/ISSN/2943-0070",
        },
        {
            "@id": "resource/ISSN/2943-0070#ReferencePublicationEvent",
            "location": "http://id.loc.gov/vocabulary/countries/gw",
        },
    ],
    "@context": {},
}


class TestPortalCompat(unittest.TestCase):

    def test_parser_issn_compact(self):
        parsed = ParserIssn(ISSN_COMPACT, "2151-2124").parse()
        self.assertEqual(parsed["id"], "2151-2124")
        self.assertEqual(parsed["link"], "0269-8803")
        self.assertEqual(parsed["title"], "Journal of psychophysiology (Online)")
        self.assertEqual(parsed["format"], "Online")
        self.assertEqual(parsed["location"], "GERMANY")
        self.assertEqual(parsed["status"], "Register")
        self.assertEqual(parsed["modified"], "2025-12-13T00:00:00")
        self.assertEqual(parsed["url"], ["http://example.invalid/journal"])
        # publisher is a legacy-only field and must not leak into the
        # default (current portal) output where it is never available.
        self.assertNotIn("publisher", parsed)

    def test_parser_issn_l_compact(self):
        parsed = ParserIssnL(ISSN_L_COMPACT, "0269-8803").parse()
        self.assertEqual(parsed["id"], "0269-8803")
        self.assertEqual(
            parsed["related"],
            [
                {"id": "2151-2124", "format": "Online"},
                {"id": "0269-8803", "format": "Print"},
            ],
        )
        # The current portal JSON-LD no longer exposes a title/name field.
        self.assertNotIn("title", parsed)

    def test_parser_issn_l_compact_no_title(self):
        parsed = ParserIssnL(ISSN_L_COMPACT_NO_TITLE, "2767-3200").parse()
        self.assertEqual(parsed["id"], "2767-3200")
        self.assertEqual(
            parsed["related"],
            [{"id": "2767-3200", "format": "Online"}],
        )
        self.assertNotIn("title", parsed)
        self.assertEqual(set(parsed.keys()), {"id", "related"})

    def test_request_prefers_jsonld_suffix_then_accept_header_fallback(self):
        with mock.patch("issnpy.client.utils.json_request", side_effect=[None, {"ok": True}]) as req:
            payload = client._request_payload(
                "https://portal.issn.org/resource/ISSN/2151-2124",
                "https://portal.issn.org/resource/ISSN/2151-2124.jsonld",
            )
            self.assertEqual(payload, {"ok": True})
            self.assertEqual(req.call_count, 2)
            self.assertEqual(
                req.call_args_list[0].args[0],
                "https://portal.issn.org/resource/ISSN/2151-2124.jsonld",
            )
            self.assertEqual(
                req.call_args_list[1].args[0],
                "https://portal.issn.org/resource/ISSN/2151-2124",
            )
            self.assertEqual(
                req.call_args_list[1].kwargs.get("headers"),
                {"Accept": "application/ld+json"},
            )


    def test_parser_issn_legacy_graph_without_legacy_flag_omits_publisher(self):
        parsed = ParserIssn(ISSN_LEGACY_GRAPH, "2943-0070").parse()
        self.assertNotIn("publisher", parsed)

    def test_parser_issn_legacy_graph(self):
        parsed = ParserIssn(ISSN_LEGACY_GRAPH, "2943-0070", legacy=True).parse()
        self.assertEqual(parsed["id"], "2943-0070")
        self.assertEqual(parsed["link"], "2943-0070")
        self.assertEqual(parsed["title"], "AI-Linguistica")
        self.assertEqual(parsed["format"], "Online")
        self.assertEqual(parsed["location"], "Germany")
        self.assertEqual(parsed["modified"], "2026-05-06T07:07:24.741482")
        self.assertEqual(
            parsed["url"],
            [
                "https://ai-ling.publia.org",
                "https://doi.org/10.62408/ai-ling",
                "https://ezb.ur.de/?3178164-0",
            ],
        )
        self.assertEqual(parsed["publisher"], "PUBLIA – SLUB Open Publishing")

    def test_request_default_issn_uses_jsonld_then_accept_fallback(self):
        with mock.patch(
            "issnpy.client.utils.json_request", side_effect=[None, ISSN_COMPACT]
        ) as req:
            client.request("2151-2124", link=False, parse=False)
            self.assertEqual(req.call_count, 2)
            self.assertEqual(
                req.call_args_list[0].args[0],
                "https://portal.issn.org/resource/ISSN/2151-2124.jsonld",
            )
            self.assertEqual(
                req.call_args_list[1].args[0],
                "https://portal.issn.org/resource/ISSN/2151-2124",
            )
            self.assertEqual(
                req.call_args_list[1].kwargs.get("headers"),
                {"Accept": "application/ld+json"},
            )

    def test_request_legacy_issn_uses_publishers_format_json(self):
        with mock.patch(
            "issnpy.client.utils.json_request", return_value=ISSN_LEGACY_GRAPH
        ) as req:
            rec = client.request("2943-0070", link=False, parse=False, legacy=True)
            req.assert_called_once_with(
                "https://publishers.issn.org/resource/ISSN/2943-0070?format=json"
            )
            self.assertEqual(rec.parse()["title"], "AI-Linguistica")

    def test_request_legacy_issn_l_uses_publishers_format_json(self):
        with mock.patch(
            "issnpy.client.utils.json_request", return_value=ISSN_LEGACY_GRAPH
        ) as req:
            client.request("2943-0070", link=True, parse=False, legacy=True)
            req.assert_called_once_with(
                "https://publishers.issn.org/resource/ISSN-L/2943-0070?format=json"
            )

    def test_find_link_legacy_does_not_hit_current_endpoint(self):
        with mock.patch(
            "issnpy.client.utils.json_request", return_value=ISSN_LEGACY_GRAPH
        ) as req:
            link = client.find_link("2943-0070", legacy=True)
            self.assertEqual(link, "2943-0070")
            req.assert_called_once_with(
                "https://publishers.issn.org/resource/ISSN/2943-0070?format=json"
            )


if __name__ == "__main__":
    unittest.main()
