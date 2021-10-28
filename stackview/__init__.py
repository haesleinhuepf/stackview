__version__ = "0.1.3"

class _SliceViewer():
    def __init__(self,
                 image,
                 slice_number: int = None,
                 axis: int = 0,
                 display_width: int = 240,
                 display_height: int = 240,
                 continuous_update: bool = False,
                 slider_text: str = "Slice"
                 ):
        import ipywidgets
        from ._numpy_image_widget import NumpyImage
        import numpy as np

        self.image = image

        if slice_number is None:
            slice_number = int(image.shape[axis] / 2)

        if len(image.shape) <= 2:
            self.view = NumpyImage(image)
        else:
            self.view = NumpyImage(np.take(image, slice_number, axis=axis))
        if display_width is not None:
            self.view.width_display = display_width
        if display_height is not None:
            self.view.height_display = display_height
        if len(image.shape) <= 2:
            self.slice_slider = None
        else:
            # setup user interface for changing the slice
            self.slice_slider = ipywidgets.IntSlider(
                value=slice_number,
                min=0,
                max=image.shape[0] - 1,
                continuous_update=continuous_update,
                description=slider_text,
            )

        # event handler when the user changed something:
        def configuration_updated(event):
            if self.slice_slider is not None:
                self.view.data = np.take(self.image, self.slice_slider.value, axis=axis)
            else:
                self.view.data = self.image

        self.configuration_updated = configuration_updated

        if self.slice_slider is not None:
            # connect user interface with event
            self.slice_slider.observe(configuration_updated)

        configuration_updated(None)



def slice(
        image,
        slice_number : int = None,
        axis : int = 0,
        display_width : int = 240,
        display_height : int = 240,
        continuous_update:bool=False,
        slider_text:str="Slice"
):
    """Shows an image with a slider to go through a stack.

    Parameters
    ----------
    image : image
        Image shown
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
    viewer = _SliceViewer(image,
        slice_number,
        axis,
        display_width,
        display_height,
        continuous_update,
        slider_text
    )
    view = viewer.view
    slice_slider = viewer.slice_slider

    return ipywidgets.VBox([view, slice_slider])


def curtain(
        image,
        image_curtain,
        slice_number: int = None,
        axis: int = 0,
        display_width: int = 240,
        display_height: int = 240,
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
    from ._numpy_image_widget import NumpyImage
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
        value=image.shape[-1] / 2,
        min=0,
        max=image.shape[-1],
        continuous_update=continuous_update,
        description="Curtain"
    )

    if len(image.shape) <= 2:
        view = NumpyImage(image)
    else:
        view = NumpyImage(np.take(image, slice_number, axis=axis))
    if display_width is not None:
        view.width_display = display_width
    if display_height is not None:
        view.height_display = display_height

    def transform_image():
        if slice_slider is None:
            image_slice = image.copy()
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
        display_width : int = 240,
        display_height : int = 240,
        continuous_update:bool=False
):
    """Show three viewers slicing the image stack in Z,Y and X.

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


def side_by_side(
        image1,
        image2,
        slice_number: int = None,
        axis: int = 0,
        display_width: int = None,
        display_height: int = None,
        continuous_update: bool = False,
        slider_text: str = "Slice"
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
        Size of the displayed image in pixels
    display_height : int, optional
        Size of the displayed image in pixels
    continuous_update : bool, optional
        Update the image while dragging the mouse, default: False

    Returns
    -------
    An ipywidget with three image displays and a slider.
    """

    import ipywidgets
    from ._numpy_image_widget import NumpyImage
    import numpy as np

    if slice_number is None:
        slice_number = int(image1.shape[axis] / 2)

    if len(image1.shape) <= 2:
        slice_image = image1
    else:
        slice_image = np.take(image1, slice_number, axis=axis)

    zeros_image = np.zeros(slice_image.shape)
    view1 = NumpyImage(slice_image)
    view2 = NumpyImage(slice_image)
    view3 = NumpyImage(slice_image)

    if display_width is not None:
        view1.width_display = display_width
        view2.width_display = display_width
        view3.width_display = display_width
    if display_height is not None:
        view1.height_display = display_height
        view2.height_display = display_height
        view3.height_display = display_height

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

    # event handler when the user changed something:
    def configuration_updated(event):
        if slice_slider is not None:
            z = slice_slider.value
            slice_image1 = np.take(image1, z, axis=axis)
            slice_image2 = np.take(image2, z, axis=axis)
        else:
            slice_image1 = image1
            slice_image2 = image2
        view1.data = np.asarray([slice_image1, zeros_image, slice_image1]).swapaxes(0, 2)
        view2.data = np.asarray([zeros_image, slice_image2, zeros_image]).swapaxes(0, 2)
        view3.data = np.asarray([slice_image1, slice_image2, slice_image1]).swapaxes(0, 2)

    configuration_updated(None)

    if slice_slider is not None:
        # connect user interface with event
        slice_slider.observe(configuration_updated)

        return ipywidgets.VBox([
            ipywidgets.HBox([view1, view2, view3]),
            slice_slider
        ])
    else:
        return ipywidgets.HBox([view1, view2, view3])


def interact(func, image, *args, **kwargs):
    """Takes a function which has an image as first parameter and additional parameters.
    It will build a user interface consisting of sliders for numeric parameters and parameters
    that are called "footprint" or "selem".

    Parameters
    ----------
    func : function
    image : Image
    args
    kwargs

    """
    import inspect
    import ipywidgets

    exposable_parameters = []
    footprint_parameters = []

    sig = inspect.signature(func)
    for key in sig.parameters.keys():
        exposable = False
        default_value = 0
        if isinstance(sig.parameters[key].default, int) or isinstance(sig.parameters[key].default, float):
            default_value = sig.parameters[key].default

        if sig.parameters[key].annotation is int:
            default_value = ipywidgets.IntSlider(min=0, max=20, step=1, value=default_value, continuous_update=False)
            exposable = True
        elif sig.parameters[key].annotation is float:
            default_value = ipywidgets.FloatSlider(min=-20, max=20, step=1, value=default_value, continuous_update=False)
            exposable = True
        elif key == 'sigma' or key == 'radius':
            default_value = ipywidgets.FloatSlider(min=-20, max=20, step=1, value=default_value, continuous_update=False)
            exposable = True
        elif key == 'footprint' or key == 'selem' or key == 'structuring_element':
            footprint_parameters.append(key)
            default_value = ipywidgets.IntSlider(min=0, max=20, step=1, value=default_value)
            exposable = True

        if exposable:
            if key in kwargs.keys():
                default_value = kwargs[key]
            exposable_parameters.append(inspect.Parameter(key, inspect.Parameter.KEYWORD_ONLY, default=default_value))

    viewer = _SliceViewer(image)
    command_label = ipywidgets.Label(value=func.__name__ + "()")

    from skimage import morphology

    def worker_function(*otherargs, **kwargs):

        command = func.__name__ + "(..."

        for key in [e.name for e in exposable_parameters]:

            if key in footprint_parameters:
                if len(image.shape) == 2:
                    command = command + ", " + key + "=disk(" + str(kwargs[key]) + ")"
                    kwargs[key] = morphology.disk(kwargs[key])
                elif len(image.shape) == 3:
                    command = command + ", " + key + "=ball(" + str(kwargs[key]) + ")"
                    kwargs[key] = morphology.ball(kwargs[key])
            else:
                command = command + ", " + key + "=" + str(kwargs[key])
        command = command + ")"
        command_label.value = command

        viewer.image = func(image, *args, **kwargs)
        viewer.configuration_updated(None)



    import ipywidgets


    worker_function.__signature__ = inspect.Signature(exposable_parameters)

    ipywidgets.interact(worker_function)

    if viewer.slice_slider is not None:
        return ipywidgets.VBox([
            viewer.view,
            viewer.slice_slider,
            command_label
        ])
    else:
        return ipywidgets.VBox([
            viewer.view,
            command_label
        ])


def picker(
        image,
        slice_number: int = None,
        display_width: int = 240,
        display_height: int = 240,
        continuous_update: bool = False,
        slider_text: str = "Slice"
):
    """Shows an image with a slider to go through a stack plus a label with the current mouse position and intensity at that position.

    Parameters
    ----------
    image : image
        Image shown
    slice_number : int, optional
        Slice-position in the stack
    display_width : int, optional
        Size of the displayed image in pixels
    display_height : int, optional
        Size of the displayed image in pixels
    continuous_update : bool, optional
        Update the image while dragging the mouse, default: False

    Returns
    -------
    An ipywidget with an image display, a slider and a label showing mouse position and intensity.
    """

    import ipywidgets
    viewer = _SliceViewer(image,
                          slice_number=slice_number,
                          display_width=display_width,
                          display_height=display_height,
                          continuous_update=continuous_update,
                          slider_text=slider_text
                          )
    view = viewer.view
    slice_slider = viewer.slice_slider
    label = ipywidgets.Label("[]:")

    from ipyevents import Event
    event_handler = Event(source=view, watched_events=['mousemove'])

    def update_display(event):

        relative_position_x = event['offsetX'] / view.width_display
        relative_position_y = event['offsetY'] / view.height_display
        absolute_position_x = int(relative_position_x * image.shape[-1])
        absolute_position_y = int(relative_position_y * image.shape[-2])

        if slice_slider is not None:
            absolute_position_z = slice_slider.value
            intensity = image[absolute_position_z, absolute_position_y, absolute_position_x]
            label.value = "[z=" + str(absolute_position_z) + ", y=" + str(absolute_position_y) + ", x=" + str(
                absolute_position_x) + "] = " + str(intensity)
        else:
            intensity = image[absolute_position_y, absolute_position_x]
            label.value = "[y=" + str(absolute_position_y) + ", x=" + str(absolute_position_x) + "] = " + str(intensity)

    event_handler.on_dom_event(update_display)

    if slice_slider is not None:
        return ipywidgets.VBox([view, slice_slider, label])
    else:
        return ipywidgets.VBox([view, label])
