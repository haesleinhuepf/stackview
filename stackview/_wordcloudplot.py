def wordcloudplot(df, column_x: str = "x", column_y: str = "y", column_text: str = "text",
                  column_selection: str = "selection",
                  figsize=(4, 4), markersize=4, width=400, height=400):
    """
    Visualizes a scatter plot of columns in a given dataframe next to a word cloud.
    Per default, the dataframe should contain a column "text".

    Parameters
    ----------
    df: pandas.DataFrame
        The dataframe to plot
    column_x: str, optional
        The column to use for the x-axis
    column_y: str, optional
        The column to use for the y-axis
    column_text: str, optional
        The column to use for the text that make the word cloud
    column_selection: str, optional
        The column to use for the selection
    figsize: tuple, optional
        The size of the scatter plot figure
    markersize: int
        The size of the markers
    width: int
        The width of the word cloud
    height: int
        The height of the word cloud

    Returns
    -------
    An ipywidgets widget
    """
    import numpy as np
    from ._grid import grid
    from ._curtain import curtain
    from ._slice import slice
    from ._scatterplot import scatterplot
    import functools
    from wordcloud import WordCloud

    if column_selection in df.columns:
        selected_texts = df[df['selection'] == 1][column_text]
        text = "\n".join(selected_texts)
    else:
        selected_texts = df[column_text]
        text = "\n".join(selected_texts)

    wordcloud = WordCloud(colormap="twilight", background_color="white", width=width, height=height).generate(text)
    image = wordcloud.to_image()
    selected_image = np.array(image)

    image_display = slice(selected_image)

    def update(selection, df, column_text, selected_image, widget):
        selected_texts = df[column_text][list(selection)]
        text = "\n".join(selected_texts)

        if len(text) == 0:
            text = "empty wordcloud"

        wordcloud = WordCloud(colormap="twilight", background_color="white", width=width, height=height).generate(text)
        image = wordcloud.to_image()
        temp = np.array(image)

        # overwrite the pixels in the given image
        np.copyto(selected_image, temp.astype(selected_image.dtype))

        # redraw the visualization
        widget.update()

    update_selection = functools.partial(update, df=df, column_text=column_text, selected_image=selected_image,
                                         widget=image_display)

    scatterplot = scatterplot(df, column_x, column_y, column_selection, figsize=figsize,
                              selection_changed_callback=update_selection, markersize=markersize)

    return grid([[
        image_display,
        scatterplot,

    ]])

