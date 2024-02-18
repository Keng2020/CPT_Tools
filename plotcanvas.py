from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backend_bases import MouseEvent
from scipy.spatial.distance import cdist
import numpy as np
import mplcursors

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

        self.hover_enabled = False  # Initially, hover is not enabled
        self.marker_data = []  # Initialize the marker_data attribute here


    def set_zoom_action(self, event_type, action):
        """
        Set a custom zoom action based on the event type and action ('zoom in' or 'zoom out')
        Also dynamically connects the event handler for the specified event type.
        :param event_type: String representing the matplotlib event name.
        :param action: 'zoom_in' or 'zoom_out'
        """
        self.zoom_actions[event_type] = action

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

        action = self.zoom_actions[event.name]

        zoom_in = action == 'zoom_in'

        self.zoom(event)

    def initialize_zoom(self):
        # # Initialize scroll event for zoom
        # self.fig.canvas.mpl_connect('scroll_event', self.zoom)
        pass
        

    def initialize_hover(self):
        """
        Initializes the hover functionality by creating an annotation for tooltips
        and connecting the motion_notify_event for hover detection.
        """
        self.annot = self.axes.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                                        bbox=dict(boxstyle="round", fc="w"),
                                        arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)


    def activate_hover(self):
        # Activate hover by connecting the event
        print("Activating hover...")
        if not self.hover_enabled:
            self.mpl_connect("motion_notify_event", self.hover)
            self.hover_enabled = True


    def initialize_dragging(self):
        """
        Initializes the dragging functionality by connecting the necessary events.
        """
        self.moving = False
        self.move_start_pos = None
        self.fig.canvas.mpl_connect('button_press_event', self.on_drag_start)
        self.fig.canvas.mpl_connect('button_release_event', self.on_drag_end)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_drag_move)


    def plot(self, data_x, data_y, line_style='-', **kwargs):
        """
        Plots data on the canvas. Automatically detects if markers are present in the line style.
        :param data_x: x data points
        :param data_y: y data points
        :param line_style: Style of the plot line, default is '-' (solid line). Can include marker styles.
        :param kwargs: Additional keyword arguments for the plot function.
        """
        has_markers = any(marker in line_style for marker in ('o', '+', '*', '.', 'x', 's', 'd', ',', '^', '<', '>', 'p', 'h', 'H', '1', '2', '3', '4', '|', '_'))
        if has_markers:
            for x, y in zip(data_x, data_y):
                self.marker_data.append((x, y))  # Assume simple case; extend as needed
        plot_ref = self.axes.plot(data_x, data_y, line_style, **kwargs)
        self.plotted_data.append({'data': (data_x, data_y), 'plot_ref': plot_ref, 'has_markers': has_markers})
        self.draw()

    def scatter(self, data_x, data_y, **kwargs):
        """
        Creates a scatter plot and stores its reference along with the data.
        :param data_x: x data points.
        :param data_y: y data points.
        :param kwargs: Additional keyword arguments for the scatter function.
        """
        plot_ref = self.axes.scatter(data_x, data_y, **kwargs)
        for x, y in zip(data_x, data_y):
            self.marker_data.append((x, y))  # Assume simple case; extend as needed
        self.plotted_data.append({'data': (data_x, data_y), 'plot_ref': plot_ref, 'has_markers': True})
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

    # def calculate_dynamic_threshold(self, data_x, data_y):
    #     # Ensure data_x and data_y are numpy arrays
    #     data_x = np.array(data_x)
    #     data_y = np.array(data_y)

    #     # Stack data_x and data_y for distance calculation
    #     points = np.vstack((data_x, data_y)).T

    #     # Calculate pairwise distances, only keep non-zero distances (to exclude self-distance)
    #     distances = cdist(points, points)
    #     distances = distances[distances != 0]

    #     # Calculate a suitable threshold based on the density or spread
    #     # For example, use the 10th percentile of non-zero distances as the threshold
    #     threshold = np.percentile(distances, 10) * 0.5  # Adjust multiplier as needed for sensitivity

    #     return threshold
    # def calculate_dynamic_threshold(self, data_x, data_y):
    #     # Ensure data_x and data_y are numpy arrays
    #     data_x = np.array(data_x)
    #     data_y = np.array(data_y)

    #     # Stack data_x and data_y for distance calculation
    #     points = np.vstack((data_x, data_y)).T

    #     # Calculate pairwise distances, only keep non-zero distances (to exclude self-distance)
    #     distances = cdist(points, points)
    #     distances = distances[np.triu_indices(distances.shape[0], k=1)]  # Exclude self-comparisons and duplicates

    #     # Check if distances array is empty
    #     if distances.size == 0:
    #         # Return a default threshold or handle as needed
    #         return 0.05  # Example default value, adjust based on your application's scale

    #     # Calculate a suitable threshold based on the density or spread
    #     threshold = np.percentile(distances, 10) * 0.5  # Adjust multiplier as needed for sensitivity

    #     return threshold
    def calculate_dynamic_threshold(self):
        # If there are no points, return a default threshold
        if not self.marker_data:
            return 0.05  # Adjust this default value as needed
        
        # Get the current axes limits to understand the zoom level
        x_lim = self.axes.get_xlim()
        y_lim = self.axes.get_ylim()
        axis_area = (x_lim[1] - x_lim[0]) * (y_lim[1] - y_lim[0])

        # Calculate the area covered by each point, assuming uniform distribution
        total_points = len(self.marker_data)
        area_per_point = axis_area / total_points if total_points else axis_area

        # Base threshold on the square root of the area per point, providing a measure of average distance between points
        # Adjust the multiplier as needed to fine-tune sensitivity
        base_threshold = np.sqrt(area_per_point) * 0.1

        # Ensure the threshold is within reasonable bounds (min and max values)
        min_threshold, max_threshold = 0.01, 0.1  # These bounds can be adjusted
        threshold = np.clip(base_threshold, min_threshold, max_threshold)

        return threshold


    # def hover(self, event):
    #     """
    #     Handles mouse movement events to display annotations for points with markers.
    #     :param event: MouseEvent instance.
    #     """
    #     vis = self.annot.get_visible()
    #     if event.inaxes == self.axes:
    #         found_point = False
    #         for plot in self.plotted_data:
    #             xdata, ydata = plot['data']
    #             if plot['has_markers']:
    #                 # Implement logic to detect proximity to points with markers
    #                 # This is a simplified example. A more comprehensive approach might be needed.
    #                 distances = np.sqrt((xdata - event.xdata)**2 + (ydata - event.ydata)**2)
    #                 closest_index = np.argmin(distances)
    #                 threshold = 0.05
    #                 if distances[closest_index] < threshold:  # Define a suitable threshold
    #                     self.update_annot(closest_index, xdata[closest_index], ydata[closest_index])
    #                     found_point = True
    #                     break
    #         if found_point:
    #             self.annot.set_visible(True)
    #             self.fig.canvas.draw_idle()
    #         else:
    #             if vis:
    #                 self.annot.set_visible(False)
    #                 self.fig.canvas.draw_idle()
    # def hover(self, event):
    #     """
    #     Handles mouse movement events to display annotations for points with markers.
    #     :param event: MouseEvent instance.
    #     """
    #     vis = self.annot.get_visible()
    #     if event.inaxes == self.axes:
    #         found_point = False
    #         for plot in self.plotted_data:
    #             xdata, ydata = plot['data']
    #             if plot['has_markers']:
    #                 # Normalize distances if x,y values are large
    #                 x_range = self.axes.get_xlim()[1] - self.axes.get_xlim()[0]
    #                 y_range = self.axes.get_ylim()[1] - self.axes.get_ylim()[0]

    #                 if len(xdata) == 1:  # If there's only one point
    #                     distances = np.sqrt(((xdata - event.xdata) / x_range) ** 2 + ((ydata - event.ydata) / y_range) ** 2)
    #                     closest_index = 0  # Only one point to check
    #                 else:
    #                     # Normalize distances
    #                     normalized_xdata = (xdata - event.xdata) / x_range
    #                     normalized_ydata = (ydata - event.ydata) / y_range
    #                     distances = np.sqrt(normalized_xdata**2 + normalized_ydata**2)
    #                     closest_index = np.argmin(distances)

    #                 # Adjust the threshold based on the scale of the plot
    #                 threshold = self.calculate_dynamic_threshold(xdata, ydata) / max(x_range, y_range)
                    
    #                 if distances[closest_index] < threshold:  # Check against adjusted threshold
    #                     self.update_annot(closest_index, xdata[closest_index], ydata[closest_index])
    #                     found_point = True
    #                     break
    #         if found_point:
    #             self.annot.set_visible(True)
    #             self.fig.canvas.draw_idle()
    #         else:
    #             if vis:
    #                 self.annot.set_visible(False)
    #                 self.fig.canvas.draw_idle()

    # def hover(self, event):
    #     if not self.hover_enabled:
    #         return  # Do nothing if hover is not enabled
    #     # Simplify hover logic by using self.marker_data
    #     if event.inaxes == self.axes:
    #         found_point = False
    #         x_range = self.axes.get_xlim()[1] - self.axes.get_xlim()[0]
    #         y_range = self.axes.get_ylim()[1] - self.axes.get_ylim()[0]

    #         for x, y in self.marker_data:
    #             distance = np.sqrt(((x - event.xdata) / x_range) ** 2 + ((y - event.ydata) / y_range) ** 2)
    #             threshold = self.calculate_dynamic_threshold([x], [y]) / max(x_range, y_range)
    #             if distance < threshold:
    #                 self.update_annot(0, x, y)  # Index 0 used as a placeholder
    #                 found_point = True
    #                 break

    #         if found_point:
    #             self.annot.set_visible(True)
    #             self.fig.canvas.draw_idle()
    #         else:
    #             self.annot.set_visible(False)
    #             self.fig.canvas.draw_idle()
    def hover(self, event):
        if not self.hover_enabled or event.inaxes != self.axes:
            return

        found_point = False
        for x, y in self.marker_data:
            distance = np.sqrt((x - event.xdata) ** 2 + (y - event.ydata) ** 2)
            threshold = 0.05  # Static threshold for testing
            if distance < threshold:
                self.update_annot(0, x, y)  # Using 0 as a placeholder
                found_point = True
                break

        if found_point:
            self.annot.set_visible(True)
            self.fig.canvas.draw_idle()
        else:
            self.annot.set_visible(False)
            self.fig.canvas.draw_idle()


    def zoom(self, event):
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