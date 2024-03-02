from func import copy_folders_with_subfolders

src_directory = r"D:\MATLAB_DRIVE\MATLAB_PROJ\Xu\CPT数据库 (1)"
target_directory = r"D:\OneDrive_Brilliant\OneDrive\Working\py\NZGD_Proj\Clusters"
folder_name = "Cluster "
subfolder_name = "results_TMCMC"
copy_folders_with_subfolders(src_directory=src_directory, dest_directory=target_directory, folder_hint=folder_name, subfolder_name=subfolder_name)