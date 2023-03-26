def switch(images,
slice_number : int = None,
        axis : int = 0,
        display_width : int = None,
        display_height : int = None,
        continuous_update:bool = True,
        slider_text:str="Slice",
        zoom_factor:float = 1.0,
        zoom_spline_order:int = 0
):
    """Allows switching between multiple images.

    Parameters
    ----------
    images : list(image), or dict(str:image)
        Images to switch between. All images should have the same shape.
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
    An ipywidget with an image display and a slider.
    """
    from ._utilities import _no_resize
    from ._slice_viewer import _SliceViewer
    import ipywidgets

    if isinstance(images, dict):
        names = list(images.keys())
        images = list(images.values())
        layout = None
    else:
        names = [str(i) for i in range(len(images))]
        layout = ipywidgets.Layout(min_width='10px', max_width='30px')

    viewer = _SliceViewer(images[0],
                          slice_number,
                          axis,
                          display_width,
                          display_height,
                          continuous_update,
                          slider_text,
                          zoom_factor=zoom_factor,
                          zoom_spline_order=zoom_spline_order
                          )
    view = viewer.view
    slice_slider = viewer.slice_slider

    buttons = []
    for name, image in zip(names, images):
        button = _make_button(name, image, layout, viewer)
        buttons.append(button)

    return ipywidgets.VBox([_no_resize(view), ipywidgets.HBox(buttons), slice_slider])

def _make_button(name, image, layout, viewer):
    import ipywidgets
    if layout is None:
        button = ipywidgets.Button(description=name)
    else:
        button = ipywidgets.Button(description=name, layout=layout)

    def act(event=None):
        viewer.image = image
        viewer.configuration_updated()

    button.on_click(act)
    return button