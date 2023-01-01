def assist(what: str,
           context:dict,
           continuous_update: bool = False,
           zoom_factor: float = 1.0,
           zoom_spline_order: int = 0,
           ):
    """
    Searches provided context (e.g. globals()) for functions that have images as parameters and provide
    a pulldown of these functions. Once the user selected a function from this pulldown, a user-interface
    is created for the function's parameters.

    Note
    ----
    There is currently a technical limitation to about 250 list entries. This is due to a maximum number of GUI
    elements. Thus, the search term `what` should be as specific as possible to limit the number of results.
    If you receive a JavaScript error or the progress bar gets stuck, try to be more specific.

    See Also
    --------
    stackview.interact()

    Parameters
    ----------
    what : str
        The task to be assisted, e.g. "denoise", "filter", "morphology", "transform", "segment", "map", "mesh"
    context : dict
        A dictionary of (name:image/function/module), allows showing pulldowns of available functions and images, e.g.: globals()
    continuous_update : bool, optional
        Update the image while dragging the mouse, default: False
    zoom_factor: float, optional
        Allows showing the image larger (> 1) or smaller (<1)
    zoom_spline_order: int, optional
        Spline order used for interpolation (default=0, nearest-neighbor)
    """
    import ipywidgets
    from ._context import Context
    from ._utilities import _no_resize
    from ._slice_viewer import _SliceViewer
    from ._utilities import logo
    from ._interact import interact

    # search is case-insensitive
    what = what.lower()

    if not isinstance(context, Context):
        context = Context(context)

    # progress bar
    progress_bar = ipywidgets.IntProgress(
        value=0,
        min=0,
        max=len(context._functions.keys()),
        step=1,
        description='Loading:',
        bar_style='',  # 'success', 'info', 'warning', 'danger' or ''
        orientation='horizontal'
    )
    from IPython.display import display
    #display(progress_bar)

    # GUI: The image viewer for all function widgets is this one:
    viewer = _SliceViewer(logo, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order, continuous_update=continuous_update)

    # search compatible functions and make widgets for them
    available_widgets = {}
    search_index = {}
    count = 0
    for index, (name, func) in enumerate(context._functions.items()):
        progress_bar.value = index
        if hasattr(func, "categories"):
            if func.categories is None or "in assistant" not in func.categories:
                continue
        #print(name)
        try:
            #print("testing " + name)
            widget = interact((func, name), context=context, viewer=viewer, continuous_update=continuous_update, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)
            #print("yes")
            search_text = (func.__name__ + str(func.__doc__)).lower()
        except:
            #print("no")
            del widget
            continue
        if search_string(what, search_text):
            count = count + 1
            search_index[search_text] = name
            available_widgets[name] = widget
            progress_bar.description = f"Loaded {name} ({count})"
            import inspect
            sig = inspect.signature(func)
            print("\n", name, sig)
        else:
            #print("no2")
            del widget

    # GUI: documentation output
    documentation_output = ipywidgets.HTML("")
    documentation_output.style.font_family = "Courier"

    # GUI: select operation
    operation_pulldown = ipywidgets.Dropdown(
        options=list(available_widgets.keys()),
        description="Operation"
    )
    def hide_all():
        """Hide all widgets"""
        for name, wi in available_widgets.items():
            wi.layout.display = 'none'
    def on_change(event):
        """Show the selected function widget"""
        if event['type'] == 'change' and event['name'] == 'value':
            func_name = event['new']
            hide_all()
            wi = available_widgets[func_name]
            wi.layout.display = 'block'
            documentation_output.value = text2html(context._functions[func_name].__doc__)
    operation_pulldown.observe(on_change)

    # GUI: Search field
    search_field = ipywidgets.Text(
        value='',
        placeholder='Type here to search',
        description='Search'
    )
    def search(event=None):
        """Update the operation pulldown based on search text"""
        search_text = str(search_field.value).lower()
        if len(search_text) < 1:
            operation_pulldown.options = list(available_widgets.keys())
        result = []
        for docstring, func_name in search_index.items():
            if search_string(search_text, docstring):
                result.append(func_name)
        operation_pulldown.options = result
    search_field.observe(search)

    # combine all widgets
    widgets_to_show = [search_field, operation_pulldown]
    for name, w in available_widgets.items():
        widgets_to_show.append(w)
    widgets_to_show.append(_no_resize(viewer.view))
    widgets_to_show.append(viewer.slice_slider)
    widgets_to_show.append(documentation_output)

    hide_all()

    progress_bar.layout.display = 'none'

    print("done", count)

    return ipywidgets.VBox(widgets_to_show)
    #display(ipywidgets.VBox(widgets_to_show))


def text2html(text):
    html = "<pre>" + str(text) + "</pre>"
    return html

def search_string(what, where):
    return what in where

