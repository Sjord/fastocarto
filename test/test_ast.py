import unittest
from fastocarto.parse import StyleParser


def create_compound_selector(mss):
    f = StyleParser().parse_mss_contents(mss.encode("utf-8"))
    return f.rulesets[0].selectors[0]


def create_simple_selector(mss):
    return create_compound_selector(mss).selectors[0]


class Test_applies_to_layer(unittest.TestCase):
    def test_layer_matches_identifier(self):
        selector = create_simple_selector("#somelayer {}")
        self.assertTrue(selector.applies_to_layer("somelayer"))
        self.assertFalse(selector.applies_to_layer("other"))

    def test_other_filters(self):
        selector = create_simple_selector("[zoom = 3] {}")
        self.assertIsNone(selector.applies_to_layer("somelayer"))


class Test_zoom_level_range(unittest.TestCase):
    def test_not_filter(self):
        selector = create_simple_selector("#somelayer {}")
        self.assertEqual(selector.zoom_level_range, (None, None))

    def test_not_zoom(self):
        selector = create_simple_selector("[height >= 500] {}")
        self.assertEqual(selector.zoom_level_range, (None, None))

    def test_equal(self):
        selector = create_simple_selector("[zoom = 3] {}")
        self.assertEqual(selector.zoom_level_range, (3, 3))

    def test_gte(self):
        selector = create_simple_selector("[zoom >= 3] {}")
        self.assertEqual(selector.zoom_level_range, (3, None))

    def test_lte(self):
        selector = create_simple_selector("[zoom <= 3] {}")
        self.assertEqual(selector.zoom_level_range, (None, 3))

    def test_gt(self):
        selector = create_simple_selector("[zoom > 3] {}")
        self.assertEqual(selector.zoom_level_range, (4, None))

    def test_lt(self):
        selector = create_simple_selector("[zoom < 3] {}")
        self.assertEqual(selector.zoom_level_range, (None, 2))

    def test_range(self):
        selector = create_compound_selector("[zoom > 3][zoom < 6] {}")
        self.assertEqual(selector.zoom_level_range, (4, 5))

    def test_multiple(self):
        selector = create_compound_selector(
            "[zoom >= 1][zoom <= 6][zoom > 3][zoom < 10] {}"
        )
        self.assertEqual(selector.zoom_level_range, (4, 6))
