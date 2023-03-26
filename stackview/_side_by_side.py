

def side_by_side(
        image1,
        image2,
        slice_number: int = None,
        axis: int = 0,
        display_width: int = None,
        display_height: int = None,
        continuous_update: bool = True,
        slider_text: str = "Slice",
        zoom_factor:float = 1.0,
        zoom_spline_order:int = 0
):
    """Shows two images in magenta and green plus a third with their colocalization / overlap view and
    a slider to go through a stack.

    Parameters
    ----------
    image1 : image
        Image shown on the left
    image2 : image
        Image shown on the right
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
    An ipywidget with three image displays and a slider.
    """

    import ipywidgets
    from ._image_widget import ImageWidget
    import numpy as np
    from ._utilities import _no_resize

    if slice_number is None:
        slice_number = int(image1.shape[axis] / 2)

    if len(image1.shape) <= 2:
        slice_image = image1
    else:
        slice_image = np.take(image1, slice_number, axis=axis)

    zeros_image = np.zeros(slice_image.shape)
    view1 = ImageWidget(slice_image, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)
    view2 = ImageWidget(slice_image, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)
    view3 = ImageWidget(slice_image, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)

    # setup user interface for changing the slice
    slice_slider = None
    if len(image1.shape) > 2:
        slice_slider = ipywidgets.IntSlider(
            value=slice_number,
            min=0,
            max=image1.shape[0] - 1,
            continuous_update=continuous_update,
            description=slider_text,
        )

    from ._image_widget import _is_label_image, _img_to_rgb

    # event handler when the user changed something:
    def configuration_updated(event):
        if slice_slider is not None:
            z = slice_slider.value
            slice_image1 = np.take(image1, z, axis=axis)
            slice_image2 = np.take(image2, z, axis=axis)
        else:
            slice_image1 = image1
            slice_image2 = image2

        if _is_label_image(slice_image1) or _is_label_image(slice_image2):
            rgb_image1 = _img_to_rgb(slice_image1)
            rgb_image2 = _img_to_rgb(slice_image2)

            if _is_label_image(slice_image1) and _is_label_image(slice_image2):
                warnings.warn("Side-by-side mixing two label images may look weird." +
                              "Consider showing original image and a label image side-by-side.")
                factor1 = 0.5
                factor2 = 0.5
            elif _is_label_image(slice_image1):
                factor1 = 0.3
                factor2 = 0.7
            elif _is_label_image(slice_image2):
                factor1 = 0.7
                factor2 = 0.3

            rgb_mix = factor1 * rgb_image1 + factor2 * rgb_image2

            view1.data = rgb_image1
            view2.data = rgb_image2
            view3.data = rgb_mix
        else:
            view1.data = np.asarray([slice_image1, zeros_image, slice_image1]).swapaxes(0, 2)
            view2.data = np.asarray([zeros_image, slice_image2, zeros_image]).swapaxes(0, 2)
            view3.data = np.asarray([slice_image1, slice_image2, slice_image1]).swapaxes(0, 2)

    configuration_updated(None)

    if slice_slider is not None:
        # connect user interface with event
        slice_slider.observe(configuration_updated)

        return ipywidgets.VBox([
            ipywidgets.HBox([_no_resize(view1), _no_resize(view2), _no_resize(view3)]),
            slice_slider
        ])
    else:
        return ipywidgets.HBox([_no_resize(view1), _no_resize(view2), _no_resize(view3)])
