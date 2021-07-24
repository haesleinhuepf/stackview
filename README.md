# stackview
Interactive image stack viewing in jupyter notebooks based on 
[numpy_image_widget](https://github.com/Who8MyLunch/Numpy_Image_Widget) and 
[ipywidgets](https://ipywidgets.readthedocs.io/en/latest/).

## Installation

```shell
pip install stackview
```

## Usage
You can use `stackview` from within jupyter notebooks as shown below.
Also check out the [demo notebook on google colab](https://colab.research.google.com/github/haesleinhuepf/stackview/blob/master/docs/demo.ipynb)

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
![](docs/images/demo_slice.gif)

Orthogonal views are also available:
```python
stackview.orthogonal(image, continuous_update=True)
```
![](docs/images/demo_orthogonal.gif)

Furthermore, to visualize an original image in combination with a processed version, a curtain view may be helpful:
```python
stackview.curtain(image, modified_image * 65537, continuous_update=True)
```
![](docs/images/demo_curtain.gif)

The curtain also works with 2D data. 
Btw. to visualize both images properly, you need adjust their grey value range yourself. 
For example, multiply a binary image with 255 so that it visualizes nicely side-by-side with the original image in 8-bit range:
```python
slice_image = imread('https://github.com/haesleinhuepf/stackview/blob/main/docs/data/blobs.tif?raw=true', plugin='tifffile')
from skimage.filters import threshold_otsu
binary = (slice_image > threshold_otsu(slice_image)) * 255
stackview.curtain(slice_image, binary, continuous_update=True)
```
![](docs/images/demo_curtain2.gif)



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

[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[image.sc]: https://image.sc
[@haesleinhuepf]: https://twitter.com/haesleinhuepf

