# CPT Data Workflow

This documentation provides a comprehensive guide to working with Cone Penetration Test (CPT) data using a suite of tools designed for data cleaning, analysis, and results inspection. Follow the steps outlined below to effectively clean your data, perform analyses, and inspect your results.

## Overview

1. **CPT Data Editor:** Clean and prepare your CPT data.
2. **Data Analysis:** Analyze the cleaned data using MATLAB scripts.
3. **CPT Results Inspector:** View and interpret the results of your CPT data analysis.

## Step 1: Cleaning Data with CPT Data Editor

CPT Data Editor is a tool designed for the visualization and manipulation of CPT data. It offers features for project selection, data visualization, data editing, depth selection, and data export.

### Installation

- Requirements: Windows environment.
- Download and run the `CPTDataEditor.exe` file from the 'dist/' folder.

### Getting Started

#### Launching the Tool

- Double-click on `CPTDataEditor.exe` to start the application.

#### File Structure

Ensure your data is organized according to the required file tree structure for the CPT Data Editor to function correctly.

```plaintext
Clusters
└─Cluster 1083
  │  Cluster 1083.csv            # Metadata
  │  ...                         # Original data files
  └─Extracted                    # Organized original data files
      │  ...                     
```

## Editing Data

- **To Clear Ambiguous Data:** Use the "Select region to clear data" button to draw a rectangle over the plot area. This action clears the data within the selected region, setting the values to NaN, which helps in excluding ambiguous or erroneous data points from your analysis.

- **To Restore Data:** If you wish to regret an action and restore the data you previously cleared, simply use the "Select region to recover data" button and draw a rectangle over the same area. This action restores the data within that region to its original state before any modifications were made.

- Specify the depth ranges to the desired analyzed interval using the "Start Depth" and "End Depth" fields, then click "Submit". This action allows you to focus on a specific interval of your data for analysis or modification.

### Exporting Data

After making the desired modifications, click the "Export to .mat file" button to save your changes. The `clean_data_from_python.mat` file will be directly saved in the "Cluster XX" folder that was selected in the dropdown list, without the need to choose a location manually. The updated structure in the chosen cluster folder will include this newly created file:

```
Clusters
└─Cluster 1083
  │  clean_data_from_python.mat  # Processed data
  │  Cluster 1083.csv            
  │  ...                         
  └─Extracted                    
      │  ...                     

```


## Step 2: Analyzing Data with MATLAB

After cleaning the data with the CPT Data Editor, the next step is to analyze the data using MATLAB. This process involves executing MATLAB scripts that require minimal setup and user input.

### Preparing for Analysis

Before running the analysis scripts:

- Ensure MATLAB is installed on your system.
- Locate the `.mat` files exported from the CPT Data Editor.

### Running Analysis Scripts

1. **Set the Site Name:** Open the MATLAB script. At the beginning of the script, find the `siteName` variable and set it to match the name of your project folder (e.g., `"Cluster 1083"`).

2. **Execute the Script:** Run the script in MATLAB. The script is designed to automatically load the necessary `.mat` file and prepare the data for analysis.

3. **Input Depth Range:** When prompted, enter the start depth and end depth for the analysis. These values define the depth interval you wish to analyze.

By following these steps, the script will analyze the CPT data within the specified depth range. This streamlined approach minimizes manual adjustments and simplifies the analysis process.

### Analysis Output

Upon completing the analysis, a new folder named `results_TMCMC` will be created within your project directory. This folder contains the analysis results, including figures and MATLAB `.mat` files with the analyzed data. The project directory will now look like this:

```
Clusters
└─Cluster 1083
  │  clean_data_from_python.mat  
  │  Cluster 1083.csv            
  │  ...                         
  └─Extracted                    
      │  ...                     
  └─results_TMCMC                # Analysis results
      │  ...                
```
## Step 3: Inspecting Results with CPT Results Inspector

The final step involves inspecting the results of your CPT data analysis.

### Installation and Launching

- Similar to the CPT Data Editor, download and run the executable for the CPT Results Inspector.

### Using the CPT Results Inspector

- Load your analysis results.
- Use the tool's features to view and interpret the data.

## Troubleshooting and Support

If you encounter issues at any step, ensure you have the necessary permissions for the directories you're working with. For specific tool-related issues, refer to the FAQs section or contact support.

## FAQs

Answers to common questions regarding the use of these tools, system requirements, and data file types.

## Support

For further assistance or to report bugs, please email support@example.com.

## License

This software is licensed under the MIT License. See the LICENSE file for more details.
