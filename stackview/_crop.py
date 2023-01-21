from ipywidgets import VBox

def crop(image,
         slice_number: int = 0,
         axis: int = 0,
         continuous_update: bool = False,
         slider_text: str = "Slice",
         axis_names=None,
         zoom_factor: float = 1.0,
         zoom_spline_order: int = 0):
    """
    Allows cropping an image along all axes.

    Parameters
    ----------
    image : image
        2D or 3D image to be cropped
    slice_number : int, optional
        Slice-position in the stack to be shown (default: center plane)
    axis : int, optional
        Axis along which we slice the shown stack (default: 0)
    continuous_update : bool, optional
        Update the image while dragging the sliders, default: False
    slider_text: str, optional
        Text to be shown next to the slider
    axis_names: list of str, optional
        Names of the axes. If not given, the default names Z,Y,X are used.
    zoom_factor: float, optional
        Allows showing the image larger (> 1) or smaller (<1)
    zoom_spline_order: int, optional
        Spline order used for interpolation (default=0, nearest-neighbor)

    """
    return _Cropper(image,
                    slice_number=slice_number,
                    axis=axis,
                    continuous_update=continuous_update,
                    slider_text=slider_text,
                    axis_names=axis_names,
                    zoom_factor=zoom_factor,
                    zoom_spline_order=zoom_spline_order)


class _Cropper(VBox):
    """
    See also
    --------
    crop()
    """
    def __init__(self,
                 image,
                 slice_number: int = 0,
                 axis: int = 0,
                 continuous_update: bool = False,
                 slider_text: str = "Slice",
                 axis_names=None,
                 zoom_factor: float = 1.0,
                 zoom_spline_order: int = 0):
        from ipywidgets import IntRangeSlider
        from ._slice_viewer import _SliceViewer
        from ._utilities import _no_resize

        self._image = image

        viewer = _SliceViewer(image,
                              slice_number,
                              axis,
                              0,
                              0,
                              continuous_update,
                              slider_text,
                              zoom_factor=zoom_factor,
                              zoom_spline_order=zoom_spline_order
                              )

        if len(image.shape) < 2 or len(image.shape) > 3:
            raise RuntimeError("Number of image dimensions must be 2 or 3, but is", len(image.shape))

        if axis_names is None:
            if len(image.shape) == 2:
                axis_names = ["Y", "X"]
            elif len(image.shape) == 3:
                axis_names = ["Z", "Y", "X"]

        view = viewer.view
        slice_slider = viewer.slice_slider

        def configuration_updated(event):
            viewer.image = image[self.range]
            viewer.slice_slider.max = viewer.image.shape[0] - 1
            viewer.configuration_updated(None)

        self._range_sliders = []
        for dim in range(len(image.shape)):
            min_ = 0
            max_ = image.shape[dim]

            range_slider = IntRangeSlider(
                value=[min_, max_],
                min=min_,
                max=max_,
                description=axis_names[dim],
                continuous_update=continuous_update,
            )
            range_slider.observe(configuration_updated)
            self._range_sliders.append(range_slider)

        widgets = []
        widgets = widgets + self._range_sliders
        widgets.append(_no_resize(view))
        if len(image.shape) > 2:
            widgets.append(slice_slider)

        super(_Cropper, self).__init__(widgets)

    @property
    def range(self):
        """
        Returns a tuple of Python slice objects that can be used to crop the image.
        """
        return tuple([slice(r.value[0], r.value[1], 1) for r in self._range_sliders])

    @range.setter
    def range(self, slices):
        """
        Sets the range of the sliders to the given Python slice objects.
        The step of the slices is ignored.
        """
        for a_slice, a_range_slider in zip(slices, self._range_sliders):
            a_range_slider.value = [a_slice.start, a_slice.stop]

    def crop(self):
        """
        Returns the cropped image.
        """
        from stackview import insight
        return insight(self._image[self.range])
