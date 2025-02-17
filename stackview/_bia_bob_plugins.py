
def list_bia_bob_plugins():
    """List of function hints for bia_bob"""
    return """
    ## Image visualization using stackview

    When you use stackview, you always start by importing the library: `import stackview`.
    When asked the following tasks, you can adapt one of the corresponding code snippet:
    * Displays an image with a slider and label showing mouse position and intensity.
      stackview.annotate(image, labels)
    
    * Allows cropping an image along all axes.
      stackview.crop(image)
    
    * Showing an image stored in variable `image` and a segmented image stored in variable `labels` on top using an interative curtain. Also works with two images or two label images.
      stackview.curtain(image, labels)
    
    * Showing an image stored in variable `image` and a segmented image stored in variable `labels` on top with animated blending. Also works with two images or two label images.
      stackview.animate_curtain(image, labels)
    
    * Showing an animation / timelapse image stored in variable `image`.
      stackview.animate(image)
    
    * Save an animation / timelapse stored in variable `image` with specified frame delay to a file.
      stackview.animate(image, filename="output.gif", frame_delay_ms=100)
    
    * Display an image stored in a variable `image` (this also works with label images). Prefer stackview.insight over matplotlib.pyplot.imshow!
      stackview.insight(image)
    
    * Display an image with a slider and label showing the mouse position and intensity.
      stackview.picker(image)
    
    * Display an image with a slider to navigate through a stack.
      stackview.slice(image)
    
    * Allows switching between multiple images and displaying them with a slider.
      stackview.switch(images:list)
    
    * Allows plotting a scatterplot of a pandas dataframe while interactively choosing the columns and using a lasso tool for selecting data points
      stackview.scatterplot(dataframe, column_x, column_y, selection_column)
    
    * Allows plotting a scatterplot of a pandas dataframe in relation to a label image and optionally an image
      stackview.clusterplot(image=image, labels=label_image, df=dataframe, labels, column_x, column_y, selection_column, image)
      
    * Show multiple images in a grid
      import stackview
      from matplotlib import pyplot as plt
      fig, ax = plt.subplots(1, 2, figsize=(10, 4))
      stackview.imshow(image, plot=ax[0])
      stackview.imshow(labels, plot=ax[1]) 
    """
