from ipycanvas import Canvas
import numpy as np
from ._colormaps import _labels_lut # for internal backwards compatibility

class ImageWidget(Canvas):
    def __init__(self, image, zoom_factor:float=1.0, zoom_spline_order:int=0, colormap:str=None, display_min:float=None, display_max:float=None):
        if not ((len(image.shape) == 2) or (len(image.shape) in [3, 4] and image.shape[-1] == 3)):
            raise NotImplementedError("Only 2D images are supported" + str(image.shape))
        height = image.shape[0] * zoom_factor
        width = image.shape[1] * zoom_factor
        self.zoom_factor = zoom_factor
        self.zoom_spline_order = zoom_spline_order
        super().__init__(width=width * zoom_factor, height=height * zoom_factor)
        self.colormap = colormap
        self.display_min = display_min
        self.display_max = display_max
        self.data = np.asarray(image)
        self.layout.stretch = False

    @property
    def data(self):
        """Image data as numpy array
        """
        return self._data

    @data.setter
    def data(self, new_data):
        """Take in new image data, compress to PNG, send to image widget.
        """
        if new_data is None:
            return

        self._data = np.asarray(new_data)
        self._update_image()
        self.height = self._data.shape[0] * self.zoom_factor
        self.width = self._data.shape[1] * self.zoom_factor

    def _update_image(self):
        if self.zoom_factor == 1.0:
            self.put_image_data(_img_to_rgb(self._data, colormap=self.colormap, display_min=self.display_min, display_max=self.display_max), 0, 0)
        else:
            zoomed = self._zoom(self._data)
            self.put_image_data(_img_to_rgb(zoomed, colormap=self.colormap, display_min=self.display_min, display_max=self.display_max), 0, 0)

    def _zoom(self, data):
        if len(data.shape) > 2 and data.shape[-1] == 3:
            # handle RGB images
            return np.asarray([self._zoom(data[:,:,i]) for i in range(data.shape[2])]).swapaxes(0, 2).swapaxes(1, 0)

        from scipy.ndimage import affine_transform
        matrix = np.asarray([[1.0 / self.zoom_factor, 0, -0.5],
                             [0, 1.0 / self.zoom_factor, -0.5],
                             [0, 0, 1],
                             ])
        zoomed_shape = (np.asarray(data.shape) * self.zoom_factor).astype(int)
        zoomed = affine_transform(data,
                                  matrix,
                                  output_shape=zoomed_shape,
                                  order=self.zoom_spline_order,
                                  mode='nearest')
        return zoomed


def _is_label_image(image):
    return image.dtype == np.uint32 or image.dtype == np.uint64 or \
           image.dtype == np.int32 or image.dtype == np.int64


def _img_to_rgb(image,
                colormap=None,
                display_min=None,
                display_max=None):
    from ._colormaps import _labels_lut, create_colormap

    if len(image.shape) > 2 and (image.shape[-1] == 3 or image.shape[-1] == 4):
        return image

    if image.dtype == bool:
        image = image * 1

    if _is_label_image(image):
        lut = _labels_lut()
        return np.asarray([lut[:, c].take(image.astype(np.int64)) for c in range(0, 3)]).swapaxes(0, 2).swapaxes(1, 0) * 255

    if display_min is None:
        display_min = image.min()
    if display_max is None:
        display_max = image.max()

    diplay_range_width = (display_max - display_min)
    if diplay_range_width == 0:
        diplay_range_width = 1

    image = (image.astype(float) - display_min) / diplay_range_width * 255
    image = np.minimum(image, 255)
    image = np.maximum(image, 0)

    if colormap is None:
        return np.asarray([image, image, image]).swapaxes(0, 2).swapaxes(1, 0)
    else:
        lut = np.asarray(create_colormap(colormap).colors)
        return np.asarray([lut[:, c].take(image.astype(int)) for c in range(0, 3)]).swapaxes(0, 2).swapaxes(1, 0) * 255
