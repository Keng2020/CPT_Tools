import os
import numpy as np
import pandas as pd
from scipy.io import savemat

class DataManager:
    def __init__(self):
        self.project_path = ""
        self.cluster_name = ""
        self.file_name_list = []
        self.nztm_data_dict = {}
        self.integrated_data_ori = None
        self.integrated_data_plot = None
        self.integrated_data_export = None
        self.keep_data_boolean_df = None
        self.keep_file_boolean_df = None

    def load_project_data(self, project_path):
        self.project_path = project_path
        # Reset or initialize other attributes if needed
        self.cluster_name = ""
        self.file_name_list = []
        self.nztm_data_dict = {}
        # Load data according to your project's structure
        # This method needs to be implemented based on your specific project data format

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
        self.set_color_for_files()
        self.closest_file_ids_dict = self.create_closest_file_ids_dict()

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

    def export_to_matlab(self, directory=None):
        if directory is None:
            directory = self.project_path
        filepath = os.path.join(directory, self.cluster_name, 'clean_data_from_python.mat')
        mat_data = {
            'integrated_data_ori': self._df_to_mat(self.integrated_data_ori),
            'integrated_data_plot': self._df_to_mat(self.integrated_data_plot),
            'integrated_data_export': self._df_to_mat(self.integrated_data_export),
            'keep_data_boolean_df': self._df_to_mat(self.keep_data_boolean_df),
            'keep_file_boolean_df': self._series_to_mat(self.keep_file_boolean_df),
            'file_name_list': self.file_name_list,
            'nztm_data': self._nztm_to_mat(),
            # Add other data as needed
        }
        savemat(filepath, mat_data)
        print(f"Data successfully exported to {filepath}")

    def _df_to_mat(self, df):
        # Convert DataFrame to MATLAB-compatible format
        return {col: df[col].values for col in df.columns}

    def _series_to_mat(self, series):
        # Convert Series to MATLAB-compatible format
        return {series.name: series.values}

    def _nztm_to_mat(self):
        # Convert NZTM data dictionary to MATLAB-compatible format
        return {
            'file_ids': list(self.nztm_data_dict.keys()),
            'nztmX': [data['nztmX'] for data in self.nztm_data_dict.values()],
            'nztmY': [data['nztmY'] for data in self.nztm_data_dict.values()],
        }
