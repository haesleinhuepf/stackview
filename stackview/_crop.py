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
    colormap: str, optional
        Matplotlib colormap name or "pure_green", "pure_magenta", ...
    display_min: float, optional
        Lower bound of properly shown intensities
    display_max: float, optional
        Upper bound of properly shown intensities

    """

    if 'cupy.ndarray' in str(type(image)):
        image = image.get()

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

        from ipyevents import Event

        event_handler_top_left = Event(source=view, watched_events=["click"])
        event_handler_bottom_right = Event(source=view, watched_events=["auxclick"])

        def update_rec_top_left(event=None):
            relative_position_x = event["relativeX"] / zoom_factor
            relative_position_y = event["relativeY"] / zoom_factor
            positions = [int(relative_position_y), int(relative_position_x)]

            for i in [-1, -2]:
                cmin, cmax = self._range_sliders[i].value
                cvalue = positions[i] + cmin  # Adjust position for current crop
                self._range_sliders[i].value = (cvalue, cmax)

            if len(self._image.shape) > 2:
                cmin, cmax = self._range_sliders[0].value
                cvalue = slice_slider.value + cmin
                self._range_sliders[0].value = (cvalue, cmax)
                slice_slider.value = 0
            self.update()

        def update_rec_bottom_right(event=None):
            relative_position_x = event["relativeX"] / zoom_factor
            relative_position_y = event["relativeY"] / zoom_factor
            positions = [int(relative_position_y), int(relative_position_x)]

            for i in [-1, -2]:
                cmin, cmax = self._range_sliders[i].value
                cvalue = positions[i] + cmin  # Adjust position for current crop
                self._range_sliders[i].value = (cmin, cvalue)

            if len(self._image.shape) > 2:
                cmin, cmax = self._range_sliders[0].value
                cvalue = slice_slider.value + cmin  + 1
                self._range_sliders[0].value = (cmin, cvalue)
                slice_slider.value = cvalue - cmin + 1
            self.update()

        event_handler_top_left.on_dom_event(update_rec_top_left)
        event_handler_bottom_right.on_dom_event(update_rec_bottom_right)

        super(_Cropper, self).__init__(widgets)

    def update(self, event=None):
        self._viewer.image = self._image[self.range]
        self._viewer.slice_slider.max = self._viewer.image.shape[0] - 1
        self._viewer.update(None)

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
