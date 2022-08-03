from lxml import etree as ET


def to_mapnik_xml(data):
    root = ET.Element("Map")
    root.extend([p.to_xml_element() for p in data])
    return ET.tostring(
        root,
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=True,
        doctype="<!DOCTYPE Map[]>",
    )


class Style:
    def __init__(self, name, rules):
        self.name = name
        self.rules = rules

    def to_xml_element(self):
        style = ET.Element("Style", {"filter-mode": "first", "name": self.name})
        for rule in self.rules:
            ET.SubElement(style, "Rule")
        return style


class Layer:
    def __init__(self, name):
        self.name = name

    def to_xml_element(self):
        return ET.Element("Layer", {"name": self.name})


class Rule:
    def __init__(self):
        pass
