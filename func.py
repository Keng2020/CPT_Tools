import os

def find_folders_with_subfolders(base_dir, parent_folder_hint, subfolder_name):
    """
    List all folders within base_dir containing a specific subfolder. This function allows 
    searching for parent folders that contain a hint in their names (like 'Cluster') and 
    check if they contain a specific subfolder.

    :param base_dir: The base directory to search within.
    :param parent_folder_hint: A substring to look for in parent folder names. Use and empty
                                string ('') to match all folders.
    :param subfolder_name: The name of the subfolder to search for within parent folders.
    """

    folders_with_subfolder = []

    for root, dirs, files in os.walk(base_dir):
        # Check if parent folder name contains the specific hint.
        if parent_folder_hint in os.path.basename(root) and subfolder_name in dirs:
            folders_with_subfolder.append(root) 
        
    return folders_with_subfolder
