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
                             QSlider, QFileDialog, QLineEdit, QShortcut, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm
import matplotlib.widgets as widgets
from matplotlib.patches import Polygon

sys.path.append(r"D:\py_function")

def calculate_center_of_geometry(x_data, y_data):
    # Check if the length of x_data and y_data are the same
    if len(x_data) != len(y_data):
        raise ValueError("X and Y data lengths must be the same.")

    center_x = np.mean(x_data)
    center_y = np.mean(y_data)

    return center_x, center_y


def ranking_pairwise_distances(X, Y):
    """
    Computes and ranks pairwise distances between points.

    Parameters:
    - X, Y: NumPy arrays representing the X and Y coordinates of points.

    Returns:
    - p1, p2: An n by 2 array containing the indices of point pairs with sorted distances.
    - sorted_distances: A sorted vector of pairwise distances.
    """
    X, Y = np.array(X), np.array(Y)
    X, Y = X.reshape(-1, 1), Y.reshape(-1, 1)

    # Combine X and Y into a single array
    points = np.column_stack((X, Y))

    # Calculate pairwise distances between points
    distances_matrix = squareform(pdist(points))

    # Extract the lower triangular matrix
    mask = np.tril(np.ones_like(distances_matrix), k=-1).astype(bool)
    distances_matrix_lower = distances_matrix[mask]

    # Creating original indices label
    original_indices_label_matrix = np.arange(1, distances_matrix.size + 1).reshape(distances_matrix.shape)
    original_indices_label_matrix_lower = np.tril(original_indices_label_matrix, k=-1)
    original_indices_label = original_indices_label_matrix_lower[original_indices_label_matrix_lower != 0]

    # Sort distances and get indices
    sorted_distances = np.sort(distances_matrix_lower)
    sorted_indices = np.argsort(distances_matrix_lower)

    sorted_original_indices_label = original_indices_label[sorted_indices]

    # Convert indices to subscripts
    p1, p2 = np.unravel_index(sorted_original_indices_label - 1, distances_matrix.shape)

    return p1, p2, sorted_distances


def find_closest_file_ids(file_id, file_ids, X, Y, num_closest=5):
    """
    Find the closest file IDs to the given file ID based on pairwise distances.

    Parameters:
    - file_id (str): The file ID for which to find the closest file IDs.
    - file_ids (list): List of all file IDs.
    - X (list or array): List or array containing the X coordinates corresponding to each file ID.
    - Y (list or array): List or array containing the Y coordinates corresponding to each file ID.
    - num_closest (int): The number of closest file IDs to return. Default is 5.

    Returns:
    - list: A list of file IDs that are closest to the given file ID.
    """
    # Convert to arrays
    X = np.array(X)
    Y = np.array(Y)

    # Calculate pairwise distances
    p1, p2, _ = ranking_pairwise_distances(X, Y)

    # Find the closest file IDs
    closest_file_ids = []
    for i in range(len(p1)):
        if file_ids[p1[i]] == file_id and file_ids[p2[i]] not in closest_file_ids:
            closest_file_ids.append(file_ids[p2[i]])
        elif file_ids[p2[i]] == file_id and file_ids[p1[i]] not in closest_file_ids:
            closest_file_ids.append(file_ids[p1[i]])

        if len(closest_file_ids) == num_closest:
            break

    return closest_file_ids


def get_unique_set(data):
    """
    Get the unique set of elements in the input data while maintaining the original order.

    Parameters:
    - data (numpy.ndarray): Input array.

    Returns:
    - numpy.ndarray: Unique set of elements in the original order.
    """
    data = data.ravel()  # Flatten the array
    unique_set, indices = np.unique(data, return_index=True)  # Use return_index to get the indices of the first occurrences
    unique_set = unique_set[np.argsort(indices)]  # Sort the unique set based on the indices
    return unique_set


class CPTDataPlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initialize_window()
        self.initialize_data()

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.setup_layout()

        self.setup_plot()
        self.setup_zoom_defaults()
        self.setup_shorcuts()
        self.setup_limits_locked_defaults()
        self.setup_interaction_variables()
        
        # Set the font type to Consolas using a style sheet
        app = QApplication.instance()
        app.setStyleSheet("QLabel, QPushButton { font-family: Consolas; font-size: 12pt; }")

    def initialize_window(self):
        self.setWindowTitle("CPT Data Plotter")
        self.setGeometry(100, 100, 1000, 800)  # Adjust the size of the window
        self.showMaximized()  # Maximize the window on startup

    def initialize_data(self):
        self.data_ori = []
        self.current_plot_index = -1
        self.current_plot_index_loc = -1
        self.data_copy = []
        self.file_colors = {}
        self.rectangle_selector_active = False
        self.current_action = None
        # Set a larger font size for labels and buttons
        font = QFont()
        font.setPointSize(12)  # Adjust the size as needed

        # Setting font for labels
        for label in self.findChildren(QLabel):
            label.setFont(font)
        # Setting font for buttons
        for button in self.findChildren(QPushButton):
            button.setFont(font)

    def setup_zoom_defaults(self):
        # Default zoom sensitivities
        self.zoom_sensitivity_x = 1.1
        self.zoom_sensitivity_y = 1.1

    def setup_limits_locked_defaults(self):
        # Default zoom sensitivities
        self.limits_locked = False

    def setup_interaction_variables(self):
        self.current_xlim = None
        self.current_ylim = None
        self.rect_selector = None
        self.dragging = False
        self.selecting = False
        self.drag_button = 3  # Right-click for dragging
        self.select_button = 1  # Left-click for selecting
    
    def setup_shorcuts(self):
        # Connect key press events to methods
        self.shortcut_previous = QShortcut(Qt.Key_Minus, self)
        self.shortcut_previous.activated.connect(self.show_previous_plot)

        self.shortcut_next = QShortcut(Qt.Key_Equal, self)
        self.shortcut_next.activated.connect(self.show_next_plot)

    def setup_layout(self):
        # Create main grid layout for the window
        main_grid_layout = QGridLayout(self.main_widget)
        # Create and add layouts for different areas
        left_layout = self.create_layout("left")
        middle_layout = self.create_layout("middle")
        right_layout = self.create_layout("right")
        # Add layouts to the main grid layout
        main_grid_layout.addLayout(left_layout, 0, 0)   # Left column
        main_grid_layout.addLayout(middle_layout, 0, 1) # Middle column
        main_grid_layout.addLayout(right_layout, 0, 2)  # Right column
        # Adjust column stretch for layout spacing
        main_grid_layout.setColumnStretch(0, 1)
        main_grid_layout.setColumnStretch(1, 2)
        main_grid_layout.setColumnStretch(2, 2)
        # Set the main grid layout as the layout for the central widget
        self.main_widget.setLayout(main_grid_layout)

    def create_layout(self, position):
        layout = QVBoxLayout()

        if position == "left":
            self.add_controls(layout)
            self.add_zoom_sliders(layout)
            # Create and add canvas for the new subplot1
            self.canvas2 = FigureCanvas(Figure(figsize=(4, 4)))
            layout.addWidget(self.canvas2)
        elif position == "middle":
            # Create and add canvas for the original plot
            self.canvas = FigureCanvas(Figure(figsize=(3, 8)))
            layout.addWidget(self.canvas)
            # Add depth control row
            self.add_depth_controls(layout)
        elif position == "right":
            # Create and add canvas for the additional plot
            self.canvas3 = FigureCanvas(Figure(figsize=(3, 8)))
            layout.addWidget(self.canvas3)
            self.add_MATLAB_export_controls(layout)
        return layout

    def add_controls(self, layout):
        self.add_control_group(layout, 
                               label="Choose Project Path:",
                               buttons=[("Browse", self.choose_project_path)])

        self.add_control_group(layout, 
                               label="Select Cluster:",
                               combo_box=True,
                               buttons=[("Submit", self.select_cluster)])

        self.add_control_group(layout, 
                        buttons=[("Reset View", self.reset_view), 
                                ("Previous", self.show_previous_plot),
                                ("Next", self.show_next_plot),
                                ("Lock/Unlock Limits", self.toggle_plot_limits)])

        self.add_control_group(layout, 
                               buttons=[("Select region to clear data", lambda: self.enable_rectangle_selector('clear')),
                                ("Select region to recover data", lambda: self.enable_rectangle_selector('recover'))])
                            
    def add_control_group(self, layout, label=None, combo_box=False, buttons=[]):
        row_layout = QHBoxLayout()
        layout.addLayout(row_layout)

        if label:
            row_layout.addWidget(QLabel(label))

        if combo_box:
            self.cluster_combobox = QComboBox(self)
            row_layout.addWidget(self.cluster_combobox)

        for button_text, button_action in buttons:
            button = QPushButton(button_text, self)
            button.clicked.connect(button_action)
            row_layout.addWidget(button)
    
    def add_depth_controls(self, layout):
        # Create a horizontal layout for the depth controls
        depth_control_layout = QHBoxLayout()
        # Start depth input
        self.start_depth_input = QLineEdit(self)
        self.start_depth_input.setPlaceholderText("Start Depth")
        depth_control_layout.addWidget(self.start_depth_input)
        # End depth input
        self.end_depth_input = QLineEdit(self)
        self.end_depth_input.setPlaceholderText("End Depth")
        depth_control_layout.addWidget(self.end_depth_input)
        # Submit button
        submit_button = QPushButton("Submit", self)
        submit_button.clicked.connect(self.on_submit_depth)
        depth_control_layout.addWidget(submit_button)
        # Delete button
        delete_button = QPushButton("Delete", self)
        delete_button.clicked.connect(self.on_delete_file)
        depth_control_layout.addWidget(delete_button)
        # Add the horizontal layout to the main layout
        layout.addLayout(depth_control_layout)

    def on_submit_depth(self):
        # Implement the logic to handle the depth input submission
        file = self.file_name_list[self.current_plot_index]
        start_depth = float(self.start_depth_input.text())
        end_depth = float(self.end_depth_input.text())
        self.keep_file_boolean_df[file] = True
        # Create a boolean mask for the specified depth range
        within_region = (self.integrated_data_ori['Depth (m)'] >= start_depth) & (self.integrated_data_ori['Depth (m)'] <= end_depth)
        # Set values to NaN outside the specified depth range
        self.integrated_data_export[file] = np.where(within_region, self.integrated_data_plot[file], np.nan)
        self.show_right_plot()

    def on_delete_file(self):
        file = self.file_name_list[self.current_plot_index]
        self.keep_file_boolean_df[file] = False
        self.show_right_plot()

    def add_MATLAB_export_controls(self, layout):
        export_button = QPushButton("Export to .mat file", self)
        export_button.clicked.connect(self.export_to_matlab)
        layout.addWidget(export_button)

    def export_to_matlab(self):
        directory = os.path.join(self.project_path, self.cluster_name)
        # Convert DataFrames to dictionaries with 2D array for each column
        def df_to_dict(df):
            return {col: df[col].values[:, None] for col in df.columns}
        # For the 1D DataFrame, convert both index and values
        def series_to_dict(series):
            return {
                'values': series.values[:, None],
                'index': np.array(series.index, dtype=object)[:, None]
            }
        # Convert nztm_data_dict to MATLAB format
        file_ids = []
        nztmX_values = []
        nztmY_values = []

        for file_id, coords in self.nztm_data_dict.items():
            file_ids.append(file_id)
            nztmX_values.append(coords['nztmX'])
            nztmY_values.append(coords['nztmY'])

        # Add nztm_data to the mat_data dictionary
        # mat_data['nztm_data'] = {
        #     'file_id': np.array(file_ids, dtype=object),
        #     'nztmX': np.array(nztmX_values),
        #     'nztmY': np.array(nztmY_values)
        # }
        try:
            mat_data = {
                'integrated_data_ori': df_to_dict(self.integrated_data_ori),
                'integrated_data_plot': df_to_dict(self.integrated_data_plot),
                'integrated_data_export': df_to_dict(self.integrated_data_export),
                'keep_data_boolean_df': df_to_dict(self.keep_data_boolean_df),
                # Handle 1D DataFrame (boolean) by converting to 2D numpy array
                'keep_file_boolean_df': series_to_dict(self.keep_file_boolean_df),
                # # Convert lists to numpy arrays
                # 'X': np.array(self.nztmX_list),
                # 'Y': np.array(self.nztmY_list),
                'nztm_data': {
                        'file_id': np.array(file_ids, dtype=object),
                        'nztmX': np.array(nztmX_values),
                        'nztmY': np.array(nztmY_values)
                    },
                'fileNameList': np.array(self.file_name_list, dtype=object)  # dtype=object for string array
            }
            # Save as .mat file
            filepath = os.path.join(directory, 'clean_data_from_python.mat')
            savemat(filepath, mat_data)
            # Save the object instance
            object_filepath = os.path.join(directory, 'object_instance.pkl')
            # with open(object_filepath, 'wb') as object_file:
            #     pickle.dump(self, object_file)
            # Pop-up message upon successful export
            QMessageBox.information(self, "Export Complete", "Data successfully exported to MATLAB .mat file.")
        except Exception as e:
            # Pop-up message in case of an error
            QMessageBox.critical(self, "Export Failed", f"An error occurred during export: {e}")

    def add_zoom_sliders(self, layout):
        # X-axis zoom slider
        self.zoom_slider_x = QSlider(Qt.Horizontal, self)
        self.zoom_slider_x.setRange(1, 20)  # Range for sensitivity
        self.zoom_slider_x.setValue(11)  # Default value
        self.zoom_slider_x.valueChanged.connect(self.adjust_zoom_sensitivity_x)
        layout.addWidget(QLabel("X-axis Zoom Sensitivity:"))
        layout.addWidget(self.zoom_slider_x)
        # Y-axis zoom slider
        self.zoom_slider_y = QSlider(Qt.Horizontal, self)
        self.zoom_slider_y.setRange(1, 20)  # Range for sensitivity
        self.zoom_slider_y.setValue(11)  # Default value
        self.zoom_slider_y.valueChanged.connect(self.adjust_zoom_sensitivity_y)
        layout.addWidget(QLabel("Y-axis Zoom Sensitivity:"))
        layout.addWidget(self.zoom_slider_y)
        
    def setup_plot(self):
        self.setup_subplot(self.canvas, "subplot1")
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.canvas.mpl_connect('button_release_event', self.on_release)

        self.setup_subplot(self.canvas2, "subplot2")
        self.canvas2.mpl_connect('motion_notify_event', self.on_hover)
        self.canvas2.mpl_connect('scroll_event', self.on_scroll)
        self.canvas2.mpl_connect('button_press_event', self.on_press)
        self.canvas2.mpl_connect('motion_notify_event', self.on_drag)
        self.canvas2.mpl_connect('button_release_event', self.on_release)

        self.setup_subplot(self.canvas3, "subplot3")
        self.canvas3.mpl_connect('motion_notify_event', self.on_hover)
        self.canvas3.mpl_connect('scroll_event', self.on_scroll)
        self.canvas3.mpl_connect('button_press_event', self.on_press)
        self.canvas3.mpl_connect('motion_notify_event', self.on_drag)
        self.canvas3.mpl_connect('button_release_event', self.on_release)

    def setup_subplot(self, canvas, subplot_name):
        subplot1 = canvas.figure.add_subplot(111)
        subplot1.my_id = subplot_name  # Adding a unique identifier
        setattr(self, subplot_name, subplot1)

    def choose_project_path(self):
        project_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        clusters = [d for d in os.listdir(project_path) if os.path.isdir(os.path.join(project_path, d)) and d.startswith('Cluster ')]
        self.cluster_combobox.addItems(clusters)
        self.project_path = project_path
    
    def select_cluster(self):
        self.cluster_name = self.cluster_combobox.currentText()

        cluster_file_path = os.path.join(self.project_path, self.cluster_name, f"{self.cluster_name}.csv")
        cluster_data = pd.read_csv(cluster_file_path)
        nztm_data_dict = {}
        index_sort = []
        for index, row in cluster_data.iterrows():
            # file_id = f"{row['ID']}.csv"  # Append ".csv" to each file_id
            file_id = row['ID']
            # Store nztmX and nztmY as a nested dictionary
            nztm_data_dict[file_id] = {'nztmX': row['nztmX'], 'nztmY': row['nztmY']}
        # Store the nested dictionary as an attribute
        self.nztm_data_dict = nztm_data_dict
        file_ids, nztmX_values, nztmY_values = self.extract_nztm_data()
        p1, p2, sorted_distances = ranking_pairwise_distances(nztmX_values, nztmY_values)
        print(sorted_distances[:5])
        index_sort = get_unique_set(np.vstack((p1, p2)).T)
        self.file_name_list = [file_ids[i] for i in index_sort]
        self.file_name_list = [file.replace('.csv', '') for file in self.file_name_list]
        self.nztmX_list, self.nztmY_list = self.extract_nztm_for_file_ids(self.file_name_list)
        # Initialize dictionary to store closest file IDs for each file ID
        closest_file_ids_dict = {}
        # Iterate through each file ID
        for file_id in file_ids:
            # Find 5 closest file IDs
            closest_file_ids = find_closest_file_ids(file_id, file_ids, nztmX_values, nztmY_values, num_closest=5)
            # Store the result in the dictionary
            closest_file_ids_dict[file_id] = closest_file_ids

        # Store the dictionary as an attribute
        self.closest_file_ids_dict = closest_file_ids_dict
        self.show_locations_plot(0)

        cluster_path = os.path.join(self.project_path, self.cluster_name, 'Extracted')
        if os.path.exists(cluster_path):
            self.data_ori = [(file, pd.read_csv(os.path.join(cluster_path, f"{file}.csv"))) for file in self.file_name_list]
            self.find_max_min_values(cluster_path)
            # Creating a uniform depth array
            depth_array = np.arange(self.min_depth, self.max_depth, 0.02)
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
            self.integrated_data_export.iloc[:, 1:] = np.nan
            self.keep_data_boolean_df = self.integrated_data_ori.iloc[:, 1:].copy()  # Copy all columns except the first (depth)
            self.keep_data_boolean_df[:] = True  # Set all values to True
            self.keep_file_boolean_df = self.integrated_data_ori.iloc[1, 1:].copy()
            self.keep_file_boolean_df[:] = False

            self.show_middle_plot(0)
            self.show_right_plot()

            # Extracting nztmX and nztmY values
            file_ids, nztmX_values, nztmY_values = self.extract_nztm_data()

            # # Perform Delaunay triangulation
            # points = np.array(list(zip(nztmX_values, nztmY_values)))
            # self.tri = Delaunay(points)

            # # Perform Voronoi tessellation
            # self.vor = Voronoi(points)


    def show_locations_plot(self, index):
        if 0 <= index < len(self.file_name_list):
            self.subplot2.clear()
            self.subplot2.plot(self.nztmX_list, self.nztmY_list, marker='o', linestyle='', markersize=5, color='black')
            self.current_plot_index_loc = index
            file = self.file_name_list[index]
            for closest_files in self.extract_closest_file_ids(file):
                nztmX, nztmY = self.extract_nztm_for_file_ids(closest_files)
                self.subplot2.plot(nztmX, nztmY, marker='o', linestyle='', markersize=5, color='orange')
            nztmX_current, nztmY_current = self.extract_nztm_for_file_ids(file)
            self.subplot2.plot(nztmX_current, nztmY_current, marker='o', linestyle='', markersize=5, color='red')
            self.subplot2.set_title(f'{self.cluster_name} NZTM Plot')
            self.subplot2.set_xlabel('NZTM X')
            self.subplot2.set_ylabel('NZTM Y')
            self.subplot2.axis('equal')
            x_limits = self.subplot2.get_xlim()
            y_limits = self.subplot2.get_ylim()
            # Set major ticks and grid lines every 10 units on both axes
            self.subplot2.set_xticks(np.arange(x_limits[0]-10.1, x_limits[1]+10.1, 10))
            self.subplot2.set_yticks(np.arange(y_limits[0]-10.1, y_limits[1]+10.1, 10))
            self.subplot2.grid(True, which='both', linestyle='--', linewidth=0.5)
            self.canvas2.draw_idle()
        
    def show_middle_plot(self, index, keep_limits=False):
        if 0 <= index < len(self.data_ori):
            self.current_plot_index = index

            file = self.file_name_list[index]

            # Get a color for the current file
            if file not in self.file_colors:
                self.file_colors[file] = cm.get_cmap('tab10')(len(self.file_colors) % 10)

            self.subplot1.clear()
            for closest_files in self.extract_closest_file_ids(file):
                self.subplot1.plot(self.integrated_data_ori[closest_files], self.integrated_data_ori['Depth (m)'], marker='o', markersize=1.5, color='lightgray')
            self.subplot1.plot(self.integrated_data_ori[file], self.integrated_data_ori['Depth (m)'], marker='o', markersize=1.5, color='lightblue')
            self.subplot1.plot(self.integrated_data_plot[file], self.integrated_data_plot['Depth (m)'], marker='o', markersize=1.5, color=self.file_colors[file])

            self.subplot1.invert_yaxis()
            self.subplot1.set_title(f'{file} Data')
            self.subplot1.set_xlabel('qt (MPa)')
            self.subplot1.set_ylabel('Depth (m)')
            self.subplot1.grid(True)  

            if keep_limits and self.limits_locked:
                # Keep the current x and y limits
                self.subplot1.set_xlim(self.current_xlim)
                self.subplot1.set_ylim(self.current_ylim)
            else:
                # Set xlim and ylim only if they have not been previously set
                if self.current_xlim is None or self.current_ylim is None:
                    self.subplot1.set_xlim([0, self.max_qt])
                    self.subplot1.set_ylim([self.max_depth, 0])
                else:
                    self.subplot1.set_xlim(self.current_xlim)
                    self.subplot1.set_ylim(self.current_ylim)
        self.canvas.draw_idle()

    def show_right_plot(self):
        self.subplot3.clear()
        for col in self.integrated_data_ori.columns[1:]:
            self.subplot3.plot(self.integrated_data_ori[col], self.integrated_data_ori['Depth (m)'], marker='o', markersize=1.5, color='lightgray')
        self.subplot3.invert_yaxis()
        self.subplot3.set_xlabel('qt (MPa)')
        self.subplot3.set_ylabel('Depth (m)')
        for file, should_plot in self.keep_file_boolean_df.items():
            if should_plot:
                self.subplot3.plot(self.integrated_data_export[file], self.integrated_data_export['Depth (m)'], marker='o', markersize=1.5, color=self.file_colors[file])
        self.subplot3.grid(True)  
        self.canvas3.draw_idle()

    # def enable_rectangle_selector(self):
    #     # Ensure the rectangle selector is only for the middle subplot1
    #     if self.rect_selector is not None:
    #         self.rect_selector.set_active(False)  # Disable any existing selector

    #     self.rect_selector = widgets.RectangleSelector(
    #         self.subplot1,  # Apply only to the middle subplot1
    #         lambda eclick, erelease: self.onselect(eclick, erelease), 
    #         useblit=True,
    #         button=[self.select_button],  # Left mouse button
    #         minspanx=5, minspany=5, spancoords='pixels',
    #         interactive=True)
    def enable_rectangle_selector(self, action):
        # Set the current action based on the button clicked
        self.current_action = action

        if self.rect_selector is not None:
            self.rect_selector.set_active(False)  # Disable any existing selector

        self.rect_selector = widgets.RectangleSelector(
            self.subplot1, 
            lambda eclick, erelease: self.onselect(eclick, erelease), 
            useblit=True,
            button=[self.select_button],
            minspanx=5, minspany=5, spancoords='pixels',
            interactive=True)

    def reset_view(self):
        """ Reset the plot to its original view. """
        if self.max_qt and self.max_depth:
            self.subplot1.set_xlim([0, self.max_qt])
            self.subplot1.set_ylim([self.max_depth, 0])
            self.canvas.draw_idle()

    def onselect(self, eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        self.process_selected_region(x1, y1, x2, y2, self.current_action)

    # def process_selected_region(self, x1, y1, x2, y2):
    #     file = self.file_name_list[self.current_plot_index]
    #     within_region = (self.integrated_data_ori[file] >= min(x1, x2)) & (self.integrated_data_ori[file] <= max(x1, x2)) & \
    #                     (self.integrated_data_ori['Depth (m)'] >= min(y1, y2)) & (self.integrated_data_ori['Depth (m)'] <= max(y1, y2))
    #     # self.keep_data_boolean_df.loc[within_region, file] = ~self.keep_data_boolean_df.loc[within_region, file].astype(bool)
    #     self.keep_data_boolean_df.loc[within_region, file] = False
    #     self.integrated_data_plot[file] = np.where(self.keep_data_boolean_df[file] == 0, np.nan, self.integrated_data_ori[file])
    #     self.show_middle_plot(self.current_plot_index)

    def process_selected_region(self, x1, y1, x2, y2, action):
        file = self.file_name_list[self.current_plot_index]
        within_region = (self.integrated_data_ori[file] >= min(x1, x2)) & (self.integrated_data_ori[file] <= max(x1, x2)) & \
                        (self.integrated_data_ori['Depth (m)'] >= min(y1, y2)) & (self.integrated_data_ori['Depth (m)'] <= max(y1, y2))

        if action == 'clear':
            self.keep_data_boolean_df.loc[within_region, file] = False
        elif action == 'recover':
            self.keep_data_boolean_df.loc[within_region, file] = True

        self.integrated_data_plot[file] = np.where(self.keep_data_boolean_df[file] == False, np.nan, self.integrated_data_ori[file])
        self.show_middle_plot(self.current_plot_index)

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

    def interpolate_data(self, data, depth_array):
        interpolated_qt = np.interp(depth_array, data['Depth (m)'], data['qt (MPa)'], left=np.nan, right=np.nan)
        return interpolated_qt

    def toggle_plot_limits(self):
        if not hasattr(self, 'limits_locked'):
            self.limits_locked = False
        self.limits_locked = not self.limits_locked
        if self.limits_locked:
            self.current_xlim = self.subplot1.get_xlim()
            self.current_ylim = self.subplot1.get_ylim()
        print("Limits are now " + ("locked" if self.limits_locked else "unlocked"))


    def adjust_zoom_sensitivity_x(self, value):
        self.zoom_sensitivity_x = value / 10  # Adjusting the sensitivity

    def adjust_zoom_sensitivity_y(self, value):
        self.zoom_sensitivity_y = value / 10  # Adjusting the sensitivity

    def on_scroll(self, event):
        subplot1 = self.get_subplot_from_event(event)
        if self.limits_locked:
            return

        if not subplot1:
            return

        # Calculate scale factors based on zoom sensitivities and scroll direction
        scale_factor_x = self.zoom_sensitivity_x if event.button == 'up' else 1 / self.zoom_sensitivity_x
        scale_factor_y = self.zoom_sensitivity_y if event.button == 'up' else 1 / self.zoom_sensitivity_y

        # Current mouse position data
        xdata, ydata = event.xdata, event.ydata

        # Current limits of the plot
        xlim = subplot1.get_xlim()
        ylim = subplot1.get_ylim()

        # Adjusting the x and y limits based on the scale factors
        subplot1.set_xlim([xdata - (xdata - xlim[0]) * scale_factor_x,
                          xdata + (xlim[1] - xdata) * scale_factor_x])
        subplot1.set_ylim([ydata - (ydata - ylim[0]) * scale_factor_y,
                          ydata + (ylim[1] - ydata) * scale_factor_y])

        subplot1.figure.canvas.draw_idle()

    def get_subplot_from_event(self, event):
        if event.inaxes == self.subplot1.axes:
            return self.subplot1
        elif event.inaxes == self.subplot2.axes:
            return self.subplot2
        elif event.inaxes == self.subplot3.axes:
            return self.subplot3
        return None

    def on_press(self, event):
        subplot1 = self.get_subplot_from_event(event)
        if not subplot1:
            return

        if event.button == self.drag_button:
            self.dragging = True
            self._drag_data = {'subplot1': subplot1, 'x': event.xdata, 'y': event.ydata}
        elif event.button == self.select_button and self.rect_selector:
            self.rect_selector.press(event)

    def on_drag(self, event):
        if self.limits_locked:
            return
        if not self.dragging:
            return

        subplot1 = self._drag_data['subplot1']
        dx = self._drag_data['x'] - event.xdata
        dy = self._drag_data['y'] - event.ydata
        xlim = subplot1.get_xlim()
        ylim = subplot1.get_ylim()
        subplot1.set_xlim(xlim[0] + dx, xlim[1] + dx)
        subplot1.set_ylim(ylim[0] + dy, ylim[1] + dy)
        subplot1.figure.canvas.draw_idle()

    def on_release(self, event):
        self.dragging = False
    
    def on_hover(self, event):
        if event.inaxes is not None:
            closest_distance = float('inf')
            closest_x = None
            closest_y = None

            # Check all lines in the subplot
            for line in event.inaxes.lines:
                xdata, ydata = line.get_xdata(), line.get_ydata()

                # Filter out nan values
                valid_indices = ~np.isnan(xdata) & ~np.isnan(ydata)
                xdata = xdata[valid_indices]
                ydata = ydata[valid_indices]

                # Calculate distances to all points in the line
                distances = np.sqrt((xdata - event.xdata)**2 + (ydata - event.ydata)**2)
                min_distance = np.min(distances)

                # Update closest point information if this point is closer
                if min_distance < closest_distance:
                    closest_distance = min_distance
                    min_index = np.argmin(distances)
                    closest_x = xdata[min_index]
                    closest_y = ydata[min_index]

            # Update the status bar with the coordinates of the closest data point
            if closest_x is not None and closest_y is not None:
                message = f"X: {closest_x:.2f}, Y: {closest_y:.2f}"  # Format to two decimal places
                self.statusBar().showMessage(message)

    def show_previous_plot(self):
        if self.current_plot_index > 0:
            self.show_middle_plot(self.current_plot_index - 1, keep_limits=self.limits_locked)
            self.show_locations_plot(self.current_plot_index_loc - 1)

    def show_next_plot(self):
        if self.current_plot_index < len(self.data_ori) - 1:
            self.show_middle_plot(self.current_plot_index + 1, keep_limits=self.limits_locked)
            self.show_locations_plot(self.current_plot_index_loc + 1)
    
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
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = CPTDataPlotter()
    main.show()
    sys.exit(app.exec_())
    attributes = dir(main)
    for attribute in attributes:
        print(attribute)