import warnings

import numpy as np


def orthogonal(
        image,
        display_width : int = None,
        display_height : int = None,
        continuous_update:bool=True,
        zoom_factor:float = 1.0,
        zoom_spline_order:int = 0,
        colormap:str = None,
        display_min:float = None,
        display_max:float = None,
        crosshairs:bool = True,
):
    """Show three viewers slicing the image stack in Z,Y and X.

    Parameters
    ----------
    image : image
        Image to be displayed
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
    colormap: str, optional
        Matplotlib colormap name or "pure_green", "pure_magenta", ...
    display_min: float, optional
        Lower bound of properly shown intensities
    display_max: float, optional
        Upper bound of properly shown intensities
    crosshairs: bool, optional
        Show crosshairs in the image corresponding to the slice position

    Returns
    -------
    An ipywidget with an image display and a slider.

    See Also
    --------
    slice()
    """
    import ipywidgets
    from ._slice import slice

    if 'cupy.ndarray' in str(type(image)):
        image = image.get()

    if len(image.shape) != 3:
        warnings.warn("Orthogonal views are only supported for 3D images. Consider using slice() instead.")

    widgets = [
        slice(image, slider_text="Z", continuous_update=continuous_update, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order, colormap=colormap, display_min=display_min, display_max=display_max),
        slice(image.swapaxes(-3,-2).swapaxes(-2,-1), slider_text="Y", continuous_update=continuous_update, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order, colormap=colormap, display_min=display_min, display_max=display_max),
        slice(image.swapaxes(-3,-1), slider_text="X", continuous_update=continuous_update, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order, colormap=colormap, display_min=display_min, display_max=display_max),
    ]

    def update(event=None):
        for widget in widgets:
            widget.update()


    if crosshairs:
        def redraw0(event=None):
            image = np.copy(widgets[0].viewer.get_view_slice())
            y = widgets[1].viewer.get_slice_index()[-1]
            x = widgets[2].viewer.get_slice_index()[-1]
            image[y,:] = image.max()
            image[:,x] = image.max()
            widgets[0].viewer.view.data = image

        def redraw1(event=None):
            image = np.copy(widgets[1].viewer.get_view_slice())
            y = widgets[2].viewer.get_slice_index()[-1]
            x = widgets[0].viewer.get_slice_index()[-1]
            image[y, :] = image.max()
            image[:, x] = image.max()
            widgets[1].viewer.view.data = image


        def redraw2(event=None):
            image = np.copy(widgets[2].viewer.get_view_slice())
            y = widgets[1].viewer.get_slice_index()[-1]
            x = widgets[0].viewer.get_slice_index()[-1]
            image[y, :] = image.max()
            image[:, x] = image.max()
            widgets[2].viewer.view.data = image
    
        widgets[0].viewer.observe(redraw0)
        widgets[0].viewer.observe(redraw1)
        widgets[0].viewer.observe(redraw2)

        widgets[1].viewer.observe(redraw0)
        widgets[1].viewer.observe(redraw1)
        widgets[1].viewer.observe(redraw2)

        widgets[2].viewer.observe(redraw0)
        widgets[2].viewer.observe(redraw1)
        widgets[2].viewer.observe(redraw2)

        redraw0()
        redraw1()
        redraw2()

    widgets[1].layout=ipywidgets.Layout(margin='0 5px 0 5px')

    result = ipywidgets.HBox(widgets)
    result.update = update
    return result
