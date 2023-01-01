def interact(func,
             image = None,
             *args,
             continuous_update: bool = False,
             context:dict = None,
             zoom_factor:float = 1.0,
             zoom_spline_order:int = 0,
             **kwargs):
    """Takes a function which has an image as first parameter and additional parameters.
    It will build a user interface consisting of sliders for numeric parameters and parameters
    that are called "footprint" or "selem".

    Parameters
    ----------
    func : function
    image : Image, optional
        If not provided, context must be provided instead.
    args
    continuous_update : bool, optioonal
        Update the image while dragging the mouse, default: False
    context:dict, optional
        A dictionary of (name:image), allows showing a pulldown of available images.
    zoom_factor: float, optional
        Allows showing the image larger (> 1) or smaller (<1)
    zoom_spline_order: int, optional
        Spline order used for interpolation (default=0, nearest-neighbor)
    context:dict
        dictionary of name, value pairs that can be selected from pulldowns, e.g.: globals()
    kwargs

    """
    import inspect
    import ipywidgets
    from ._utilities import parameter_is_image_parameter, _no_resize
    from ._context import Context

    exposable_parameters = []
    footprint_parameters = []
    image_parameters = []

    if context is not None:
        context = Context(context)

    image_passed = image is not None
    if context is not None and image is None:
        image = next(iter(context._images.values()))


    sig = inspect.signature(func)
    for key in sig.parameters.keys():
        exposable = False
        default_value = 0
        if isinstance(sig.parameters[key].default, int) or isinstance(sig.parameters[key].default, float):
            default_value = sig.parameters[key].default
        min_value, max_value, step = guess_range(key, sig.parameters[key].annotation)

        if min_value is not None:
            int_slider = ipywidgets.IntSlider
            float_slider = ipywidgets.FloatSlider
        else:
            int_slider = ipywidgets.IntText
            float_slider = ipywidgets.FloatText

        if sig.parameters[key].annotation is int:
            default_value = int_slider(min=min_value, max=max_value, step=step, value=default_value, continuous_update=continuous_update)
            exposable = True
        elif sig.parameters[key].annotation is float or 'sigma' in key or 'radius' in key:
            default_value = float_slider(min=min_value, max=max_value, step=step, value=default_value, continuous_update=continuous_update)
            exposable = True
        elif key.startswith("is_") or sig.parameters[key].annotation is bool:
            default_value = ipywidgets.Checkbox(value=default_value)
            exposable = True
        elif key == 'footprint' or key == 'selem' or key == 'structuring_element':
            footprint_parameters.append(key)
            default_value = ipywidgets.IntSlider(min=min_value, max=max_value, step=step, value=default_value, continuous_update=continuous_update)
            exposable = True
        elif parameter_is_image_parameter(sig.parameters[key]) and "destination" not in key and key != "out"  and key != "output":
            if context is not None:
                image_parameters.append(key)
                default_value = ipywidgets.Dropdown(
                    options=list(context._images.keys())
                    #options=[(k, v) for k, v in context._images.items()],
                )
                exposable = True

        if exposable:
            if key in kwargs.keys():
                default_value = kwargs[key]
            exposable_parameters.append(inspect.Parameter(key, inspect.Parameter.KEYWORD_ONLY, default=default_value))

    viewer = _SliceViewer(image, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)
    if viewer.slice_slider is not None:
        viewer.slice_slider.continuous_update=continuous_update
    command_label = ipywidgets.Label(value=func.__name__ + "()")

    from skimage import morphology

    def worker_function(*otherargs, **kwargs):

        command = func.__name__ + "("
        if image_passed:
            command = command + "..."

        for key in [e.name for e in exposable_parameters]:

            if key in footprint_parameters:
                if len(image.shape) == 2:
                    command = command + ", " + key + "=disk(" + str(kwargs[key]) + ")"
                    kwargs[key] = morphology.disk(kwargs[key])
                elif len(image.shape) == 3:
                    command = command + ", " + key + "=ball(" + str(kwargs[key]) + ")"
                    kwargs[key] = morphology.ball(kwargs[key])
            elif key in image_parameters:
                command = command + ", " + key + "=" + str(kwargs[key])
                kwargs[key] = context._images[kwargs[key]]
            else:
                command = command + ", " + key + "=" + str(kwargs[key])
        command = command + ")"
        command_label.value = command.replace("(,", "(")

        if image_passed:
            viewer.image = func(image, *args, **kwargs)
        else:
            viewer.image = func(*args, **kwargs)
        if viewer.slice_slider is not None:
            viewer.slice_slider.max = viewer.image.shape[0] - 1
        viewer.configuration_updated(None)


    worker_function.__signature__ = inspect.Signature(exposable_parameters)
    ipywidgets.interact(worker_function)

    #inter = ipywidgets.interactive(worker_function, dict(manual=False, auto_display=False))
    #inter.update()

    if viewer.slice_slider is not None:
        return ipywidgets.VBox([
            _no_resize(viewer.view),
            #ipywidgets.VBox(inter.result),
            viewer.slice_slider,
            command_label
        ])
    else:
        return ipywidgets.VBox([
            _no_resize(viewer.view),
            #ipywidgets.VBox(inter.result),
            command_label
        ])

def guess_range(name, annotation):
    if name == 'footprint' or name == 'selem' or name == 'structuring_element':
        return 0, 100, 1
    if 'sigma' in name:
        return 0, 10, 1
    if 'radius' in name:
        return 0, 100, 1
    if 'factor' in name:
        return 0, 100, 1
    if name == 'angle' or "degrees" in name:
        return 0, 360, 15
    return None, None, None
