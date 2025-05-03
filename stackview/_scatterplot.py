import numpy as np

def scatterplot(df, column_x: str = "x", column_y: str = "y", column_selection: str = "selection", figsize=(4, 4), selection_changed_callback=None, markersize:int=4):
    """
    Create a scatterplot of a pandas dataframe while interactively choosing the columns and using a lasso tool for selecting data points

    Parameters
    ----------
    df: pandas.DataFrame
        The dataframe to plot
    column_x: str
        The column to use for the x-axis
    column_y: str
        The column to use for the y-axis
    column_selection: str
        The column to use for the selection
    figsize: tuple
        The size of the scatter plot figure
    selection_changed_callback: function
        The function to call when the selection changes
    markersize: int
        The size of the markers

    Returns
    -------
    An ipywidgets widget
    """

    from ipywidgets import VBox, HBox, Layout, Output, Dropdown, Label
    from IPython.display import display

    if column_x == column_y:
        plotter = HistogramPlotter(df, column_x, column_selection, figsize, selection_changed_callback, bins=50)
    else:
        plotter = ScatterPlotter(df, column_x, column_y, column_selection, figsize, selection_changed_callback, markersize)

    small_layout = Layout(width='auto', padding='0px', margin='0px', align_items='center', justify_content='center')

    x_pulldown = Dropdown(options=list(df.columns), value=column_x, layout=small_layout)
    y_pulldown = Dropdown(options=list(df.columns), value=column_y, layout=small_layout)

    plot_output = Output()
    with plot_output:
        display(plotter.widget)

    def on_change(event):
        if event['type'] == 'change' and event['name'] == 'value':
            x_col = x_pulldown.value
            y_col = y_pulldown.value

            nonlocal plotter

            is_histogram_now = (x_col == y_col)
            is_histogram_current = (plotter.column_x == plotter.column_y)

            if is_histogram_now != is_histogram_current:
                if is_histogram_now:
                    new_plotter = HistogramPlotter(df, x_col, column_selection, figsize, selection_changed_callback, bins=50)
                else:
                    new_plotter = ScatterPlotter(df, x_col, y_col, column_selection, figsize, selection_changed_callback, markersize)
                plotter = new_plotter

                with plot_output:
                    plot_output.clear_output(wait=True)
                    display(new_plotter.widget)
            else:
                if is_histogram_now:
                    plotter.set_data(df, x_col)
                else:
                    plotter.set_data(df, x_col, y_col)
                plotter.update()

    x_pulldown.observe(on_change)
    y_pulldown.observe(on_change)

    result = VBox([
        HBox([Label("Axes "), x_pulldown, y_pulldown], layout=small_layout),
        plot_output
    ])

    result.update = plotter.update
    return result


class ScatterPlotter():
    def __init__(self, df, column_x, column_y, column_selection, figsize, selection_changed_callback, markersize):
        """
        An interactive scatter plotter for pandas dataframes.
        Use `.widget` on this object to get access to the graphical user interface.

        Parameters
        ----------
        df: pandas.DataFrame
            The dataframe to plot
        column_x: str
            The column to use for the x-axis
        column_y: str
            The column to use for the y-axis
        column_selection: str
            The column to use for the selection
        figsize: tuple
            The size of the figure
        selection_changed_callback: function
            The function to call when the selection changes
        markersize: int
            The size of the markers
        """
        import matplotlib.pyplot as plt
        from matplotlib._pylab_helpers import Gcf
        from IPython import get_ipython

        ipython = get_ipython()
        if ipython is not None:
            ipython.run_line_magic("matplotlib", "ipympl")
        plt.ion()

        self.set_data(df, column_x, column_y)
        self.selection_column = column_selection
        self.selection_changed_callback = selection_changed_callback
        self.markersize = markersize

        self.fig = plt.figure(figsize=figsize)
        plt.subplots_adjust(left=0.15, right=1, top=1, bottom=0.1)

        self.ax = None
        self.plotted_points = None
        self.update()

        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = False
        self.fig.canvas.resizable = False

        manager = Gcf.get_active()
        Gcf.figs.pop(manager.num, None)

        self.selector = None
        self.update()

        if column_selection in df.columns:
            self.selector.set_selection(df[column_selection])
            self.update()

        self.widget = self.fig.canvas

    def set_data(self, df, column_x, column_y):
        self.dataframe = df
        self.column_x = column_x
        self.column_y = column_y
        self.data = np.asarray((df[column_x], df[column_y]))

    def set_selection(self, selection):
        self.dataframe[self.selection_column] = selection
        self.selector.set_selection(selection)
        if self.selection_changed_callback is not None:
            self.selection_changed_callback(selection)

    def update(self):
        self.fig.clf()
        self.ax = self.fig.gca()
        self.plotted_points = self.ax.scatter(self.data[0], self.data[1], s=self.markersize)
        self.ax.set_xlabel(self.column_x)
        self.ax.set_ylabel(self.column_y)
        self.selector = Selector(self.fig, self.ax, self.plotted_points, callback=self.set_selection)
        if self.selection_column in self.dataframe.columns:
            self.selector.set_selection(self.dataframe[self.selection_column])
        self.selector.update()

        
class HistogramPlotter:

    def __init__(self, df, column, column_selection, figsize, selection_changed_callback, bins=15):
        """
        An interactive histogram plotter for a single column of a pandas DataFrame.
        Designed to be used in combination with ipywidgets for dynamic display.

        Parameters
        ----------
        df : pandas.DataFrame
            The dataframe containing the data to plot
        column : str
            The column of the dataframe to plot as a histogram
        column_selection : str
            The name of the column storing selection status (currently unused for histograms)
        figsize : tuple
            The size of the figure (width, height)
        selection_changed_callback : function or None
            Callback function triggered when selection changes (not used in histogram)
        bins : int
            Number of bins to use for the histogram

        Attributes
        ----------
        widget : matplotlib.backend_bases.FigureCanvasBase
            The canvas widget to be displayed in a Jupyter notebook
        """
        import matplotlib.pyplot as plt
        from matplotlib._pylab_helpers import Gcf
        from IPython import get_ipython

        ipython = get_ipython()
        if ipython is not None:
            ipython.run_line_magic("matplotlib", "ipympl")
        plt.ion()

        self.dataframe = df
        self.column = column
        self.column_x = column
        self.column_y = column
        self.selection_column = column_selection
        self.selection_changed_callback = selection_changed_callback
        self.bins = bins

        self.fig = plt.figure(figsize=figsize)
        plt.subplots_adjust(left=0.15, right=1, top=1, bottom=0.1)
        self.ax = self.fig.gca()

        self.update()

        self.selector = Selector(self.fig, self.ax, self.ax.patches, callback=self.set_selection, mode="hist")
        self.widget = self.fig.canvas

        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = False
        self.fig.canvas.resizable = False

        manager = Gcf.get_active()
        Gcf.figs.pop(manager.num, None)

        self.widget = self.fig.canvas

    def set_data(self, df, column):
        self.dataframe = df
        self.column = column
        self.column_x = column
        self.column_y = column
    
    def set_selection(self, selection):
        import numpy as np

        # Get the bin edges used by the current histogram
        bin_counts, bin_edges = np.histogram(self.dataframe[self.column], bins=self.bins)

        # Create a boolean selection mask over the dataframe
        selected = np.zeros(len(self.dataframe), dtype=bool)

        for i, selected_bin in enumerate(selection):
            if selected_bin:
                if i == len(bin_edges) - 2:
                    # Include right edge for last bin
                    in_bin = (self.dataframe[self.column] >= bin_edges[i]) & (self.dataframe[self.column] <= bin_edges[i + 1])
                else:
                    in_bin = (self.dataframe[self.column] >= bin_edges[i]) & (self.dataframe[self.column] < bin_edges[i + 1])
                selected |= in_bin

        self.dataframe[self.selection_column] = selected
        if self.selection_changed_callback is not None:
            self.selection_changed_callback(selected)


    def update(self):
        self.fig.clf()
        self.ax = self.fig.gca()
        counts, bins, patches = self.ax.hist(self.dataframe[self.column], bins=self.bins, color='steelblue')
        self.ax.set_xlabel(self.column)
        self.ax.set_ylabel("Frequency")
        self.fig.canvas.draw_idle()

        if hasattr(self, "selector"):
            self.selector = Selector(self.fig, self.ax, self.ax.patches, callback=self.set_selection, mode="hist")

# modified from https://matplotlib.org/3.1.1/gallery/widgets/lasso_selector_demo_sgskip.html
class Selector:
    def __init__(self, parent, ax, collection, callback, mode= "scatter"):
        """
        Interactive Lasso-based point selector for matplotlib scatter plots.
        Highlights selected points and invokes a callback with the selection mask.

        Parameters
        ----------
        parent : matplotlib.figure.Figure
            The matplotlib figure containing the plot
        ax : matplotlib.axes.Axes
            The axes to attach the lasso selector to
        collection : matplotlib.collections.PathCollection
            The scatter plot collection from which points are selected
        callback : function
            A function that receives a boolean mask of selected points

        Attributes
        ----------
        selected_indices : list
            Indices of the currently selected points
        face_colors : ndarray
            Array of RGBA colors used to visualize selected/unselected points
        """
        from matplotlib.widgets import LassoSelector
        from matplotlib.path import Path

        self.parent = parent
        self.ax = ax
        self.canvas = ax.figure.canvas
        self.collection = collection
        self.mode = mode
        self.callback = callback
        self.lasso = LassoSelector(ax, onselect=self.on_select, props=dict(color='magenta'))

        if mode == "scatter":
            self.offsets = collection.get_offsets()
            self.num_points = len(self.offsets)

            self.face_colors = collection.get_facecolors()
            if len(self.face_colors) == 0:
                raise ValueError('Collection must have a face color')
            elif len(self.face_colors) == 1:
                self.face_colors = np.tile(self.face_colors, (self.num_points, 1))
        elif mode == "hist":
            self.offsets = None
            self.num_points = len(collection)

    def on_select(self, verts):
        from matplotlib.path import Path
        path = Path(verts)

        if self.mode == "scatter":
            selection = path.contains_points(self.offsets)
            self.callback(selection)
        elif self.mode == "hist":
            selection = np.zeros(len(self.collection), dtype=bool)
            for i, patch in enumerate(self.collection):
                x = patch.get_x()
                y = patch.get_y()
                width = patch.get_width()
                height = patch.get_height()

                # Define key points inside the bar (corners + center)
                test_points = [
                    (x + width * 0.5, y + height * 0.5),  # center
                    (x, y),                               # bottom-left
                    (x + width, y),                       # bottom-right
                    (x, y + height),                      # top-left
                    (x + width, y + height)               # top-right
                ]

                if any(path.contains_point(pt) for pt in test_points):
                    selection[i] = True

            self.callback(selection)
            self.set_selection(selection)

    def set_selection(self, selection):
        blue = [31 / 255, 119 / 255, 180 / 255]   # #1f77b4
        orange = [255 / 255, 127 / 255, 14 / 255] # #ff7f0e

        if self.mode == "scatter":
            self.selected_indices = np.nonzero(selection)
            self.face_colors[:, :3] = blue  # reset all to blue
            self.face_colors[self.selected_indices, :3] = orange  # selected to orange
            self.collection.set_facecolors(self.face_colors)

        elif self.mode == "hist":
            for i, bar in enumerate(self.collection):
                bar.set_facecolor(orange if selection[i] else blue)

        self.update()

    def update(self):
        self.canvas.draw_idle()

    def disconnect(self):
        self.lasso.disconnect_events()
        self.canvas.draw_idle()
