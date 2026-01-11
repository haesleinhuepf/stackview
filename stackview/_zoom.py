def zoom(
        image,
        slice_number: int = None,
        slider_text: str = "[{}]",
        zoom_factor: float = 1.0,
        zoom_spline_order: int = 0,
        colormap:str = None,
        display_min:float = None,
        display_max:float = None,
        max_height: int = 300,
):
    """Shows an image with a slider to go through a stack plus a label with the current mouse position and intensity at that position.

    Parameters
    ----------
    image : image
        Image shown
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
    max_height: int, optional
        Maximum height of the image display in pixels

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
    view.layout = ipywidgets.Layout(max_height=f'{max_height}px')

    # setup user interface for changing the slice
    slice_slider = viewer.slice_slider

    # Get the correct width and height for both RGB and grayscale images
    if image.ndim > 2 and image.shape[-1] in [3,4]:
        img_width = image.shape[-2]
        img_height = image.shape[-3]
    else:
        img_width = image.shape[-1]
        img_height = image.shape[-2]

    former_drawn_position = {'state': "mouse-up",
                             'start_x': 0,
                             'start_y': 0,
                             'end_x': int(img_width/2),
                             'end_y': int(img_height/2),
                             }

    def create_zoom_image(image, x, y, width, height):
        if image.ndim > 2 and image.shape[-1] in [3,4]: #RGB image
            zoomed_image = image[..., y:y+height, x:x+width, :]
        else:
            zoomed_image = image[..., y:y+height, x:x+width]
        return zoomed_image

    # For RGB images, shape is (..., height, width, channels), for grayscale it's (..., height, width)
    if image.ndim > 2 and image.shape[-1] in [3,4]:
        height = image.shape[-3]
        width = image.shape[-2]
    else:
        height = image.shape[-2]
        width = image.shape[-1]
    zoom_image = create_zoom_image(image, 0, 0, int(img_width/2), int(img_height/2))
    
    # Calculate the zoom factor for the zoom viewer so it matches the height of the main view
    # Main view height = image.shape[-2] * zoom_factor (for grayscale) or image.shape[-3] * zoom_factor (for RGB)
    # We want zoom_viewer height = main view height
    # So: zoom_image.shape[-2] * zoom_viewer_zoom_factor = actual_height * zoom_factor
    if image.ndim > 2 and image.shape[-1] in [3,4]:
        main_view_height = image.shape[-3] * zoom_factor
    else:
        main_view_height = image.shape[-2] * zoom_factor
    zoom_viewer_zoom_factor = main_view_height / zoom_image.shape[-2] if zoom_image.shape[-2] > 0 else 1.0
    
    zoom_viewer = _SliceViewer(zoom_image, 
                               zoom_factor=zoom_viewer_zoom_factor, 
                               zoom_spline_order=zoom_spline_order,
                               colormap=colormap,
                               display_min=display_min,
                               display_max=display_max)
    zoom_viewer.view.layout = ipywidgets.Layout(max_height=f'{max_height}px')

    layout = layout=ipywidgets.Layout(display="flex", max_height="25px")
    slice_lbl = ipywidgets.Label(f"(..., 0:{height}, 0:{width}", layout=layout)

    layout = ipywidgets.Layout(display="flex", justify_content="flex-end", min_width="50px", max_height="25px")

    table = grid([
        [ipywidgets.Label("slice", layout=layout), slice_lbl],
    ])

    # event handler when the user changed the slider:
    def update_display(event=None, height=height):
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
        else:
            bb = {
                'x': 0,
                'y': 0,
                'width': 50,
                'height': 50
            }
            
        annotated_image = add_bounding_boxes(rgb_image1, [bb], line_width=max(1, int(height/500 + 0.5)))
        slice_lbl.value = f"(..., {bb['y']}:{bb['y']+bb['height']}, {bb['x']}:{bb['x']+bb['width']})"

        if former_drawn_position['state'] == "mouse-up" and bb is not None:
            h_image = create_zoom_image(slice_image1, bb['x'], bb['y'], bb['width'], bb['height'])
            # Calculate zoom factor to match the main view height
            zoom_viewer_zoom_factor = main_view_height / h_image.shape[-2] if h_image.shape[-2] > 0 else 1.0
            zoom_viewer.view.zoom_factor = zoom_viewer_zoom_factor
            zoom_viewer.view.data = h_image
            former_drawn_position['state'] = None

        view.data = annotated_image

    # user interface for zoomed area
    tool_box = ipywidgets.VBox([
        _no_resize(zoom_viewer.view),
        table
    ])


    event_handler = Event(source=view, watched_events=['mousemove'])

    if slice_slider is not None:
        # connect user interface with event
        result = _no_resize(ipywidgets.HBox([
            ipywidgets.VBox([_no_resize(view), slice_slider]),
            ipywidgets.Label(" "),
            tool_box
        ]))
    else:
        result = _no_resize(ipywidgets.VBox([
            ipywidgets.HBox([_no_resize(view),
                             ipywidgets.Label(" "),
                             tool_box]),
        ]))

    # event handler for when something was drawn
    def update_display_while_drawing(event):

        # The event coordinates (relativeX, relativeY) are in the display widget's coordinate system
        # We need to map them to the actual image pixel coordinates
        # 
        # The Image widget displays the image data, and when the image is larger than the widget's
        # display area, it scales the image down. We need to calculate the scale factor between
        # the displayed size and the actual image size.
        
        # Get the displayed dimensions from the event (these are the actual rendered dimensions)
        displayed_width = event['boundingRectWidth']
        displayed_height = event['boundingRectHeight']
        
        # Calculate the actual image dimensions - handle RGB images differently
        if image.ndim > 2 and image.shape[-1] in [3,4]:
            actual_image_width = image.shape[-2]
            actual_image_height = image.shape[-3]
        else:
            actual_image_width = image.shape[-1]
            actual_image_height = image.shape[-2]
        
        # Calculate scale factors: display pixels -> image pixels
        scale_x = actual_image_width / displayed_width
        scale_y = actual_image_height / displayed_height

        # Map event coordinates to image pixel coordinates
        absolute_position_x = int(event['relativeX'] * scale_x)
        absolute_position_y = int(event['relativeY'] * scale_y)


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

        #update_display()

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
