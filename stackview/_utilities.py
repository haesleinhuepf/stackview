import numpy as np
def merge_rgb(image_red, image_green, image_blue):
    """
    Turns three images (channels) into a scikit-image-style RGB image
    with the last dimension being the channel axis.
    """
    return np.asarray([image_red, image_green, image_blue]).swapaxes(0, 2)

def is_image(image):
    return isinstance(image, np.ndarray) or \
        str(type(image)) in ["<class 'cupy._core.core.ndarray'>",
                             "<class 'dask.array.core.Array'>",
                             "<class 'xarray.core.dataarray.DataArray'>",
                             "<class 'resource_backed_dask_array.ResourceBackedDaskArray'>",
                             "<class 'torch.Tensor'>",
                             "<class 'pyclesperanto_prototype._tier0._cuda_backend.CUDAArray'>",
                             "<class 'pyclesperanto_prototype._tier0._pycl.OCLArray'>"]
        # isinstance(image, tuple) or \
        # isinstance(image, list) or \


def is_label_image(image):
    if isinstance(image, tuple) or \
            isinstance(image, list):
        return False

    return image.dtype == np.uint32 or image.dtype == np.uint64 or \
        image.dtype == np.int32 or image.dtype == np.int64


def count_image_parameters(func):
    import inspect
    try:
        sig = inspect.signature(func)
    except:
        return 0

    n = 0

    for i, key in enumerate(list(sig.parameters.keys())):
        if parameter_is_image_parameter(sig.parameters[key]):
            n = n + 1
    return n


def parameter_is_image_parameter(parameter):
    type_annotation = str(parameter.annotation)
    name = parameter.name

    return ("NewType.<locals>.new_type" in type_annotation or \
            "Image" in type_annotation or \
            "LabelsData" in type_annotation or \
            "LayerData" in type_annotation or \
            "image" in name.lower() or \
            "label" in name.lower() or \
            "mask" in name.lower()
            )

def _no_resize(widget):
    import ipywidgets
    return ipywidgets.HBox([ipywidgets.VBox([widget])])




def numpy_to_gif_bytestream(timelapse, frame_delay_ms=100, num_loops=1000):
    """Turn a NumPy array into a bytestream"""
    import numpy as np
    import imageio
    import io

    # Convert the NumPy array to a PIL Image
    # image = Image.fromarray(data.astype(np.uint8)).convert("RGBA")

    # Create a BytesIO object
    bytes_io = io.BytesIO()

    # Save the PIL image to the BytesIO object as a PNG
    # image.save(bytes_io, format='GIF')

    with imageio.get_writer(bytes_io, mode='I', duration=frame_delay_ms, loop=num_loops, format="GIF") as writer:
        for frame in timelapse:
            writer.append_data(frame.astype(np.uint8))

    # return the beginning of the file as a bytestream
    bytes_io.seek(0)
    return bytes_io.read()


def _gif_to_html(gif, width=None):
    import base64

    style = ""
    if width is not None:
        style = f"style=\"width: {width}px;\""

    url = 'data:image/gif;base64,' + base64.b64encode(gif).decode('utf-8')
    return f'<img src="{url}" {style}></img>'
