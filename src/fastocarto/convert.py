from fastocarto.output import Style, Layer

def carto_to_mapnik(carto_model):
    result = []
    for layer in carto_model["Layer"]:
        assert layer["id"]
        # add multiple styles
        style = Style(layer["id"])
        # add layer
        layer = Layer(layer["id"])
        result.append(style)
        result.append(layer)
    return result



