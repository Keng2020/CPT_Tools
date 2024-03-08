import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import os
import pandas as pd  # Assuming the data files are in CSV format
from shapely.geometry import Point, Polygon
from plotcanvas import PlotCanvas  # Import your PlotCanvas class here
from controlpanel import ControlPanel  # Import your ControlPanel class here

class CPTSubdivider(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Data Visualization and Selection Tool")
        self.setGeometry(100, 100, 800, 600)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)

        # Initialize Control Panel
        self.control_panel = ControlPanel(self)
        self.directory_button = self.control_panel.addButton('Choose Directory', self.open_directory_dialog)
        layout.addWidget(self.control_panel)

        # Initialize Plot Canvas
        self.plot_canvas = PlotCanvas(self, width=5, height=4, dpi=100)
        self.addToolBar(NavigationToolbar(self.plot_canvas, self))
        layout.addWidget(self.plot_canvas)

        # To store the polygon points drawn by the user
        self.polygon_points = []

        self.directory = []

        # Added: For real-time polygon drawing
        self.current_polygon, = self.plot_canvas.axes[0].plot([], [], 'r-', marker='o', lw=2)  # Prepare line object


        # Connect polygon draw action
        self.plot_canvas.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def open_directory_dialog(self):
        # """
        # Opens a dialog for the user to select a directory and plots data from the files in the directory.
        # """
        # self.directory = QFileDialog.getExistingDirectory(self, "Select Directory")

        self.directory = r"D:\MATLAB_DRIVE\MATLAB_PROJ\Clusters\Cluster 1083"
        self.plot_data_from_directory()

    def plot_data_from_directory(self):
        """
        Plots XY coordinates from files in the specified directory.
        """
        # Assuming files are CSVs with 'x' and 'y' columns
        for filename in os.listdir(self.directory):
            if filename.endswith('.csv'):
                file_path = os.path.join(self.directory, filename)
                self.data = pd.read_csv(file_path)
                self.plot_canvas.plot(self.data['nztmX'], self.data['nztmY'], marker='o')  # Plot each file's data

    def on_click(self, event):
        """
        Handles clicks on the plot canvas to draw or complete a polygon for selecting points.
        """
        if event.button == 3:  # Right-click to complete the polygon
            if len(self.polygon_points) > 2:  # Ensure the polygon can be formed
                self.polygon_points.append(self.polygon_points[0])  # Close the polygon
                self.update_polygon_plot()  # Update the polygon drawing
                self.process_polygon()  # Process the polygon (e.g., filter points)
                self.polygon_points = []  # Reset for the next polygon
                self.current_polygon.set_data([], [])  # Clear current polygon line
                self.plot_canvas.draw_idle()  # Redraw canvas
        else:
            # Left-click to add a point
            if event.xdata is not None and event.ydata is not None:  # Click was inside the axes
                self.polygon_points.append((event.xdata, event.ydata))
                self.update_polygon_plot()  # Update the polygon drawing with new point


    def update_polygon_plot(self):
        """
        Updates the current polygon plot with the vertices in `self.polygon_points`.
        """
        if self.polygon_points:
            x, y = zip(*self.polygon_points)
            self.current_polygon.set_data(x, y)
            self.plot_canvas.draw_idle()  # Redraw canvas
    

    def process_polygon(self):
        """
        Process the defined polygon to filter points within it, refreshing the plot each time.
        """
        # Convert the list of polygon points into a shapely Polygon object
        polygon = Polygon(self.polygon_points)

        # Assuming 'self.data' contains the DataFrame loaded with the data points
        # We'll add a column to the DataFrame indicating whether each point is within the polygon
        self.data['within_polygon'] = self.data.apply(lambda row: polygon.contains(Point(row['nztmX'], row['nztmY'])), axis=1)

        # Clear the previous plot  
        self.plot_canvas.clear_plot()

        # Plot all points with a default style
        self.plot_canvas.plot(self.data['nztmX'], self.data['nztmY'], marker='o', linestyle='None', color='blue')

        # Now, filter the DataFrame to only include points within the polygon
        filtered_data = self.data[self.data['within_polygon']]

        # Plot only the points within the polygon with a distinct style
        if not filtered_data.empty:
            self.plot_canvas.plot(filtered_data['nztmX'], filtered_data['nztmY'], marker='o', linestyle='None', color='green')

        # Optionally, refresh the canvas (if it's not automatically done in your plot method)
        self.plot_canvas.draw_idle()


            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = CPTSubdivider()
    main.show()
    sys.exit(app.exec_())
