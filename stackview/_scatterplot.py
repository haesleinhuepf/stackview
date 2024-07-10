import numpy as np

def scatterplot(df, x: str = "x", y: str = "y", selection: str = "selection", figsize=(5, 5), selection_changed_callback=None):

    from ._grid import grid

    sp = ScatterPlot(df, x, y, selection, figsize, selection_changed_callback=selection_changed_callback)
    sp.widget.scatterplot = sp

    import ipywidgets
    x_pulldown = ipywidgets.Dropdown(
        options=list(df.columns),
        value=x,
        description="X"
    )
    y_pulldown = ipywidgets.Dropdown(
        options=list(df.columns),
        value=y,
        description="Y"
    )

    def on_change(event):

        if event['type'] == 'change' and event['name'] == 'value':
            sp.set_data(df, x_pulldown.value, y_pulldown.value)
            sp.update()

    x_pulldown.observe(on_change)
    y_pulldown.observe(on_change)

    result = grid([
        [x_pulldown],
        [y_pulldown],
        [sp.widget]
    ])

    return result


class ScatterPlot():
    def __init__(self, df, x, y, selection, figsize, selection_changed_callback):
        import matplotlib.pyplot as plt
        from matplotlib._pylab_helpers import Gcf

        # print("A")

        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is not None:
            ipython.run_line_magic("matplotlib", "ipympl")

        import ipywidgets as widgets
        import numpy as np

        self.set_data(df, x, y)
        self.selection_column = selection
        self.selection_changed_callback = selection_changed_callback
        # np.random.random((2, 100))

        # print("B")
        # ensure we are interactive mode
        plt.ion()

        self.fig = plt.figure(figsize=figsize)
        self.fig.tight_layout()
        self.ax = self.fig.gca()

        self.update()

        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.fig.canvas.footer_visible = False
        self.fig.canvas.resizable = False

        # prevent immediate display of the canvas
        manager = Gcf.get_active()
        Gcf.figs.pop(manager.num, None)

        self.selector = Selector(self.fig, self.ax, self.pts, callback=self.set_selection)

        if selection in df.columns:
            self.selector.set_selection(df[selection])

        self.widget = self.fig.canvas

        self.update()

    def set_data(self, df, x, y):
        self.dataframe = df
        self.x = x
        self.y = y
        self.data = np.asarray((df[x], df[y]))

    def set_selection(self, selection):
        self.dataframe[self.selection_column] = selection
        self.selector.set_selection(selection)
        if self.selection_changed_callback is not None:
            self.selection_changed_callback(selection)

    def update(self):
        self.fig.clf()
        self.ax = self.fig.gca()
        self.pts = self.ax.scatter(self.data[0], self.data[1])
        self.ax.set_xlabel(self.x)
        self.ax.set_ylabel(self.y)
        self.selector = Selector(self.fig, self.ax, self.pts, callback=self.set_selection)
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
        self.xys = collection.get_offsets()
        self.Npts = len(self.xys)
        self.collection = collection

        self.lasso = LassoSelector(ax, onselect=self.onselect)
        self.ind = []
        self.ind_mask = []
        self.callback = callback

        self.alpha_other = 0.3
        self.fc = collection.get_facecolors()
        if len(self.fc) == 0:
            raise ValueError('Collection must have a facecolor')
        elif len(self.fc) == 1:
            self.fc = np.tile(self.fc, (self.Npts, 1))

    def onselect(self, verts):
        from matplotlib.path import Path
        self.path = Path(verts)
        selection = self.path.contains_points(self.xys)
        self.callback(selection)

    def set_selection(self, selection):
        self.ind = np.nonzero(selection)
        self.fc[:, -1] = self.alpha_other
        self.fc[self.ind, -1] = 1
        self.collection.set_facecolors(self.fc)
        self.update()

    def update(self):
        self.canvas.draw_idle()

    def disconnect(self):
        self.lasso.disconnect_events()
        self.canvas.draw_idle()
