from ipywidgets import VBox

def crop(image,
         slice_number: int = None,
         axis: int = 0,
         continuous_update: bool = True,
         slider_text: str = "Slice",
         axis_names=None,
         zoom_factor: float = 1.0,
         zoom_spline_order: int = 0,
         colormap:str = None,
         display_min:float = None,
         display_max:float = None):
    """
    Allows cropping an image along all axes.

    Parameters
    ----------
    image : image
        2D or 3D image to be cropped
    slice_number : int, optional
        Slice-position in the stack to be shown (default: center plane)
    axis : int, optional
        This parameter is obsolete. If you want to show any other axis than the first, you need to transpose the image before, e.g. using np.swapaxes().
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
    colormap: str, optional
        Matplotlib colormap name or "pure_green", "pure_magenta", ...
    display_min: float, optional
        Lower bound of properly shown intensities
    display_max: float, optional
        Upper bound of properly shown intensities

    """
    import warnings

    if 'cupy.ndarray' in str(type(image)):
        image = image.get()

    if len(image.shape) > 3:
        warnings.warn("Orthogonal views are only supported for 3D images. Consider using slice() instead.")

    return _Cropper(image,
                    slice_number=slice_number,
                    axis=axis,
                    continuous_update=continuous_update,
                    slider_text=slider_text,
                    axis_names=axis_names,
                    zoom_factor=zoom_factor,
                    zoom_spline_order=zoom_spline_order,
                    colormap=colormap,
                    display_min=display_min,
                    display_max=display_max)




class _Cropper(VBox):
    """
    See also
    --------
    crop()
    """
    def __init__(self,
                 image,
                 slice_number: int = None,
                 axis: int = 0,
                 continuous_update: bool = False,
                 slider_text: str = "Slice",
                 axis_names=None,
                 zoom_factor: float = 1.0,
                 zoom_spline_order: int = 0,
                 colormap:str = None,
                 display_min:float = None,
                 display_max:float = None):
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
                              zoom_spline_order=zoom_spline_order,
                              colormap=colormap,
                              display_min=display_min,
                              display_max=display_max
                              )

        if len(image.shape) < 2 or len(image.shape) > 3:
            raise RuntimeError("Number of image dimensions must be 2 or 3, but is", len(image.shape))

        if axis_names is None:
            if len(image.shape) == 2:
                axis_names = ["Y", "X"]
            elif len(image.shape) == 3:
                axis_names = ["Z", "Y", "X"]

        self._viewer = viewer
        view = viewer.view
        slice_slider = viewer.slice_slider

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
            range_slider.observe(self.update)
            self._range_sliders.append(range_slider)

        widgets = []
        widgets = widgets + self._range_sliders
        widgets.append(_no_resize(view))
        if len(image.shape) > 2:
            widgets.append(slice_slider)

        super(_Cropper, self).__init__([_no_resize(VBox(widgets))])

    def update(self, event=None):
        import numpy as np
        self._viewer.image = self._image[self.range]
        self._viewer.slice_slider.max = self._viewer.image.shape[0] - 1
        try:
            self._viewer.update(None)
        except:
            self._viewer.view.data = np.zeros((2,2))


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
