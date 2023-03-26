def slice(
        image,
        slice_number : int = None,
        axis : int = 0,
        display_width : int = None,
        display_height : int = None,
        continuous_update:bool = True,
        slider_text:str="Slice",
        zoom_factor:float = 1.0,
        zoom_spline_order:int = 0
):
    """Shows an image with a slider to go through a stack.

    Parameters
    ----------
    image : image
        Image shown
    slice_number : int, optional
        Slice-position in the stack
    axis : int, optional
        Axis in case we are slicing a stack
    display_width : int, optional
        This parameter is obsolete. Use zoom_factor instead
    display_height : int, optional
        This parameter is obsolete. Use zoom_factor instead
    continuous_update : bool, optional
        Update the image while dragging the mouse, default: False
    zoom_factor: float, optional
        Allows showing the image larger (> 1) or smaller (<1)
    zoom_spline_order: int, optional
        Spline order used for interpolation (default=0, nearest-neighbor)

    Returns
    -------
    An ipywidget with an image display and a slider.
    """
    from ._utilities import _no_resize
    from ._slice_viewer import _SliceViewer

    import ipywidgets
    viewer = _SliceViewer(image,
        slice_number,
        axis,
        display_width,
        display_height,
        continuous_update,
        slider_text,
        zoom_factor=zoom_factor,
        zoom_spline_order=zoom_spline_order
    )
    view = viewer.view
    slice_slider = viewer.slice_slider

    return ipywidgets.VBox([_no_resize(view), slice_slider])
