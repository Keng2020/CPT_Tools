from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QGridLayout,
                             QVBoxLayout, QFileDialog, QShortcut, QProgressBar,
                             QHBoxLayout, QLineEdit, QPushButton)
from PyQt5.QtCore import Qt
from plotcanvas import PlotCanvas
from controlpanel import ControlPanel
from scipy.io import loadmat
import numpy as np
import pandas as pd
import sys, os
import math

class CPTResultInspector(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.initParam()
        self.setup_layout()
        self.setup_shortcuts()
        self.showMaximized()
    

    def initParam(self):
        self.data_cache = {}  # Initialize the cache
        self.mat_files = []  # To store paths of .mat files
        self.current_file_index = 0  # To keep track of the current .mat file being plotted
        self.checkbox_states = {}  # To store checkbox states
        self.folder_path = ""  # Directory of .mat files
    
        
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
        main_grid_layout.setColumnStretch(1, 1)
        main_grid_layout.setColumnStretch(2, 1)

        self.populate_result_window()
        self.populate_left_panel()
        self.populate_middle_panel()
        self.populate_right_panel()


    def setup_shortcuts(self):
        # Connect key press events to methods
        self.shortcut_previous = QShortcut(Qt.Key_Minus, self)
        self.shortcut_previous.activated.connect(self.prev_mat_file)

        self.shortcut_next = QShortcut(Qt.Key_Equal, self)
        self.shortcut_next.activated.connect(self.next_mat_file)

    
    def populate_result_window(self):
        self.result_window = QMainWindow()  
        self.result_window.setWindowTitle("Plot Canvas Result")
        self.result_window.setWindowFlags(self.result_window.windowFlags() | Qt.WindowStaysOnTopHint)

        result_widget = QWidget()
        self.result_window.setCentralWidget(result_widget)

        result_layout = QHBoxLayout(result_widget)
        self.control_panel_1 = ControlPanel()
        # result_layout.addLayout(self.plot_canvas_result.get_layout())
        self.control_panel_1.addFlexibleRow([
            ('button', 'Previous', self.prev_mat_file),
            ('button', 'Next', self.next_mat_file),
        ])

        self.plot_canvas_result = PlotCanvas(parent=self, use_subplots=True, nrows=2, ncols=2)
        self.control_panel_1.addPlotCanvas(self.plot_canvas_result.get_layout())
        
        self.control_panel_2 = ControlPanel()
        self.ticklist_widgets = self.control_panel_2.addFlexibleRow([
            ('ticklist', [
                ('sofv',  False, 'Identifiable', 'Unidentifiable'), 
                ('nuv',   False, 'Identifiable', 'Unidentifiable'),
                ('sofh',  False, 'Identifiable', 'Unidentifiable'), 
                ('nuh',   False, 'Identifiable', 'Unidentifiable'),
                ('sig',   False, 'Identifiable', 'Unidentifiable'), 
                ('sigt',  False, 'Identifiable', 'Unidentifiable'),
                ('sofvt', False, 'Identifiable', 'Unidentifiable'), 
                ('sofht', False, 'Identifiable', 'Unidentifiable'),
            ], 'vertical'),
        ])
        # self.checkboxList = [self.ticklist_widgets.get(f"ticklist_{item_text}") for item_text in ['sofv', 'nuv', 'sofh', 'nuh', 'sig', 'sigt', 'sofvt', 'sofht']]
            # Assuming checkboxes are stored in a list or dict for easy access
        self.checkbox_params = ['δv', 'νv', 'δh', 'νh', 'σ', 'σt', 'δvt', 'δht']
        self.checkbox_widgets = {
            'δv': self.ticklist_widgets.get("ticklist_sofv"),
            'νv': self.ticklist_widgets.get("ticklist_nuv"),
            'δh': self.ticklist_widgets.get("ticklist_sofh"),
            'νh': self.ticklist_widgets.get("ticklist_nuh"),
            'σ': self.ticklist_widgets.get("ticklist_sig"),
            'σt': self.ticklist_widgets.get("ticklist_sigt"),
            'δvt': self.ticklist_widgets.get("ticklist_sofvt"),
            'δht': self.ticklist_widgets.get("ticklist_sofht"),
        }

        for param in self.checkbox_params:
            checkbox = self.checkbox_widgets[param]
            checkbox.stateChanged.connect(
                lambda state, param=param: self.update_df_value(param, state)
            )

        # Add a submit button to handle updates
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_changes)


        self.control_panel_2.addWidget(self.submit_button)

        result_layout.addWidget(self.control_panel_1)
        result_layout.addWidget(self.control_panel_2)
        self.result_window.resize(600, 400)
        self.result_window.show()


    def populate_left_panel(self):
        self.left_control_panel.addFlexibleRow([
            ('button', 'Choose Project Path', self.choose_project_path)
        ])
        temp = self.left_control_panel.addFlexibleRow([
            ('combo', 'Select File', ["Please Choose Project Path first"])
        ])
        self.left_control_panel.addFlexibleRow([
            ('button', 'Export to csv', self.export_to_csv)
        ])
        self.mat_file_dropdown = temp.get('combo_Select File')
        self.mat_file_dropdown.setGeometry(50, 50, 400, 30)  # Set position and size
        self.mat_file_dropdown.currentIndexChanged.connect(self.on_mat_file_selected)  # Connect to the handler

        self.plot_canvas_loc = PlotCanvas(parent=self)
        self.left_control_panel.addPlotCanvas(self.plot_canvas_loc.get_layout())


    def populate_middle_panel(self):
        pass


    def populate_right_panel(self):
        pass


    def choose_project_path(self):
        # folder_path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        self.folder_path = r"D:\MATLAB_DRIVE\MATLAB_PROJ\Xu\CPT数据库 (1)"
        if self.folder_path:
            self.initPD()
            self.load_mat_files(self.folder_path)
            self.update_mat_file_dropdown()  # Update the dropdown list
            self.plot_current_mat_file(initial=True)


    def initPD(self):
        input_csv_file_path = os.path.join(self.folder_path, 'results_summary.csv')
        if os.path.exists(input_csv_file_path):
            self.df = pd.read_csv(input_csv_file_path)
        else:
            self.df = pd.DataFrame(columns=["Site Name", "Cluster", "File Name", "δv", "νv", "δh", "νh", "σ", "σt", "δvt", "δht"])
    
    
    def update_mat_file_dropdown(self):
        # Clear existing items
        self.mat_file_dropdown.clear()
        # Populate the dropdown with .mat file names
        for mat_path in self.mat_files:
            # Split the path into directory and base file
            directory, base_file = os.path.split(mat_path)
            # Get the directory 2 levels up
            up_two_levels = os.path.abspath(os.path.join(directory, '..'))
            # Get the folder name from the 2 levels up directory
            folder_name = os.path.basename(up_two_levels)
            self.mat_file_dropdown.addItem(f"{folder_name}-{os.path.basename(mat_path)}", mat_path)


    # def update_checkbox_state(self, checkbox_name, state):
    #     mat_path = self.mat_files[self.current_file_index]
    #     if mat_path not in self.checkbox_states:
    #         self.checkbox_states[mat_path] = {}
    #     self.checkbox_states[mat_path][checkbox_name] = state


    #     # Example method to connect to checkbox stateChanged signal
    # def checkbox_state_changed(self, state, checkbox_name):
    #     # Convert state to boolean
    #     is_checked = state == Qt.Checked
    #     # Update the state in the dictionary
    #     self.update_checkbox_state(checkbox_name, is_checked)


    def on_mat_file_selected(self, index):
        if index >= 0 and index < len(self.mat_files):
            self.current_file_index = index
            mat_path = self.mat_files[self.current_file_index]
            
            # Check if the .mat file has been visited before
            if mat_path not in self.checkbox_states:
                # Initialize the state to "Unidentifiable" for each checkbox
                self.checkbox_states[mat_path] = {'Checkbox 1': False, 'Checkbox 2': False}
            
            # Apply the stored or default states
            states = self.checkbox_states[mat_path]
            # for checkbox_name, checkbox_widget in self.control_panel.created_widgets.items():
            #     if checkbox_name in states:
            #         checkbox_widget.setChecked(states[checkbox_name])
                
            self.plot_current_mat_file()


    def list_mat_files(self, project_folder):
        mat_files = []
        # Walk through the directory tree starting from the project_folder
        for root, dirs, files in os.walk(project_folder):
            # Check if the current folder's name is 'results TMCMC'
            if 'results_TMCMC' in root:
                for file in files:
                    # Check if the file ends with '.mat'
                    if file.endswith('.mat'):
                        # Construct the file's path and add it to the list
                        mat_files.append(os.path.join(root, file))
        return mat_files


    def load_mat_files(self, folder_path):
        self.mat_files.clear()
        # Walk through the directory
        i = 0
        for root, dirs, files in os.walk(folder_path):
            # Check if 'results_TMCMC' is in the path and the folder starts with "Cluster"
            if 'results_TMCMC' in root and any(dir_name.startswith("Cluster ") for dir_name in root.split(os.sep)):
                for file in files:
                    if file.endswith(".mat"):
                        mat_path = os.path.join(root, file)
                        self.mat_files.append(mat_path)
                        self.cache_mat_file(mat_path)
                        print(f'Caching {mat_path} ...')
                        directory, base_file = os.path.split(mat_path)
                        up_two_levels = os.path.abspath(os.path.join(directory, '..'))
                        cluster_name = os.path.basename(up_two_levels)
                        # Append a new row to the DataFrame
                        if self.df[(self.df["Cluster"] == cluster_name) & (self.df["File Name"] == base_file)].empty:
                            new_row = pd.DataFrame({
                                "Site Name": "",  # Assuming Site Name is not determined here
                                "Cluster": cluster_name,
                                "File Name": base_file,
                                "δv": "",
                                "νv": "",
                                "δh": "",
                                "νh": "",
                                "σ": "",
                                "σt": "",
                                "δvt": "",
                                "δht": "",
                            }, index=[0])
                            print(new_row)
                            # Correct usage of append method
                            self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.current_file_index = 0
        print(self.df)


    def cache_mat_file(self, mat_path):
        # Check if data is in cache
        if mat_path in self.data_cache:
            return self.data_cache[mat_path]

        # Load and process data if not in cache
        data = loadmat(mat_path)
        x, x_low_GP, x_up_GP = data['x'], data['x_low'], data['x_up']
        processed_data = self.extract_data(x, x_low_GP, x_up_GP)  # Assume this is a method you define to process your data

        # Store in cache
        self.data_cache[mat_path] = processed_data


    def extract_data(self, x, x_low_GP, x_up_GP):
        # Calculating various parameters from x
        x_low_GP = x_low_GP.flatten()
        x_up_GP = x_up_GP.flatten()
    
        sig = np.sqrt(1/np.exp(x[:, 0]))
        sofv = np.exp(x[:, 1])
        sofh = np.exp(x[:, 2])
        nuv = np.exp(x[:, 3])
        nuh = np.exp(x[:, 4])
        sig_t = np.sqrt(1/np.exp(x[:, 5]))
        sofv_t = np.exp(x[:, 6])
        sofh_t = np.exp(x[:, 7])
        
        # Adjusting limits
        xlim_low = np.exp(x_low_GP)
        xlim_low[0], xlim_low[5] = np.sqrt(1/xlim_low[0]), np.sqrt(1/xlim_low[5])
        xlim_up = np.exp(x_up_GP)
        xlim_up[0], xlim_up[5] = np.sqrt(1/xlim_up[0]), np.sqrt(1/xlim_up[5])
        
        return sig, sofv, sofh, nuv, nuh, sig_t, sofv_t, sofh_t, xlim_low, xlim_up
    
    
    def plot_current_mat_file(self, initial=False, show_95_line=False):
        if not self.mat_files:
            return

        self.plot_canvas_result.clear_plot()  # Clear existing plots

        mat_path = self.mat_files[self.current_file_index]
        # processed_data = self.cache_mat_file(mat_path)
        processed_data = self.data_cache.get(mat_path)
        sig, sofv, sofh, nuv, nuh, sig_t, sofv_t, sofh_t, xlim_low, xlim_up = processed_data

        # Plot the data
        # self.plot_canvas_multiple.plot_extracted_data(sig, sofv, sofh, nuv, nuh, sig_t, sofv_t, sofh_t, xlim_low, xlim_up)
        plot_param = {'marker':'s', 'markersize':4, 'color':'lightgrey', 'linestyle':'', 'alpha':0.5}
        plot_param_mean = {'marker':'o', 'markersize':4, 'color':'red', 'linestyle':''}
        line_param = {'color':'lightblue', 'linestyle':'--'}
        self.plot_canvas_result.loglog(nuv, sofv, subplot_index=0, **plot_param)
        self.plot_canvas_result.loglog(np.mean(nuv), np.mean(sofv), subplot_index=0, **plot_param_mean)
        self.plot_canvas_result.set_plot_attributes(subplot_index=0, xlim=(xlim_low[3], xlim_up[3]), ylim=(xlim_low[1], xlim_up[1]))
        self.plot_canvas_result.set_aspect_ratio(aspect='auto', subplot_index=0)
        self.plot_canvas_result.loglog(nuh, sofh, subplot_index=1, **plot_param)
        self.plot_canvas_result.loglog(np.mean(nuh), np.mean(sofh), subplot_index=1, **plot_param_mean)
        self.plot_canvas_result.set_plot_attributes(subplot_index=1, xlim=(xlim_low[4], xlim_up[4]), ylim=(xlim_low[2], xlim_up[2]))
        self.plot_canvas_result.loglog(sig, sig_t, subplot_index=2, **plot_param)
        self.plot_canvas_result.loglog(np.mean(sig), np.mean(sig_t), subplot_index=2, **plot_param_mean)
        self.plot_canvas_result.set_plot_attributes(subplot_index=2, xlim=(xlim_up[0], xlim_low[0]), ylim=(xlim_up[5], xlim_low[5]))
        self.plot_canvas_result.loglog(sofv_t, sofh_t, subplot_index=3, **plot_param)
        self.plot_canvas_result.loglog(np.mean(sofv_t), np.mean(sofh_t), subplot_index=3, **plot_param_mean)
        self.plot_canvas_result.set_plot_attributes(subplot_index=3, xlim=(xlim_low[6], xlim_up[6]), ylim=(xlim_low[7], xlim_up[7]))

        if show_95_line:
            self.plot_canvas_result.add_hline(np.percentile(sofv, 2.5), subplot_index=0, **line_param)
            self.plot_canvas_result.add_hline(np.percentile(sofv, 97.5), subplot_index=0, **line_param)
            self.plot_canvas_result.add_vline(np.percentile(nuv, 2.5), subplot_index=0, **line_param)
            self.plot_canvas_result.add_vline(np.percentile(nuv, 97.5), subplot_index=0, **line_param)
            self.plot_canvas_result.add_hline(np.percentile(sofh, 2.5), subplot_index=1, **line_param)
            self.plot_canvas_result.add_hline(np.percentile(sofh, 97.5), subplot_index=1, **line_param)
            self.plot_canvas_result.add_vline(np.percentile(nuh, 2.5), subplot_index=1, **line_param)
            self.plot_canvas_result.add_vline(np.percentile(nuh, 97.5), subplot_index=1, **line_param)
            self.plot_canvas_result.add_hline(np.percentile(sig_t, 2.5), subplot_index=2, **line_param)
            self.plot_canvas_result.add_hline(np.percentile(sig_t, 97.5), subplot_index=2, **line_param)
            self.plot_canvas_result.add_vline(np.percentile(sig, 2.5), subplot_index=2, **line_param)
            self.plot_canvas_result.add_vline(np.percentile(sig, 97.5), subplot_index=2, **line_param)
            self.plot_canvas_result.add_hline(np.percentile(sofh_t, 2.5), subplot_index=3, **line_param)
            self.plot_canvas_result.add_hline(np.percentile(sofh_t, 97.5), subplot_index=3, **line_param)
            self.plot_canvas_result.add_vline(np.percentile(sofv_t, 2.5), subplot_index=3, **line_param)
            self.plot_canvas_result.add_vline(np.percentile(sofv_t, 97.5), subplot_index=3, **line_param)
        if initial:
            self.plot_canvas_result.store_initial_limits()
        # self.plot_canvas_result.set_axis_to_log(axis='both')
        # Set the title
        cluster_name = os.path.basename(os.path.dirname(os.path.dirname(mat_path)))
        mat_file_name = os.path.basename(mat_path)
        title = f"{cluster_name}, {mat_file_name.replace('_', '-')}"
        self.plot_canvas_result.set_suptitle(title)

        directory, base_file = os.path.split(mat_path)
        up_two_levels = os.path.abspath(os.path.join(directory, '..'))
        cluster_name = os.path.basename(up_two_levels)
        self.set_checkboxes(cluster_name, base_file)

    
    def set_checkboxes(self, cluster_name, base_file):
        row = self.df[(self.df["Cluster"] == cluster_name) & (self.df["File Name"] == base_file)]
        if not row.empty:
            for param in self.checkbox_params:
                value = row.iloc[0][param]
                checkbox = self.checkbox_widgets[param]
                try:
                    # Attempt to convert the value to float
                    float_value = float(value)
                    if math.isnan(float_value):
                        checkbox.setChecked(False)
                        checkbox.setText("To check")
                    else:
                        checkbox.setChecked(True)
                        checkbox.setText("Identifiable")
                except ValueError:
                    # If conversion fails, check if it's NaN
                    if pd.isna(value):
                        checkbox.setText("To check")
                    else:
                        checkbox.setChecked(False)
                        checkbox.setText("Unidentifiable")
                except TypeError:
                    # Handle the case where value is None or similar
                    checkbox.setText("To check")


    def update_df_value(self, param, state):
        # Find the current mat file's cluster name and file name
        mat_path = self.mat_files[self.current_file_index]
        directory, base_file = os.path.split(mat_path)
        up_two_levels = os.path.abspath(os.path.join(directory, '..'))
        cluster_name = os.path.basename(up_two_levels)

        # Locate the row in the DataFrame
        # row_index = self.df[(self.df["Cluster"] == cluster_name) & (self.df["File Name"] == base_file)].index
        # Locate the row in the DataFrame
        row_indices = self.df[(self.df["Cluster"] == cluster_name) & (self.df["File Name"] == base_file)].index.tolist()        # # Check the state and update the DataFrame accordingly
        #  Check if row_indices is not empty and contains exactly one index
        if row_indices:
            row_index = row_indices[0]  # Assuming only one match, otherwise, you'll need to handle multiple matches
            if state == Qt.Checked:
                # If checked, mark as "Identifiable"
                self.df.at[row_index, param] = 1
            else:
                # If unchecked, mark as "Unidentifiable"
                self.df.at[row_index, param] = "<0"
        else:
            print("Row not found.")

        # print(self.df.at[row_index, param])


    def submit_changes(self):
        pass

    
    def export_to_csv(self):
        output_csv_file_path = os.path.join(self.folder_path, 'results_summary.csv')
        self.df.to_csv(output_csv_file_path, index=False)


    def prev_mat_file(self):
        if self.current_file_index > 0:
            self.current_file_index -= 1
            self.plot_current_mat_file(initial=True)


    def next_mat_file(self):
        if self.current_file_index < len(self.mat_files) - 1:
            self.current_file_index += 1
            self.plot_current_mat_file(initial=True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CPTResultInspector()
    window.show()
    sys.exit(app.exec_())
