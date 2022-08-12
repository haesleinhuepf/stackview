from ipycanvas import Canvas
import numpy as np
from functools import lru_cache

class ImageWidget(Canvas):
    def __init__(self, image):
        if len(image.shape) != 2:
            raise NotImplementedError("Only 2D images are supported")

        width = image.shape[1]
        height = image.shape[0]
        super().__init__(width=width, height=height)
        self.fill_style = "red"
        self.stroke_style = "blue"
        self.stroke_rect(0, 0, width=width, height=height)
        self.data = np.asarray(image)
        self.layout.stretch = False


    @property
    def data(self):
        """Image data as numpy array
        """
        return self._data.swapaxes(0, 1)

    @data.setter
    def data(self, new_data):
        """Take in new image data, compress to PNG, send to image widget.
        """
        if new_data is None:
            return

        self._data = np.asarray(new_data).swapaxes(0, 1)
        self._update_image()

    def _update_image(self):
        self.put_image_data(_img_to_rgb(self._data), 0, 0)


def _img_to_rgb(image,
                display_min=None,
                display_max=None):

    if len(image.shape) == 3 and image.shape[2] == 3:
        return image

    if image.dtype == np.uint32:
        lut = _labels_lut()
        return np.asarray([lut[:, c].take(image) for c in range(0, 3)]).swapaxes(0, 2) * 255

    if display_min is None:
        display_min = image.min()
    if display_max is None:
        display_max = image.max()

    img_range = (display_max - display_min)
    if img_range == 0:
        img_range = 1

    image = (image - display_min) / img_range * 255
    return np.asarray([image, image, image]).swapaxes(0, 2)

@lru_cache(maxsize=1)
def _labels_lut():
    from numpy.random import MT19937
    from numpy.random import RandomState, SeedSequence
    rs = RandomState(MT19937(SeedSequence(3)))
    lut = rs.rand(65537, 3)
    lut[0, :] = 0
    return lut