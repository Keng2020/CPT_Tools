from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backend_bases import MouseEvent
import numpy as np

class PlotCanvas(FigureCanvas):
    """
    A canvas that displays a matplotlib plot within a PyQt5 application.
    
    This class extends FigureCanvas, making it possible to embed a matplotlib
    figure in a PyQt5 widget. It is designed to be flexible, allowing for
    different types of plots to be displayed and updated as needed.
    """
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """
        Initializes a PlotCanvas instance.
        
        :param parent: The parent QWidget to which this PlotCanvas belongs. Default is None.
        :param width: The width of the canvas. Default is 5.
        :param height: The height of the canvas. Default is 4.
        :param dpi: The resolution of the canvas in dots per inch. Default is 100.
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

        self.initialize_zoom()
        self.initialize_hover()
        self.initialize_dragging()

        self.zoom_actions = {} # Store zoom actions and their sensitivities
        self.event_connections = {} # Keep track of connection events and their ids

        # Initialize scale factors with a default value
        self.zoom_sensitivity_x = 1.1
        self.zoom_sensitivity_y = 1.1

        self.plotted_data = [] 

    
    def set_zoom_action(self, event_type, action, sensitivity_x=None, sensitivity_y=None):
        """
        Set a custom zoom action based on the event type and action ('zoom in' or 'zoom out')
        Also dynamically connects the event handler for the specified event type.
        :param event_type: String representing the matplotlib event name.
        :param action: 'zoom_in' or 'zoom_out'
        :param sensitivity_x: Sensitivity for horizontal zooming. Defaults to 'self.default_sensitivity' if None
        :param sensitivity_y: Sensitivity for vertical zooming. Same default as 'sensitivity_x'
        """
        if sensitivity_x is None:
            sensitivity_x = self.default_zoom_sensitivity
        if sensitivity_y is None:
            sensitivity_y = self.default_zoom_sensitivity
        
        self.zoom_actions[event_type] = (action, sensitivity_x, sensitivity_y)

        # If the event is already connected, no need to reconenct it.
        if event_type in self.event_connections:
            return
        
        # Connect he event and store its conenction id
        cid = self.fig.canvas.mpl_connect(event_type, self.handle_zoom_event)
        self.event_connections[event_type] = cid

    
    def handle_zoom_event(self, event):
        """
        Handles zoom events according to the user defined actions and sensitivities. 
        """
        if event.name not in self.zoom_actions:
            return

        action, sensitivity_x, sensitivity_y = self.zoom_actions[event.name]

        zoom_in = action == 'zoom_in'

        # Use event details to determine zoom direction and apply sensitivity
        # Placeholder: Implement logic for zoom direction from event
        scale_factor_x = sensitivity_x if zoom_in else 1 / sensitivity_x
        scale_factor_y = sensitivity_y if zoom_in else 1 / sensitivity_y

        self.zoom(event, scale_factor_x, scale_factor_y)

    def initialize_zoom(self):
        # Initialize scroll event for zoom
        self.fig.canvas.mpl_connect('scroll_event', self.zoom)
        

    def initialize_hover(self):
        """
        Initializes the hover functionality by creating an annotation for tooltips
        and connecting the motion_notify_event for hover detection.
        """
        self.annot = self.axes.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                                        bbox=dict(boxstyle="round", fc="w"),
                                        arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)

        # Connect the hover event
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

        # Ensure the canvas is ready and updated
        self.draw()


    def initialize_dragging(self):
        """
        Initializes the dragging functionality by connecting the necessary events.
        """
        self.moving = False
        self.move_start_pos = None
        self.fig.canvas.mpl_connect('button_press_event', self.on_drag_start)
        self.fig.canvas.mpl_connect('button_release_event', self.on_drag_end)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag_move)


    def plot(self, data_x, data_y, plot_type='line', **kwargs):
        # Modify this method to track plotted data
        if plot_type == 'line':
            plot_ref = self.axes.plot(data_x, data_y, **kwargs)
        elif plot_type == 'scatter':
            # For scatter, store the collection returned by scatter() for hover detection
            plot_ref = self.axes.scatter(data_x, data_y, **kwargs)
        else:
            raise ValueError(f"Unsupported plot type: {plot_type}")
        
        self.plotted_data.append((plot_type, plot_ref, (data_x, data_y)))
        self.draw()


    def clear_plot(self):
        """
        Clears the current plot.

        This method removes all data and graphical elements from the plot, including any interactive annotations. 
        It also resets the `self.plotted_data` list to ensure that new plots start with a clean state.
        """
        # Clear the axes for a fresh start
        self.axes.clear()
        self.initialize_zoom()
        self.initialize_hover()
        self.initialize_dragging()
        # Clear any stored data references
        self.plotted_data = []


    def update_plot(self, data_series, plot_styles=None):
        """
        Updates the plot with new data series.
        
        :param data_series: A list of tuples, each containing x and y data arrays.
        :param plot_styles: A list of dictionaries, each containing style options for the corresponding data series.
        """
        self.clear_plot()
        if plot_styles is None:
            plot_styles = [{}] * len(data_series)  # Default empty style dicts if none provided
        
        for data, style in zip(data_series, plot_styles):
            self.plot_data(data[0], data[1], **style)


    def highlight_points(self, points, **kwargs):
        """
        Highlights specific points on the plot.
        
        :param points: A list of tuples, each containing the x and y coordinates of a point.
        :param kwargs: style options for highlighting (color, marker, markersize, etc.)
        """
        for x, y in points:
            self.axes.plot(x, y, **kwargs)
        self.draw()


    def set_plot_attributes(self, title="", xlabel="", ylabel="", xticks=None, yticks=None, grid=True, **kwargs):
        """
        Sets various attributes of the plot.
        """
        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        if xticks is not None:
            self.axes.set_xticks(xticks)
        if yticks is not None:
            self.axes.set_yticks(yticks)
        self.axes.grid(grid, **kwargs)
        self.draw()


    def adjust_plot_view(self, equal_aspect=False, tick_interval=10, adjust_limits=True, margin=10.1):
        """
        Adjusts the plot view with specified configurations.
        
        :param equal_aspect: If True, sets the plot to have an equal aspect ratio.
        :param tick_interval: The interval between major ticks on both axes.
        :param adjust_limits: If True, adjusts the axis limits based on the data range and specified margin.
        :param margin: The margin to add to the axis limits when adjust_limits is True.
        """
        if adjust_limits:
            x_limits = self.axes.get_xlim()
            y_limits = self.axes.get_ylim()
            # Expanding the limits by the specified margin
            self.axes.set_xlim([x_limits[0] - margin, x_limits[1] + margin])
            self.axes.set_ylim([y_limits[0] - margin, y_limits[1] + margin])
        
        # Setting tick intervals
        if tick_interval:
            x_ticks = np.arange(round(self.axes.get_xlim()[0]), round(self.axes.get_xlim()[1]) + tick_interval, tick_interval)
            y_ticks = np.arange(round(self.axes.get_ylim()[0]), round(self.axes.get_ylim()[1]) + tick_interval, tick_interval)
            self.axes.set_xticks(x_ticks)
            self.axes.set_yticks(y_ticks)
        
        # Setting equal aspect ratio if required
        if equal_aspect:
            self.axes.axis('equal')
        
        self.draw()


    def update_annot(self, ind, x, y):
        # Update the annotation text and position
        self.annot.xy = (x, y)
        text = f"{x:.2f}, {y:.2f}"
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.4)


    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.axes:
            found_point = False
            for plot_type, plot_ref, data in self.plotted_data:
                xdata, ydata = data
                if plot_type == 'scatter':
                    # Use the correct scatter object reference for contains()
                    # This ensures hover functionality works after clearing and re-plotting
                    cont, ind = plot_ref.contains(event)
                    if cont:
                        self.update_annot(ind["ind"][0], xdata[ind["ind"][0]], ydata[ind["ind"][0]])
                        found_point = True
                        break
                else:  
                    # Placeholder for future implementation for other plot types
                    pass

            if found_point:
                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()

    def zoom(self, event, scale_factor_x, scale_factor_y):
        """
        Zoom in or out of the plot using separate scale factors for x and y directions.

        :param event: The event that triggered the zoom.
        :param scale_factor_x: Scale factor for horizontal zooming.
        :param scale_factor_y: Scale factor for vertical zooming.
        """
        if not event.inaxes:
            return

        # Determine scale factors based on event direction
        scale_factor_x = self.zoom_sensitivity_x if event.button == 'up' else 1 / self.zoom_sensitivity_x
        scale_factor_y = self.zoom_sensitivity_y if event.button == 'up' else 1 / self.zoom_sensitivity_y

        xdata, ydata = event.xdata, event.ydata  # Current mouse position

        # Adjust axis limits
        cur_xlim = self.axes.get_xlim()
        cur_ylim = self.axes.get_ylim()

        # Calculate new limits
        self.axes.set_xlim([xdata - (xdata - cur_xlim[0]) * scale_factor_x,
                            xdata + (cur_xlim[1] - xdata) * scale_factor_x])
        self.axes.set_ylim([ydata - (ydata - cur_ylim[0]) * scale_factor_y,
                            ydata + (cur_ylim[1] - ydata) * scale_factor_y])

        self.draw()

    def set_zoom_sensitivity_x(self, zoom_sensitivity_x):
        """
        Sets the scale factor for zooming in the x direction.
        
        :param scale_factor_x: The new scale factor for x direction.
        """
        self.zoom_sensitivity_x = zoom_sensitivity_x

    def set_zoom_sensitivity_y(self, zoom_sensitivity_y):
        """
        Sets the scale factor for zooming in the y direction.
        
        :param scale_factor_y: The new scale factor for y direction.
        """
        self.zoom_sensitivity_y = zoom_sensitivity_y
    
    def on_drag_start(self, event):
        """
        Handles the beginning of a drag operation.
        """
        if event.button == 1:  # Left mouse button
            self.moving = True
            self.move_start_pos = (event.xdata, event.ydata)

    def on_drag_end(self, event):
        """
        Handles the end of a drag operation.
        """
        self.moving = False
        self.move_start_pos = None

    def on_drag_move(self, event):
        """
        Handles the movement of the mouse during a drag operation.
        """
        if self.moving and self.move_start_pos is not None and event.xdata is not None and event.ydata is not None:
            dx = event.xdata - self.move_start_pos[0]
            dy = event.ydata - self.move_start_pos[1]
            cur_xlim = self.axes.get_xlim()
            cur_ylim = self.axes.get_ylim()
            self.axes.set_xlim(cur_xlim[0] - dx, cur_xlim[1] - dx)
            self.axes.set_ylim(cur_ylim[0] - dy, cur_ylim[1] - dy)

            self.move_start_pos = (event.xdata, event.ydata)
            self.draw()