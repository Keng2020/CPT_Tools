from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
        
        self.axes.set_title('Sample Plot') 
        self.axes.set_xlabel('X Axis')
        self.axes.set_ylabel('Y Axis')

    def plot(self, data_x, data_y, plot_type='line'):
        """
        Plots data on the canvas.
        
        :param data_x: A list or array of x values.
        :param data_y: A list or array of y values.
        :param plot_type: The type of plot to display ('line' or 'scatter'). Default is 'line'.
        """
        if plot_type == 'line':
            self.axes.plot(data_x, data_y)
        elif plot_type == 'scatter':
            self.axes.scatter(data_x, data_y)
        self.draw()

    def clear_plot(self):
        """
        Clears the current plot.
        
        This method removes all data from the plot, but keeps the plot titles and axis labels.
        """
        self.axes.clear()
        self.axes.set_title('Sample Plot')
        self.axes.set_xlabel('X Axis')
        self.axes.set_ylabel('Y Axis')
        self.draw()

    def update_plot(self, data_x, data_y, plot_type='line'):
        """
        Updates the plot with new data.
        
        This method clears the current plot and then creates a new plot with the provided data.
        
        :param data_x: A list or array of x values.
        :param data_y: A list or array of y values.
        :param plot_type: The type of plot to display ('line' or 'scatter'). Default is 'line'.
        """
        self.clear_plot()
        self.plot(data_x, data_y, plot_type)
