def clusterplot(df, labels, column_x:str="x", column_y:str="y", column_selection:str="selection", image=None,
                     zoom_factor:float=1, zoom_spline_order:int=0, figsize=(5, 5)):
    """
    Visualizes a scatter plot of columns in a given dataframe next to a segmented image.

    Inspired by the napari clusters plotter:
    https://github.com/BiAPoL/napari-clusters-plotter

    Parameters
    ----------
    df: pandas.DataFrame
        The dataframe to plot
    labels: np.ndarray
        The labels to overlay
    column_x: str
        The column to use for the x-axis
    column_y: str
        The column to use for the y-axis
    column_selection: str
        The column to use for the selection
    image: np.ndarray, optional
        The image to overlay
    zoom_factor: float, optional
        Allows showing the image larger (> 1) or smaller (<1)
    zoom_spline_order: int, optional
        Spline order used for interpolation (default=0, nearest-neighbor)
    figsize: tuple
        The size of the scatter plot figure

    Returns
    -------
    An ipywidgets widget
    """
    import numpy as np
    from ._grid import grid
    from ._curtain import curtain
    from ._slice import slice
    from ._scatterplot import scatterplot
    import functools

    if column_selection in df.columns:
        selection = df["selection"].tolist()

        selected_image = np.take(np.asarray([-1] + list(selection)) * 1 + 1, labels).astype(np.uint32)
    else:
        selected_image = ((labels > 0) * 1).astype(np.uint32)

    if image is None:
        image_display = slice(labels)
    else:
        image_display = curtain(image, selected_image, zoom_factor=zoom_factor, zoom_spline_order=zoom_spline_order)

    def update(selection, label_image, selected_image, widget):

        temp = np.take(np.asarray([-1] + list(selection)) * 1 + 1, label_image)

        # overwrite the pixels in the given image
        np.copyto(selected_image, temp.astype(selected_image.dtype))

        # redraw the visualization
        widget.update()

    update_selection = functools.partial(update, label_image=labels, selected_image=selected_image,
                                         widget=image_display)

    scatterplot = scatterplot(df, column_x, column_y, column_selection, figsize=figsize,
                                        selection_changed_callback=update_selection)

    return grid([[
        image_display,
        scatterplot
    ]])

