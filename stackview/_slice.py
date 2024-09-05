def slice(
        image,
        slice_number : int = None,
        axis : int = 0,
        display_width : int = None,
        display_height : int = None,
        continuous_update:bool = True,
        slider_text:str="[{}]",
        zoom_factor:float = 1.0,
        zoom_spline_order:int = 0,
        colormap:str = None,
        display_min:float = None,
        display_max:float = None
):
    """Shows an image with a slider to go through a stack.

    Parameters
    ----------
    image : image
        Image shown
    slice_number : int, optional
        Slice-position in the stack
    axis : int, optional
        This parameter is obsolete. If you want to show any other axis than the first, you need to transpose the image before, e.g. using np.swapaxes().
    display_width : int, optional
        This parameter is obsolete. Use zoom_factor instead
    display_height : int, optional
        This parameter is obsolete. Use zoom_factor instead
    continuous_update : bool, optional
        Update the image while dragging the mouse, default: False
    slider_text: list or str, optional
        Text shown next to the slider(s).
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

    Returns
    -------
    An ipywidget with an image display and a slider.
    """
    from ._utilities import _no_resize
    from ._slice_viewer import _SliceViewer

    if 'cupy.ndarray' in str(type(image)):
        image = image.get()

    import ipywidgets
    viewer = _SliceViewer(image,
        slice_number,
        axis,
        display_width,
        display_height,
        continuous_update,
        slider_text,
        zoom_factor=zoom_factor,
        zoom_spline_order=zoom_spline_order,
        colormap=colormap,
        display_min=display_min,
        display_max=display_max
    )
    view = viewer.view
    slice_slider = viewer.slice_slider

    result = _no_resize(ipywidgets.VBox([_no_resize(view), slice_slider]))
    result.update = viewer.update
    result.viewer = viewer
    return result
