__version__ = "0.1.0"


def slice(
        image,
        slice_number : int = None,
        axis : int = 0,
        display_width : int = 256,
        display_height : int = 256,
        continuous_update:bool=False,
        slider_text:str="Slice"
):
    """Shows an image with a slider to go through a stack.

    Parameters
    ----------
    image : image
        Image shown on the left (behind the curtain)
    slice_number : int, optional
        Slice-position in the stack
    axis : int, optional
        Axis in case we are slicing a stack
    display_width : int, optional
        Size of the displayed image in pixels
    display_height : int, optional
        Size of the displayed image in pixels
    continuous_update : bool, optional
        Update the image while dragging the mouse, default: False

    Returns
    -------
    An ipywidget with an image display and a slider.
    """

    import ipywidgets
    import numpy_image_widget as niw
    import numpy as np

    if slice_number is None:
        slice_number = int(image.shape[axis] / 2)

    if len(image.shape) <= 2:
        view = niw.NumpyImage(image)
    else:
        view = niw.NumpyImage(np.take(image, slice_number, axis=axis))
    if display_width is not None:
        view.width_display = display_width
    if display_height is not None:
        view.height_display = display_height
    if len(image.shape) <= 2:
        return view

    # setup user interface for changing the slice
    slice_slider = ipywidgets.IntSlider(
        value=slice_number,
        min=0,
        max=image.shape[0]-1,
        continuous_update=continuous_update,
        description = slider_text,
    )

    def transform_image(z):
        return np.take(image, z, axis=axis)

    # event handler when the user changed something:
    def configuration_updated(event):
        view.data = transform_image(slice_slider.value)

    # connect user interface with event
    slice_slider.observe(configuration_updated)

    configuration_updated(None)

    return ipywidgets.VBox([view, slice_slider])


def curtain(
        image,
        image_curtain,
        slice_number: int = None,
        axis: int = 0,
        display_width: int = 256,
        display_height: int = 256,
        continuous_update: bool = False
):
    """Show two images and allow with a slider to show either the one or the other image.

    Parameters
    ----------
    image : image
        Image shown on the left (behind the curtain)
    image_curtain : image
        Image shown on the right (in front of the curtain)
    slice_number : int, optional
        Slice-position in case we are looking at an image stack
    axis : int, optional
        Axis in case we are slicing a stack
    display_width : int, optional
        Size of the displayed image in pixels
    display_height : int, optional
        Size of the displayed image in pixels
    continuous_update : bool, optional
        Update the image while dragging the mouse, default: False

    Returns
    -------
    An ipywidget with an image display and a slider.
    """
    import ipywidgets
    import numpy_image_widget as niw
    import numpy as np

    slice_slider = None
    if len(image.shape) > 2:
        if slice_number is None:
            slice_number = int(image.shape[0] / 2)

        # setup user interface for changing the slice
        slice_slider = ipywidgets.IntSlider(
            value=slice_number,
            min=0,
            max=image.shape[0]-1,
            continuous_update=continuous_update,
            description="Slice"
        )

    # setup user interface for changing the curtain position
    curtain_slider = ipywidgets.IntSlider(
        value=slice_number,
        min=0,
        max=image.shape[-2],
        continuous_update=continuous_update,
        description="Curtain"
    )

    view = niw.NumpyImage(np.take(image, slice_number, axis=axis))
    if display_width is not None:
        view.width_display = display_width
    if display_height is not None:
        view.height_display = display_height

    def transform_image():
        if slice_slider is None:
            image_slice = image
            image_slice_curtain = image_curtain
        else:
            image_slice = np.take(image, slice_slider.value, axis=axis)
            image_slice_curtain = np.take(image_curtain, slice_slider.value, axis=axis)

        image_slice[:, curtain_slider.value:] = image_slice_curtain[:, curtain_slider.value:]
        return image_slice

    # event handler when the user changed something:
    def configuration_updated(event):
        view.data = transform_image()

    configuration_updated(None)

    # connect user interface with event
    curtain_slider.observe(configuration_updated)

    if slice_slider is not None:
        # connect user interface with event
        slice_slider.observe(configuration_updated)

        return ipywidgets.VBox([view, slice_slider, curtain_slider])
    else:
        return ipywidgets.VBox([view, curtain_slider])

def orthogonal(
        image,
        display_width : int = 256,
        display_height : int = 256,
        continuous_update:bool=False
):
    """

    Parameters
    ----------
    image : image
        Image to be displayed
    display_width : int, optional
        Size of the displayed image in pixels
    display_height : int, optional
        Size of the displayed image in pixels
    continuous_update : bool, optional
        Update the image while dragging the mouse, default: False

    Returns
    -------
    An ipywidget with an image display and a slider.

    See Also
    --------
    slice()
    """
    import ipywidgets

    return ipywidgets.HBox([
        slice(image, axis=0, slider_text="Z", display_width=display_width, display_height=display_height, continuous_update=continuous_update),
        slice(image, axis=1, slider_text="Y", display_width=display_width, display_height=display_height, continuous_update=continuous_update),
        slice(image, axis=2, slider_text="X", display_width=display_width, display_height=display_height, continuous_update=continuous_update),
    ])
