from tree_sitter import Language

Language.build_library(
    "build/cartocss.so",
    [
        "tree-sitter-cartocss",
    ],
)
