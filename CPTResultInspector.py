from plotcanvas import PlotCanvas
from controlpanel import ControlPanel
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QGridLayout,
                             QFileDialog)
import numpy as np
from scipy.io import loadmat
import os

class CPTResultsInspector(QMainWindow):
    def __init__(self):
        super().__init__()

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        
        self.setup_layout()

        self.mat_files = []  # To store paths of .mat files
        self.current_file_index = 0  # To keep track of the current .mat file being plotted

    def setup_layout(self):
        main_grid_layout = QGridLayout(self.main_widget)

        self.control_panel_1 = ControlPanel(self)
        self.control_panel_2 = ControlPanel(self)

        # Add control panel instances to the layout 
        main_grid_layout.addWidget(self.control_panel_1, 0, 0)
        # main_grid_layout.addWidget(self.control_panel_2, 0, 1)

        main_grid_layout.setColumnStretch(0, 1)
        # main_grid_layout.setColumnStretch(1, 2)

        self.populate_left_panel()
        self.populate_middle_panel()
        # self.populate_right_panel()

    def populate_left_panel(self):
        self.control_panel_1.addFlexibleRow([
            ('button', 'Choose Project Path', self.choose_project_path)
        ])
        self.control_panel_1.addFlexibleRow([
            ('button', 'Previous', self.prev_mat_file),
            ('button', 'Next', self.next_mat_file)
        ])
        self.plot_canvas_multiple = PlotCanvas(parent=self, use_subplots=True, nrows=2, ncols=2)

                
        self.control_panel_1.addWidget(self.plot_canvas_multiple)

            # Assuming you have your data (x, x_low_GP, x_up_GP) ready
        # sig, sofv, sofh, nuv, nuh, sig_t, sofv_t, sofh_t, xlim_low, xlim_up = self.extract_data(x, x_low_GP, x_up_GP)
        
        # # Now plot using the adapted method in PlotCanvas
        # self.plot_canvas_multiple.plot_extracted_data(sig, sofv, sofh, nuv, nuh, sig_t, sofv_t, sofh_t, xlim_low, xlim_up)

    def choose_project_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder_path:
            self.load_mat_files(folder_path)
            self.plot_current_mat_file()

    # def load_mat_files(self, folder_path):
    #     self.mat_files.clear()
    #     for root, dirs, files in os.walk(folder_path):
    #         for file in files:
    #             if file.endswith(".mat") and 'results_TMCMC' in root:
    #                 self.mat_files.append(os.path.join(root, file))
    #     self.current_file_index = 0
    def load_mat_files(self, folder_path):
        self.mat_files.clear()
        # Walk through the directory
        for root, dirs, files in os.walk(folder_path):
            # Check if 'results_TMCMC' is in the path and the folder starts with "Cluster"
            if 'results_TMCMC' in root and any(dir_name.startswith("Cluster ") for dir_name in root.split(os.sep)):
                for file in files:
                    if file.endswith(".mat"):
                        self.mat_files.append(os.path.join(root, file))
        self.current_file_index = 0
        if self.mat_files:
            self.plot_current_mat_file()
        else:
            print("No .mat files found in the specified directory.")

    # def plot_current_mat_file(self):
    #     if not self.mat_files:
    #         return
    #     mat_path = self.mat_files[self.current_file_index]
    #     data = loadmat(mat_path)
    #     # Assuming the .mat file contains 'x', 'x_low_GP', and 'x_up_GP'
    #     x, x_low_GP, x_up_GP = data['x'], data['x_low'], data['x_up']
        
    #     # Extract data
    #     sig, sofv, sofh, nuv, nuh, sig_t, sofv_t, sofh_t, xlim_low, xlim_up = self.extract_data(x, x_low_GP, x_up_GP)
        
    #     # Plot the data
    #     self.plot_canvas_multiple.plot_extracted_data(sig, sofv, sofh, nuv, nuh, sig_t, sofv_t, sofh_t, xlim_low, xlim_up)

    #     # Set the title based on the cluster and .mat file name
    #     cluster_name = os.path.basename(os.path.dirname(os.path.dirname(mat_path)))
    #     mat_file_name = os.path.basename(mat_path)
    #     title = f"Cluster {cluster_name}, {mat_file_name.replace('_', '-')}"
    #     # print(cluster_name)
    #     # print(mat_file_name)
    #     # title = 'test'
    #     self.plot_canvas_multiple.fig.suptitle(title)  # Assuming you're using matplotlib's Figure for PlotCanvas
    #     self.plot_canvas_multiple.draw()
    def plot_current_mat_file(self):
        if not self.mat_files:
            return

        self.plot_canvas_multiple.clear_plots()  # Clear existing plots

        mat_path = self.mat_files[self.current_file_index]
        data = loadmat(mat_path)
        x, x_low_GP, x_up_GP = data['x'], data['x_low'], data['x_up']

        sig, sofv, sofh, nuv, nuh, sig_t, sofv_t, sofh_t, xlim_low, xlim_up = self.extract_data(x, x_low_GP, x_up_GP)

        # Plot the data
        self.plot_canvas_multiple.plot_extracted_data(sig, sofv, sofh, nuv, nuh, sig_t, sofv_t, sofh_t, xlim_low, xlim_up)

        # Set the title
        cluster_name = os.path.basename(os.path.dirname(os.path.dirname(mat_path)))
        mat_file_name = os.path.basename(mat_path)
        title = f"{cluster_name}, {mat_file_name.replace('_', '-')}"
        self.plot_canvas_multiple.fig.suptitle(title)
        # self.plot_canvas_multiple.make_subplots_square()  # Make all subplots square
        self.plot_canvas_multiple.draw()
        self.plot_canvas_multiple.adjust_subplots()


    def prev_mat_file(self):
        if self.current_file_index > 0:
            self.current_file_index -= 1
            self.plot_current_mat_file()

    def next_mat_file(self):
        if self.current_file_index < len(self.mat_files) - 1:
            self.current_file_index += 1
            self.plot_current_mat_file()

    def populate_middle_panel(self):
        self.plot_canvas_2 = PlotCanvas(self)

        self.control_panel_2.addWidget(self.plot_canvas_2)

    
    
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
    

    
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = CPTResultsInspector()
    window.show()
    sys.exit(app.exec_())