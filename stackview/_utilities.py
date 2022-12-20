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
            "label" in name.lower()
            )
