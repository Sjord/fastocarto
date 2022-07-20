from pathlib import Path
from yaml import safe_load
import fastocarto.ast


class StyleParser:
    def __init__(self, mml_path: Path):
        from tree_sitter import Language, Parser

        self.parser = Parser()
        self.parser.set_language(Language("build/cartocss.so", "cartocss"))
        self.mml_path = mml_path

    def parse(self, mss_path):
        abs_path = self.mml_path.parent / mss_path
        with open(abs_path, "rb") as fp:
            cst = self.parser.parse(fp.read())
            return fastocarto.ast.source_file(cst.root_node, mss_path)


def parse_mml(mml_path):
    # parse mml and stylesheets and return in some data structure
    mml_path = Path(mml_path)
    p = StyleParser(mml_path)

    with open(mml_path, "r") as fp:
        mml_tree = safe_load(fp)
        mml_tree["Stylesheet"] = [p.parse(s) for s in mml_tree["Stylesheet"]]
        return mml_tree
