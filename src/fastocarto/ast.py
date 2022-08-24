from collections import defaultdict
import sys
from keyword import iskeyword
from typing import List, Set, Dict, Tuple, Optional
from tree_sitter import Node


class ast_node:
    pass


def get_single_child(node) -> Node:
    try:
        (child,) = node.children
    except ValueError:
        raise ValueError(
            f"Expected one child in `{node.type}` node, but got {node.children}"
        )
    return child


def select_child(node: Node, *types) -> Node:
    children = select_children(node, *types)
    try:
        (child,) = children
    except ValueError:
        raise ValueError(
            f"Expected one child of type {types} in {node}, but got {children}"
        )
    return child


def select_children(node: Node, *types) -> List[Node]:
    if len(types) == 1:
        return [child for child in node.children if child.type == types[0]]
    else:
        result = []
        for subnode in select_children(node, types[0]):
            result += select_children(subnode, *types[1:])
        return result


def children_by_type(node: Node) -> Dict[str, List[Node]]:
    result = defaultdict(list)
    for child in node.children:
        result[child.type].append(child)
    return result


def convert_child_by_type(node: Node) -> ast_node:
    child = get_single_child(node)
    return convert_node_by_type(child)


def convert_node_by_type(node: Node) -> ast_node:
    type = node.type
    if iskeyword(type):
        type += "_"

    func = getattr(sys.modules[__name__], type)
    return func(node)


class selector_base:
    def applies_to_layer(self, layer_id: str) -> Optional[bool]:
        return None

    @property
    def zoom_level_range(self):
        return (None, None)


def convert_selector_by_type(node: Node) -> selector_base:
    converted = convert_node_by_type(node)
    assert isinstance(converted, selector_base)
    return converted


class _identifier_wrapper:
    def __init__(self, node):
        self.identifier = identifier(select_child(node, "identifier"))

    def __repr__(self):
        return f"{type(self).__name__}({self.identifier})"


class source_file(ast_node):
    def __init__(self, node):
        self.assignments = []
        self.rulesets = []

        statements = select_children(node, "statement")
        for statement in statements:
            children = children_by_type(statement)
            self.assignments += [assignment(n) for n in children["assignment"]]
            self.rulesets += [ruleset(n) for n in children["ruleset"]]


class assignment(ast_node):
    def __init__(self, node: Node):
        self.variable = identifier(select_child(node, "variable", "identifier"))
        self.values = [
            convert_child_by_type(n) for n in select_children(node, "values", "value")
        ]


class ruleset(ast_node):
    def __init__(self, node: Node):
        self.selectors = [
            selector(n) for n in select_children(node, "selectors", "selector")
        ]
        self.declarations = [
            declaration(n)
            for n in select_children(
                node, "ruleset_body", "declarations", "declaration"
            )
        ]
        self.rulesets = [
            ruleset(n) for n in select_children(node, "ruleset_body", "ruleset")
        ]

    def __repr__(self):
        return f"ruleset[{self.selectors}]"


class color(ast_node):
    def __init__(self, node: Node):
        child = get_single_child(node)
        self.value = child.text.decode("utf-8")


class expression(ast_node):
    def __init__(self, node: Node):
        pass  # TODO


class function(ast_node):
    def __init__(self, node: Node):
        self.identifier = identifier(select_child(node, "identifier"))
        self.parameters = [
            convert_child_by_type(n) for n in select_children(node, "values", "value")
        ]


class string_expr(ast_node):
    def __init__(self, node: Node):
        self.values = [convert_node_by_type(n) for n in node.children if n.type != "+"]


def boolean(node: Node) -> bool:
    return bool(node.text)


def string(node: Node) -> str:
    return node.children[1].text.decode("utf-8")


def percentage(node: Node) -> float:
    return int(node.children[0].text) / 100


class Map(ast_node):
    def __init__(self, node: Node):
        pass


class layer(ast_node, selector_base, _identifier_wrapper):
    def applies_to_layer(self, layer_id) -> Optional[bool]:
        return self.identifier == layer_id


class variable(ast_node, _identifier_wrapper):
    pass


class keyword(ast_node, _identifier_wrapper):
    pass


class field(ast_node, _identifier_wrapper):
    pass


class comparison(ast_node):
    def __init__(self, node):
        self.operator = node.text.decode("utf-8")


def number(node):
    return float(node.text.decode("utf-8"))


def identifier(node: Node) -> str:
    return node.text.decode("utf-8")


class selector:
    def __init__(self, node: Optional[Node]):
        # This object represents a compound selector, which is made up of multiple simple selectors.
        if node is None:
            self.selectors: List[selector_base] = []
        else:
            self.selectors = [convert_selector_by_type(n) for n in node.children]

    def __add__(self, other):
        result = selector(None)
        result.selectors = self.selectors + other.selectors
        return result

    def applies_to_layer(self, layer_id) -> bool:
        for part in self.selectors:
            applies = part.applies_to_layer(layer_id)
            if applies is not None:
                return applies
        assert False, self

    @property
    def zoom_level_range(self):
        min = None
        max = None
        for s in self.selectors:
            smin, smax = s.zoom_level_range
            if min is None or (smin is not None and smin > min):
                min = smin
            if max is None or (smax is not None and smax < max):
                max = smax
        return (min, max)

    def __repr__(self):
        return repr(self.selectors)


class filter(ast_node, selector_base):
    def __init__(self, node):
        self.left = convert_node_by_type(node.child_by_field_name("left"))
        self.comparison = comparison(node.child_by_field_name("comparison"))
        self.right = convert_node_by_type(node.child_by_field_name("right"))

    @property
    def is_zoom_filter(self):
        return self.left == "zoom"

    @property
    def zoom_level_range(self):
        """
        [zoom >= 5] -> (5, None)
        """
        if not self.is_zoom_filter:
            return (None, None)
        right = int(self.right)
        return {
            ">": (right + 1, None),
            ">=": (right, None),
            "<": (None, right - 1),
            "<=": (None, right),
            "=": (right, right),
        }[self.comparison.operator]


class attachment(ast_node, selector_base, _identifier_wrapper):
    pass


class class_(ast_node, selector_base, _identifier_wrapper):
    pass


class declaration(ast_node):
    def __init__(self, node: Node):
        # self.instance = select_child(node, "instance") # TODO
        property_node = select_child(node, "property")
        self.property = property_node.text.decode("utf-8")
        self.values = [
            convert_child_by_type(n) for n in select_children(node, "values", "value")
        ]

    def __repr__(self) -> str:
        return f"declaration {self.property}={self.values}"


class url(ast_node):
    def __init__(self, node: Node):
        pass  # TODO
