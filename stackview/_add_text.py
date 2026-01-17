import numpy as np
from typing import List, Union

def add_text(
    images: Union[List[np.ndarray], np.ndarray],
    texts: List[str],
    font_size: int = 16,
    text_color: str = 'white',
    bg_color: str = 'black',
    position: str = 'top',
    colormap: str = 'Greys_r'
) -> List[np.ndarray]:
    """
    Burn text onto images using matplotlib.

    Parameters:
    -----------
    images : list of np.ndarray or np.ndarray
        List of images or n-dimensional array where first dimension is images
    texts : list of str
        List of text strings to burn onto each image
    font_size : int
        Font size for the text (default: 16)
    text_color : str
        Color of the text (default: 'white')
    position : str
        Text position: 'top', 'bottom', 'center', 'top-left', 'top-right', 
        'bottom-left', 'bottom-right', 'center-left', 'center-right' (default: 'top')
    colormap : str
        Colormap to use for displaying the image (default: 'Greys_r')

    Returns:
    --------
    list of np.ndarray
        List of images with text burned in
    """
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    # Convert to list if numpy array
    if isinstance(images, np.ndarray):
        images = [images[i] for i in range(images.shape[0])]

    if len(images) != len(texts):
        raise ValueError(f"Number of images ({len(images)}) must match number of texts ({len(texts)})")

    result_images = []

    for img, text in zip(images, texts):
        # Create figure with exact image size
        h, w = img.shape[:2]
        dpi = 100
        fig = plt.figure(figsize=(w/dpi, h/dpi), dpi=dpi)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')

        # Display the image
        ax.imshow(img, cmap=colormap)

        # Determine text position
        # Default to center
        x_pos, y_pos = 0.5, 0.5
        ha, va = 'center', 'center'
        
        # Vertical positioning
        if 'top' in position:
            y_pos, va = 0.95, 'top'
        elif 'bottom' in position:
            y_pos, va = 0.05, 'bottom'
        
        # Horizontal positioning
        if 'left' in position:
            x_pos, ha = 0.05, 'left'
        elif 'right' in position:
            x_pos, ha = 0.95, 'right'

        # Add text with background
        px = 1.0 / w
        for delta_x, delta_y in [(-px, -px), (px, -px), (-px, px), (px, px)]:
            ax.text(
                x_pos+delta_x, y_pos+delta_y, text,
                transform=ax.transAxes,
                fontsize=font_size,
                color=bg_color,
                ha=ha,
                va=va
            )
        ax.text(
            x_pos, y_pos, text,
            transform=ax.transAxes,
            fontsize=font_size,
            color=text_color,
            ha=ha,
            va=va
        )

        # Convert figure to numpy array
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        buf = canvas.buffer_rgba()
        result = np.asarray(buf)

        # Convert RGBA to RGB if original was RGB
        if img.ndim == 3 and img.shape[2] == 3:
            result = result[:, :, :3]
        # Convert back to single-channel if original was single-channel
        elif img.ndim == 2 or img.shape[-1] not in [3, 4]:
            result = result[:, :, 0]
        result = result.astype(img.dtype)

        result_images.append(result)
        plt.close(fig)

    return result_images