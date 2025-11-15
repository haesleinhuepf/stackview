import numpy
import ipywidgets
from ._slice_viewer import _SliceViewer
from ._utilities import _no_resize
from ipyevents import Event

def vis(
        image,
        slice_number: int = None,
        slider_text: str = "Slice",
        display_min: float = None,
        display_max: float = None,
        mode: str = 'mag'
):
    """Shows an image stack with controls for slice and display range, plus a label with the current mouse position and intensity at that position.

    Parameters
    ----------
    image : image
        Image shown
    slice_number : int, optional
        Slice-position in the stack
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

    image = numpy.transpose(image, (2, 1, 0))
    if numpy.iscomplexobj(image):
        modes = ['mag', 'real', 'imag', 'phase']
    else:
        modes = ['real', 'mag']
    true_image = image.copy()

    def get_image_mode(im, mo):
        if mo == 'mag':
            im = numpy.abs(im)
        elif numpy.iscomplexobj(im):
            if mo == 'real':
                im = numpy.real(im)
            elif mo == 'imag':
                im = numpy.imag(im)
            elif mo == 'phase':
                im = numpy.angle(im)
        else:
            mo = 'real'
        return im
    
    image = get_image_mode(true_image, mode)

    viewer = _SliceViewer(image,
                          slice_number=slice_number,
                          continuous_update=True,
                          slider_text=slider_text,
                          colormap=None,
                          display_min=display_min,
                          display_max=display_max
                          )
    view = viewer.view
    label = ipywidgets.Label("():")

    mode_dropdown = ipywidgets.Dropdown(
        options=modes,
        value=mode,
        # description='Mode:',
        disabled=False,
        layout=ipywidgets.Layout(margin='0px 20px 0px 0px')
    )

    def on_mode_change(event=None):
        if event is None or event["name"] != "value":
            return
        mode = event['new']
        image = get_image_mode(true_image, mode)
        viewer.set_image(image)

        new_min_value = min(viewer.display_range_slider.value[0], image.min())
        new_max_value = max(viewer.display_range_slider.value[1], image.max())
        viewer.display_range_slider._set_value_min_max((new_min_value, new_max_value), image.min(), image.max())
        viewer.update()

    mode_dropdown.observe(on_mode_change)
    
    modelabel = ipywidgets.Label('Mode:')
    mode_box = ipywidgets.HBox([ipywidgets.HBox([modelabel, mode_dropdown])])

    event_handler = Event(source=view, watched_events=['mousemove'])

    image_shape = image.shape

    def update_display(event=None):
        slice_number = viewer.get_slice_index()
        bbox_width, bbox_height = int(event['boundingRectWidth']), int(event['boundingRectHeight'])
        relative_position_x = event['relativeX']
        relative_position_y = event['relativeY']

        relative_position_x_scaled = relative_position_x / bbox_width
        relative_position_y_scaled = relative_position_y / bbox_height

        absolute_position_x = int(relative_position_x_scaled * image_shape[2])
        absolute_position_y = int(relative_position_y_scaled * image_shape[1])

        intensity = image[slice_number, absolute_position_y, absolute_position_x].item()
        label.value = f"({absolute_position_x}, {absolute_position_y}, {slice_number[0]}) = {intensity:03f}"

    event_handler.on_dom_event(update_display)

    display_elements = [_no_resize(view)]
    display_elements.extend(viewer.controls)
    # display_elements.append(mode_dropdown)
    # display_elements.append(label)

    display_elements.append(ipywidgets.HBox([mode_box, label]))

    result = _no_resize(ipywidgets.VBox(display_elements, stretch=False))
    result.update = update_display
    return result
