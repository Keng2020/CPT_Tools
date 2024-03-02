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

### Choosing a Project Path

1. Click on the "Choose Project Path" button in the left control panel.
2. Navigate to the directory containing your CPT data and select it.

### Viewing and Editing Data

- Use the dropdown menus in the left control panel to select clusters and processed clusters.
- Navigate through the plots using the "Previous plot" and "Next plot" buttons.
- To edit data, use the "Select region to clear data" or "Select region to recover data" buttons and draw a rectangle over the plot area.
- Specify depth ranges for modifications using the "Start Depth" and "End Depth" fields, then click "Submit".

### Exporting Data

After making the desired modifications, click the "Export to .mat file" button to save your changes. Choose a location to save the exported `.mat` file.

## Troubleshooting

If you encounter issues while using the CPT Data Editor, please ensure that you have the necessary permissions to read and write to the chosen project directory. For other issues, refer to the FAQs section or contact support.

## FAQs

*Q: Can I run this tool on macOS or Linux?*

A: Currently, the CPT Data Editor is only available for Windows. Support for other operating systems is planned for future releases.

*Q: What types of CPT data files can I use with this tool?*

A: The tool is designed to work with `.csv` files for CPT data and `.mat` files for MATLAB integration.

## Support

For further assistance or to report bugs, please email support@example.com.

## License

This software is licensed under the MIT License. See the LICENSE file for more details.
