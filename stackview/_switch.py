def switch(images,
           slice_number : int = None,
           axis : int = 0,
           display_width : int = None,
           display_height : int = None,
           continuous_update:bool = True,
           slider_text:str="[{}]",
           zoom_factor:float = 1.0,
           zoom_spline_order:int = 0,
           colormap:str = None,
           display_min:float = None,
           display_max:float = None,
           toggleable:bool = False
):
    """Allows switching between multiple images.

    Parameters
    ----------
    images : list(image), or dict(str:image)
        Images to switch between. All images should have the same shape.
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
    colormap: str, or list of str optional
        Matplotlib colormap name or "pure_green", "pure_magenta", ...
    display_min: float or list of float, optional
        Lower bound of properly shown intensities
    display_max: float of list of float, optional
        Upper bound of properly shown intensities
    toggleable: bool, optional
        If true, multiple images can be shown at the same time.
        In that case, it is recommended to pass a list as colormap as well.

    Returns
    -------
    An ipywidget with an image display and a slider.
    """
    from ._utilities import _no_resize
    from ._slice_viewer import _SliceViewer
    import ipywidgets
    from functools import partial
    from ._image_widget import _img_to_rgb
    import numpy as np

    if not isinstance(colormap, list):
        colormap = [colormap] * len(images)
    if not isinstance(display_min, list):
        display_min = [display_min] * len(images)
    if not isinstance(display_max, list):
        display_max = [display_max] * len(images)

    if isinstance(images, dict):
        names = list(images.keys())
        images = list(images.values())
        layout = None
    else:
        names = [str(i) for i in range(len(images))]
        layout = ipywidgets.Layout(min_width='10px', max_width='30px')

    images = [image.get() if 'cupy.ndarray' in str(type(image)) else image for image in images]

    viewer = _SliceViewer(images[0],
                          slice_number,
                          axis,
                          display_width,
                          display_height,
                          continuous_update,
                          slider_text,
                          zoom_factor=zoom_factor,
                          zoom_spline_order=zoom_spline_order,
                          colormap=colormap[0],
                          display_min=display_min[0],
                          display_max=display_max[0]
                          )
    view = viewer.view
    slice_slider = viewer.slice_slider

    buttons = []

    if toggleable:
        def display_(buttons, images, colormap, display_min, display_max):
            display_image = None
            for button, image, colormap_, display_min_, display_max_ in zip(buttons, images, colormap,
                                                                             display_min, display_max):
                if button.value:
                    display_image_to_add = _image_stack_to_rgb(image, display_min=display_min_, display_max=display_max_, colormap=colormap_)
                        
                    if display_image is None:
                        display_image = display_image_to_add
                    else:
                        display_image = display_image + display_image_to_add

            display_image = np.minimum(display_image, np.asarray([[255]]))

            viewer.view.colormap = None
            viewer.view.display_min = None
            viewer.view.display_max = None
            viewer.image = display_image
            viewer.update()

        display_function = partial(display_, buttons, images, colormap, display_min, display_max)
    else:
        def display_(image, colormap, display_min, display_max):
            viewer.view.colormap = colormap
            viewer.view.display_min = display_min
            viewer.view.display_max = display_max
            viewer.image = image
            viewer.update()

    for i, name, image, colormap_, display_min_, display_max_ in zip(range(len(names)), names, images, colormap, display_min, display_max):
        if toggleable:
            button = _make_toggle_button(name, layout, True, display_function)
        else:
            display_function = partial(display_, image, colormap_, display_min_, display_max_)
            button = _make_button(name, layout, display_function)

        buttons.append(button)
    if toggleable:
        display_function()
    result = _no_resize(ipywidgets.VBox([_no_resize(view), ipywidgets.HBox(buttons), slice_slider]))
    result.update = display_function
    return result


def _make_button(name, layout, display_function):
    import ipywidgets
    if layout is None:
        button = ipywidgets.Button(description=name)
    else:
        button = ipywidgets.Button(description=name, layout=layout)

    def act(event=None):
        display_function()

    button.on_click(act)
    return button

def _make_toggle_button(name, layout, value, display_function):
    import ipywidgets
    if layout is None:
        button = ipywidgets.ToggleButton(description=name, value=value)
    else:
        button = ipywidgets.ToggleButton(description=name, layout=layout, value=value)

    def act(event=None):
        display_function()

    button.observe(act, 'value')
    return button

def _image_stack_to_rgb(image, display_min, display_max, colormap):
    import numpy as np
    from ._image_widget import _img_to_rgb

    dims = list(image.shape)
    if 3 <= dims[-1] <= 4:
        dims = dims[:-1]

    if len(dims) > 2:
        return np.asarray([_image_stack_to_rgb(i, display_min=display_min, display_max=display_max, colormap=colormap) for i in image])
    return _img_to_rgb(image, display_min=display_min, display_max=display_max, colormap=colormap)
