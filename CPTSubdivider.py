import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import os
import pandas as pd  # Assuming the data files are in CSV format

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

        # Connect polygon draw action
        self.plot_canvas.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def open_directory_dialog(self):
        """
        Opens a dialog for the user to select a directory and plots data from the files in the directory.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.plot_data_from_directory(directory)

    def plot_data_from_directory(self, directory):
        """
        Plots XY coordinates from files in the specified directory.
        """
        # Assuming files are CSVs with 'x' and 'y' columns
        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                file_path = os.path.join(directory, filename)
                data = pd.read_csv(file_path)
                self.plot_canvas.plot(data['x'], data['y'], 'o')  # Plot each file's data

    def on_click(self, event):
        """
        Handles clicks on the plot canvas to draw a polygon for selecting points.
        """
        # Right click to end the polygon
        if event.button == 3:  # Right click
            self.polygon_points.append(self.polygon_points[0])  # Close the polygon
            self.plot_canvas.axes.plot(*zip(*self.polygon_points), marker='o', color='r')  # Draw the polygon
            self.plot_canvas.draw()
            
            # After drawing the polygon, you can filter points that lie within the polygon
            # This part requires further implementation

            self.polygon_points = []  # Reset for the next polygon
        else:
            # Left click to add a point
            if event.xdata is not None and event.ydata is not None:  # Click was inside the axes
                self.polygon_points.append((event.xdata, event.ydata))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = CPTSubdivider()
    main.show()
    sys.exit(app.exec_())
