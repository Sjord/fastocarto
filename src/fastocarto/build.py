from tree_sitter import Language, Parser

Language.build_library(
    "build/cartocss.so",
    [
        "tree-sitter-cartocss",
    ],
)
