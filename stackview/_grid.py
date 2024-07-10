
def grid(tiles):
    from ipywidgets import VBox, HBox
    return VBox(tuple([HBox(tuple(_remove_none(line))) for line in tiles]))

def _remove_none(line):
    import ipywidgets
    result = []
    for cell in line:
        result.append(cell if cell is not None else ipywidgets.Label(""))
    return result
