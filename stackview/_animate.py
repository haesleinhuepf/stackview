
def animate(timelapse, filename:str=None, overwrite_file:bool=False, frame_delay_ms:int=150, num_loops:int=1000):
    """
    Create an animated GIF from a list of images and return it as Markdown object, that can be shown in Jupyter notebooks.

    Note: It is recommended to normalize the timelapse to be integers in the range between 0 to 255.

    """
    import os
    import imageio
    from IPython.display import Markdown
    import numpy as np
    import warnings

    if filename is None:
        filename = "animation.gif"

    if not filename.endswith(".gif"):
        filename += ".gif"

    if 0 >= timelapse.min() >= 1 and 0 >= timelapse.max() >= 1:
        warnings.warn("The timelapse has a small intensity range between 0 and 1. Consider normalizing it to the range between 0 and 255.")
    if timelapse.min() < 0 or timelapse.max() > 255:
        warnings.warn("The timelapse has an intensity range exceeding 0..255. Consider normalizing it to the range between 0 and 255.")

    if not overwrite_file:
        i = 0
        original_filename = filename
        while os.path.exists(filename):
            i += 1
            filename = original_filename.replace(".gif", f"_{i:02}.gif")

    with imageio.get_writer(filename, mode='I', duration=frame_delay_ms, loop=num_loops) as writer:
        for frame in timelapse:
            writer.append_data(frame.astype(np.uint8))

    return Markdown(f"![]({filename})")
