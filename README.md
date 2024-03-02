# CPT Data Editor

CPT Data Editor is a comprehensive tool designed for the visualization and manipulation of Cone Penetration Test (CPT) data. Built using PyQt5, it provides a user-friendly interface for selecting projects, visualizing data, editing data within selected depth ranges, and exporting the modified data for further analysis.

## Features

- **Project Selection:** Easily choose a project path to work with CPT data.
- **Data Visualization:** View plots of CPT data, including location plots, main data plots, and export plots.
- **Data Editing:** Interactively select regions within the plot to clear or recover data points.
- **Depth Selection:** Specify depth ranges for focused analysis or modifications.
- **Export Functionality:** Export modified data to MATLAB `.mat` files for further analysis.

## Installation

To run the CPT Data Editor, you'll need a Windows environment. The tool is packaged as an executable file for ease of use.

1. **Download the Tool:** Download the `CPTDataEditor.exe` file from 'dist/' folder.
2. **Run the Executable:** Double-click on the executable file to launch the application. No installation is required.

## Getting Started

### Launching the Tool

After downloading, simply double-click on `CPTDataEditor.exe` to start the application. The main interface will open, presenting you with the control panels and plot areas.

## File Structure

Before using the CPT Data Editor, ensure your data is organized according to the following file tree structure:


```
Clusters
└─Cluster 1083
  │  Cluster 1083.csv            # Metadata (include location for each soundings)
  │  ...                         # Original data files
  └─Extracted                    # Organized original data files
      │  ...                     

```
This structure is crucial for the CPT Data Editor to correctly locate and process your CPT data.


### Choosing a Project Path

1. Click on the "Choose Project Path" button in the left control panel.
2. Upon selecting the "Clusters" directory, a dropdown list will appear, displaying each available cluster. Select the desired cluster from this list to proceed with your analysis. This step ensures you're working within the structured directory outlined in the File Structure section above.


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

## Troubleshooting

If you encounter issues while using the CPT Data Editor, please ensure that you have the necessary permissions to read and write to the chosen project directory. For other issues, refer to the FAQs section or contact support.

## FAQs

*Q: Can I run this tool on macOS or Linux?*

A: Currently, the CPT Data Editor is only available for Windows. Support for other operating systems is planned for future releases.

*Q: What types of CPT data files can I use with this tool?*

A: The tool is designed to work with `.csv` files for CPT data and `.mat` files for MATLAB integration.

## Support

For further assistance or to report bugs, please email yongkengabc.com.

## License

This software is licensed under the MIT License. See the LICENSE file for more details.
