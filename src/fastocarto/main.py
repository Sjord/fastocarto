from fastocarto.parse import parse_mml
from fastocarto.output import to_mapnik_xml
from fastocarto.convert import carto_to_mapnik
from pathlib import Path
import sys


def mml_to_mapnik_xml(mml_path):
    data = parse_mml(mml_path)
    data = carto_to_mapnik(data)
    return to_mapnik_xml(data)


def main():
    sys.stdout.buffer.write(mml_to_mapnik_xml(sys.argv[1]))
