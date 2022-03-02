import sys
from pathlib import Path
from yaml import safe_load


def print_siblings(cursor, indent):
    while True:
        print("  " * indent + cursor.node.type)

        if cursor.goto_first_child():
            print_siblings(cursor, indent + 1)
            cursor.goto_parent()

        if not cursor.goto_next_sibling():
            break


def print_tree(tree):
    cursor = tree.walk()
    print_siblings(cursor, 0)

def print_siblings2(node, indent):
    print("  " * indent + node.type)
    for child in node.children:
        print_siblings2(child, indent + 1)

# ~18% slower than print_tree
def print_tree2(tree):
    node = tree.root_node
    print_siblings2(node, 0)


class StyleParser:
    def __init__(self):
        from tree_sitter import Language, Parser
        self.parser = Parser()
        self.parser.set_language(Language('build/cartocss.so', 'cartocss'))
    
    def parse(self, stylesheet):
        with open(stylesheet, "rb") as fp:
            return self.parser.parse(fp.read())



p = StyleParser()

mml_file = Path(sys.argv[1])

with open(mml_file, "r") as fp:
    tree = safe_load(fp)
    styles = tree['Stylesheet']
    for s in styles:
        abs_file = mml_file.parent / s
        tree = p.parse(abs_file)
        print_tree(tree)
