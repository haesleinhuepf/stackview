# stackview 🧊👀
Interactive image stack viewing in jupyter notebooks based on 
[ipycanvas](https://ipycanvas.readthedocs.io/) and 
[ipywidgets](https://ipywidgets.readthedocs.io/en/latest/). 
TL;DR:
```python
stackview.curtain(image, labels, continuous_update=True)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/banner2.gif)

## Installation

stackview can be installed using conda or pip.

```
conda install -c conda-forge stackview
```

OR

```
pip install stackview
```

If you run the installation from within a notebook, you need to restart Jupyter (not just the kernel), before you can use stackview.

## Usage
You can use `stackview` from within jupyter notebooks as shown below.
Also check out the demo in [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/haesleinhuepf/stackview/HEAD?filepath=docs%2Fdemo.ipynb)

There is also a notebook demonstrating [how to use stack in Google Colab](https://colab.research.google.com/github/haesleinhuepf/stackview/blob/master/docs/colab_clesperanto_demo.ipynb).

More example notebooks can be found in [this folder](https://github.com/haesleinhuepf/stackview/tree/main/docs).

Starting point is a 3D image dataset provided as numpy array. 
```python
from skimage.io import imread
image = imread('data/Haase_MRT_tfl3d1.tif', plugin='tifffile')
```

### Slice view

You can then view it slice-by-slice:
```python
import stackview
stackview.slice(image, continuous_update=True)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_slice.gif)

### Static insight views

The `insight` function turns a numpy-array into a numpy-compatible array that has an image-display in jupyter notebooks.

```python
insight(image[60])
```

![img.png](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/insight_demo.png)

Images of 32-bit and 64-bit type integer are displayed as labels. 

```python
blobs = imread('data/blobs.tif')
labels = label(blobs > 120)

insight(labels)
```

![img.png](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/labels_demo.png)

### Annotate regions

To create label images interactively, e.g. for machine learning training, the `stackview.annotate` function offers basic label drawing tools. 
Click and drag for drawing. Hold the `ALT` key for erasing.
Annotations are drawn into a `labels` image you need to create before drawing.

```python
import numpy as np
labels = np.zeros(image.shape).astype(np.uint32)

stackview.annotate(image, labels)
```

![img.png](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_annotate.gif)

Note: In case the interface is slow, consider using smaller images, e.g. by cropping or resampling.

### Pick intensities

To read the intensity of pixels where the mouse is moving, use the picker.
```python
stackview.picker(image, continuous_update=True)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_picker.gif)

### Orthogonal view

Orthogonal views are also available:
```python
stackview.orthogonal(image, continuous_update=True)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_orthogonal.gif)

### Curtain

Furthermore, to visualize an original image in combination with a processed version, a curtain view may be helpful:
```python
stackview.curtain(image, modified_image * 65537, continuous_update=True)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_curtain.gif)

The curtain also works with 2D data. 
Btw. to visualize both images properly, you need adjust their grey value range yourself. 
For example, multiply a binary image with 255 so that it visualizes nicely side-by-side with the original image in 8-bit range:
```python
binary = (slice_image > threshold_otsu(slice_image)) * 255
stackview.curtain(slice_image, binary, continuous_update=True)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_curtain2.gif)

The same also works with label images
```python
from skimage.measure import label
labels = label(binary)
stackview.curtain(slice_image, labels, continuous_update=True)
```

![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_curtain3.gif)

### Side-by-side view

A side-by-side view for colocalization visualization is also available.
If you're working with time-lapse data, you can also use this view for visualizing differences between timepoints:
```python
stackview.side_by_side(image_stack[1:], image_stack[:-1], continuous_update=True, display_width=300)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_side_by_side.gif)

### Interact

Exploration of the parameter space of image processing functions is available using `interact`:
```python
from skimage.filters.rank import maximum
stackview.interact(maximum, slice_image)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_interact1.gif)

This might be useful for custom functions implementing image processing workflows:
```python
from skimage.filters import gaussian, threshold_otsu, sobel
def my_custom_code(image, sigma:float = 1, show_labels: bool = True):
    sigma = abs(sigma)
    blurred_image = gaussian(image, sigma=sigma)
    binary_image = blurred_image > threshold_otsu(blurred_image)
    edge_image = sobel(binary_image)
    
    if show_labels:
        return label(binary_image)
    else:
        return edge_image * 255 + image 

stackview.interact(my_custom_code, slice_image)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_interact3.gif)

If you want to use a pulldown for selecting input image(s), you need to pass a dictionary of `(name, image)` pairs as `context`, e.g. `context=globals()`:

```python
image1 = imread("data/Haase_MRT_tfl3d1.tif")
image2 = image1[:,:,::-1]

stackview.interact(gaussian, context=globals(), continuous_update=True)
```

![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_interact4.gif)

To add an `insight`-view automatically to results of functions, you can add this.

```python
@jupyter_displayable_output
def my_gaussian(image, sigma):
    return gaussian(image, sigma)

my_gaussian(image[60], 2)
```

![img.png](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/jupyter_displayable_output.png)

## Contributing

Contributions, bug-reports and ideas for further development are very welcome.

## License

Distributed under the terms of the [BSD-3] license,
"stackview" is free and open source software

## Issues

If you encounter any problems, please create a thread on [image.sc] along with a detailed description and tag [@haesleinhuepf].

## See also
There are other libraries doing similar stuff
* [ipyannotations](https://github.com/janfreyberg/ipyannotations)
* [napari](https://github.com/napari/napari)
* [JNI's Volume Viewer based on Matplotlib](https://github.com/jni/mpl-volume-viewer)
* [Holoviz hvPlot](https://hvplot.holoviz.org/user_guide/Gridded_Data.html#n-d-plots)
* [magicgui](https://github.com/napari/magicgui)
* [ipywidgets interact](https://ipywidgets.readthedocs.io/en/latest/examples/Using%20Interact.html)

[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[image.sc]: https://image.sc
[@haesleinhuepf]: https://twitter.com/haesleinhuepf

