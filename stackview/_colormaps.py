# the code in this file is modified from
# https://github.com/guiwitz/microfilm/blob/c0666e19b77db66b0af3a4d3759baaf19243b9db/microfilm/colorify.py#L11

# BSD 3-Clause License
#
# Copyright (c) 2021, Bern University, Mathematical Institute and Microscopy
# Imaging Center, Guillaume Witz
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from functools import lru_cache

@lru_cache(maxsize=16)
def create_colormap(cmap_name, num_colors=256):
    """
    Return a colormap defined by its name

    Parameters
    ----------
    cmap_name: str
        {'pure_red', 'pure_green', 'pure_blue', 'pure_magenta',
        'pure_cyan', 'pure_yellow'} or Matplotlib colormap
        Colors will be reversed if the name ends with '_r'
    num_colors: int
        number of steps in color scale
    Returns
    -------
    cmap: Matplotlib colormap
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.colors import ListedColormap

    if cmap_name in plt.colormaps():
        flip_map = False
        cmap = _convert_to_listed_colormap(plt.get_cmap(cmap_name, num_colors), num_colors)
    else:
        flip_map = cmap_name.endswith("_r")
        if flip_map:
            cmap_name = cmap_name[:-2]

        if cmap_name == 'pure_red':
            cmap = ListedColormap(np.c_[np.linspace(0, 1, num_colors), np.zeros(num_colors), np.zeros(num_colors)])
        elif cmap_name == 'pure_green':
            cmap = ListedColormap(np.c_[np.zeros(num_colors), np.linspace(0, 1, num_colors), np.zeros(num_colors)])
        elif cmap_name == 'pure_blue':
            cmap = ListedColormap(np.c_[np.zeros(num_colors), np.zeros(num_colors), np.linspace(0, 1, num_colors)])
        elif cmap_name == 'pure_cyan':
            cmap = ListedColormap(np.c_[np.zeros(num_colors), np.linspace(0, 1, num_colors), np.linspace(0, 1, num_colors)])
        elif cmap_name == 'pure_magenta':
            cmap = ListedColormap(np.c_[np.linspace(0, 1, num_colors), np.zeros(num_colors), np.linspace(0, 1, num_colors)])
        elif cmap_name == 'pure_yellow':
            cmap = ListedColormap(np.c_[np.linspace(0, 1, num_colors), np.linspace(0, 1, num_colors), np.zeros(num_colors)])
        elif cmap_name == 'segmentation':
            cmap = ListedColormap(_labels_lut())
        elif cmap_name == 'ran_gradient':
            cmap = random_grandient_cmap(num_colors=num_colors)
        else:
            raise Exception(f"Your colormap {cmap_name} doesn't exist either in Matplotlib or microfilm.")

    if flip_map:
        cmap = cmap.reversed()

    return cmap


def random_grandient_cmap(num_colors=25, seed=42):
    """Create a colormap as the gradient of a given random color"""
    from skimage.color import hsv2rgb
    import numpy as np
    from matplotlib.colors import ListedColormap

    rgb = hsv2rgb([np.random.random(1)[0], 0.95, 0.95])

    cmap = ListedColormap(np.c_[
        np.linspace(0,rgb[0],num_colors),
        np.linspace(0,rgb[1],num_colors),
        np.linspace(0,rgb[2],num_colors)
        ])
    return cmap


@lru_cache(maxsize=1)
def _labels_lut():
    from numpy.random import MT19937
    from numpy.random import RandomState, SeedSequence
    rs = RandomState(MT19937(SeedSequence(3)))
    lut = rs.rand(65537, 3)
    lut[0, :] = 0
    # these are the first four colours from matplotlib's default
    lut[1] = [0.12156862745098039, 0.4666666666666667, 0.7058823529411765]
    lut[2] = [1.0, 0.4980392156862745, 0.054901960784313725]
    lut[3] = [0.17254901960784313, 0.6274509803921569, 0.17254901960784313]
    lut[4] = [0.8392156862745098, 0.15294117647058825, 0.1568627450980392]
    return lut


def _convert_to_listed_colormap(colormap, num_samples):
    import numpy as np
    from matplotlib.colors import ListedColormap
    samples = np.linspace(0, 1, num_samples)
    colors = colormap(samples)
    return ListedColormap(colors)
