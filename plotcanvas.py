from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QSizePolicy, QVBoxLayout, QWidget, QAction
from matplotlib.figure import Figure
import numpy as np

class CustomNavigationToolbar(NavigationToolbar):
    def __init__(self, canvas, parent, coordinates=True):
        super().__init__(canvas, parent, coordinates)
        self.plot_locked = False
        self.add_custom_button()
        self.update_action_connections()

    def add_custom_button(self):
        self.lock_action = QAction('Lock Plot', self)
        self.lock_action.setCheckable(True)
        self.lock_action.setChecked(self.plot_locked)
        self.lock_action.triggered.connect(self.toggle_plot_lock)
        self.addAction(self.lock_action)

    def toggle_plot_lock(self):
        self.plot_locked = not self.plot_locked
        self.lock_action.setChecked(self.plot_locked)
        self.update_action_connections()

    def update_action_connections(self):
        # Disable or enable specific actions based on the lock state
        actions_to_toggle = ['Back', 'Forward', 'Pan', 'Zoom']
        for action in self.actions():
            if action.text() in actions_to_toggle:
                action.setEnabled(not self.plot_locked)

    def pan(self, *args):
        if self.plot_locked:
            return
        super().pan(*args)


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, use_subplots=False, nrows=1, ncols=1, add_toolbar=True):
        # Initialize the figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)  # Initialize the parent class (FigureCanvas)
        self.setParent(parent)  # Set the parent widget

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

        # Creating subplots based on the input
        if use_subplots:
            self.axes = self.fig.subplots(nrows=nrows, ncols=ncols)
        else:
            self.axes = np.array([self.fig.add_subplot(111)])

        # Flatten the axes array for uniform handling
        self.axes = np.atleast_1d(self.axes).flatten()

        if add_toolbar and parent:
            self.toolbar = CustomNavigationToolbar(self, parent)
            self.modify_toolbar()
        else:
            self.toolbar = None

        # Create a vertical layout to include the toolbar
        self.layout = QVBoxLayout()
        self.layout.addWidget(self)  # add canvas itself
        if self.toolbar:
            self.layout.addWidget(self.toolbar)

        self.initial_limits = {}
        self.axis_inversion_states = {i: {'x': False, 'y': False} for i in range(nrows*ncols)}
        self.initZoom()
        self.initHover()


    def store_initial_limits(self):
        """
        Store the initial limits for all axes to enable resetting to this state.
        """
        for ax in self.axes:
            self.initial_limits[ax] = (ax.get_xlim(), ax.get_ylim())


    def initZoom(self):
        self.fig.canvas.mpl_connect('scroll_event', self.zoom)


    def initHover(self):
        """
        Initialize hover functionality with text annotations for each subplot.
        """
        # Enable mouse motion events for the figure
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

        # Initialize annotations for each subplot
        self.text_annotations = {
            ax: ax.text(0, 0, "", va="bottom", ha="left", visible=False,
                        bbox=dict(boxstyle="round,pad=0.5", facecolor="yellow", alpha=0.5))
            for ax in self.axes
        }

    def plot(self, datax, datay, subplot_index=0, **kwargs):
        """
        Plot data on a specified subplot.
        """
        # Default to the first subplot if index is out of range
        ax = self.axes[subplot_index % len(self.axes)]

        line, = ax.plot(datax, datay, **kwargs)
        ax.figure.canvas.draw()
        # self.store_initial_limits()
        # Store line for hover functionality
        if hasattr(line, 'set_picker'):
            line.set_picker(5)  # 5 points tolerance

        return line
    

    def loglog(self, datax, datay, subplot_index=0, **kwargs):
        """
        Plot data on a specified subplot.
        """
        # Default to the first subplot if index is out of range
        ax = self.axes[subplot_index % len(self.axes)]

        line, = ax.loglog(datax, datay, **kwargs)
        ax.figure.canvas.draw()
        # self.store_initial_limits()
        # Store line for hover functionality
        if hasattr(line, 'set_picker'):
            line.set_picker(5)  # 5 points tolerance

        return line
    

    def highlight_y_region(self, ymin, ymax, subplot_index=0, color='yellow', alpha=0.3):
        """
        Highlights a horizontal region across the entire x-range of a subplot.

        Parameters:
        - ymin: The lower y-boundary of the region to highlight.
        - ymax: The upper y-boundary of the region to highlight.
        - subplot_index: Index of the subplot on which to apply the highlight. Defaults to 0.
        - color: The color of the highlighted region. Defaults to 'yellow'.
        - alpha: The transparency of the highlighted region. Defaults to 0.3.
        """
        # Validate subplot index
        if not self._validate_subplot_index(subplot_index):
            return  # Or handle the invalid index as appropriate

        ax = self.axes[subplot_index]
        ax.axhspan(ymin, ymax, color=color, alpha=alpha)

        self.draw_idle()  # Redraw the figure to update the view


    def add_vline(self, x, subplot_index=0, **kwargs):
        # Default to the first subplot if index is out of range
        ax = self.axes[subplot_index % len(self.axes)]

        ax.axvline(x=x, **kwargs)

    
    def add_hline(self, y, subplot_index=0, **kwargs):
        # Default to the first subplot if index is out of range
        ax = self.axes[subplot_index % len(self.axes)]

        ax.axhline(y=y, **kwargs)
    

    def clear_plot(self):
        """
        Clears the plot and optionally resets the axes to their initial state.
        """
        # Loop through all axes and clear each one
        for ax in self.axes:
            ax.clear()

        # Redraw the canvas to reflect the changes
        self.draw_idle()

        # Reinitialize
        self.initZoom()
        self.initHover()


    def set_plot_attributes(self, subplot_index=0, **attributes):
        """
        Dynamically sets various plot attributes for a specified subplot
        using keyword arguments.

        Parameters:
        - subplot_index: Index of the subplot to modify (default is 0).
        - **attributes: Arbitrary keyword arguments representing the attributes to set.
                        Keys should match the Matplotlib setter methods without the 'set_' prefix.
                        For example, to set the title, use title="My Plot".
        """
        # Ensure subplot_index is within the range of existing subplots
        if subplot_index >= len(self.axes):
            print(f"Invalid subplot_index: {subplot_index}. Must be less than {len(self.axes)}.")
            return

        ax = self.axes[subplot_index]

        for attr, value in attributes.items():
            # Construct the method name from the attribute key
            method_name = f'set_{attr}'
            # Check if the method exists for the subplot
            if hasattr(ax, method_name):
                # Get the method and call it with the value
                getattr(ax, method_name)(value)
            else:
                print(f"Attribute '{attr}' not recognized or not supported by this subplot.")

        # Redraw the canvas to reflect attribute changes
        self.draw_idle()


    def invert_axis(self, subplot_index=0, axis='y'):
        """
        Inverts the specified axis of a given subplot.

        Parameters:
        - subplot_index: Index of the subplot whose axis is to be inverted (default is 0).
        - axis: The axis to invert. 'y' for the y-axis, 'x' for the x-axis, and 'both' for both axes.
        """
        # Ensure subplot_index is within the range of existing subplots
        if not self._validate_subplot_index(subplot_index):
            return None  # Or handle the invalid index as appropriate

        ax = self.axes[subplot_index]
        if axis == 'y':
            ax.invert_yaxis()
            self.axis_inversion_states[subplot_index]['y'] = not self.axis_inversion_states[subplot_index]['y']
        elif axis == 'x':
            ax.invert_xaxis()
            self.axis_inversion_states[subplot_index]['x'] = not self.axis_inversion_states[subplot_index]['x']
        elif axis == 'both':
            ax.invert_yaxis()
            ax.invert_xaxis()
            self.axis_inversion_states[subplot_index]['y'] = not self.axis_inversion_states[subplot_index]['y']
            self.axis_inversion_states[subplot_index]['x'] = not self.axis_inversion_states[subplot_index]['x']
        else:
            print(f"Invalid axis: {axis}. Use 'x', 'y', or 'both'.")

        # Redraw the canvas to reflect the changes
        self.draw_idle()


    def set_axis_to_log(self, subplot_index=0, axis='both'):
        """
        Sets the specified axis (or axes) to logarithmic scale.

        :param axis: 'x' for the x-axis, 'y' for the y-axis, or 'both' for both axes.
        """
            # Ensure subplot_index is within the range of existing subplots
        if subplot_index >= len(self.axes):
            print(f"Invalid subplot_index: {subplot_index}. Must be less than {len(self.axes)}.")
            return

        ax = self.axes[subplot_index]
        if axis == 'x' or axis == 'both':
            ax.set_xscale('log')
        if axis == 'y' or axis == 'both':
            ax.set_yscale('log')

        self.draw()


    def set_aspect_ratio(self, aspect, subplot_index=0, adjustable='box', anchor='C'):
        """
        Sets the aspect ratio of the specified subplot.

        Parameters:
        - aspect: The aspect ratio, which could be a string or a number. A string must be one of 'auto', 'equal', or a number. If a number, it defines the ratio of y-unit to x-unit.
        - subplot_index: Index of the subplot to modify (default is 0).
        - adjustable: Determines which parameter will be adjusted to meet the required aspect. It can be either 'box', 'datalim', or 'box-forced'.
        - anchor: Determines the position of the axes. It can be 'C', 'SW', 'S', 'SE', 'E', 'NE', 'N', 'NW', and 'W'.
        """
        if not self._validate_subplot_index(subplot_index):
            return  # Or handle the invalid index as appropriate
        
        ax = self.axes[subplot_index]
        ax.set_aspect(aspect, adjustable=adjustable, anchor=anchor)
        self.fig.tight_layout()  # Optional: Adjust layout to prevent overlap
        self.draw_idle()  # Redraw the figure to update the view


    def set_subplot_title(self, title, subplot_index=0, **kwargs):
        # Set title for a specific subplot
        # Ensure subplot_index is within the range of created subplots
        ax = self.axes[subplot_index % len(self.axes)]
        ax.set_title(title, **kwargs)

    def set_suptitle(self, title, **kwargs):
            # Set an overall title (suptitle) for the figure
            self.figure.suptitle(title, **kwargs)
    
    def get_x_lim(self, subplot_index=0):
        """
        Returns the x-axis limits of the specified subplot.
        """
        if not self._validate_subplot_index(subplot_index):
            return None  # Or handle the invalid index as appropriate

        ax = self.axes[subplot_index]
        return ax.get_xlim()
    

    def get_y_lim(self, subplot_index=0):
        """
        Returns the y-axis limits of the specified subplot.
        """
        if not self._validate_subplot_index(subplot_index):
            return None  # Or handle the invalid index as appropriate

        ax = self.axes[subplot_index]
        return ax.get_ylim()


    def zoom(self, event):
        """
        Handles zooming in or out of the plot using the scroll wheel, affecting only the subplot under the cursor.
        """
        if self.toolbar.plot_locked:
            return  # Ignore zoom events when plot is locked
        ax = event.inaxes
        if ax is None:
            return  # Ignore scroll events outside the axes

        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        xdata, ydata = event.xdata, event.ydata
        if xdata is None or ydata is None:
            return  # Ignore if cursor is not over the axes

        # Define zoom sensitivity
        base_scale = 1.05

        # Perform zoom
        if event.button == 'up':  # Zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':  # Zoom out
            scale_factor = base_scale

        # Update axes limits for the subplot under the cursor
        ax.set_xlim([xdata - (xdata - xlim[0]) * scale_factor,
                     xdata + (xlim[1] - xdata) * scale_factor])
        ax.set_ylim([ydata - (ydata - ylim[0]) * scale_factor,
                     ydata + (ylim[1] - ydata) * scale_factor])

        self.draw_idle()  # Redraw the figure to update the view


    def hover(self, event):
        """
        Handle hover events, showing annotations on lines when hovered.
        """
        visible = False
        for ax in self.axes:
            if event.inaxes == ax:
                for line in ax.get_lines():
                    cont, ind = line.contains(event)
                    if cont:
                        annot = self.text_annotations[ax]
                        xdata, ydata = line.get_data()
                        ind = ind['ind'][0]
                        x, y = xdata[ind], ydata[ind]
                        self.update_annot(annot, x, y)
                        visible = True
                        break  # Stop checking after finding the hovered line
        if not visible:
            for annot in self.text_annotations.values():
                annot.set_visible(False)
        self.fig.canvas.draw_idle()


    def update_annot(self, annot, x, y):
        """
        Update annotation with new position and text.
        """
        annot.set_position((x, y))
        annot.set_text(f"({x:.3f}, {y:.3f})")
        annot.set_visible(True)


    def get_layout(self):
        """
        Returns the QVBoxLayout containing the canvas and optionally the toolbar.
        """
        return self.layout


    def modify_toolbar(self):
        """
        Find the 'Home' button and connect its triggered signal to a custom slot/method.
        """
        for action in self.toolbar.actions():
            if action.text() == 'Home':
                action.triggered.disconnect()
                action.triggered.connect(self.reset_view)
                break


    def reset_view(self):
        if self.toolbar.plot_locked:
            return  # Ignore reset view when plot is locked 
        for ax, (xlim, ylim) in self.initial_limits.items():
            subplot_index = self.axes.tolist().index(ax)  # Find the index of the current subplot
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
            # Reapply inversion state if necessary
            if self.axis_inversion_states[subplot_index]['y']:
                ax.invert_yaxis()
            if self.axis_inversion_states[subplot_index]['x']:
                ax.invert_xaxis()
        self.draw_idle()


    def _validate_subplot_index(self, subplot_index):
        """
        Validates the given subplot index is within the valid range.

        Parameters:
        - subplot_index: The index of the subplot to validate.

        Returns:
        - True if the index is valid, False otherwise.
        """
        if subplot_index < 0 or subplot_index >= len(self.axes):
            print(f"Invalid subplot_index: {subplot_index}. Must be in the range 0 to {len(self.axes)-1}.")
            return False
        return True