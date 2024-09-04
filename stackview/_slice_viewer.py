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
                 display_max:float = None
                 ):
        import ipywidgets
        from ._image_widget import ImageWidget

        self.image = image
        #self.axis = axis

        if slice_number is None:
            slice_number = [int(s / 2) for s in image.shape[:-2]]
        if isinstance(slice_number, int):
            slice_number = [slice_number] * (len(image.shape) - 2)
        if not isinstance(slider_text, list):
            slider_text = [slider_text] * (len(image.shape) - 2)

        self.sliders = []
        offset = 2
        if 3 >= image.shape[-1] >= 4: # RGB or RGBA images
            offset = 3
        for d in range(len(image.shape) - offset):
            slider = ipywidgets.IntSlider(
                value=slice_number[d],
                min=0,
                max=image.shape[d] - 1,
                continuous_update=continuous_update,
                description=slider_text[d].format(d),
            )
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
        # widgets.link((sliders1, 'value'), (slider2, 'value'))

        # connect user interface with event
        #self.slice_slider.observe(self.update)

        self.update()

    # event handler when the user changed something:
    def update(self, event=None):
        self.view.data = self.get_view_slice()
        return
        if len(self.image.shape) == 3 and self.image.shape[-1] != 3: # 3D
            self.slice_slider.layout.display = None
            self.view.data = np.take(self.image, self.slice_slider.value, axis=self.axis)
        elif len(self.image.shape) == 4 and self.image.shape[-1] == 3: # 3D RGB
            self.slice_slider.layout.display = None
            self.view.data = np.take(self.image, self.slice_slider.value, axis=self.axis)
        elif len(self.image.shape) == 4:
            raise NotImplementedError("Only 2D and 3D images are supported" + str(self.image.shape))
        else:
            self.view.data = self.image
            self.slice_slider.layout.display = 'none'

    def configuration_updated(self, event=None):
        warnings.warn('SliceViewer.configuration_updated is deprecated, use SliceViewer.update instead.')
        return self.update(event)

    def get_view_slice(self):
        data = self.image
        for d, slider in enumerate(self.sliders):
            data = np.take(data, slider.value, axis=0)
        return data