
def picker(
        image,
        slice_number: int = None,
        display_width: int = None,
        display_height: int = None,
        continuous_update: bool = False,
        slider_text: str = "Slice",
        zoom_factor:float = 1.0,
        zoom_spline_order:int = 0
):
    """Shows an image with a slider to go through a stack plus a label with the current mouse position and intensity at that position.

    Parameters
    ----------
    image : image
        Image shown
    slice_number : int, optional
        Slice-position in the stack
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
    An ipywidget with an image display, a slider and a label showing mouse position and intensity.
    """

    import ipywidgets
    viewer = _SliceViewer(image,
                          slice_number=slice_number,
                          display_width=display_width,
                          display_height=display_height,
                          continuous_update=continuous_update,
                          slider_text=slider_text,
                          zoom_factor=zoom_factor,
                          zoom_spline_order=zoom_spline_order
                          )
    view = viewer.view
    slice_slider = viewer.slice_slider
    label = ipywidgets.Label("[]:")

    from ipyevents import Event
    event_handler = Event(source=view, watched_events=['mousemove'])

    def update_display(event):
        relative_position_x = event['relativeX'] / zoom_factor
        relative_position_y = event['relativeY'] / zoom_factor
        absolute_position_x = int(relative_position_x)
        absolute_position_y = int(relative_position_y)

        if slice_slider is not None:
            absolute_position_z = slice_slider.value
            intensity = image[absolute_position_z, absolute_position_y, absolute_position_x]
            label.value = "[z=" + str(absolute_position_z) + ", y=" + str(absolute_position_y) + ", x=" + str(
                absolute_position_x) + "] = " + str(intensity)
        else:
            intensity = image[absolute_position_y, absolute_position_x]
            label.value = "[y=" + str(absolute_position_y) + ", x=" + str(absolute_position_x) + "] = " + str(intensity)

    event_handler.on_dom_event(update_display)

    if slice_slider is not None:
        return ipywidgets.VBox([_no_resize(view), slice_slider, label], stretch=False)
    else:
        return ipywidgets.VBox([_no_resize(view), label])

