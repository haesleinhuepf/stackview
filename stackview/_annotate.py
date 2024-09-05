import warnings


def draw_circle(x, y, z, axis, radius, value, image):
    from skimage.draw import disk

    # draw circle
    rr, cc = disk((y, x), radius)
    if z is not None:
        if axis == 0:
            image_slice = image[z]
        elif axis == 1:
            image_slice = image[:, z]
        elif axis == 2:
            image_slice = image[:, :, z]
        image_slice[rr, cc] = value
    else:
        image[rr, cc] = value


def annotate(
        image,
        labels,
        slice_number: int = None,
        alpha: float = 0.5,
        axis: int = 0,
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
    axis: int, optional
        This parameter is obsolete. If you want to show any other axis than the first, you need to transpose the image before, e.g. using np.swapaxes().
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
    from ._image_widget import _is_label_image, _img_to_rgb
    import ipywidgets
    from ._image_widget import ImageWidget
    import numpy as np
    from ipyevents import Event
    from ._uint_field import UIntField
    from ._slice_viewer import _SliceViewer

    if 'cupy.ndarray' in str(type(image)):
        image = image.get()

    if 'cupy.ndarray' in str(type(labels)):
        labels = labels.get()

    if not _is_label_image(labels):
        warnings.warn("Labels are not an image of type uint32 or uint64. Consider converting to this type for best performance.")

    if slice_number is None:
        slice_number = int(image.shape[axis] / 2)

    #if len(image.shape) <= 2:
    #    slice_image = image
    #else:
    #    slice_image = np.take(image, slice_number, axis=axis)

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


    # event handler when the user changed the slider:
    def update_display(event=None):
        slice_image1 = viewer.get_view_slice()
        slice_image2 = viewer.get_view_slice(labels)

        if not _is_label_image(slice_image2):
            # necessary to display the labels in colour correctly
            slice_image2 = slice_image2.astype(np.uint64)

        rgb_image1 = _img_to_rgb(slice_image1, colormap=colormap, display_min=display_min, display_max=display_max)
        rgb_image2 = _img_to_rgb(slice_image2, colormap=colormap, display_min=display_min, display_max=display_max)

        factor1 = 1.0 - alpha
        factor2 = alpha

        rgb_mix = factor1 * rgb_image1 + factor2 * rgb_image2

        view.data = rgb_mix

    # user interface for drawing
    label_id_slider = UIntField(1)
    radius_slider = UIntField(2)
    radius_eraser_slider = UIntField(4)
    tool_box = ipywidgets.VBox([
        ipywidgets.Label("Label ID:"),
        label_id_slider,
        ipywidgets.Label("Draw radius:"),
        radius_slider,
        ipywidgets.Label("Eraser radius:"),
        radius_eraser_slider
    ])

    event_handler = Event(source=view, watched_events=['mousemove'])

    former_drawn_position = [None, 0, 0, 0]

    # event handler for when something was drawn
    def update_display_while_drawing(event):
        if event['buttons'] == 0:
            former_drawn_position[0] = None
            return

        # 'altKey' makes use of the eraser
        label_id_to_draw = label_id_slider.value
        radius = radius_slider.value
        if event['altKey']:
            label_id_to_draw = 0
            radius = radius_eraser_slider.value

        # get position from event
        relative_position_x = event['relativeX'] / zoom_factor
        relative_position_y = event['relativeY'] / zoom_factor
        absolute_position_x = int(relative_position_x)
        absolute_position_y = int(relative_position_y)

        labels_2d = labels
        # differentiate nd/2D drawing
        slice_indices = viewer.get_slice_index()
        while len(slice_indices) > 0:
            index = slice_indices.pop(0)
            labels_2d = labels_2d[index]
        position = [absolute_position_x, absolute_position_y, label_id_to_draw]

        # compare position and label with last known postion. If equal, don't update / redraw
        if np.array_equal(former_drawn_position, position):
            return

        # draw one circle
        draw_circle(absolute_position_x,
                    absolute_position_y,
                    None,
                    axis,
                    radius,
                    label_id_to_draw,
                    labels_2d)

        # draw circles along a line we've beend drawing
        if former_drawn_position[0] is not None:
            distance = np.linalg.norm(np.asarray(position[0:2]) - np.asarray(former_drawn_position[0:2]))
            for i in range(int(distance)):
                relative_position = i / int(distance)
                position_to_draw = relative_position * np.asarray(former_drawn_position[0:2]) + \
                                   (1.0 - relative_position) * np.asarray(position[0:2])
                draw_circle(position_to_draw[0],
                            position_to_draw[1],
                            None,
                            axis,
                            radius,
                            label_id_to_draw,
                            labels_2d)

        # store position
        for i in range(4):
            if i < len(position):
                former_drawn_position[i] = position[i]
        update_display()

    # draw everything once
    update_display()

    # connect events
    event_handler.on_dom_event(update_display_while_drawing)

    viewer.observe(update_display)
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
    result.update = update_display
    return result
