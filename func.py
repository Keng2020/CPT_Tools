import os
import shutil

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


def copy_folders_with_subfolders(src_directory, dest_directory, folder_hint='', subfolder_name=''):
    """
    Copies all folders from src_directory that contain a specified subfolder to dest_directory.

    :param src_directory: The base directory to search within.
    :param dest_directory: The destination directory where folders are copied.
    :param folder_hint: A substring to identify relavant folders. Use an empty string to match all folders.
    :param subfolder_name: The name of the subfolder to seach for within the parent folders.
    """
    for root, dirs, _ in os.walk(src_directory):
        folder_name = os.path.basename(root)
        # Check if the folder matches the hint (if provided) and contains the specific subfolder.
        if (folder_hint in folder_name or not folder_hint) and subfolder_name in dirs:
            dest_path = os.path.join(dest_directory, os.path.relpath(root, src_directory))
            try:
                # Ensure the destination path does not already exist to prevent overwriting.
                if not os.path.exists(dest_path):
                    shutil.copytree(root, dest_path)
                    print(f"Copied '{root}' to '{dest_path}'")
                else:
                    print(f"Destination '{dest_path}' already exists. Skipping.")
            except Exception as e:
                print(f"Error copying '{root}' to '{dest_path}': {e}")
