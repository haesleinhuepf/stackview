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
        from ._uint_field import intSlider
        self.update_active = True

        self.image = image

        if slice_number is None:
            slice_number = [int(s / 2) for s in image.shape[:-2]]
        if isinstance(slice_number, int):
            slice_number = [slice_number] * (len(image.shape) - 2)
        if not isinstance(slider_text, list):
            slider_text = [slider_text] * (len(image.shape) - 2)

        self.sliders = []
        offset = 2
        if image.shape[-1] == 3 or image.shape[-1] == 4: # RGB or RGBA images
            offset = 3

        for d in range(len(image.shape) - offset):
            slider = intSlider(
                value=slice_number[d],
                min=0,
                max=image.shape[d] - 1,
                continuous_update=continuous_update,
                description=slider_text[d].format(d)
            )
            slider.layout.width = '100%'  # Make the slider full-width

            slider.observe(self.update)
            self.sliders.append(slider)

        self.view = ImageWidget(self.get_view_slice(),
                                zoom_factor=zoom_factor,
                                zoom_spline_order=zoom_spline_order,
                                colormap=colormap,
                                display_min=display_min,
                                display_max=display_max)

        # setup user interface for changing the slice

        self.slice_slider = ipywidgets.VBox(self.sliders[::-1])
        self.update()

    def set_image(self, image):
        for i, s in enumerate(self.sliders):
            s._set_value_min_max(int(image.shape[i] / 2), 0, image.shape[i] - 1)
        self.image = image

    def observe(self, x):
        self.update_active = False
        for s in self.sliders:
            s.observe(x)

    # event handler when the user changed something:
    def update(self, event=None):
        if self.update_active:
            self.view.data = self.get_view_slice()

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
