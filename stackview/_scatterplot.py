import numpy as np

def scatterplot(df, column_x="x", column_y="y", column_selection="selection", figsize=(4, 4), selection_changed_callback=None, markersize=4):
    """
    Create an interactive plot (scatter plot or histogram) based on selected columns.

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
        The size of the markers (for scatter plots)

    Returns
    -------
    An ipywidgets widget
    """
    from ipywidgets import VBox, HBox, Layout
    from ._utilities import _no_resize
    import matplotlib.pyplot as plt
    import ipywidgets as widgets

    # Layout for dropdown menus
    small_layout = Layout(width="auto", padding="0px", margin="0px", align_items="center", justify_content="center")

    # Dropdowns for axis selection
    x_pulldown = widgets.Dropdown(
        options=list(df.columns),
        value=column_x,
        layout=small_layout,
        description="X-axis",
    )
    y_pulldown = widgets.Dropdown(
        options=list(df.columns),
        value=column_y,
        layout=small_layout,
        description="Y-axis",
    )

    # Container for the plot canvas
    plot_output = widgets.Output()

    # Helper function to create the appropriate plot
    def create_plot():
        with plot_output:
            # Clear previous output and figure
            plot_output.clear_output(wait=True)
            plt.close("all")

            # Create a new plot based on the selected columns
            if x_pulldown.value == y_pulldown.value:
                plotter = HistogramPlotter(df, x_pulldown.value, y_pulldown.value, column_selection, figsize, selection_changed_callback, markersize)
            else:
                plotter = ScatterPlotter(df, x_pulldown.value, y_pulldown.value, column_selection, figsize, selection_changed_callback, markersize)

            # Render the figure
            plt.show(plotter.fig)
            return plotter

    # Initialize the plotter
    plotter = create_plot()

    # Callback for dropdown changes
    def on_change(change):
        nonlocal plotter
        if change["name"] == "value":
            # Update or recreate the plotter based on the new column values
            plotter = create_plot()

    # Attach observers to dropdowns
    x_pulldown.observe(on_change, names="value")
    y_pulldown.observe(on_change, names="value")

    # Combine dropdowns and plot into a single widget
    result = _no_resize(VBox([
        HBox([x_pulldown, y_pulldown], layout=small_layout),
        plot_output,
    ]))

    return result


class Plotter:
    """
    Base class for creating interactive plots.
    """
    def __init__(self, df, column_x, column_y, column_selection, figsize, selection_changed_callback, markersize):
        self.df = df
        self.column_x = column_x
        self.column_y = column_y
        self.column_selection = column_selection
        self.figsize = figsize
        self.selection_changed_callback = selection_changed_callback
        self.markersize = markersize

    def set_data(self, df, column_x, column_y):
        self.df = df
        self.column_x = column_x
        self.column_y = column_y

    def update(self):
        raise NotImplementedError("Subclasses must implement this method.")


class ScatterPlotter(Plotter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import matplotlib.pyplot as plt
        from matplotlib._pylab_helpers import Gcf

        # Set up interactive mode for Jupyter notebooks
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            ipython.run_line_magic("matplotlib", "ipympl")
        plt.ion()

        # Create figure
        self.fig = plt.figure(figsize=self.figsize)
        plt.subplots_adjust(left=0.15, right=1, top=1, bottom=0.1)
        self.ax = None
        self.plotted_points = None

        # Selector initialization (to be updated during plotting)
        self.selector = None
        self.update()

    def update(self):
        self.fig.clf()
        self.ax = self.fig.gca()
        self.plotted_points = self.ax.scatter(
            self.df[self.column_x], self.df[self.column_y], s=self.markersize
        )
        self.ax.set_xlabel(self.column_x)
        self.ax.set_ylabel(self.column_y)
        self.setup_selector()

    def setup_selector(self):
        self.selector = Selector(self.fig, self.ax, self.plotted_points, callback=self.set_selection)
        if self.column_selection in self.df.columns:
            self.selector.set_selection(self.df[self.column_selection])

    def set_selection(self, selection):
        self.df[self.column_selection] = selection
        self.selector.set_selection(selection)
        if self.selection_changed_callback:
            self.selection_changed_callback(selection)


class HistogramPlotter(Plotter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import matplotlib.pyplot as plt
        from matplotlib._pylab_helpers import Gcf

        # Set up interactive mode for Jupyter notebooks
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            ipython.run_line_magic("matplotlib", "ipympl")
        plt.ion()

        # Create figure
        self.fig = plt.figure(figsize=self.figsize)
        plt.subplots_adjust(left=0.15, right=1, top=1, bottom=0.1)
        self.ax = None
        self.update()

    def update(self):
        self.fig.clf()
        self.ax = self.fig.gca()
        self.ax.hist(self.df[self.column_x], bins=30, alpha=0.7)
        self.ax.set_xlabel(self.column_x)
        self.ax.set_ylabel("Frequency")

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
