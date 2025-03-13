# stackview 🧊👀
[![PyPI](https://img.shields.io/pypi/v/stackview.svg?color=green)](https://pypi.org/project/stackview)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/stackview/badges/version.svg)](https://anaconda.org/conda-forge/stackview)
[![Contributors](https://img.shields.io/github/contributors-anon/haesleinhuepf/stackview)](https://github.com/haesleinhuepf/stackview/graphs/contributors)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/stackview)](https://pypistats.org/packages/stackview)
[![GitHub stars](https://img.shields.io/github/stars/haesleinhuepf/stackview?style=social)](https://github.com/haesleinhuepf/stackview/)
[![GitHub forks](https://img.shields.io/github/forks/haesleinhuepf/stackview?style=social)](https://github.com/haesleinhuepf/stackview/)
[![License](https://img.shields.io/pypi/l/stackview.svg?color=green)](https://github.com/haesleinhuepf/stackview/raw/main/LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14281364.svg)](https://doi.org/10.5281/zenodo.14281364)


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

There is also a notebook demonstrating [how to use stackview in Google Colab](https://colab.research.google.com/github/haesleinhuepf/stackview/blob/master/docs/colab_clesperanto_demo.ipynb).

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

### Pick intensities

To read the intensity of pixels where the mouse is moving, use the picker.
```python
stackview.picker(image)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_picker.gif)

### Display range

To adjust the minimum and maximum intensity shown when displaying an image, use the `display_range` function.
```python
stackview.display_range(image)
```

![img.png](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_display_range.gif)



### Static insight views

The `insight` function turns a numpy-array into a numpy-compatible array that has an image-display in jupyter notebooks.

```python
stackview.insight(image[60])
```

![img.png](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/insight_demo.png)

Images of 32-bit and 64-bit type integer are displayed as labels. 

```python
blobs = imread('data/blobs.tif')
labels = label(blobs > 120)

stackview.insight(labels)
```

![img.png](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/labels_demo.png)

### matplotlib-like imshow

To visualize images with more flexibility, there is `imshow`, which works similar like matplotlib's imshow and yet adds more flexibily, e.g. when it comes to colormaps. It supports `pure...` colormaps introduced in [microfilm](https://github.com/guiwitz/microfilm).

```python
stackview.imshow(image, axes=True, colorbar=True, colormap='pure_magenta')
```

![img.png](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/imshow_pure_magenta.png)

... or drawing label images. 

```python
import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 3, figsize=(15,15))

stackview.imshow(image, plot=axs[0], title='image', axes=True)
stackview.imshow(labels, plot=axs[1], title='labels')

stackview.imshow(image, plot=axs[2], continue_drawing=True)
stackview.imshow(labels, plot=axs[2], alpha=0.4, title='image + labels')
```

![img.png](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/imshow.png)


### Static animations

The `animate` and `animate_curtain` functions can be used to store animations of image stacks / images blended over each other as gif to disk.

```python
stackview.animate(blobs_images, frame_delay_ms=50)
```

![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/timelapse2.gif)

```python
stackview.animate_curtain(blobs, blobs > 128)
```

![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/timelapse3.gif)

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



### Orthogonal view

Orthogonal views are also available:
```python
stackview.orthogonal(image)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_orthogonal.gif)

### Curtain

Furthermore, to visualize an original image in combination with a processed version, a curtain view may be helpful:
```python
stackview.curtain(image, modified_image * 65537)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_curtain.gif)

The curtain also works with 2D data. 
Btw. to visualize both images properly, you need adjust their grey value range yourself. 
For example, multiply a binary image with 255 so that it visualizes nicely side-by-side with the original image in 8-bit range:
```python
binary = (slice_image > threshold_otsu(slice_image)) * 255
stackview.curtain(slice_image, binary)
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_curtain2.gif)

The same also works with label images
```python
from skimage.measure import label
labels = label(binary)
stackview.curtain(slice_image, labels)
```

![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_curtain3.gif)

### Side-by-side view

A side-by-side view for colocalization visualization is also available.
If you're working with time-lapse data, you can also use this view for visualizing differences between timepoints:
```python
stackview.side_by_side(image_stack[1:], image_stack[:-1])
```
![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_side_by_side.gif)

### Switch

The `switch` function allows to switch between a list or dictionary of images.

```
stackview.switch([
    slice_image,
    binary,
    labels
])
```

![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_switch.gif)

### Switch toggleable

You can also view multiple channels with different colormaps at the same time using the `toggleable` parameter of `switch`. 
It is recommended to also pass a list of colormaps. Colormap names can be taken from [Matplotlib](https://matplotlib.org/stable/tutorials/colors/colormaps.html) and stackview aims at compatibility with [microfilm](https://github.com/guiwitz/microfilm).

```
hela_cells = imread("data/hela-cells.tif")

stackview.switch(
    {"lysosomes":   hela_cells[:,:,0],
     "mitochondria":hela_cells[:,:,1],
     "nuclei":      hela_cells[:,:,2]
    },
    colormap=["pure_magenta", "pure_green", "pure_blue"],
    toggleable=True
)
```

![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/demo_switch_toggleable.gif)

### nD-Viewer

You can also use all functions above with n-dimensional data (since stackview 0.10.0). You will then see multiple sliders for navigating through dimensions such as space and time.
In case you work with multiple channels, using `stackview.switch()` with `toggleable=True` is recommended ([Read more](https://github.com/haesleinhuepf/stackview/blob/main/docs/nd-data.ipynb)).

![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/nd-data.gif)


### Crop

You can crop images interactively:
```python
crop_widget = stackview.crop(image_stack)
crop_widget
```

![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/crop.gif)

... and retrieve the crop range as a tuple of `slice` objects:
```python
r = crop_widget.range
r
```
Output:
```
(slice(0, 40, 1), slice(40, 80, 1), slice(80, 120, 1))
```
... or you can crop the image directly:
```python
cropped_image = crop_widget.crop()
cropped_image.shape
```
Output:
```
(40, 40, 40)
```

### Bounding boxes

You can draw bounding boxes into images using the `add_bounding_boxes` function. 
The bounding boxes are defined as a list of dictionaries, each with 'x', 'y', 'width', 'height' keys, optional also 'color' and 'description'.
If you work with nD data, you can also pass a list of bounding boxes for each slice. [Read more](https://github.com/haesleinhuepf/stackview/blob/main/docs/add_bounding_boxes.ipynb)).

```
cat = imread("data/real_cat.png")
bb = {'x': 110, 'y': 30, 'width': 290, 'height': 350, 'color': 'lightgreen', 'description':'cat', 'font_size':50}

stackview.add_bounding_boxes(cat, [bb])
```

![img.png](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/bounding_boxes.png)

### scatterplot and clusterplot

Using `stackview.scatterplot()` you can create interactive plots for pandas DataFrames ([full example](https://github.com/haesleinhuepf/stackview/blob/main/docs/scatterplot.ipynb)).

```python
stackview.scatterplot(df, 'area', 'feret_diameter_max', "selection", figsize=(5,4))
```

If you want to visualize such a DataFrame side-by-side with the label image its measurements belong to, you can use the 
`clusterplot`:

```python
stackview.clusterplot(image=image,
                     labels=labeled_image,
                     df=df,
                     column_x="area",
                     column_y="aspect_ratio", 
                     zoom_factor=1.6,
                     alpha=0.7)
``` 

This functionality is inspired from the [napari-clusters-plotter](https://github.com/BiAPoL/napari-clusters-plotter).

![clusterplot.gif](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/clusterplot.gif)

### Sliceplot

Another similar interactive plot is the `sliceplot`: In case you have a pandas DataFrame with a columns representing measurements of slices in an image stack, you can use this function to visualize the slices in a plot. 

```python
stackview.sliceplot(df, images, column_x="UMAP0", column_y="UMAP1")
```

![](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/sliceplot.gif)


### Wordcloudplot

If you have a pandas DataFrame with a column containing text and additionally numeric columns related to the text, you can use the `wordcloudplot` function to visualize selected texts in a wordcloud.

![img.png](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/wordcloudplot.png)

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

stackview.interact(gaussian, context=globals())
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

## Voila

If you combine stackview with [voila](https://voila.readthedocs.io/en/stable/), you can build powerful, interactive, browser-based image processing apps and demonstrators. Just build a graphical user interface in a Jupyter notebook and then start it using

![img.png](https://raw.githubusercontent.com/haesleinhuepf/stackview/main/docs/images/voila.png)

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
* [ipyvolume](https://github.com/widgetti/ipyvolume/)

[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[image.sc]: https://image.sc
[@haesleinhuepf]: https://twitter.com/haesleinhuepf

