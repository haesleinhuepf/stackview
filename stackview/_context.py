import numpy as np

blacklist = ["try_all_threshold",
             "test",
             "minimum_of_touching_neighbors_map",
             "maximum_of_touching_neighbors_map",
             "standard_deviation_of_touching_neighbors_map",
             "mean_of_touching_neighbors_map",
             "z_position_of_minimum_z_projection",
             "z_position_of_maximum_z_projection",
             ]

def nop(image):
    """No operation, returns the image unchanged"""
    return image



class Context():
    def __init__(self, variables):
        from ._utilities import logo

        self._functions = {"stackview.nop": nop}
        self._modules = { }
        self._images = {"no_image": logo}
        #self._label_images = {}

        self.parse(variables.items())

    def parse(self, items, prefix: str = None):

        from types import ModuleType
        from typing import Callable
        import stackview
        from ._utilities import is_image, is_label_image, count_image_parameters

        for name, value in items:
            if not name.startswith("_"):
                if isinstance(value, ModuleType) and value is not stackview:
                    if prefix is None:
                        self._modules[name] = value
                        self.parse({key: getattr(value, key) for key in dir(value)}.items(), prefix=name + ".")
                elif isinstance(value, Callable):
                    if count_image_parameters(value) > 0:
                        if name not in blacklist:
                            if prefix is None:
                                self._functions[name] = value
                            else:
                                self._functions[prefix + name] = value
                elif is_image(value):
                    if prefix is None:
                        #if is_label_image(value):
                        #    self._label_images[name] = value
                        #else:
                            self._images[name] = value

