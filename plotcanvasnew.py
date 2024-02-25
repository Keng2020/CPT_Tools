from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QSizePolicy, QVBoxLayout, QWidget
from matplotlib.figure import Figure
import numpy as np

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, use_subplots=False, nrows=1, ncols=1, add_toolbar=True):
        # Initialize the figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig) # Initialize the parent class (FigureCanvas)
        self.setParent(parent) # Set the parent widget

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

        if use_subplots:
            self.axes = self.fig.subplots(nrows=nrows, ncols=ncols)
        else:
            self.axes = self.fig.add_subplot(111)

        print(self.axes)

        # Ensure self.axes is always an array for consistency
        if not hasattr(self.axes, 'flatten'):
            self.axes = np.array([self.axes])

        self.toolbar = NavigationToolbar(self, parent) if add_toolbar and parent else None

        # Create a vertical layout to include the toolbar
        self.layout = QVBoxLayout()
        self.layout.addWidget(self) # add canvas itself
        if self.toolbar:
            self.layout.addWidget(self.toolbar)

        # Dictionary to cache subplot axes objects
        self._subplots_cache = {}
        self.initHover()

    
    def initHover(self):
        """
        Initialize text annotation for hover effect.
        Initializes a text annotation for each axes.
        """
        self.lines = []
        self.text_annotations = {ax: ax.text(0, 0, "", va="bottom", ha="left", visible=False,
                                             bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.5))
                                 for ax in np.atleast_1d(self.axes).flatten()}
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)


    def plot(self, datax, datay, subplot_index=None, **kwargs):
        ax = self._get_subplot_axes(subplot_index)
        
        line, = ax.plot(datax, datay, **kwargs)
        self.lines.append((ax, line))
        self.draw()
        return line # Return the line object for external use


    def _get_subplot_axes(self, subplot_spec):
        if subplot_spec and subplot_spec in self._subplots_cache:
            return self._subplots_cache[subplot_spec]
        elif subplot_spec:
            nrows, ncols, index = self._parse_subplot_spec(subplot_spec)
            ax = self.fig.add_subplot(nrows, ncols, index)
            self._subplots_cache[subplot_spec] = ax
            return ax
        else:
            return self.axes.flatten()[0]  # Default to the first subplot
    

    def _parse_subplot_spec(self, spec):
        assert 100 <= spec <= 999, "Subplot specification must me a three-digit number"
        nrows = spec // 100
        ncols = (spec // 10) % 10
        index = spec % 10

        return nrows, ncols, index
    

    def __call__(self, subplot_spec):
        """Enable calling the instance to get a subplot axes using the Matplotlib notation."""
        return self._get_subplot_axes(subplot_spec)
    

    def get_layout(self):
        """
        Returns the QVBoxLayout containing the canvas and optionally the toolbar.
        This method can be used to add the canvas and toolbar to the main application layout.
        """
        return self.layout
    

    def update_annot(self, annot, x, y):
        annot.set_text(f"({x:.3f}), ({y:.3f})")
        annot.set_position((x, y))
        annot.set_visible(True)


    # def hover(self, event):
    #     for ax, annot in self.text_annotations.items():
    #         if event.inaxes == ax:
    #             for ax_line, line in self.lines:
    #                 if ax_line is ax:  # Check if the line belongs to the current axis
    #                     cont, ind = line.contains(event)
    #                     if cont:
    #                         xdata, ydata = line.get_data()
    #                         x, y = xdata[ind['ind'][0]], ydata[ind['ind'][0]]
    #                         self.update_annot(annot, ax, x, y)
    #                         break
    #             else:  # No line contains the event
    #                 annot.set_visible(False)
    #             self.draw_idle()
    #             return  # Stop once the correct axes is found
            
    # def hover(self, event):
    #     # Updated to correctly identify hover events on all subplots and update annotations accordingly.
    #     annot_visible = False
    #     for ax, line in self.lines:
    #         if event.inaxes == ax:
    #             cont, ind = line.contains(event)
    #             if cont:
    #                 annot = self.text_annotations[ax]  # Get the correct annotation for this ax
    #                 x, y = line.get_data()
    #                 ind = ind["ind"][0]  # Assume single point
    #                 self.update_annot(annot, x[ind], y[ind])
    #                 annot_visible = True
    #                 break
    #     if not annot_visible:
    #         for annot in self.text_annotations.values():
    #             annot.set_visible(False)
    #     self.fig.canvas.draw_idle()
        
    # def hover(self, event):
    #     visible = False
    #     for ax, line in self.lines:
    #         print(ax)
    #         if event.inaxes == ax:  # Check if the event is in the current subplot
    #             cont, ind = line.contains(event)
    #             if cont:
    #                 print("yes")
    #                 annot = self.text_annotations[ax]  # Use the correct annotation for the subplot
    #                 xdata, ydata = line.get_data()
    #                 ind = ind["ind"][0]  # Get the index of the hovered point
    #                 x, y = xdata[ind], ydata[ind]
    #                 # Update the annotation for the hovered point
    #                 self.update_annot(annot, x, y)
    #                 visible = True
    #                 break  # Stop checking other lines once a match is found
    #     if not visible:
    #         # If no line is hovered, hide all annotations
    #         for annot in self.text_annotations.values():
    #             if annot.get_visible():
    #                 annot.set_visible(False)
    #     self.fig.canvas.draw_idle()


    def hover(self, event):
        visible = False
        for ax, line in self.lines:
            if event.inaxes == ax:
                cont, ind = line.contains(event)
                if cont:
                    annot = self.text_annotations[ax]
                    xdata, ydata = line.get_data()
                    ind = ind['ind'][0]
                    x, y = xdata[ind], ydata[ind]
                    self.update_annot(annot, x, y)
                    visible = True
                    break
        if not visible:
            for annot in self.text_annotations.values():
                annot.set_visible(False)
        self.fig.canvas.draw_idle()

    def hover(self, event):
        visible = False
        for ax, line in self.lines:
            if event.inaxes == ax:
                # Optionally, ensure lines have a picker threshold set.
                cont, ind = line.contains(event)
                if cont:
                    annot = self.text_annotations[ax]
                    xdata, ydata = line.get_data()
                    ind = ind['ind'][0]  # Assuming single point for simplicity.
                    x, y = xdata[ind], ydata[ind]
                    self.update_annot(annot, x, y)
                    visible = True
                    break  # Found the hovered line, no need to check others.
        # if not visible:
        #     for annot in self.text_annotations.values():
        #         annot.set_visible(False)
        self.fig.canvas.draw_idle()
