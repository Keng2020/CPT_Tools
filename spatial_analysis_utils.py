import numpy as np
from scipy.spatial.distance import pdist, squareform

def calculate_center_of_geometry(x_data, y_data):
    """
    Calculate the geometric center (centroid) of a set of points.

    Parameters:
    - x_data (iterable): The x-coordinates of the points.
    - y_data (iterable): The y-coordinates of the points.

    Returns:
    - tuple: (center_x, center_y) representing the centroid of the points.

    Raises:
    - ValueError: If x_data and y_data have different lengths.
    """
    if len(x_data) != len(y_data):
        raise ValueError("X and Y data lengths must be the same.")

    center_x = np.mean(x_data)
    center_y = np.mean(y_data)

    return center_x, center_y

def ranking_pairwise_distances(X, Y):
    """
    Computes and ranks pairwise distances between points in 2D space.

    Parameters:
    - X (iterable): X-coordinates of points.
    - Y (iterable): Y-coordinates of points.

    Returns:
    - p1 (numpy.ndarray): Indices of the first point in each point pair.
    - p2 (numpy.ndarray): Indices of the second point in each point pair.
    - sorted_distances (numpy.ndarray): Sorted distances between point pairs.
    """
    X, Y = np.array(X), np.array(Y)
    X, Y = X.reshape(-1, 1), Y.reshape(-1, 1)

    points = np.column_stack((X, Y))
    distances_matrix = squareform(pdist(points))

    mask = np.tril(np.ones_like(distances_matrix), k=-1).astype(bool)
    distances_matrix_lower = distances_matrix[mask]

    original_indices_label_matrix = np.arange(1, distances_matrix.size + 1).reshape(distances_matrix.shape)
    original_indices_label_matrix_lower = np.tril(original_indices_label_matrix, k=-1)
    original_indices_label = original_indices_label_matrix_lower[original_indices_label_matrix_lower != 0]

    sorted_distances = np.sort(distances_matrix_lower)
    sorted_indices = np.argsort(distances_matrix_lower)

    sorted_original_indices_label = original_indices_label[sorted_indices]
    p1, p2 = np.unravel_index(sorted_original_indices_label - 1, distances_matrix.shape)

    return p1, p2, sorted_distances

def find_closest_file_ids(file_id, file_ids, X, Y, num_closest=5):
    """
    Find the closest file IDs to a given file ID based on spatial proximity.

    Parameters:
    - file_id (str): Target file ID.
    - file_ids (list of str): List of all file IDs.
    - X (iterable): X-coordinates associated with each file ID.
    - Y (iterable): Y-coordinates associated with each file ID.
    - num_closest (int, optional): Number of closest file IDs to find. Defaults to 5.

    Returns:
    - list of str: List of the closest file IDs to the given file ID.
    """
    X = np.array(X)
    Y = np.array(Y)

    p1, p2, _ = ranking_pairwise_distances(X, Y)

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
    Extract a unique set from the input data while maintaining the original order.

    Parameters:
    - data (numpy.ndarray): Input array.

    Returns:
    - numpy.ndarray: Array of unique elements in their original order.
    """
    data = data.ravel()
    unique_set, indices = np.unique(data, return_index=True)
    unique_set = unique_set[np.argsort(indices)]
    return unique_set
