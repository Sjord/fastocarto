from pathlib import Path
from yaml import safe_load
import fastocarto.ast


class StyleParser:
    def __init__(self):
        from tree_sitter import Language, Parser

        self.parser = Parser()
        self.parser.set_language(Language("build/cartocss.so", "cartocss"))

    def parse_mss_file(self, mss_path):
        with open(mss_path, "rb") as fp:
            return self.parse_mss_contents(fp.read())

    def parse_mss_contents(self, mss_content):
        cst = self.parser.parse(mss_content)
        return fastocarto.ast.source_file(cst.root_node)


def parse_mml(mml_path):
    # parse mml and stylesheets and return in some data structure
    mml_path = Path(mml_path)
    p = StyleParser()

    with open(mml_path, "r") as fp:
        mml_tree = safe_load(fp)
        mss_paths = [mml_path.parent / mss_path for mss_path in mml_tree["Stylesheet"]]
        mml_tree["Stylesheet"] = [p.parse_mss_file(s) for s in mss_paths]
        return mml_tree
