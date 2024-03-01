import os
import csv
import scipy.io
import numpy as np

def read_mat_file(root_directory, cluster_folder, mat_file, writer, X_c, Y_c, lon_c, lat_c, road, suburb, city, county, state, postcode, site_name):
    mat_file_path = os.path.join(root_directory, cluster_folder, 'results_TMCMC', mat_file)
    mat_data = scipy.io.loadmat(mat_file_path)
    X, Y = mat_data['X'], mat_data['Y']

    # Example of how to read additional data from the mat file
    # Update these variables based on actual data structure
    temp_h = mat_data.get('temp_h', np.array([]))
    z = mat_data.get('z', np.array([]))
    x = mat_data.get('x', np.zeros((2000, 8)))  # Assuming 'x' is the matrix mentioned for calculations

    no_of_soundings = temp_h.size
    length = z[-1] - z[0] if len(z) > 0 else 'N/A'
    min_dist = np.sort(temp_h.flatten())[:3] if temp_h.size >= 3 else ['N/A'] * 3  # Flatten in case temp_h is not 1-D
    max_dist = np.max(z) if len(z) > 0 else 'N/A'
    
    # Calculations for sig, sof_v, sof_h, nu_v, nu_h, sig_t, sof_v_t, sof_h_t
    sig = np.sqrt(1 / np.exp(x[:, 0]))
    sof_v = np.exp(x[:, 1])
    sof_h = np.exp(x[:, 2])
    nu_v = np.exp(x[:, 3])
    nu_h = np.exp(x[:, 4])
    sig_t = np.sqrt(1 / np.exp(x[:, 5]))
    sof_v_t = np.exp(x[:, 6])
    sof_h_t = np.exp(x[:, 7])
    
    # Calculating means and percentiles
    def calculate_stats(arr):
        return np.mean(arr), np.percentile(arr, 2.5), np.percentile(arr, 97.5)

    sig_mean, sig_2_5, sig_97_5 = calculate_stats(sig)
    sof_v_mean, sof_v_2_5, sof_v_97_5 = calculate_stats(sof_v)
    sof_h_mean, sof_h_2_5, sof_h_97_5 = calculate_stats(sof_h)
    nu_v_mean, nu_v_2_5, nu_v_97_5 = calculate_stats(nu_v)
    nu_h_mean, nu_h_2_5, nu_h_97_5 = calculate_stats(nu_h)
    sig_t_mean, sig_t_2_5, sig_t_97_5 = calculate_stats(sig_t)
    sof_v_t_mean, sof_v_t_2_5, sof_v_t_97_5 = calculate_stats(sof_v_t)
    sof_h_t_mean, sof_h_t_2_5, sof_h_t_97_5 = calculate_stats(sof_h_t)
    

    result = {
        "Cluster": cluster_folder,
        "mat_file_name": mat_file,
        "X_c": X_c,
        "Y_c": Y_c,
        "lon_c": lon_c,
        "lat_c": lat_c,
        "road": road,
        "suburb": suburb,
        "city": city,
        "county": county,
        "state": state,
        "postcode": postcode,
        "site name": site_name,
        "no_of_soundings": no_of_soundings,
        "length": length,
        "min_dist_1": min_dist[0],
        "min_dist_2": min_dist[1],
        "min_dist_3": min_dist[2],
        "max_dist": max_dist,
        "sig_mean": sig_mean,
        "sig_2.5": sig_2_5,
        "sig_97.5": sig_97_5,
        "sof_v_mean": sof_v_mean,
        "sof_v_2.5": sof_v_2_5,
        "sof_v_97.5": sof_v_97_5,
        "sof_h_mean": sof_h_mean,
        "sof_h_2.5": sof_h_2_5,
        "sof_h_97.5": sof_h_97_5,
        "nu_v_mean": nu_v_mean,
        "nu_v_2.5": nu_v_2_5,
        "nu_v_97.5": nu_v_97_5,
        "nu_h_mean": nu_h_mean,
        "nu_h_2.5": nu_h_2_5,
        "nu_h_97.5": nu_h_97_5,
        "sig_t_mean": sig_t_mean,
        "sig_t_2.5": sig_t_2_5,
        "sig_t_97.5": sig_t_97_5,
        "sof_v_t_mean": sof_v_t_mean,
        "sof_v_t_2.5": sof_v_t_2_5,
        "sof_v_t_97.5": sof_v_t_97_5,
        "sof_h_t_mean": sof_h_t_mean,
        "sof_h_t_2.5": sof_h_t_2_5,
        "sof_h_t_97.5": sof_h_t_97_5,
    }
    writer.writerow(result)

def process_file(file_name, root_directory, cluster_folder, writer, X_c, Y_c, lon_c, lat_c, road, suburb, city, county, state, postcode, site_name):
    read_mat_file(root_directory, cluster_folder, file_name, writer, X_c, Y_c, lon_c, lat_c, road, suburb, city, county, state, postcode, site_name)


if __name__ == "__main__":
    root_directory = r"../"  # Adjust as necessary
    input_csv_file_path = 'updated_results.csv'  # Ensure this is your input CSV

    with open('results_final.csv', 'w', newline='', encoding='utf-8') as output_csvfile:
        fieldnames = ['Cluster', 'mat_file_name', 'X_c', 'Y_c', 'lon_c', 'lat_c', 'road', 'suburb', 'city', 'county', 'state', 'postcode', 'site name',
                      'no_of_soundings', 'length', 'min_dist_1', 'min_dist_2', 'min_dist_3', 'max_dist',
                      'sig_mean', 'sig_2.5', 'sig_97.5', 'sof_v_mean', 'sof_v_2.5', 'sof_v_97.5',
                      'sof_h_mean', 'sof_h_2.5', 'sof_h_97.5', 'nu_v_mean', 'nu_v_2.5', 'nu_v_97.5',
                      'nu_h_mean', 'nu_h_2.5', 'nu_h_97.5', 'sig_t_mean', 'sig_t_2.5', 'sig_t_97.5',
                      'sof_v_t_mean', 'sof_v_t_2.5', 'sof_v_t_97.5', 'sof_h_t_mean', 'sof_h_t_2.5', 'sof_h_t_97.5']
        writer = csv.DictWriter(output_csvfile, fieldnames=fieldnames)
        writer.writeheader()

        with open(input_csv_file_path, mode='r', encoding='utf-8') as input_csvfile:
            csvreader = csv.DictReader(input_csvfile)
            for row in csvreader:
                cluster_folder = row['Cluster']
                mat_file_name = row['mat_file_name']
                cluster_path = os.path.join(root_directory, cluster_folder, 'results_TMCMC')
                if os.path.exists(cluster_path) and os.path.isdir(cluster_path):
                    for mat_file in os.listdir(cluster_path):
                        if mat_file.endswith('.mat'):
                                process_file(mat_file, root_directory, cluster_folder, writer,
                                    row['X_c'], row['Y_c'], row['lon_c'], row['lat_c'], 
                                    row['road'], row['suburb'], row['city'], row['county'], 
                                    row['state'], row['postcode'], row['site name'])