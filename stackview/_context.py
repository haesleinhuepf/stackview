import numpy as np

def nop(image):
    """No operation, returns the image unchanged"""
    return image

class Context():
    def __init__(self, variables):
        self._functions = {"stackview.nop": nop}
        self._modules = {}
        self._images = {}
        self._label_images = {}

        self.parse(variables.items())

    def parse(self, items, prefix: str = None):

        from types import ModuleType
        from typing import Callable
        from ._utilities import is_image, is_label_image, count_image_parameters

        for name, value in items:
            if not name.startswith("_"):
                if isinstance(value, ModuleType):
                    if prefix is None:
                        self._modules[name] = value
                        self.parse({key: getattr(value, key) for key in dir(value)}.items(), prefix=name + ".")
                elif isinstance(value, Callable):
                    if count_image_parameters(value) > 0:
                        if prefix is None:
                            self._functions[name] = value
                        else:
                            self._functions[prefix + name] = value
                elif is_image(value):
                    if prefix is None:
                        if is_label_image(value):
                            self._label_images[name] = value
                        else:
                            self._images[name] = value








