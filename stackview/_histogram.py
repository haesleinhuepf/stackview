import warnings

def histogram(
        image,
        slice_number: int = None,
        alpha: float = 0.5,
        continuous_update: bool = True,
        slider_text: str = "[{}]",
        zoom_factor: float = 1.0,
        zoom_spline_order: int = 0,
        colormap:str = None,
        display_min:float = None,
        display_max:float = None
):
    """Shows an image with a slider to go through a stack plus a label with the current mouse position and intensity at that position.

    Parameters
    ----------
    image : image
        Image shown
    labels: label image
        Labels which can be manually modified to draw annotations
    slice_number : int, optional
        Slice-position in the stack
    alpha : float, optional
        Alpha blending value for the labels on top of the image
    continuous_update : bool, optional
        Update the image while dragging the mouse on the slider, default: False
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
    from ._utilities import _no_resize
    from ._image_widget import _img_to_rgb
    import ipywidgets
    from ipyevents import Event
    from ._slice_viewer import _SliceViewer
    import numpy as np
    import matplotlib.pyplot as plt
    from ._grid import grid

    if 'cupy.ndarray' in str(type(image)):
        image = image.get()

    if slice_number is None:
        slice_number = int(image.shape[0] / 2)

    total_min = float(image.min())
    total_max = float(image.max())

    # Image view
    viewer = _SliceViewer(image,
                          zoom_factor=zoom_factor,
                          zoom_spline_order=zoom_spline_order,
                          colormap=colormap,
                          display_min=display_min,
                          display_max=display_max,
                          slider_text=slider_text)
    view = viewer.view
    # setup user interface for changing the slice
    slice_slider = viewer.slice_slider

    former_drawn_position = {'state':None,
                             'start_x': 0,
                             'start_y': 0,
                             'end_x': image.shape[-1],
                             'end_y': image.shape[-2],
                             }

    def create_histogram_plot(image, x, y, width, height):
        #return np.random.normal(50, y, (100, 100))
        cropped_image = image[..., y:y+height, x:x+width]

        min_val = np.min(cropped_image)
        max_val = np.max(cropped_image)

        #histogram = np.histogram(cropped_image, bins=256, range=(0, 255))
        # plot histogram and store histogram as numpy RGB array
        plt.figure(figsize=(1.8, 1.4))
        # measure how long this takes

        plt.hist(cropped_image.flatten(), bins=32)
        plt.xlim(total_min, total_max)
        plt.yticks([])
        plt.xticks([total_min, int((total_min + total_max) / 2), total_max])
        plt.tight_layout()

        from io import BytesIO
        from PIL import Image

        with BytesIO() as file_obj:
            plt.savefig(file_obj, format='png')
            plt.close()  # supress plot output
            file_obj.seek(0)

            # Open the image using PIL's Image.open() which accepts a file-like object
            histogram_image = Image.open(file_obj)

            # Convert the PIL image to a numpy array
            return np.array(histogram_image)[...,:3], min_val, max_val

    histogram_image, min_val, max_val = create_histogram_plot(image, 0, 0, image.shape[-2], image.shape[-1])
    histogram_viewer = _SliceViewer(histogram_image)

    width = image.shape[-1]
    height = image.shape[-2]
    layout = layout=ipywidgets.Layout(display="flex", max_height="25px")
    slice_lbl = ipywidgets.Label(f"(..., 0:{height}, 0:{width}", layout=layout)
    dtype_lbl = ipywidgets.Label(str(image.dtype), layout=layout)
    min_intensity_lbl = ipywidgets.Label(str(min_val), layout=layout)
    max_intensity_lbl = ipywidgets.Label(str(max_val), layout=layout)

    layout = ipywidgets.Layout(display="flex", justify_content="flex-end", min_width="50px", max_height="25px")

    table = grid([
        [ipywidgets.Label("slice", layout=layout), slice_lbl],
        [ipywidgets.Label("dtype", layout=layout), dtype_lbl],
        [ipywidgets.Label("min", layout=layout), min_intensity_lbl],
        [ipywidgets.Label("max", layout=layout), max_intensity_lbl],
    ])

    # event handler when the user changed the slider:
    def update_display(event=None):
        slice_image1 = viewer.get_view_slice()

        rgb_image1 = _img_to_rgb(slice_image1, colormap=colormap, display_min=display_min, display_max=display_max)
        from ._add_bounding_boxes import add_bounding_boxes
        bb = None
        if former_drawn_position['state'] is not None:
            bb = {
                'x': min(former_drawn_position['start_x'], former_drawn_position['end_x']),
                'y': min(former_drawn_position['start_y'], former_drawn_position['end_y']),
                'width': abs(former_drawn_position['start_x'] - former_drawn_position['end_x']),
                'height': abs(former_drawn_position['start_y'] - former_drawn_position['end_y'])
            }
            annotated_image = add_bounding_boxes(rgb_image1, [bb])
            slice_lbl.value = f"(..., {bb['y']}:{bb['y']+bb['height']}, {bb['x']}:{bb['x']+bb['width']})"
        else:
            annotated_image = rgb_image1

        if former_drawn_position['state'] == "mouse-up" and bb is not None:
            h_image, min_val, max_val = create_histogram_plot(slice_image1, bb['x'], bb['y'], bb['width'], bb['height'])
            histogram_viewer.view.data = h_image
            former_drawn_position['state'] = None
            min_intensity_lbl.value = str(min_val)
            max_intensity_lbl.value = str(max_val)

        view.data = annotated_image


    # user interface for histogram
    tool_box = ipywidgets.VBox([
        table,
        histogram_viewer.view
    ])

    event_handler = Event(source=view, watched_events=['mousemove'])

    if slice_slider is not None:
        # connect user interface with event
        result = _no_resize(ipywidgets.HBox([
            ipywidgets.VBox([_no_resize(view), slice_slider]),
            tool_box
        ]))
    else:
        result = _no_resize(ipywidgets.VBox([
            ipywidgets.HBox([_no_resize(view), tool_box]),
        ]))

    # event handler for when something was drawn
    def update_display_while_drawing(event):

        # get position from event
        relative_position_x = event['relativeX'] / zoom_factor
        relative_position_y = event['relativeY'] / zoom_factor
        absolute_position_x = int(relative_position_x)
        absolute_position_y = int(relative_position_y)


        if event['buttons'] == 0:
            if former_drawn_position['state'] == 'mouse-down':
                # not clicked
                former_drawn_position['state'] = 'mouse-up'
                update_display()
            return

        # compare position and last known position. If equal, don't update / redraw
        if former_drawn_position["end_x"] == absolute_position_x and former_drawn_position["end_y"] == absolute_position_y:
            return

        if former_drawn_position['state'] is None:
            # mouse-down event
            former_drawn_position['state'] = 'mouse-down'
            former_drawn_position['start_x'] = absolute_position_x
            former_drawn_position['start_y'] = absolute_position_y

        former_drawn_position['end_x'] = absolute_position_x
        former_drawn_position['end_y'] = absolute_position_y

        x = min(former_drawn_position['start_x'], former_drawn_position['end_x'])
        y = min(former_drawn_position['start_y'], former_drawn_position['end_y'])
        w = abs(former_drawn_position['start_x'] - former_drawn_position['end_x'])
        h = abs(former_drawn_position['start_y'] - former_drawn_position['end_y'])

        update_display()

    # draw everything once
    update_display()

    # connect events
    event_handler.on_dom_event(update_display_while_drawing)

    def viewer_update(e=None):
        former_drawn_position['state'] = 'mouse-up'
        update_display()
    viewer.observe(viewer_update)

    result.update = update_display
    return result
