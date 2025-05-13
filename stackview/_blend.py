def blend(
        image1,
        image2,
        slice_number: int = None,
        axis: int = 0,
        continuous_update: bool = True,
        blend_factor: float = 0.5,
        zoom_factor: float = 1.0,
        zoom_spline_order: int = 0,
        colormap1: str = None,
        display_min1: float = None,
        display_max1: float = None,
        colormap2: str = None,
        display_min2: float = None,
        display_max2: float = None
):
    """Show two images blended together with a slider to control the blend factor.

    Parameters
    ----------
    image1 : image
        First image to blend
    image2 : image
        Second image to blend
    slice_number : int, optional
        Slice-position in case we are looking at an image stack
    axis : int, optional
        This parameter is obsolete. If you want to show any other axis than the first, you need to transpose the image before, e.g. using np.swapaxes().
    continuous_update : bool, optional
        Update the image while dragging the mouse, default: True
    blend_factor: float, optional
        Controls the blend between images (0 = only image1, 1 = only image2)
    zoom_factor: float, optional
        Allows showing the image larger (> 1) or smaller (<1)
    zoom_spline_order: int, optional
        Spline order used for interpolation (default=0, nearest-neighbor)
    colormap1: str, optional
        Matplotlib colormap name or "pure_green", "pure_magenta", ... for first image
    display_min1: float, optional
        Lower bound of properly shown intensities for first image
    display_max1: float, optional
        Upper bound of properly shown intensities for first image
    colormap2: str, optional
        Matplotlib colormap name or "pure_green", "pure_magenta", ... for second image
    display_min2: float, optional
        Lower bound of properly shown intensities for second image
    display_max2: float, optional
        Upper bound of properly shown intensities for second image

    Returns
    -------
    An ipywidget with an image display and a slider.
    """
    import ipywidgets
    from ._image_widget import ImageWidget
    from ._slice_viewer import _SliceViewer
    import numpy as np
    from ._utilities import _no_resize
    from ._uint_field import intSlider

    if 'cupy.ndarray' in str(type(image1)):
        image1 = image1.get()

    if 'cupy.ndarray' in str(type(image2)):
        image2 = image2.get()

    # setup user interface for changing the blend factor
    blend_slider = intSlider(
        value=blend_factor,
        min=0,
        max=100,
        continuous_update=continuous_update,
        description="Blend"
    )

    viewer = None
    from ._image_widget import _img_to_rgb

    def transform_image():
        image_slice1 = _img_to_rgb(viewer.get_view_slice(), colormap=colormap1, display_min=display_min1, display_max=display_max1).copy()
        image_slice2 = _img_to_rgb(viewer.get_view_slice(image2), colormap=colormap2, display_min=display_min2, display_max=display_max2)
        blend_value = blend_slider.value / 100
        blended_image = (1 - blend_value) * image_slice1 + blend_value * image_slice2
        return blended_image

    viewer = _SliceViewer(image1, continuous_update=continuous_update, zoom_factor=zoom_factor,
                          zoom_spline_order=zoom_spline_order, colormap=colormap1, display_min=display_min1,
                          display_max=display_max1)

    view = viewer.view
    sliders = viewer.slice_slider

    # event handler when the user changed something:
    def configuration_updated(event=None):
        view.data = transform_image()

    configuration_updated(None)

    # connect user interface with event
    blend_slider.observe(configuration_updated)

    # connect user interface with event
    viewer.observe(configuration_updated)
    result = _no_resize(ipywidgets.VBox([_no_resize(view), sliders, blend_slider]))
    result.update = configuration_updated
    result.viewer = viewer
    return result 