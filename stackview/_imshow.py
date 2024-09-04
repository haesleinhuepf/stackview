import warnings


def imshow(image,
           title:str = None,
           labels: bool = None,
           min_display_intensity: float = None,
           max_display_intensity: float = None,
           plot=None,
           colorbar: bool = False,
           colormap=None,
           alpha: float = None,
           continue_drawing: bool = False,
           axes:bool = False,
           cmap:str = None,
           vmin:float = None,
           vmax:float = None):
    """Visualize an image, e.g. in Jupyter notebooks.

    Parameters
    ----------
    image: np.ndarray
        numpy or OpenCL-backed image to visualize
    title: str

    labels: bool
        None: auto-detect (default): if image of type uint16, 32 or 64: True, False otherwise
        True: integer labels will be visualized with colors
        False: Specified or default colormap will be used to display intensities.
    min_display_intensity: float
        lower limit for display range
    max_display_intensity: float
        upper limit for display range
    plot: matplotlib axis
        Plot object where the image should be shown. Useful for putting multiple images in subfigures.
    colorbar: bool
        True puts a colorbar next to the image. Will not work with label images and when visualizing multiple
        images (continue_drawing=True).
        Fqlse: no colorbar (default)
    colormap: str
        matplotlib colormap or microfilm names such as "pure_green", "pure_magenta",...
    alpha: float
        blending value (between 0 and 1)
    continue_drawing: bool, optional
        True: the next shown image can be visualized on top of the current one, e.g. with alpha = 0.5
        False: the image is shown instantly and the cache is emptied (default)
    axes: bool
        turn axes on/off (default: False)
    """
    import numpy as np
    from ._utilities import is_label_image
    from ._colormaps import _labels_lut, create_colormap

    if cmap is not None:
        warnings.warn("The parameter cmap is deprecated, use colormap instead.")
        colormap = cmap

    if vmin is not None:
        warnings.warn("The parameter min_display_intensity is deprecated, use min_display_intensity instead.")
        min_display_intensity = vmin

    if vmax is not None:
        warnings.warn("The parameter max_display_intensity is deprecated, use max_display_intensity instead.")
        max_display_intensity = vmax

    while len(image.shape) > 2 and image.shape[-1] not in [3, 4]: #[3,4]: RGB, RGBA
        image = image.max(axis=0)

    if 'cupy.ndarray' in str(type(image)):
        image = image.get()

    image = np.asarray(image)
    if len(image.shape) == 1:
        image = image[np.newaxis]

    if labels is None:
        labels = is_label_image(image)

    if colormap is None:
        colormap = "Greys_r"

    if colormap.startswith("pure_"):
        colormap = create_colormap(colormap)

    if labels:
        import matplotlib
        import numpy as np

        if not hasattr(imshow, "labels_cmap"):
            lut = _labels_lut()
            imshow.labels_cmap = matplotlib.colors.ListedColormap(lut)
        colormap = imshow.labels_cmap

        if min_display_intensity is None:
            min_display_intensity = 0
        if max_display_intensity is None:
            max_display_intensity = 65536

    if plot is None:
        import matplotlib.pyplot as plt
        plt.imshow(image, cmap=colormap, vmin=min_display_intensity, vmax=max_display_intensity, interpolation='nearest',
                   alpha=alpha)

        if axes is not None:
            plt.axis('on' if axes else 'off')

        if title is not None:
            plt.title(title)

        if colorbar:
            plt.colorbar()
        if not continue_drawing:
            plt.show()
    else:
        ims = plot.imshow(image, cmap=colormap, vmin=min_display_intensity, vmax=max_display_intensity,
                          interpolation='nearest', alpha=alpha)
        if colorbar:
            fig = plot.get_figure()
            cax = fig.add_axes([plot.get_position().x1 + 0.01, plot.get_position().y0, 0.005,
                                plot.get_position().height])
            fig.colorbar(ims, cax=cax)

        if title is not None:
            plot.set_title(title)

        if axes is not None:
            plot.axis('on' if axes else 'off')
