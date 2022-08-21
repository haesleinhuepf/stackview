from ipywidgets import VBox, HBox

class MyVBox(VBox):
    def _repr_html_(self):
        output = "".join([_child_to_html(child) for child in self.children])
        return output

class MyHBox(HBox):
    def _repr_html_(self):
        output = "".join([_child_to_html(child) for child in self.children])
        return output

def _child_to_html(child):
    if hasattr(child, "_repr_html_"):
        return child._repr_html_()
    return str(child)

