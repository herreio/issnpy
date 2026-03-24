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


if __name__ == "__main__":
    unittest.main()
