
def orthogonal(
        image,
        display_width : int = None,
        display_height : int = None,
        continuous_update:bool=False,
        zoom_factor:float = 1.0,
        zoom_spline_order:int = 0
):
    """Show three viewers slicing the image stack in Z,Y and X.

    Parameters
    ----------
    image : image
        Image to be displayed
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

    See Also
    --------
    slice()
    """
    import ipywidgets
    from ._slice import slice

    return ipywidgets.HBox([
        slice(image, axis=0, slider_text="Z", continuous_update=continuous_update, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order),
        slice(image, axis=1, slider_text="Y", continuous_update=continuous_update, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order),
        slice(image, axis=2, slider_text="X", continuous_update=continuous_update, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order),
    ])