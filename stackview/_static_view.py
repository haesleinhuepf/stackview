import numpy as np
from typing import Callable
from functools import wraps
from toolz import curry

def insight(image, library_name=None, help_url=None):
    """
    Converts a numpy-array-like image to numpy-compatible array with a convenient display in Jupyter notebooks
    including shape, min/max intensity, histogram and viewing 32-bit and 64-bit integer images as coloured labels.
    """
    return StackViewNDArray(image, library_name, help_url)

@curry
def jupyter_displayable_output(
        function: Callable,
        library_name:str = None,
        help_url:str = None
) -> Callable:
    """Wraps a given function so that it outputs a nice image view in jupyter notebooks
    The view will contain a link to the specified library to guide users to read more.
    """
    @wraps(function)
    def worker_function(*args, **kwargs):
        # call the decorated function
        result = function(*args, **kwargs)

        # Attach _repr_html_ function
        result = StackViewNDArray(result, library_name, help_url)

        return result

    return worker_function


class StackViewNDArray(np.ndarray):

    def __new__(cls, input_array, library_name=None, help_url=None):
        if 'cupy.ndarray' in str(type(input_array)):
            input_array = input_array.get()
        obj = np.asarray(input_array).view(cls)
        obj.library_name = library_name
        obj.help_url = help_url
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.library_name = getattr(obj, 'library_name', None)
        self.help_url = getattr(obj, 'help_url', None)
        self.obj = obj

    def __getattr__(self, name):
        if name == "_repr_html_":
            return self._repr_html_
        return getattr(self.obj, name)

    def _repr_html_(self):
        """HTML representation of the image object for IPython.
                Returns
                -------
                HTML text with the image and some properties.
                """
        if len(self.obj.shape) < 2:
            return str(self.obj)

        import numpy as np
        size_in_pixels = np.prod(self.obj.shape)
        size_in_bytes = size_in_pixels * self.obj.dtype.itemsize

        from ._image_widget import _is_label_image
        labels = _is_label_image(self.obj)

        import matplotlib.pyplot as plt
        from ._imshow import imshow
        imshow(self.obj,
                labels=labels,
                continue_drawing=True,
                colorbar=not labels)
        image = _png_to_html(_plt_to_png())

        if size_in_bytes > 1024:
            size_in_bytes = size_in_bytes / 1024
            if size_in_bytes > 1024:
                size_in_bytes = size_in_bytes / 1024
                if size_in_bytes > 1024:
                    size_in_bytes = size_in_bytes / 1024
                    size = "{:.1f}".format(size_in_bytes) + " GB"
                else:
                    size = "{:.1f}".format(size_in_bytes) + " MB"
            else:
                size = "{:.1f}".format(size_in_bytes) + " kB"
        else:
            size = "{:.1f}".format(size_in_bytes) + " B"

        histogram = ""

        if size_in_bytes < 100 * 1024 * 1024:
            if not labels:
                import numpy as np

                num_bins = 32
                h, _ = np.histogram(self.obj, bins=num_bins)

                plt.figure(figsize=(1.8, 1.2))
                plt.bar(range(0, len(h)), h)

                # hide axis text
                # https://stackoverflow.com/questions/2176424/hiding-axis-text-in-matplotlib-plots
                # https://pythonguides.com/matplotlib-remove-tick-labels
                frame1 = plt.gca()
                frame1.axes.xaxis.set_ticklabels([])
                frame1.axes.yaxis.set_ticklabels([])
                plt.tick_params(left=False, bottom=False)

                histogram = _png_to_html(_plt_to_png())

            min_max = "<tr><td>min</td><td>" + str(self.obj.min()) + "</td></tr>" + \
                      "<tr><td>max</td><td>" + str(self.obj.max()) + "</td></tr>"

        else:

            min_max = ""

        help_text = ""
        if self.library_name is not None and len(self.library_name) > 0:
            self.library_name = self.library_name + " made "
            if self.help_url is not None:
                help_text = "<b><a href=\"" + self.help_url + "\" target=\"_blank\">" + self.library_name + "</a>image</b><br/>"

        all = [
            "<table>",
            "<tr>",
            "<td>",
            image,
            "</td>",
            "<td style=\"text-align: center; vertical-align: top;\">",
            help_text,
            "<table>",
            "<tr><td>shape</td><td>" + str(self.shape).replace(" ", "&nbsp;") + "</td></tr>",
            "<tr><td>dtype</td><td>" + str(self.dtype) + "</td></tr>",
            "<tr><td>size</td><td>" + size + "</td></tr>",
            min_max,
            "</table>",
            histogram,
            "</td>",
            "</tr>",
            "</table>",
        ]

        return "\n".join(all)


def _png_to_html(png):
    import base64
    url = 'data:image/png;base64,' + base64.b64encode(png).decode('utf-8')
    return f'<img src="{url}"></img>'


# adapted from https://github.com/napari/napari/blob/d6bc683b019c4a3a3c6e936526e29bbd59cca2f4/napari/utils/notebook_display.py#L54-L73
def _plt_to_png():
    """PNG representation of the image object for IPython.
    Returns
    -------
    In memory binary stream containing a PNG matplotlib image.
    """
    import matplotlib.pyplot as plt
    from io import BytesIO

    with BytesIO() as file_obj:
        plt.savefig(file_obj, format='png')
        plt.close() # supress plot output
        file_obj.seek(0)
        png = file_obj.read()
    return png


def _imshow(image, title: str = None, labels: bool = False, min_display_intensity: float = None,
            max_display_intensity: float = None, plot=None, colorbar: bool = False, colormap=None,
            alpha: float = None, continue_drawing: bool = False):
    """Visualize an image, e.g. in Jupyter notebooks.

    Parameters
    ----------
    image: np.ndarray
        numpy or OpenCL-backed image to visualize
    title: str
        Obsolete (kept for ImageJ-compatibility)
    labels: bool
        True: integer labels will be visualized with colors
        False: Specified or default colormap will be used to display intensities.
    min_display_intensity: float
        lower limit for display range
    max_display_intensity: float
        upper limit for display range
    color_map: str
        deprecated, use colormap instead
    plot: matplotlib axis
        Plot object where the image should be shown. Useful for putting multiple images in subfigures.
    colorbar: bool
        True puts a colorbar next to the image. Will not work with label images and when visualizing multiple
        images (continue_drawing=True).
    colormap: str or matplotlib colormap
    alpha: float
        alpha blending value
    continue_drawing: float
        True: the next shown image can be visualized on top of the current one, e.g. with alpha = 0.5
    """
    import numpy as np

    if len(image.shape) == 3 and image.shape[2] == 3: # RGB image
        import matplotlib.pyplot as plt
        plt.imshow(image, vmin=min_display_intensity, vmax=max_display_intensity,
                   interpolation='nearest', alpha=alpha)
        if not continue_drawing:
            plt.show()
        return

    if len(image.shape) == 3:
        image = np.asarray(image).max(axis=0)

    image = np.asarray(image)
    if len(image.shape) == 1:
        image = image[np.newaxis]

    if colormap is None:
        colormap = "Greys_r"

    cmap = colormap
    if labels:
        import matplotlib
        import numpy as np

        if not hasattr(_imshow, "labels_cmap"):
            from ._image_widget import _labels_lut
            _imshow.labels_cmap = matplotlib.colors.ListedColormap(_labels_lut())
        cmap = _imshow.labels_cmap

        if min_display_intensity is None:
            min_display_intensity = 0
        if max_display_intensity is None:
            max_display_intensity = 65536

    if plot is None:
        import matplotlib.pyplot as plt
        plt.clf()
        plt.imshow(image, cmap=cmap, vmin=min_display_intensity, vmax=max_display_intensity,
                   interpolation='nearest', alpha=alpha)
        if colorbar:
            plt.colorbar()
        if not continue_drawing:
            plt.show()
    else:
        plot.imshow(image, cmap=cmap, vmin=min_display_intensity, vmax=max_display_intensity,
                    interpolation='nearest', alpha=alpha)
        if colorbar:
            plot.colorbar()