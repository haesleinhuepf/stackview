
def grid(tiles):
    from ipywidgets import VBox, HBox
    return VBox(tuple([HBox(tuple(line)) for line in tiles]))

