def curtain(
        image,
        image_curtain,
        slice_number: int = None,
        axis: int = 0,
        display_width: int = None,
        display_height: int = None,
        continuous_update: bool = True,
        alpha: float = 1,
        zoom_factor: float = 1.0,
        zoom_spline_order: int = 0,
        colormap: str = None,
        display_min: float = None,
        display_max: float = None,
        curtain_colormap: str = None,
        curtain_display_min: float = None,
        curtain_display_max: float = None
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
        This parameter is obsolete. If you want to show any other axis than the first, you need to transpose the image before, e.g. using np.swapaxes().
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
    from ._slice_viewer import _SliceViewer
    import numpy as np
    from ._utilities import _no_resize
    from ._uint_field import intSlider

    if 'cupy.ndarray' in str(type(image)):
        image = image.get()

    if 'cupy.ndarray' in str(type(image_curtain)):
        image_curtain = image_curtain.get()

    # setup user interface for changing the curtain position
    slice_shape = list(image.shape)
    slice_shape.pop(axis)

    max_curtain_position = slice_shape[-1]
    if image.shape[-1] == 3:
        # RGB image
        max_curtain_position = slice_shape[-2]

    curtain_slider = intSlider(
        value=max_curtain_position / 2,
        min=0,
        max=max_curtain_position,
        continuous_update=continuous_update,
        description="Curtain"
    )

    viewer = None
    from ._image_widget import _img_to_rgb

    def transform_image():
        image_slice = _img_to_rgb(viewer.get_view_slice(), colormap=colormap, display_min=display_min, display_max=display_max).copy()
        image_slice_curtain = _img_to_rgb(viewer.get_view_slice(image_curtain), colormap=curtain_colormap, display_min=curtain_display_min, display_max=curtain_display_max)
        composited_image = image_slice.copy()
        composited_image[:, curtain_slider.value:] = (1 - alpha) * composited_image[:, curtain_slider.value:] + \
                                                     alpha * image_slice_curtain[:, curtain_slider.value:]
        return composited_image

    viewer = _SliceViewer(image, continuous_update=continuous_update, zoom_factor=zoom_factor,
                          zoom_spline_order=zoom_spline_order, colormap=colormap, display_min=display_min,
                          display_max=display_max)

    view = viewer.view  # ImageWidget(transform_image(), zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)
    sliders = viewer.slice_slider

    # event handler when the user changed something:
    def configuration_updated(event=None):
        view.data = transform_image()

    configuration_updated(None)

    # connect user interface with event
    curtain_slider.observe(configuration_updated)

    # connect user interface with event
    viewer.observe(configuration_updated)
    result = _no_resize(ipywidgets.VBox([_no_resize(view), sliders, curtain_slider]))
    result.update = configuration_updated
    result.viewer = viewer
    return result
