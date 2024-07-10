def scatterplot(df, x: str = "x", y: str = "y", selection: str = "selection"):
    sp = ScatterPlot(df, x, y, selection)
    sp.widget.scatterplot = sp
    return sp.widget


class ScatterPlot():
    def __init__(self, df, x, y, selection):
        import matplotlib.pyplot as plt
        import numpy as np
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
        # np.random.random((2, 100))

        # print("B")
        # ensure we are interactive mode
        plt.ion()

        # subplot_kw = dict(xlim=(0, 1), ylim=(0, 1), autoscale_on=False)
        # fig, ax = plt.subplots(subplot_kw=subplot_kw)

        fig = plt.figure()
        ax = fig.gca()
        pts = ax.scatter(self.data[0], self.data[1])

        # prevent immediate display of the canvas
        manager = Gcf.get_active()
        Gcf.figs.pop(manager.num, None)

        self.selector = Selector(fig, ax, pts, callback=self.set_selection)

        self.widget = fig.canvas

    def set_data(self, df, x, y):
        self.data = np.asarray((df[x], df[y]))

    def set_selection(self, selection):
        self.dataframe[self.selection_column] = selection
        self.selector.set_selection(selection)


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
        import numpy as np
        self.path = Path(verts)
        selection = self.path.contains_points(self.xys)
        self.callback(selection)

    def set_selection(self, selection):
        import numpy as np
        self.ind = np.nonzero(selection)
        self.fc[:, -1] = self.alpha_other
        self.fc[self.ind, -1] = 1
        self.collection.set_facecolors(self.fc)
        self.canvas.draw_idle()

    def disconnect(self):
        self.lasso.disconnect_events()
        self.canvas.draw_idle()
