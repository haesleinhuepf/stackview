import numpy as np

def scatterplot(df, x: str = "x", y: str = "y", selection: str = "selection", figsize=(5, 5), selection_changed_callback=None):
    sp = ScatterPlot(df, x, y, selection, figsize, selection_changed_callback=selection_changed_callback)
    sp.widget.scatterplot = sp
    return sp.widget


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

        self.dataframe = df
        self.set_data(df, x, y)
        self.selection_column = selection
        self.selection_changed_callback = selection_changed_callback
        # np.random.random((2, 100))

        # print("B")
        # ensure we are interactive mode
        plt.ion()

        fig = plt.figure(figsize=figsize)
        fig.tight_layout()
        ax = fig.gca()
        pts = ax.scatter(self.data[0], self.data[1])
        ax.set_xlabel(x)
        ax.set_ylabel(y)

        fig.canvas.toolbar_visible = False
        fig.canvas.header_visible = False
        fig.canvas.footer_visible = False
        fig.canvas.resizable = False

        # prevent immediate display of the canvas
        manager = Gcf.get_active()
        Gcf.figs.pop(manager.num, None)

        self.selector = Selector(fig, ax, pts, callback=self.set_selection)

        if selection in df.columns:
            self.selector.set_selection(df[selection])

        self.widget = fig.canvas

    def set_data(self, df, x, y):
        self.data = np.asarray((df[x], df[y]))

    def set_selection(self, selection):
        self.dataframe[self.selection_column] = selection
        self.selector.set_selection(selection)
        self.hello = "sending callback"
        if self.selection_changed_callback is not None:
            self.selection_changed_callback(selection)
            self.hello = "callback sent"

    def update_display(self):
        self.selector.update_display()


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
        self.update_display()

    def update_display(self):
        self.canvas.draw_idle()

    def disconnect(self):
        self.lasso.disconnect_events()
        self.canvas.draw_idle()
