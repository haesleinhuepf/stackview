import ipywidgets

class UIntField(ipywidgets.HBox):
    """
    A text field where users can select a positive integer number from.
    Similar to ipywidgets.IntText
    """

    def __init__(self, value):
        self._value = value
        self._label = ipywidgets.Label(str(value))
        layout = ipywidgets.Layout(min_width='10px', max_width='30px')
        self._button_up = ipywidgets.Button(description="+", layout=layout)
        self._button_down = ipywidgets.Button(description="-", layout=layout)
        super().__init__([self._button_down, self._label, self._button_up])

        def increase(event=None):
            self.value = self.value + 1

        def decrease(event=None):
            self.value = self.value - 1

        self._button_up.on_click(increase)
        self._button_down.on_click(decrease)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value >= 0:
            self._value = value
            self._label.value = str(value)