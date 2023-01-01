
class _SliceViewer():
    def __init__(self,
                 image,
                 slice_number: int = None,
                 axis: int = 0,
                 display_width: int = None,
                 display_height: int = None,
                 continuous_update: bool = False,
                 slider_text: str = "Slice",
                 zoom_factor:float = 1.0,
                 zoom_spline_order:int = 0
                 ):
        import ipywidgets
        from ._image_widget import ImageWidget
        import numpy as np

        self.image = image

        if slice_number is None:
            slice_number = int(image.shape[axis] / 2)

        if len(self.image.shape) == 3 and self.image.shape[-1] != 3:
            self.view = ImageWidget(np.take(image, slice_number, axis=axis), zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)
        else:
            self.view = ImageWidget(image, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)

        if display_width is not None:
            self.view.width = display_width
        if display_height is not None:
            self.view.height = display_height

        # setup user interface for changing the slice
        self.slice_slider = ipywidgets.IntSlider(
            value=slice_number,
            min=0,
            max=image.shape[axis] - 1,
            continuous_update=continuous_update,
            description=slider_text,
        )
        # widgets.link((sliders1, 'value'), (slider2, 'value'))

        # event handler when the user changed something:
        def configuration_updated(event):
            if len(self.image.shape) == 3 and self.image.shape[-1] != 3:
                self.slice_slider.layout.display = None
                self.view.data = np.take(self.image, self.slice_slider.value, axis=axis)
            else:
                self.view.data = self.image
                self.slice_slider.layout.display = 'none'

        self.configuration_updated = configuration_updated

        # connect user interface with event
        self.slice_slider.observe(configuration_updated)

        configuration_updated(None)