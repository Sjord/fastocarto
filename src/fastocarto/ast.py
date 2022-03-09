from collections import defaultdict
import sys
from keyword import iskeyword


class ast_node:
    pass


def get_single_child(node):
    try:
        (child,) = node.children
    except ValueError:
        raise ValueError(
            f"Expected one child in `{node.type}` node, but got {node.children}"
        )
    return child


def select_child(node, *types):
    children = select_children(node, *types)
    try:
        (child,) = children
    except ValueError:
        raise ValueError(
            f"Expected one child of type {types} in {node}, but got {children}"
        )
    return child


def select_children(node, *types):
    if len(types) == 1:
        return [child for child in node.children if child.type == types[0]]
    else:
        result = []
        for subnode in select_children(node, types[0]):
            result += select_children(subnode, *types[1:])
        return result


def children_by_type(node):
    result = defaultdict(list)
    for child in node.children:
        result[child.type].append(child)
    return result


def convert_child_by_type(node):
    child = get_single_child(node)
    return convert_node_by_type(child)


def convert_node_by_type(node):
    type = node.type
    if iskeyword(type):
        type += "_"

    func = getattr(sys.modules[__name__], type)
    return func(node)


class _identifier_wrapper:
    def __init__(self, node):
        self.identifier = identifier(select_child(node, "identifier"))

    def __repr__(self):
        return f"{type(self).__name__}({self.identifier})"


class source_file(ast_node):
    def __init__(self, node, filename):
        self.filename = filename
        self.assignments = []
        self.rulesets = []

        statements = select_children(node, "statement")
        for statement in statements:
            children = children_by_type(statement)
            self.assignments += [assignment(n) for n in children["assignment"]]
            self.rulesets += [ruleset(n) for n in children["ruleset"]]

    def __repr__(self):
        return f"source_file({self.filename})"


class assignment(ast_node):
    def __init__(self, node):
        self.variable = identifier(select_child(node, "variable", "identifier"))
        self.values = [
            convert_child_by_type(n) for n in select_children(node, "values", "value")
        ]


class ruleset(ast_node):
    def __init__(self, node):
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


class color(ast_node):
    def __init__(self, node):
        child = get_single_child(node)
        self.value = child.text.decode("utf-8")


class expression(ast_node):
    def __init__(self, node):
        pass  # TODO


class function(ast_node):
    def __init__(self, node):
        self.identifier = identifier(select_child(node, "identifier"))
        self.parameters = [
            convert_child_by_type(n) for n in select_children(node, "values", "value")
        ]


class string_expr(ast_node):
    def __init__(self, node):
        self.values = [convert_node_by_type(n) for n in node.children if n.type != "+"]


def boolean(node):
    return bool(node.text)


def string(node):
    return node.children[1].text.decode("utf-8")


def percentage(node):
    return int(node.children[0].text) / 100


class Map(ast_node):
    def __init__(self, node):
        pass


class layer(ast_node, _identifier_wrapper):
    pass


class variable(ast_node, _identifier_wrapper):
    pass


class keyword(ast_node, _identifier_wrapper):
    pass


class field(ast_node, _identifier_wrapper):
    pass


def identifier(node):
    return node.text.decode("utf-8")


def selector(node):
    return [convert_node_by_type(n) for n in node.children]


class filter(ast_node):
    def __init__(self, node):
        pass  # TODO


class attachment(ast_node, _identifier_wrapper):
    pass


class class_(ast_node, _identifier_wrapper):
    pass


class declaration(ast_node):
    def __init__(self, node):
        # self.instance = select_child(node, "instance") # TODO
        self.property = select_child(node, "property")
        self.values = [
            convert_child_by_type(n) for n in select_children(node, "values", "value")
        ]


class url(ast_node):
    def __init__(self, node):
        pass  # TODO
