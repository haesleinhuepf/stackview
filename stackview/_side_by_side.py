import warnings

def side_by_side(
        image1,
        image2,
        slice_number: int = None,
        axis: int = 0,
        display_width: int = None,
        display_height: int = None,
        continuous_update: bool = True,
        slider_text: str = "[{}]",
        zoom_factor:float = 1.0,
        zoom_spline_order:int = 0,
        colormap:list = ["pure_magenta", "pure_green"],
        display_min:float = None,
        display_max:float = None
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
        This parameter is obsolete. If you want to show any other axis than the first, you need to transpose the image before, e.g. using np.swapaxes().
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
    colormap: list, optional
        list of two Matplotlib colormap names or "pure_green", "pure_magenta", ...
    display_min: float, optional
        Lower bound of properly shown intensities
    display_max: float, optional
        Upper bound of properly shown intensities

    Returns
    -------
    An ipywidget with three image displays and a slider.
    """
    from ._slice_viewer import _SliceViewer

    import ipywidgets
    from ._image_widget import ImageWidget
    import numpy as np
    from ._utilities import _no_resize

    if 'cupy.ndarray' in str(type(image1)):
        image1 = image1.get()

    if 'cupy.ndarray' in str(type(image2)):
        image2 = image2.get()

    viewer = _SliceViewer(image1, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order, continuous_update=continuous_update, slider_text=slider_text, slice_number=slice_number)
    view1 = viewer.view #ImageWidget(slice_image, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)
    view2 = ImageWidget(viewer.view.data, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)
    view3 = ImageWidget(viewer.view.data, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)

    # setup user interface for changing the slice
    from ._image_widget import _is_label_image, _img_to_rgb

    # event handler when the user changed something:
    def configuration_updated(event=None):
        slice_image1 = viewer.get_view_slice(image1)
        slice_image2 = viewer.get_view_slice(image2)
        zeros_image = np.zeros(slice_image1.shape)
        if True or _is_label_image(slice_image1) or _is_label_image(slice_image2):
            rgb_image1 = _img_to_rgb(slice_image1, colormap=colormap[0], display_min=display_min, display_max=display_max)
            rgb_image2 = _img_to_rgb(slice_image2, colormap=colormap[1], display_min=display_min, display_max=display_max)

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
            else:
                factor1 = 0.5
                factor2 = 0.5

            rgb_mix = factor1 * rgb_image1 + factor2 * rgb_image2

            view1.data = rgb_image1
            view2.data = rgb_image2
            view3.data = rgb_mix
        else:
            view1.data = np.asarray([slice_image1, zeros_image, slice_image1]).swapaxes(0, 2)
            view2.data = np.asarray([zeros_image, slice_image2, zeros_image]).swapaxes(0, 2)
            view3.data = np.asarray([slice_image1, slice_image2, slice_image1]).swapaxes(0, 2)

    configuration_updated(None)

    # connect user interface with event
    viewer.observe(configuration_updated)

    result = _no_resize(ipywidgets.VBox([
        ipywidgets.HBox([_no_resize(view1), _no_resize(view2), _no_resize(view3)]),
    ] + viewer.sliders))

    result.update = configuration_updated

    print("side_by_side")

    return result
