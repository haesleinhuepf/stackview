import warnings

import numpy as np

class _SliceViewer():
    def __init__(self,
                 image,
                 slice_number: int = None,
                 axis: int = 0,
                 display_width: int = None,
                 display_height: int = None,
                 continuous_update: bool = True,
                 slider_text: str = "[{}]",
                 zoom_factor:float = 1.0,
                 zoom_spline_order:int = 0,
                 colormap:str = None,
                 display_min:float = None,
                 display_max:float = None,
                 ):
        import ipywidgets
        from ._image_widget import ImageWidget

        self.image = image

        if slice_number is None:
            slice_number = [int(s / 2) for s in image.shape[:-2]]
        if isinstance(slice_number, int):
            slice_number = [slice_number] * (len(image.shape) - 2)
        if not isinstance(slider_text, list):
            slider_text = [slider_text] * (len(image.shape) - 2)

        self.sliders = []
        self.slider_guis = []
        offset = 2
        if 3 >= image.shape[-1] >= 4: # RGB or RGBA images
            offset = 3
        for d in range(len(image.shape) - offset):
            slider = ipywidgets.IntSlider(
                value=slice_number[d],
                min=0,
                max=image.shape[d] - 1,
                continuous_update=continuous_update,
            )
            slider.layout.width = '100%'  # Make the slider full-width

            slider.observe(self.update)
            self.sliders.append(slider)

            self.slider_guis.append(ipywidgets.HBox([ipywidgets.Label(slider_text[d].format(d)), slider]))

        self.view = ImageWidget(self.get_view_slice(),
                                zoom_factor=zoom_factor,
                                zoom_spline_order=zoom_spline_order,
                                colormap=colormap,
                                display_min=display_min,
                                display_max=display_max)

        # setup user interface for changing the slice
        custom_css = "<style>.widget-readout { min-width: 1px !important; }</style>"
        self.slice_slider = ipywidgets.VBox(self.slider_guis[::-1] + [ipywidgets.HTML(custom_css)])
        self.update()

    def observe(self, x):
        for s in self.sliders:
            s.unobserve_all()
            s.observe(x)

    # event handler when the user changed something:
    def update(self, event=None):
        self.view.data = self.get_view_slice()
        return

    def configuration_updated(self, event=None):
        warnings.warn('SliceViewer.configuration_updated is deprecated, use SliceViewer.update instead.')
        return self.update(event)

    def get_view_slice(self, data=None):
        if data is None:
            data = self.image
        for d, slider in enumerate(self.sliders):
            data = np.take(data, slider.value, axis=0)
        return data

    def get_slice_index(self):
        return [s.value for s in self.sliders]
