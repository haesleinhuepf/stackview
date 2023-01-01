
def curtain(
        image,
        image_curtain,
        slice_number: int = None,
        axis: int = 0,
        display_width: int = None,
        display_height: int = None,
        continuous_update: bool = False,
        alpha: float = 1,
        zoom_factor :float = 1.0,
        zoom_spline_order :int = 0
):
    """Show two images and allow with a slider to show either the one or the other image.

    Parameters
    ----------
    image : image
        Image shown on the left (behind the curtain)
    image_curtain : image
        Image shown on the right (in front of the curtain)
    slice_number : int, optional
        Slice-position in case we are looking at an image stack
    axis : int, optional
        Axis in case we are slicing a stack
    display_width : int, optional
        This parameter is obsolete. Use zoom_factor instead
    display_height : int, optional
        This parameter is obsolete. Use zoom_factor instead
    continuous_update : bool, optional
        Update the image while dragging the mouse, default: False
    alpha: float, optional
        sets the transperancy of the curtain
    zoom_factor: float, optional
        Allows showing the image larger (> 1) or smaller (<1)
    zoom_spline_order: int, optional
        Spline order used for interpolation (default=0, nearest-neighbor)

    Returns
    -------
    An ipywidget with an image display and a slider.
    """
    import ipywidgets
    from ._image_widget import ImageWidget
    import numpy as np
    from ._utilities import _no_resize

    slice_slider = None
    if len(image.shape) > 2:
        if slice_number is None:
            slice_number = int(image.shape[axis] / 2)

        # setup user interface for changing the slice
        slice_slider = ipywidgets.IntSlider(
            value=slice_number,
            min=0,
            max=image.shape[axis ] -1,
            continuous_update=continuous_update,
            description="Slice"
        )

    # setup user interface for changing the curtain position
    slice_shape = list(image.shape)
    slice_shape.pop(axis)
    curtain_slider = ipywidgets.IntSlider(
        value=slice_shape[-1] / 2,
        min=0,
        max=slice_shape[-1],
        continuous_update=continuous_update,
        description="Curtain"
    )

    if len(image.shape) <= 2:
        view = ImageWidget(image, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)
    else:
        view = ImageWidget(np.take(image, slice_number, axis=axis), zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)
    if display_width is not None:
        view.width = display_width
    if display_height is not None:
        view.height = display_height

    from ._image_widget import _img_to_rgb

    def transform_image():
        if len(image.shape) < 3:
            image_slice = _img_to_rgb(image.copy())
            image_slice_curtain = _img_to_rgb(image_curtain)
        else:
            image_slice = _img_to_rgb(np.take(image, slice_slider.value, axis=axis))
            image_slice_curtain = _img_to_rgb(np.take(image_curtain, slice_slider.value, axis=axis))

        image_slice[curtain_slider.value:] = (1 - alpha) * image_slice[curtain_slider.value:] + \
                                             alpha * image_slice_curtain[curtain_slider.value:]
        return image_slice

    # event handler when the user changed something:
    def configuration_updated(event):
        view.data = transform_image()

    configuration_updated(None)

    # connect user interface with event
    curtain_slider.observe(configuration_updated)

    # connect user interface with event
    slice_slider.observe(configuration_updated)
    return ipywidgets.VBox([_no_resize(view), slice_slider, curtain_slider])
