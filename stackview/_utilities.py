import numpy as np
def merge_rgb(image_red, image_green, image_blue):
    """
    Turns three images (channels) into a scikit-image-style RGB image
    with the last dimension being the channel axis.
    """
    return np.asarray([image_red, image_green, image_blue]).swapaxes(0, 2)

