import unittest
from glob import glob
from fastocarto.main import mml_to_mapnik_xml
from lxml.etree import canonicalize

class TestCartoTests(unittest.TestCase):
    def test_mml_render(self):
        mmls = glob("carto/test/*/*.mml")
        for mml in mmls:
            with self.subTest(mml):
                actual = mml_to_mapnik_xml(mml)

                xml_fname = mml.replace(".mml", ".result")
                with open(xml_fname, "rb") as fp:
                    expected = fp.read()
                    self.assertEqualXml(actual, expected)
            
    def assertEqualXml(self, xml1, xml2):
        self.assertEqual(canonicalize(xml1.decode("utf-8")), canonicalize(xml2.decode("utf-8")))
