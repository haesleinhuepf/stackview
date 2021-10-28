# This file is an adapted version from P.V. Villeneuve originating from
# https://github.com/Who8MyLunch/Image_Attendant/tree/master/image_attendant

# MIT License
#
# Copyright (c) 2017 Pierre V. Villeneuve
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

from __future__ import division, print_function, unicode_literals, absolute_import

import io

import numpy as np
import PIL.Image

from ._utility import *

def compress(data, fmt, **kwargs):
    """Compress image, return bytes buffer.

    fmt: 'png', 'jpeg', etc.

    Alpha channel will be collapsed if fmt == 'jpeg'.

    Returns a byte buffer of compressed data.

    Parameter options: http://pillow.readthedocs.org/handbook/image-file-formats.html
    """
    # Enforce 8-byte data
    data = setup_uint8(data)

    fmt = fmt.lower()
    if fmt == 'jpg':
        fmt = 'jpeg'

    if fmt == 'jpeg':
        if data.ndim == 3:
            if data.shape[2] == 4:
                data = collapse_alpha(data)

    buff = io.BytesIO()
    image_io_write(buff, data, fmt, **kwargs)

    data_comp = buff.getvalue()

    return data_comp



def decompress(data_comp):
    """Decompress image from supplied buffer byte data.
    """
    buff = io.BytesIO(data_comp)
    img = PIL.Image.open(buff)

    data = np.asarray(img)

    return data


def image_io_write(fp, data, fmt=None, **kwargs):
    """Write image data from Numpy array to file-like object.
    File format is automatically determined from fp if it's a filename, otherwise you
    must specify format via fmt keyword, e.g. fmt = 'png'.
    Parameter options: http://pillow.readthedocs.io/en/4.2.x/handbook/image-file-formats.html
    """
    img = PIL.Image.fromarray(data)
    img.save(fp, format=fmt, **kwargs)

