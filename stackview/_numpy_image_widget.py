# This file is an adapted version from P.V. Villeneuve originating from
# https://github.com/Who8MyLunch/Numpy_Image_Widget/blob/master/numpy_image_widget/numpy_image_widget.py

# MIT License
#
# Copyright (c) 2018 Pierre V. Villeneuve
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import traitlets
import IPython
import numpy as np
import ipywidgets
import ipyevents

from ._utility import get_image_size
from ._image_attendant import compress, decompress


class NumpyImage(ipywidgets.Image):
    """Easy-to-use image widget with numpy data array access.
    """
    def __init__(self, data=None, value=b'', format='jpeg',
                 compound=False,
                 splash=True, splash_aspect_ratio=2,
                 quality=85, width_max=1000, auto_size=False):
        """Create new image widget instance

        Provide one of the following as input:
        data  - numpy array of image data.
        value - bytes representing compressed image (e.g. png, jpeg).  Must also provide format.
        url   - link to remote image.
        """
        super().__init__()
        self.quality = quality

        self.compound = compound
        self._wid_label = None

        self._data = None
        self._width_data = None
        self._height_data = None
        self._width_display = None
        self._height_display = None
        self.width_max = width_max
        self.auto_size = auto_size

        if value:
            self.value = value

        self.format = format

        if data is None and splash:
            data = np.zeros(shape=(int(self.width_max/splash_aspect_ratio), self.width_max), dtype=np.uint8) + 220

        self.data = data

    @property
    def data(self):
        """Image data as numpy array
        """
        if self._data is None:
            # Extract numpy array from compressed byte string
            self._data = decompress(self.value)

        return self._data

    @data.setter
    def data(self, new_data):
        """Take in new image data, compress to PNG, send to image widget.
        """
        if new_data is None:
            return

        self._data = new_data
        self.value = compress(self._data, self.format, quality=self.quality)

    @property
    def shape(self):
        return self._height_data, self._width_data

    @traitlets.observe('value')
    def _value_changed(self, change):
        """Event handler for changes in `value` property
        """
        self._data = None
        fmt, W, H = get_image_size(self.value)
        self.format = fmt
        self._width_data, self._height_data = W, H

        if self.auto_size:
            self._set_width_height_display(W, H)

    @property
    def width_data(self):
        """Data width (read only)
        """
        return self._width_data

    @property
    def height_data(self):
        """Data height (read only)
        """
        return self._height_data

    @property
    def width_display(self):
        """Image display width
        """
        return self._width_display

    @width_display.setter
    def width_display(self, W):
        self._set_width_height_display(W=W)

    @property
    def height_display(self):
        """Image display height
        """
        return self._height_display

    @height_display.setter
    def height_display(self, H):
        self._set_width_height_display(H=H)

    def resize(self, W=None, H=None):
        """Coneinience function for adjusting image display size.

        Call with no arguments to reset image to default size.
        """
        self._set_width_height_display(W=W, H=H)

    def _set_width_height_display(self, W=None, H=None):
        if not W and not H:
            W = self.width_data
            H = self.height_data
        elif not H:
            H = W/self.width_data*self.height_data
        elif not W:
            W = H/self.height_data*self.width_data
        else:
            # Both H and W are defined, nothing to do up here.
            pass

        self._width_display = int(W)
        self._height_display = int(H)

        if self._width_display > self.width_max:
            self._width_display = self.width_max
            self._height_display = int(self._width_display/self.width_data*self.height_data)

        self.width = '{:d}pt'.format(self._width_display)
        self.height = '{:d}pt'.format(self._height_display)

    def _ipython_display_(self):
        super()._ipython_display_()

        if self.compound:

            self._wid_lab._ipython_display_()


def number_of_digits(x):
    """Return number of digits to the left of the decimal point
    """
    return int(np.floor(np.log10(x))) + 1