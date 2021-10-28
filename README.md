# stackview
Interactive image stack viewing in jupyter notebooks based on a fork of 
[numpy_image_widget](https://github.com/Who8MyLunch/Numpy_Image_Widget) and 
[ipywidgets](https://ipywidgets.readthedocs.io/en/latest/).

![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/banner.gif)

## Installation

```shell
pip install stackview
```

## Usage
You can use `stackview` from within jupyter notebooks as shown below.
Also check out the [demo notebook on google colab](https://colab.research.google.com/github/haesleinhuepf/stackview/blob/master/docs/demo.ipynb) or in
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/haesleinhuepf/stackview/HEAD?filepath=docs%2Fdemo.ipynb)

Starting point is a 3D image dataset provided as numpy array. 
```python
from skimage.io import imread
image = imread('data/Haase_MRT_tfl3d1.tif', plugin='tifffile')
```

You can then view it slice-by-slice:
```python
import stackview
stackview.slice(image, continuous_update=True)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_slice.gif)

To read the intensity of pixels where the mouse is moving, use the picker.
```python
stackview.picker(image, continuous_update=True)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_picker.gif)

Orthogonal views are also available:
```python
stackview.orthogonal(image, continuous_update=True)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_orthogonal.gif)

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

A side-by-side view for colocalization visualization is also available.
If you're working with time-lapse data, you can also use this view for visualizing differences between timepoints:
```python
stackview.side_by_side(image_stack[1:], image_stack[:-1], continuous_update=True, display_width=300)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_side_by_side.gif)

Exploration of the parameter space of image processing functions is available using `interact`:
```python
from skimage.filters.rank import maximum
stackview.interact(maximum, slice_image)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_interact1.gif)

This might be useful for custom functions implementing image processing workflows:
```python
from skimage.filters import gaussian, threshold_otsu, sobel
def my_custom_code(image, sigma:float = 1):
    blurred_image = gaussian(image, sigma=sigma)
    binary_image = blurred_image > threshold_otsu(blurred_image)
    edge_image = sobel(binary_image)
    
    return edge_image * 255 + image 

stackview.interact(my_custom_code, slice_image)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_interact2.gif)

## Contributing

Contributions, bug-reports and ideas for further development are very welcome.

## License

Distributed under the terms of the [BSD-3] license,
"stackview" is free and open source software

## Issues

If you encounter any problems, please create a thread on [image.sc] along with a detailed description and tag [@haesleinhuepf].

## See also
There are other libraries doing similar stuff
* [napari](https://github.com/napari/napari)
* [JNI's Volume Viewer based on Matplotlib](https://github.com/jni/mpl-volume-viewer)
* [Holoviz hvPlot](https://hvplot.holoviz.org/user_guide/Gridded_Data.html#n-d-plots)
* [magicgui](https://github.com/napari/magicgui)
* [ipywidgets interact](https://ipywidgets.readthedocs.io/en/latest/examples/Using%20Interact.html)

[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[image.sc]: https://image.sc
[@haesleinhuepf]: https://twitter.com/haesleinhuepf

