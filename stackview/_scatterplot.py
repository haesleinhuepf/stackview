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

    from ipywidgets import VBox, HBox, Layout
    from ._utilities import _no_resize

    plotter = ScatterPlotter(df, column_x, column_y, column_selection, figsize, selection_changed_callback=selection_changed_callback, markersize=markersize)
    small_layout = Layout(width='auto', padding='0px', margin='0px', align_items='center', justify_content='center')

    import ipywidgets
    x_pulldown = ipywidgets.Dropdown(
        options=list(df.columns),
        value=column_x,
        layout=small_layout
    )
    y_pulldown = ipywidgets.Dropdown(
        options=list(df.columns),
        value=column_y,
        layout=small_layout
    )

    def on_change(event):
        """Executed when the user changes the pulldown selection."""
        if event['type'] == 'change' and event['name'] == 'value':
            plotter.set_data(df, x_pulldown.value, y_pulldown.value)
            plotter.update()

    x_pulldown.observe(on_change)
    y_pulldown.observe(on_change)

    result = _no_resize(VBox([
        HBox([ipywidgets.Label("Axes "), x_pulldown, y_pulldown], layout=small_layout),
        plotter.widget
    ]))

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

        # switch to interactive mode if we are in a Jupyter notebook
        ipython = get_ipython()
        if ipython is not None:
            ipython.run_line_magic("matplotlib", "ipympl")
        plt.ion()

        # store variables
        self.set_data(df, column_x, column_y)
        self.selection_column = column_selection
        self.selection_changed_callback = selection_changed_callback
        self.markersize = markersize

        # create figure
        self.fig = plt.figure(figsize=figsize)
        #self.fig.tight_layout(pad=0, h_pad=0, w_pad=0)
        plt.subplots_adjust(left=0.15, right=1, top=1, bottom=0.1)

        self.ax = None
        self.plotted_points = None
        self.update()

        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = False
        self.fig.canvas.resizable = False

        # prevent immediate display of the canvas
        manager = Gcf.get_active()
        Gcf.figs.pop(manager.num, None)

        self.selector = None
        #self.selector = Selector(self.fig, self.ax, self.plotted_points, callback=self.set_selection)
        self.update()

        # show selection if defined
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


# modified from https://matplotlib.org/3.1.1/gallery/widgets/lasso_selector_demo_sgskip.html
class Selector:
    def __init__(self, parent, ax, collection, callback):
        from matplotlib.widgets import LassoSelector
        self.parent = parent
        self.ax = ax
        self.canvas = ax.figure.canvas
        self.offsets = collection.get_offsets()
        self.num_points = len(self.offsets)
        self.collection = collection

        self.lasso = LassoSelector(ax, onselect=self.on_select, props=dict(color='magenta'))
        self.selected_indices = []
        self.callback = callback

        self.face_colors = collection.get_facecolors()
        if len(self.face_colors) == 0:
            raise ValueError('Collection must have a face color')
        elif len(self.face_colors) == 1:
            self.face_colors = np.tile(self.face_colors, (self.num_points, 1))

    def on_select(self, verts):
        from matplotlib.path import Path
        path = Path(verts)
        selection = path.contains_points(self.offsets)
        self.callback(selection)

    def set_selection(self, selection):
        from ._colormaps import _labels_lut
        self.selected_indices = np.nonzero(selection)
        labels_lut = _labels_lut()

        for i in range(3):
            self.face_colors[:, i] = labels_lut[1,i]
            self.face_colors[self.selected_indices, i] = labels_lut[2,i]

        self.collection.set_facecolors(self.face_colors)
        self.update()

    def update(self):
        self.canvas.draw_idle()

    def disconnect(self):
        self.lasso.disconnect_events()
        self.canvas.draw_idle()
