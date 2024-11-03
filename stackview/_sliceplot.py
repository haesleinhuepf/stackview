def sliceplot(df, images, column_x: str = "x", column_y: str = "y", column_selection: str = "selection",
              zoom_factor: float = 1.0, zoom_spline_order: int = 0,
              figsize=(4, 4), selection_changed_callback=None, markersize:int=4):
    """
    Visualizes a scatter plot of columns in a given dataframe next to a stack of images which correspond to the datapoints.

    Parameters
    ----------
    df: pandas.DataFrame
        The dataframe to plot
    images: np.ndarray
        The images where the slices correspond to rows in the dataframe
    column_x: str, optional
        The column to use for the x-axis
    column_y: str, optional
        The column to use for the y-axis
    column_selection: str, optional
        The column to use for the selection
    zoom_factor: float, optional
        Allows showing the image larger (> 1) or smaller (<1)
    zoom_spline_order: int, optional
        Spline order used for interpolation (default=0, nearest-neighbor)
    figsize: tuple, optional
        The size of the scatter plot figure
    selection_changed_callback: function
        The function to call when the selection changes
    markersize: int
        The size of the markers

    Returns
    -------
    An ipywidgets widget
    """
    import ipywidgets as widgets
    from ipywidgets import HBox
    from ._slice import slice
    from ._scatterplot import scatterplot

    widget1 = slice(images, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)

    def update_stack(e=None):
        widget1.viewer.set_image(images[df[column_selection]])
        widget1.update()
        if selection_changed_callback is not None:
            selection_changed_callback()

    widget2 = scatterplot(df, column_x=column_x, column_y=column_y, column_selection=column_selection, figsize=figsize, selection_changed_callback=update_stack, markersize=markersize)

    # Arrange the widgets side by side using HBox
    return HBox([widget1, widget2])
