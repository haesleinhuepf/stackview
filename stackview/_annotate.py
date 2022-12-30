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
        continuous_update: bool = False,
        slider_text: str = "Slice",
        zoom_factor: float = 1.0,
        zoom_spline_order: int = 0
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
        Axis where the slice-position can be modified interactively
    alpha : float, optional
        Alpha blending value for the labels on top of the image
    continuous_update : bool, optional
        Update the image while dragging the mouse on the slider, default: False
    zoom_factor: float, optional
        Allows showing the image larger (> 1) or smaller (<1)
    zoom_spline_order: int, optional
        Spline order used for interpolation (default=0, nearest-neighbor)

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

    if not _is_label_image(labels):
        warnings.warn("Labels are not an image of type uint32 or uint64. Consider converting to this type for best performance.")

    if slice_number is None:
        slice_number = int(image.shape[axis] / 2)

    if len(image.shape) <= 2:
        slice_image = image
    else:
        slice_image = np.take(image, slice_number, axis=axis)

    # Image view
    view = ImageWidget(slice_image, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)

    # setup user interface for changing the slice
    slice_slider = None
    if len(image.shape) > 2:
        slice_slider = ipywidgets.IntSlider(
            value=slice_number,
            min=0,
            max=image.shape[axis] - 1,
            continuous_update=continuous_update,
            description=slider_text,
        )

    # event handler when the user changed the slider:
    def update_display(event=None):
        if slice_slider is not None:
            z = slice_slider.value
            slice_image1 = np.take(image, z, axis=axis)
            slice_image2 = np.take(labels, z, axis=axis)
        else:
            slice_image1 = image
            slice_image2 = labels

        if not _is_label_image(slice_image2):
            # necessary to display the labels in colour correctly
            slice_image2 = slice_image2.astype(np.uint64)

        rgb_image1 = _img_to_rgb(slice_image1)
        rgb_image2 = _img_to_rgb(slice_image2)

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

        # differentiate 3D/2D drawing
        if slice_slider is not None:
            absolute_position_z = slice_slider.value
            position = [absolute_position_x, absolute_position_y, absolute_position_z]
        else:
            absolute_position_z = None
            position = [absolute_position_x, absolute_position_y]

        # compare position and label with last known postion. If equal, don't update / redraw
        position.append(label_id_to_draw)
        if np.array_equal(former_drawn_position, position):
            label.value = 'skip'
            return

        # draw one circle
        draw_circle(absolute_position_x,
                    absolute_position_y,
                    absolute_position_z,
                    axis,
                    radius,
                    label_id_to_draw,
                    labels)

        # draw circles along a line we've beend drawing
        if former_drawn_position[0] is not None:
            distance = np.linalg.norm(np.asarray(position[0:2]) - np.asarray(former_drawn_position[0:2]))
            for i in range(int(distance)):
                relative_position = i / int(distance)
                position_to_draw = relative_position * np.asarray(former_drawn_position[0:2]) + \
                                   (1.0 - relative_position) * np.asarray(position[0:2])
                draw_circle(position_to_draw[0],
                            position_to_draw[1],
                            absolute_position_z,
                            axis,
                            radius,
                            label_id_to_draw,
                            labels)

        # store position
        for i in range(4):
            former_drawn_position[i] = position[i]
        update_display()

    # draw everything once
    update_display()

    # connect events
    event_handler.on_dom_event(update_display_while_drawing)

    if slice_slider is not None:
        # connect user interface with event
        slice_slider.observe(update_display)

        return ipywidgets.VBox([
            ipywidgets.HBox([_no_resize(view), tool_box]),
            slice_slider
        ])
    else:
        return ipywidgets.VBox([
            ipywidgets.HBox([_no_resize(view), tool_box]),
        ])
