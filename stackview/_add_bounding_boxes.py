import numpy as np
from ._static_view import jupyter_displayable_output

def color_name_to_rgb(color_name):
    import matplotlib.colors as mcolors
    import numpy as np
    # Convert the color name to RGB (values between 0 and 1)
    rgb_tuple = mcolors.to_rgb(color_name)
    # Convert the RGB tuple to a numpy array with values between 0 and 255
    return np.array([int(rgb_tuple[0] * 255), int(rgb_tuple[1] * 255), int(rgb_tuple[2] * 255)])




@jupyter_displayable_output
def add_bounding_boxes(image, bounding_boxes, line_width=2):
    """
    Adds bounding boxes to an image by drawing them on top.

    Note
    ----
    The image is modified. It is potentially converted to RGB and the pixel values of the frames
    of the bounding boxes are overwritten. You should not analyse pixel intensities of the resulting image,
    but of the raw data instead.

    Parameters:
    -----------
    image : numpy.ndarray
        The input image to visualize
    bounding_boxes : list of dict
        List of dictionaries, each with 'x', 'y', 'width', 'height' keys, optional also 'color' and 'description'.
        If image is a 3D image, the list of bounding boxes should be a list of lists of dictionaries,
        for each image slice a separate list.
    linewidth : int, optional
        Width of the bounding box lines, default is 2
    """
    # handle n-d images and bounding boxes
    shape = np.asarray(image).shape
    if len(shape) > 3 or (len(shape) == 3 and shape[-1] not in [3, 4]):
        return np.asarray([add_bounding_boxes(i, b) for i, b in zip(image, bounding_boxes)])

    from ._image_widget import _img_to_rgb
    from PIL import Image, ImageDraw, ImageFont

    # Create a copy of the image to avoid modifying the original
    img_with_boxes = _img_to_rgb(image)

    if img_with_boxes is image:
        img_with_boxes = img_with_boxes.copy()

    # Draw each bounding box directly on the image pixels
    for bbox in bounding_boxes:
        x = bbox['x']
        y = bbox['y']
        width = bbox['width']
        height = bbox['height']
        color_name = bbox['color'] if 'color' in bbox else "red"

        # Convert color name to RGB
        color = color_name_to_rgb(color_name)

        # Draw the rectangle borders directly into the image pixels
        for i in range(line_width):
            # Top line
            if y + i < img_with_boxes.shape[0]:
                img_with_boxes[y + i, x:x + width + 1, :] = color

            # Bottom line
            if y + height - i < img_with_boxes.shape[0]:
                img_with_boxes[y + height - i, x:x + width + 1, :] = color

            # Left line
            if x + i < img_with_boxes.shape[1]:
                img_with_boxes[y:y + height + 1, x + i, :] = color

            # Right line
            if x + width - i < img_with_boxes.shape[1]:
                img_with_boxes[y:y + height + 1, x + width - i, :] = color

        # Add description if it exists
        if 'description' in bbox:
            # Convert numpy array to PIL Image for text drawing
            img_uint8 = img_with_boxes.astype(np.uint8)
            pil_img = Image.fromarray(img_uint8)
            draw = ImageDraw.Draw(pil_img)

            # Use a default font
            font_size = bbox['font_size'] if 'font_size' in bbox else 15
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default(size=font_size)

            # Draw text at the top left corner of the bounding box
            # Convert color from numpy array to tuple for PIL
            text_color = tuple(color)
            draw.text((x+line_width, y), bbox['description'], fill=text_color, font=font)

            # Convert back to numpy array
            img_with_boxes = np.array(pil_img)

    return img_with_boxes
