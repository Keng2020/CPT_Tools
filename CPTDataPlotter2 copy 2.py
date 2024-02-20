import os
import sys
import pickle
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.spatial import Delaunay, Voronoi, voronoi_plot_2d
from scipy.io import savemat
import pandas as pd

from PyQt5.QtWidgets import (QApplication, QMainWindow, QGridLayout, QVBoxLayout, 
                             QWidget, QPushButton, QLabel, QComboBox, QHBoxLayout, 
                             QSlider, QFileDialog, QLineEdit, QShortcut, QMessageBox, 
                             QStatusBar, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm
import matplotlib.widgets as widgets
from matplotlib.patches import Polygon
from plotcanvas import PlotCanvas
from controlpanel import ControlPanel
from spatial_analysis_utils import *

class CPTDataPlotter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.init_param()
        self.setup_layout()
        self.setup_shortcuts()
        

    def init_param(self):
        self.file_colors = {}
        # Interaction variables
        self.current_xlim = None # x lim for main plot
        self.current_ylim = None # y lim for main plot
        self.rect_selector = None # rectangle selector for clear/recover data
        self.dragging = False 
        self.selecting = False
        self.drag_button = 3  # Right-click for dragging
        self.select_button = 1  # Left-click for selecting
        self.limits_locked = True
        self.current_plot_index = -1 # index for main plot
        self.current_plot_index_loc = -1 # index for loc plot
    
    def setup_layout(self):
        main_grid_layout = QGridLayout(self.main_widget)

        # Create control panel instances for each setion
        self.left_control_panel = ControlPanel(self)
        self.middle_control_panel = ControlPanel(self)
        self.right_control_panel = ControlPanel(self)

        # Add control panel instances to the layout 
        main_grid_layout.addWidget(self.left_control_panel, 0, 0)
        main_grid_layout.addWidget(self.middle_control_panel, 0, 1)
        main_grid_layout.addWidget(self.right_control_panel, 0, 2)

        main_grid_layout.setColumnStretch(0, 1)
        main_grid_layout.setColumnStretch(1, 2)
        main_grid_layout.setColumnStretch(2, 2)

        self.populate_left_panel()
        self.populate_middle_panel()
        self.populate_right_panel()

    
    def populate_left_panel(self):
        # Zoom setting
        self.scale_factor = 10 # scale the parameter of tick into int
        min_value = int(0.5 * self.scale_factor)  # 5
        max_value = int(1.5 * self.scale_factor)  # 15
        initial_value = int(1 * self.scale_factor)  # 10
        tick_interval = int(0.1 * self.scale_factor)  # 1

        # Add controls to the left panel
        self.left_control_panel.addButton("Choose Project Path", self.choose_project_path)
        widgets = self.left_control_panel.addFlexibleRow([
            ('combo', 'Select Cluster', ["Please Choose Project Path first"]),
            ('button', 'Submit', self.select_cluster)
        ])
        self.left_control_panel.addFlexibleRow([
            ('button', 'Previous plot', self.show_previous_plot),
            ('button', 'Next plot', self.show_next_plot)
        ])
        widgets_sliders = self.left_control_panel.addFlexibleRow([
            ('slider', 'zoom_sensitivity_x', Qt.Horizontal, min_value, max_value, initial_value, tick_interval, self.on_zoom_sensitivity_x_changed),
            ('slider', 'zoom_sensitivity_y', Qt.Horizontal, min_value, max_value, initial_value, tick_interval, self.on_zoom_sensitivity_y_changed)
        ])
        widgets_temp = self.left_control_panel.addFlexibleRow([
            ('button', 'Lock/Unlock xy lim', self.toggle_plot_limits),
            ('button', 'Reset plot limit', self.reset_view)
        ])
        self.left_control_panel.addFlexibleRow([
        ('button', 'Select region to clear data', lambda: self.enable_rectangle_selector('clear')),
        ('button', 'Select region to recover data', lambda: self.enable_rectangle_selector('recover'))
        ])
        
        self.lock_lim_button = widgets_temp.get('button_Lock/Unlock xy lim')
        self.left_control_panel.setup_color_toggle_button(
            self.lock_lim_button, 
            color1=(0, 255, 0),  # Green
            color2=(255, 0, 0),  # Red
            transparency=25  # 10% opacity
        )
        self.cluster_combobox = widgets.get('combo_Select Cluster')


        self.slider_zoom_sensitivity_x = widgets_sliders.get('slider_zoom_sensitivity_x')
        self.slider_zoom_sensitivity_y = widgets_sliders.get('slider_zoom_sensitivity_y')
        labels = {1: 'Min', 10: 'Default', 20: 'Max'}
        # self.left_control_panel.set_tick_labels(self.slider_zoom_sensitivity_x, labels, QSlider.TicksBelow)
        # self.left_control_panel.set_tick_labels(self.slider_zoom_sensitivity_y, labels, QSlider.TicksBelow)

        self.loc_plot_canvas = PlotCanvas()
        self.loc_plot_canvas.set_zoom_action(event_type='scroll_event', action='zoom')
        self.left_control_panel.addWidget(self.loc_plot_canvas) 

    def enable_rectangle_selector(self, action):
        if self.rect_selector is not None:
            self.rect_selector.set_active(False)  # Disable any existing selector

        # Determine the callback function based on the action
        callback = self.onselect_clear if action == 'clear' else self.onselect_recover

        # Create a new rectangle selector on the main plot canvas
        self.rect_selector = widgets.RectangleSelector(
            self.main_plot_canvas.axes, 
            callback,
            useblit=True,
            button=[self.select_button],  # Left mouse button
            minspanx=5, minspany=5, spancoords='pixels',
            interactive=True)
        
    def onselect_clear(self, eclick, erelease):
        """Callback for clearing data in the selected region."""
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        self.process_selected_region(x1, y1, x2, y2, action='clear')

    def onselect_recover(self, eclick, erelease):
        """Callback for recovering data in the selected region."""
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        self.process_selected_region(x1, y1, x2, y2, action='recover')

    def process_selected_region(self, x1, y1, x2, y2, action):
        # Convert the plot coordinates to data indices
        depth_range = [min(y1, y2), max(y1, y2)]
        qt_range = [min(x1, x2), max(x1, x2)]

        # Identify the data within the selected region
        within_region = (self.integrated_data_ori['Depth (m)'] >= depth_range[0]) & \
                        (self.integrated_data_ori['Depth (m)'] <= depth_range[1]) & \
                        (self.integrated_data_ori[self.file_name_list[self.current_plot_index]] >= qt_range[0]) & \
                        (self.integrated_data_ori[self.file_name_list[self.current_plot_index]] <= qt_range[1])

        # Get current xlim and ylim to preserve the view
        current_xlim = self.main_plot_canvas.axes.get_xlim()
        current_ylim = self.main_plot_canvas.axes.get_ylim()

        if action == 'clear':
            # Clear data by setting it to NaN
            self.integrated_data_plot.loc[within_region, self.file_name_list[self.current_plot_index]] = np.nan
        elif action == 'recover':
            # Recover data by copying from the original dataset
            self.integrated_data_plot.loc[within_region, self.file_name_list[self.current_plot_index]] = \
                self.integrated_data_ori.loc[within_region, self.file_name_list[self.current_plot_index]]

        # Redraw the plot to reflect the changes
        self.show_main_plot(self.current_plot_index)

    def populate_middle_panel(self):
        self.main_plot_canvas = PlotCanvas(self, width=5, height=4, dpi=100)
        self.main_plot_canvas.set_zoom_action(event_type='scroll_event', action='zoom')
        self.middle_control_panel.addWidget(self.main_plot_canvas)


    def populate_right_panel(self):
        self.export_plot_canvas = PlotCanvas()
        self.export_plot_canvas.set_zoom_action(event_type='scroll', action='zoom')
        self.right_control_panel.addWidget(self.export_plot_canvas)
    

    def setup_shortcuts(self):
        # Connect key press events to methods
        self.shortcut_previous = QShortcut(Qt.Key_Minus, self)
        self.shortcut_previous.activated.connect(self.show_previous_plot)

        self.shortcut_next = QShortcut(Qt.Key_Equal, self)
        self.shortcut_next.activated.connect(self.show_next_plot)

    
    def choose_project_path(self):
        project_path = QFileDialog.getExistingDirectory(self, "Select Directory")

        self.cluster_combobox.clear()

        # Check if a path was chosen (dialog not canceled)        
        if project_path:
            try:
                # List directories that match the criteria
                clusters = [d for d in os.listdir(project_path) if os.path.isdir(os.path.join(project_path, d)) and d.startswith('Cluster ')]

                # Add the found clusters to the combo box
                if clusters:
                    self.cluster_combobox.addItems(clusters)
                else:
                    QMessageBox.information(self, "No Clusters Found", "No cluster directories found in the selected path.")
            except Exception as e:
                # Handle errors during directory listing
                QMessageBox.critical(self, "Error", f"Failed to list directories: {e}")
        else:
            # Optionally inform the user that no directory was selected if desired
            QMessageBox.warning(self, "No Directory Selected", "No directory was selected.")
        # Update project_path attribute only if a valid path was chosen
        self.project_path = project_path if project_path else ""


    def select_cluster(self):
        self.cluster_name = self.cluster_combobox.currentText()
        self.process_cpt_locations()
        self.process_cpt_data()
        # Enable the hover func of plot only after the Cluster is selected
        self.loc_plot_canvas.activate_hover()
        self.main_plot_canvas.activate_hover()
        self.export_plot_canvas.activate_hover()
        

    def process_cpt_locations(self):
        cluster_file_path = os.path.join(self.project_path, self.cluster_name, f"{self.cluster_name}.csv")
        if not os.path.exists(cluster_file_path):
            QMessageBox.warning(self, "File Not Found", f"Cluster file not found: {cluster_file_path}")
            return
        
        cluster_data = pd.read_csv(cluster_file_path)
        self.nztm_data_dict = self.create_nztm_data_dict(cluster_data)
        self.update_file_lists()
        self.closest_file_ids_dict = self.create_closest_file_ids_dict()

    
    def create_nztm_data_dict(self, cluster_data):
        nztm_data_dict = {}
        for _, row in cluster_data.iterrows():
            # file_id = f"{row['ID']}.csv"  # Append ".csv" to each file_id
            file_id = row['ID']
            # Store nztmX and nztmY as a nested dictionary
            nztm_data_dict[file_id] = {'nztmX': row['nztmX'], 'nztmY': row['nztmY']}

        return nztm_data_dict
    
    
    def update_file_lists(self):
        file_ids, nztmX_values, nztmY_values = self.extract_nztm_data()
        p1, p2, _ = ranking_pairwise_distances(nztmX_values, nztmY_values)
        index_sort = get_unique_set(np.vstack((p1, p2)).T)
        self.file_name_list = [file_ids[i] for i in index_sort]
        self.file_name_list = [file.replace('.csv', '') for file in self.file_name_list]
        self.nztmX_list, self.nztmY_list = self.extract_nztm_for_file_ids(self.file_name_list)


    def create_closest_file_ids_dict(self):
        # Initialize dictionary to store closest file IDs for each file ID
        closest_file_ids_dict = {}
        
        file_ids, nztmX_values, nztmY_values = self.extract_nztm_data()

        # Iterate through each file ID
        for file_id in file_ids:
            # Find 5 closest file IDs
            closest_file_ids = find_closest_file_ids(file_id, file_ids, nztmX_values, nztmY_values, num_closest=5)
            # Store the result in the dictionary
            closest_file_ids_dict[file_id] = closest_file_ids
    
        return closest_file_ids_dict


    def process_cpt_data(self):
        cluster_path = os.path.join(self.project_path, self.cluster_name, 'Extracted')
        if os.path.exists(cluster_path):
            self.data_ori = [(file, pd.read_csv(os.path.join(cluster_path, f"{file}.csv"))) for file in self.file_name_list]
            self.find_max_min_values(cluster_path) 
            # Updating data_ori and data_copy with interpolated data
            integrated_data_ori = []
            # Creating a uniform depth array
            depth_array = np.arange(self.min_depth, self.max_depth, 0.02)
            integrated_data_ori = pd.DataFrame({'Depth (m)': depth_array})
            # Interpolating and adding qt data as new columns
            for file, data in self.data_ori:
                interpolated_qt = self.interpolate_data(data, depth_array)
                integrated_data_ori[file] = interpolated_qt  # Using filename as the column name
            self.integrated_data_ori = integrated_data_ori  # Storing the integrated data
            self.integrated_data_plot = integrated_data_ori.copy()
            self.integrated_data_export = integrated_data_ori.copy()
            self.integrated_data_export.iloc[:, 1:] = np.nan # Initialize the export data
            self.keep_data_boolean_df = self.integrated_data_ori.iloc[:, 1:].copy()  # Copy all columns except the first (depth)
            self.keep_data_boolean_df[:] = True  # Set all values to True 
            self.keep_file_boolean_df = self.integrated_data_ori.iloc[1, 1:].copy()
            self.keep_file_boolean_df[:] = False 

            self.show_locations_plot(0)
            self.show_main_plot(0)
            self.show_export_plot()

            # Extracting nztmX and nztmY values
            file_ids, nztmX_values, nztmY_values = self.extract_nztm_data()


    def show_locations_plot(self, index):
        if 0 <= index < len(self.file_name_list):
            self.current_plot_index_loc = index

            # Clear the plot canvas and prepare for new data
            self.loc_plot_canvas.clear_plot()
            
            # Highlight the current file's location in red
            current_file = self.file_name_list[index]
            nztmX_current, nztmY_current = self.extract_nztm_for_file_ids([current_file])
            highlighted_points = [(nztmX_current, nztmY_current)]
            
            # Highlight the closest files' locations in orange
            closest_files = self.extract_closest_file_ids(current_file)
            for file_id in closest_files:
                nztmX, nztmY = self.extract_nztm_for_file_ids([file_id])
                highlighted_points.append((nztmX, nztmY))
            
            # Update the plot with the new data and styles
            self.loc_plot_canvas.plot(np.array(self.nztmX_list), np.array(self.nztmY_list), line_style='o')

            
            # Specifically highlight the current and closest points after plotting all points
            for point in highlighted_points:
                self.loc_plot_canvas.plot(point[0], point[1], line_style='o', **{'markersize':5, 'color':('red' if point == highlighted_points[0] else 'orange')})
                
            # Set plot attributes
            self.loc_plot_canvas.set_plot_attributes(
                title=f'{self.cluster_name} NZTM Plot',
                xlabel='NZTM X',
                ylabel='NZTM Y',
                grid=True,
                linestyle='--',
                linewidth=0.5
            )
        
        self.loc_plot_canvas.adjust_plot_view(equal_aspect=True, tick_interval=10, adjust_limits=True, margin=10.1)
        self.loc_plot_canvas.draw()  # Ensure the canvas is updated with all changes

    def show_main_plot(self, index, keep_limits=False):
        if 0 <= index < len(self.data_ori):
            
            self.current_plot_index = index
            file = self.file_name_list[index]

            # Get a color for the current file
            if file not in self.file_colors:
                self.file_colors[file] = cm.get_cmap('tab10')(len(self.file_colors) % 10)

            # Clear the existing plot
            self.main_plot_canvas.clear_plot()

            # Plot data for closest files
            closest_files_data = [(self.integrated_data_ori[closest_file], self.integrated_data_ori['Depth (m)']) for closest_file in self.extract_closest_file_ids(file)]
            closest_files_styles = {'markersize': 3.5, 'color': 'lightgray'}
            plot_ori_styles = {'markersize': 3.5, 'color': 'lightblue'}
            plot_file_styles = {'markersize': 3.5, 'color': self.file_colors[file]}

            for x_data, y_data in closest_files_data:
                self.main_plot_canvas.plot(x_data, y_data, line_style='-*', **closest_files_styles)

            # Plot data for the current file in light blue
            self.main_plot_canvas.plot(self.integrated_data_ori[file], self.integrated_data_ori['Depth (m)'], line_style='-*', **plot_ori_styles)
            # Highlight the current file with a specific color
            self.main_plot_canvas.plot(self.integrated_data_plot[file], self.integrated_data_plot['Depth (m)'], line_style='-*', **plot_file_styles)

            # Set plot attributes
            self.main_plot_canvas.set_plot_attributes(
                title=f'{file} Data',
                xlabel='qt (MPa)',
                ylabel='Depth (m)',
                grid=True
            )

            self.main_plot_canvas.axes.set_xlim(np.sort(self.current_xlim) if self.current_xlim else np.array([0, self.max_qt]))
            self.main_plot_canvas.axes.set_ylim(np.sort(self.current_ylim) if self.current_ylim else np.array([0, self.max_depth]))

            self.main_plot_canvas.axes.invert_yaxis()  # Ensure y-axis is inverted for depth plots
            self.main_plot_canvas.draw()  # Redraw the canvas with all changes

    
    def show_export_plot(self):
        self.export_plot_canvas.clear_plot()
        for col in self.integrated_data_ori.columns[1:]:
            self.export_plot_canvas.plot(self.integrated_data_ori[col], self.integrated_data_ori['Depth (m)'], line_style='-', **{'markersize':1.5, 'color':'lightgray'})
        self.export_plot_canvas.axes.invert_yaxis()
        self.export_plot_canvas.draw()
        self.export_plot_canvas.axes.set_xlabel('qt (MPa)')
        self.export_plot_canvas.axes.set_ylabel('Depth (m)')
        for file, should_plot in self.keep_file_boolean_df.items():
            if should_plot:
                self.export_plot_canvas.plot(self.integrated_data_ori[col], self.integrated_data_ori['Depth (m)'], line_style='-', **{'markersize':1.5, 'color':self.file_colors[file]})

    def on_zoom_sensitivity_x_changed(self, value):
        value = value / self.scale_factor
        self.main_plot_canvas.set_zoom_sensitivity_x(value)
        self.export_plot_canvas.set_zoom_sensitivity_x(value)
        

    def on_zoom_sensitivity_y_changed(self, value):
        value = value / self.scale_factor
        self.main_plot_canvas.set_zoom_sensitivity_y(value)
        self.main_plot_canvas.set_zoom_sensitivity_y(value)
    
    def exportToMATLAB(self):
        pass
    
    def show_previous_plot(self):
        self.current_xlim = self.main_plot_canvas.axes.get_xlim()
        self.current_ylim = self.main_plot_canvas.axes.get_ylim()
        if self.current_plot_index > 0:
            self.show_main_plot(self.current_plot_index - 1, keep_limits=self.limits_locked)
            self.show_locations_plot(self.current_plot_index_loc - 1)

    def show_next_plot(self):
        self.current_xlim = self.main_plot_canvas.axes.get_xlim()
        self.current_ylim = self.main_plot_canvas.axes.get_ylim()
        if self.current_plot_index < len(self.data_ori) - 1:
            self.show_main_plot(self.current_plot_index + 1, keep_limits=self.limits_locked)
            self.show_locations_plot(self.current_plot_index_loc + 1)


    def reset_view(self):
        # Check if plot limits are locked or not
        if not self.main_plot_canvas.enable_interactions:
            # If plot limits are locked, display a message and do not reset
            QMessageBox.warning(self, "Locked", "Plot limits are locked. Unlock to reset view.")
            return
        self.current_xlim = (0, self.max_qt)
        self.current_ylim = (0, self.max_depth)
        self.show_main_plot(self.current_plot_index)
    
    def toggle_plot_limits(self):
        """
        Toggles the ability to lock or unlock plot limits, affecting zooming and dragging.
        """
        # Toggle interactions on the main plot canvas
        self.main_plot_canvas.toggle_interactions()
        # Optionally, apply to other plot canvases if needed
        # self.loc_plot_canvas.toggle_interactions()
        # self.export_plot_canvas.toggle_interactions()

        # Update the button text or color based on the state
        if self.main_plot_canvas.enable_interactions:
            self.lock_lim_button.setText("xy lim Unlocked")
            # Adjust color for unlocked state if desired
        else:
            self.lock_lim_button.setText("xy lim Locked")
            # Adjust color for locked state if desired

    def on_submit_depth(self):
        pass

    def on_delete_file(self):
        pass

    def interpolate_data(self, data, depth_array):
        interpolated_qt = np.interp(depth_array, data['Depth (m)'], data['qt (MPa)'], left=np.nan, right=np.nan)
        return interpolated_qt
    

    def extract_nztm_data(self):
        # Assuming self.nztm_data_dict is a dictionary with the structure {file_id: {'nztmX': value, 'nztmY': value}, ...}

        # Extracting file IDs, nztmX, and nztmY while maintaining the original order
        file_ids = sorted(self.nztm_data_dict.keys(), key=lambda x: list(self.nztm_data_dict).index(x))
        nztmX_values = [self.nztm_data_dict[file_id]['nztmX'] for file_id in file_ids]
        nztmY_values = [self.nztm_data_dict[file_id]['nztmY'] for file_id in file_ids]

        return file_ids, nztmX_values, nztmY_values


    def extract_nztm_for_file_ids(self, file_ids):
        nztmX_values = []
        nztmY_values = []

        # Convert to list if a single string is provided
        if isinstance(file_ids, str):
            file_ids = [file_ids]

        for file_id in file_ids:
            if file_id in self.nztm_data_dict:
                nztmX_values.append(self.nztm_data_dict[file_id]['nztmX'])
                nztmY_values.append(self.nztm_data_dict[file_id]['nztmY'])
            else:
                print(f"Data not found for {file_id}")

        return nztmX_values, nztmY_values
    

    def extract_closest_file_ids(self, file_ids):
        return self.closest_file_ids_dict[file_ids]
    

    def find_max_min_values(self, cluster_path):
        self.max_qt = 0
        self.max_depth = 0
        self.min_depth = float('inf')
        for file in os.listdir(cluster_path):
            if file.endswith('.csv'):
                data = pd.read_csv(os.path.join(cluster_path, file))
                self.max_qt = max(self.max_qt, data['qt (MPa)'].max())
                self.max_depth = max(self.max_depth, data['Depth (m)'].max())
                self.min_depth = min(self.min_depth, data['Depth (m)'].min())

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = CPTDataPlotter()
    window.show()
    sys.exit(app.exec_())
    