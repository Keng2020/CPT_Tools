import os

def list_mat_files(project_folder):
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

# Example usage
project_folder = "D:\MATLAB_DRIVE\MATLAB_PROJ\Xu\CPT数据库 (1)"
mat_files = list_mat_files(project_folder)
print(mat_files)
