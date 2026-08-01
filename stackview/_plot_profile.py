def plot_profile(image, point1, point2, linecolor='orange'):
    """
    Extract intensity along a line between two points and create a combined figure.

    Parameters:
    -----------
    image : numpy.ndarray
        Input image (2D grayscale or 3D RGB)
    point1 : tuple
        First point coordinates (x, y)
    point2 : tuple
        Second point coordinates (x, y)
    linecolor : str
        Color for the line and points on the image and the intensity profile plot

    Returns:
    --------
    numpy.ndarray
        Combined figure as a numpy array (RGB image)
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import ndimage
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    x1, y1 = point1
    x2, y2 = point2

    # Calculate number of points along the line
    length = int(np.hypot(x2 - x1, y2 - y1))

    # Generate coordinates along the line
    x_coords = np.linspace(x1, x2, length)
    y_coords = np.linspace(y1, y2, length)

    # Extract intensity values along the line
    if image.ndim == 2:  # Grayscale image
        intensities = ndimage.map_coordinates(image, [y_coords, x_coords], order=1)
    else:  # RGB image - use average of channels or first channel
        intensities = ndimage.map_coordinates(
            np.mean(image, axis=2), [y_coords, x_coords], order=1
        )

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Plot the image with the line
    if image.ndim == 2:
        ax1.imshow(image, cmap='gray')
    else:
        ax1.imshow(image)

    ax1.plot([x1, x2], [y1, y2], '-', color=linecolor, linewidth=2, label='Profile Line')
    ax1.plot([x1, x2], [y1, y2], 'o', color=linecolor, markersize=8)
    ax1.axis('off')

    # Plot the intensity profile
    ax2.plot(intensities, linewidth=2, color=linecolor)
    ax2.set_xlabel('Distance along line (pixels)')
    ax2.set_ylabel('Intensity')
    ax2.grid(True, alpha=0.3)

    plt.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0.05)

    # Convert figure to numpy array
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    buf = canvas.buffer_rgba()
    result = np.asarray(buf)

    plt.close(fig)  # Close figure to prevent displaying

    return result