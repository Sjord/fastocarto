from pprint import pprint
from fastocarto.output import Style, Layer, Rule
import fastocarto.ast as ast
from typing import List


class FlatRuleset:
    # selectors, declarations, but no nested rulesets
    def __init__(self, selector, declarations):
        self.selector = selector
        self.declarations = declarations

    def __repr__(self):
        return f"FlatRuleset[{self.selector}]{self.declarations}"

    def applies_to_layer(self, layer_id: str) -> bool:
        return self.selector.applies_to_layer(layer_id)

    def to_output_rule(self) -> Rule:
        r = Rule()
        # TODO
        return r


def flatten_rulesets(rulesets, parent_selector=ast.selector(None)) -> List[FlatRuleset]:
    """
    a[foo=3] {
        [bar=5] {
            color: red
        }
    }

    ->

    a[foo=3][bar=5] {
        color: red
    }
    """
    result = []

    for ruleset in rulesets:
        for selector in ruleset.selectors:
            if ruleset.declarations:
                result.append(
                    FlatRuleset(parent_selector + selector, ruleset.declarations)
                )

            result.extend(
                flatten_rulesets(ruleset.rulesets, parent_selector + selector)
            )

    return result


def flatten_stylesheets(stylesheets) -> List[FlatRuleset]:
    result = []
    for stylesheet in stylesheets:
        result.extend(flatten_rulesets(stylesheet.rulesets))
    return result


def rules_for_layer(stylesheets, layer_id) -> List[Rule]:
    # TODO use all stylesheets, filter on layer (and zoom level?) and flatten, and convert to mapnik rule with symbolizers
    flattened = flatten_stylesheets(stylesheets)
    flat_applicable = [r for r in flattened if r.applies_to_layer(layer_id)]
    rules = [r.to_output_rule() for r in flat_applicable]
    return rules


def carto_to_mapnik(carto_model):
    result = []
    for layer in carto_model["Layer"]:
        assert layer["id"]

        # add multiple styles
        rules = rules_for_layer(carto_model["Stylesheet"], layer["id"])
        style = Style(layer["id"], rules)
        result.append(style)

        # add layer
        layer = Layer(layer["id"])
        result.append(layer)
    return result
