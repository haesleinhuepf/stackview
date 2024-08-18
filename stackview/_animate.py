
def animate(timelapse, filename:str=None, overwrite_file:bool=True, frame_delay_ms:int=150, num_loops:int=1000, colormap=None, display_min=None, display_max=None, zoom_factor:float=1.0):
    """
    Create an animated GIF from a list of 2D images and return it as Markdown object, that can be shown in Jupyter notebooks.
    RGB images are supported as well, but no 3D image stacks.

    Note: It is recommended to normalize the timelapse to be integers in the range between 0 to 255.

    Parameters
    ----------
    timelapse: np.ndarray
        2D image or 3D image stack
    filename: str, optional
        Name of the file where the animation will be saved
    overwrite_file: bool, optional
        Overwrite the file if it already exists. Default: True
    frame_delay_ms: int, optional
        Delay between frames in milliseconds
    num_loops: int, optional
        Number of loops in the animation
    zoom_factor: float, optional
        Allows showing the image larger (> 1) or smaller (<1)
    colormap: str, optional
        Matplotlib colormap name or "pure_green", "pure_magenta", ...
    display_min: float, optional
        Lower bound of properly shown intensities
    display_max: float, optional
        Upper bound of properly shown intensities
    """
    import os
    import imageio
    from IPython.display import HTML
    import numpy as np
    import warnings
    from stackview._image_widget import _img_to_rgb
    from ._utilities import numpy_to_gif_bytestream, _gif_to_html

    if isinstance(timelapse, list):
        timelapse = np.asarray(timelapse)

    if 0 <= timelapse.min() <= 1 and 0 <= timelapse.max() <= 1:
        warnings.warn("The timelapse has a small intensity range between 0 and 1. Consider normalizing it to the range between 0 and 255.")
    if timelapse.min() < 0 or timelapse.max() > 255:
        warnings.warn("The timelapse has an intensity range exceeding 0..255. Consider normalizing it to the range between 0 and 255.")

    image_rgb = np.asarray([_img_to_rgb(i, colormap=colormap, display_min=display_min, display_max=display_max) for i in timelapse]).astype(np.uint8)

    if filename is not None:
        if not filename.endswith(".gif"):
            filename += ".gif"
        if not overwrite_file:
            i = 0
            original_filename = filename
            while os.path.exists(filename):
                i += 1
                filename = original_filename.replace(".gif", f"_{i:02}.gif")

        with imageio.get_writer(filename, mode='I', duration=frame_delay_ms, loop=num_loops) as writer:
            for frame in image_rgb:
                writer.append_data(frame)


    if np.prod(image_rgb.shape) > 1024 * 1024 * 10:
        warnings.warn("The image is quite large (> 10 MByte) and might not be properly shown in the notebook when rendered over the internet. Consider subsampling or cropping the image for visualization purposes.")

    bytestream = numpy_to_gif_bytestream(image_rgb, frame_delay_ms=frame_delay_ms, num_loops=num_loops)
    return HTML(_gif_to_html(bytestream, width=int(image_rgb.shape[-2] * zoom_factor)))

def animate_curtain(timelapse, timelapse_curtain,
                    axis: int = 0,
                    alpha: float = 1,
                    num_steps:int = 20,
                    zoom_factor: float = 1,
                    colormap=None, display_min=None, display_max=None,
                    curtain_colormap:str = None,
                    curtain_display_min:float = None,
                    curtain_display_max:float = None,
                    filename:str=None, overwrite_file:bool=False, frame_delay_ms:int=150, num_loops:int=1000):
    """
    Render a curtain showing two 2D images. RGB images are supported as well, but no 3D image stacks.

    Parameters
    ----------
    timelapse: np.ndarray
        2D image or 3D image stack
    timelapse_curtain: np.ndarray
        2D image or 3D image stack
    axis: int, optional
        Axis in case we are slicing a stack
    alpha: float, optional
        sets the transparency of the curtain
    num_steps: int, optional
        number of steps in the animation, half of them the curtain will go left-right, the other half right-left
    zoom_factor: float, optional
        Allows showing the image larger (> 1) or smaller (<1)
    colormap: str, optional
        Matplotlib colormap name or "pure_green", "pure_magenta", ...
    display_min: float, optional
        Lower bound of properly shown intensities
    display_max: float, optional
        Upper bound of properly shown intensities
    curtain_colormap: str, optional
        Matplotlib colormap name or "pure_green", "pure_magenta", ...
    curtain_display_min: float, optional
        Lower bound of properly shown intensities
    curtain_display_max: float, optional
        Upper bound of properly shown intensities
    filename: str, optional
        Name of the file where the animation will be saved
    overwrite_file: bool, optional
        Overwrite the file if it already exists
    frame_delay_ms: int, optional
        Delay between frames in milliseconds
    num_loops: int, optional
        Number of loops in the animation

    """
    import numpy as np
    from ._image_widget import _img_to_rgb


    if isinstance(timelapse, list):
        timelapse = np.asarray(timelapse)

    if isinstance(timelapse_curtain, list):
        timelapse_curtain = np.asarray(timelapse_curtain)

    max_size = timelapse.shape[1]

    images = []
    steps = list(range(0, max_size + 1, int(max_size / num_steps * 2)))
    steps = steps + steps[::-1]

    for slider_value in steps:
        if len(timelapse.shape) < 3 or (len(timelapse.shape) == 3 and timelapse.shape[-1] == 3):
            image_slice = _img_to_rgb(timelapse.copy(), colormap=colormap, display_min=display_min, display_max=display_max)
            image_slice_curtain = _img_to_rgb(timelapse_curtain, colormap=curtain_colormap, display_min=curtain_display_min,
                                              display_max=curtain_display_max)
        else:
            image_slice = _img_to_rgb(np.take(timelapse, slider_value, axis=axis), colormap=colormap,
                                      display_min=display_min, display_max=display_max)
            image_slice_curtain = _img_to_rgb(np.take(timelapse_curtain, slider_value, axis=axis),
                                              colormap=curtain_colormap, display_min=curtain_display_min,
                                              display_max=curtain_display_max)
        image_slice[:, slider_value:] = (1 - alpha) * image_slice[:, slider_value:] + \
                                                alpha * image_slice_curtain[:, slider_value:]

        images.append(image_slice)

    return animate(np.asarray(images), filename=filename, overwrite_file=overwrite_file, frame_delay_ms=frame_delay_ms, num_loops=num_loops, zoom_factor=zoom_factor)
