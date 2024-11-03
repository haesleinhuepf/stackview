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

def intSlider(min:int=0, max:int=100, step:int=1, value:int=1, continuous_update:bool=True, description:str=""):
    slider = ipywidgets.IntSlider(
        value=value,
        min=min,
        max=max,
        step=step,
        continuous_update=continuous_update
    )
    slider.layout.width = '100%'

    label = ipywidgets.Label(description)

    custom_css = "<style>.widget-readout { min-width: 20px !important; }</style>"
    html = ipywidgets.HTML(custom_css)

    box = ipywidgets.VBox([ipywidgets.HBox([label, slider]),html])

    def observe(*args, **kwargs):
        slider.observe(*args, **kwargs)
    box.observe = observe

    def update(event=None):
        box.value = slider.value

    slider.observe(update)

    def _set_value_min_max(value, min, max):
        slider.value = value
        slider.min = min
        slider.max = max

    box._set_value_min_max = _set_value_min_max

    update()

    return box
