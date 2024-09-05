
def picker(
        image,
        slice_number: int = None,
        display_width: int = None,
        display_height: int = None,
        continuous_update: bool = True,
        slider_text: str = "[{}]",
        zoom_factor:float = 1.0,
        zoom_spline_order:int = 0,
        colormap:str = None,
        display_min:float = None,
        display_max:float = None
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
    slider_text: str, optional
        Text shown on the slider
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
    An ipywidget with an image display, a slider and a label showing mouse position and intensity.
    """

    import ipywidgets
    from ._slice_viewer import _SliceViewer
    from ._utilities import _no_resize

    if 'cupy.ndarray' in str(type(image)):
        image = image.get()

    viewer = _SliceViewer(image,
                          slice_number=slice_number,
                          continuous_update=continuous_update,
                          slider_text=slider_text,
                          zoom_factor=zoom_factor,
                          zoom_spline_order=zoom_spline_order,
                          colormap=colormap,
                          display_min=display_min,
                          display_max=display_max
                          )
    view = viewer.view
    slice_slider = viewer.slice_slider
    label = ipywidgets.Label("[]:")

    from ipyevents import Event
    event_handler = Event(source=view, watched_events=['mousemove'])

    def update_display(event=None):
        relative_position_x = event['relativeX'] / zoom_factor
        relative_position_y = event['relativeY'] / zoom_factor
        absolute_position_x = int(relative_position_x)
        absolute_position_y = int(relative_position_y)
        intensity = viewer.get_view_slice()[absolute_position_y, absolute_position_x]
        label.value = str(viewer.get_slice_index())[:-1] + ", " + str(absolute_position_y) + ", " + str(absolute_position_x) + "] = " + str(intensity)

    event_handler.on_dom_event(update_display)

    result = _no_resize(ipywidgets.VBox([_no_resize(view), slice_slider, label], stretch=False))
    result.update = update_display
    return result
