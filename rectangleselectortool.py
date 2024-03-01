from matplotlib.widgets import RectangleSelector

class RectangleSelectorTool:
    def __init__(self, ax, on_select_callback, button_press_callback=None, button_release_callback=None, drawtype='box', useblit=True, button=[1], minspanx=5, minspany=5, spancoords='pixels', interactive=True):
        self.ax = ax
        self.on_select_callback = on_select_callback
        self.button_press_callback = button_press_callback
        self.button_release_callback = button_release_callback
        self.rect_selector = RectangleSelector(ax, self.on_select,
                                               drawtype=drawtype,
                                               useblit=useblit,
                                               button=button,
                                               minspanx=minspanx,
                                               minspany=minspany,
                                               spancoords=spancoords,
                                               interactive=interactive)
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_button_release)

    def on_select(self, eclick, erelease):
        if self.on_select_callback:
            self.on_select_callback(eclick, erelease)

    def on_button_press(self, event):
        if self.button_press_callback:
            self.button_press_callback(event)

    def on_button_release(self, event):
        if self.button_release_callback:
            self.button_release_callback(event)

    def set_active(self, active):
        self.rect_selector.set_active(active)
