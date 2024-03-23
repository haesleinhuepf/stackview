
def curtain(
        image,
        image_curtain,
        slice_number: int = None,
        axis: int = 0,
        display_width: int = None,
        display_height: int = None,
        continuous_update: bool = True,
        alpha: float = 1,
        zoom_factor :float = 1.0,
        zoom_spline_order :int = 0,
        colormap:str = None,
        display_min:float = None,
        display_max:float = None,
        curtain_colormap:str = None,
        curtain_display_min:float = None,
        curtain_display_max:float = None
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
    colormap: str, optional
        Matplotlib colormap name or "pure_green", "pure_magenta", ...
    display_min: float, optional
        Lower bound of properly shown intensities
    display_max: float, optional
        Upper bound of properly shown intensities
    curtain_colormap: str, optional
        Matplotlib colormap name or "pure_green", "pure_magenta", ...
    curtain_display_min: float, optional
        Lower bound of properly shown intensities
    curtain_display_max: float, optional
        Upper bound of properly shown intensities

    Returns
    -------
    An ipywidget with an image display and a slider.
    """
    import ipywidgets
    from ._image_widget import ImageWidget
    import numpy as np
    from ._utilities import _no_resize

    if 'cupy.ndarray' in str(type(image)):
        image = image.get()

    if 'cupy.ndarray' in str(type(image_curtain)):
        image_curtain = image_curtain.get()

    slice_slider = None

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
    if len(image.shape) < 3 or (len(image.shape) == 3 and image.shape[-1] == 3):
        slice_slider.layout.display = 'none'

    # setup user interface for changing the curtain position
    slice_shape = list(image.shape)
    slice_shape.pop(axis)

    max_curtain_position = slice_shape[-1]
    if image.shape[-1] == 3:
        # RGB image
        max_curtain_position = slice_shape[-2]

    curtain_slider = ipywidgets.IntSlider(
        value=max_curtain_position / 2,
        min=0,
        max=max_curtain_position,
        continuous_update=continuous_update,
        description="Curtain"
    )

    from ._image_widget import _img_to_rgb
    def transform_image():
        if len(image.shape) < 3 or (len(image.shape) == 3 and image.shape[-1] == 3):
            image_slice = _img_to_rgb(image.copy(), colormap=colormap, display_min=display_min, display_max=display_max)
            image_slice_curtain = _img_to_rgb(image_curtain, colormap=curtain_colormap, display_min=curtain_display_min, display_max=curtain_display_max)
        else:
            image_slice = _img_to_rgb(np.take(image, slice_slider.value, axis=axis), colormap=colormap, display_min=display_min, display_max=display_max)
            image_slice_curtain = _img_to_rgb(np.take(image_curtain, slice_slider.value, axis=axis), colormap=curtain_colormap, display_min=curtain_display_min, display_max=curtain_display_max)
        image_slice[:,curtain_slider.value:] = (1 - alpha) * image_slice[:,curtain_slider.value:] + \
                                             alpha * image_slice_curtain[:,curtain_slider.value:]
        return image_slice
    view = ImageWidget(transform_image(), zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)

    # event handler when the user changed something:
    def configuration_updated(event=None):
        view.data = transform_image()

    configuration_updated(None)

    # connect user interface with event
    curtain_slider.observe(configuration_updated)

    # connect user interface with event
    slice_slider.observe(configuration_updated)
    result = ipywidgets.VBox([_no_resize(view), slice_slider, curtain_slider])
    result.update = configuration_updated
    return result
