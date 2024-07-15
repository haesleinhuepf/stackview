
def list_bia_bob_plugins():
    """List of function hints for bia_bob"""
    return """    * Displays an image with a slider and label showing mouse position and intensity.
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
    
    * Build a user interface with sliders for numeric parameters
    stackview.interact(func, image)
    
    * Display an image and allows slicing in three dimensions (Z, Y, and X).
    stackview.orthogonal(image)
    
    * Display an image with a slider and label showing the mouse position and intensity.
    stackview.picker(image)
    
    * Display two images side by side, with an additional overlay view of their overlap
    stackview.side_by_side(image1, image2)
    
    * Display an image with a slider to navigate through a stack.
    stackview.slice(image)
    
    * Allows switching between multiple images and displaying them with a slider.
    stackview.switch(images:list)
    
    * Allows plotting a scatterplot of a pandas dataframe while interactively choosing the columns and using a lasso tool for selecting data points
    stackview.scatterplot(dataframe, column_x, column_y, selection_column)
    
    * Allows plotting a scatterplot of a pandas dataframe in relation to a label image and optionally an image
    stackview.clusterplot(image=image, labels=label_image, df=dataframe, labels, column_x, column_y, selection_column, image)
    
    * Draw two connected scatterplots of a pandas dataframe in relation to a label image and optionally an image
    import ipywidgets as widgets
    from ipywidgets import HBox
    import stackview
    def update2(e=None):
        widget2.update()
    def update1(e=None):
        widget1.update()
    widget1 = stackview.scatterplot(df=dataframe, column_x="column1", column_y="column2", selection_changed_callback=update2)
    widget2 = stackview.scatterplot(df=dataframe, column_x="column3", column_y="column4", selection_changed_callback=update1)
    display(HBox([widget1, widget2])) # Arrange the widgets side by side using HBox
    """
