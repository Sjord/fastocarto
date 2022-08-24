
build/cartocss.so: tree-sitter-cartocss/src/parser.c
	python3 src/fastocarto/build.py

tree-sitter-cartocss/src/parser.c: tree-sitter-cartocss/grammar.js
	cd tree-sitter-cartocss && tree-sitter generate

test:
	PYTHONPATH=src python -m unittest

mypy:
	MYPYPATH=src .venv/bin/mypy -m fastocarto

.PHONY: test mypy
