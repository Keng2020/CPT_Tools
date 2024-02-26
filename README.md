# CPT Data Editor

CPT Data Editor is a comprehensive application designed for geotechnical engineers and researchers to visualize, analyze, and edit Cone Penetration Test (CPT) data. Built with PyQt5 and integrating powerful data processing libraries like Pandas and NumPy, this tool provides a user-friendly interface for managing CPT data, including viewing plots, editing data ranges, and exporting modified datasets for further analysis.

## Features

- **Data Visualization**: Easily visualize CPT data in interactive plots. Compare multiple datasets simultaneously for in-depth analysis.
- **Data Editing**: Select specific data regions for detailed editing. Clear or recover data points to refine your analysis.
- **Export Capabilities**: Export your edited datasets to MATLAB format for further analysis or integration with other tools.
- **Interactive Selection**: Use rectangle selectors to interactively choose data points on plots for editing.
- **Cluster Management**: Organize your CPT data into clusters and select clusters for detailed examination.
- **Customizable Plots**: Adjust plot settings and export visualization as needed.

## Installation

The CPT Data Editor is distributed as an executable file (.exe), simplifying the installation process. There's no need to install Python or any dependencies manually.

### Steps to install:

1. Download the `CPTDataEditor.exe` file from the latest release.
2. Place the `.exe` file in a desired directory.
3. Double-click the `.exe` file to launch the CPT Data Editor.

Note: Depending on your Windows security settings, you may need to allow permissions or create an exception in your firewall to run the application for the first time.

## Usage

Upon launching the CPT Data Editor, you will be greeted with a user-friendly interface divided into several panels for data management and visualization.

## Choosing the Project Folder

The CPT Data Editor organizes CPT data into clusters within the project folder. Each cluster contains individual CPT data files and an `Extracted` subfolder for processed data. To efficiently use the application, your project folder should follow this structure:

project_folder/
└── Cluster 1/
    ├── CPT xxx.xlsx
    ├── CPT yyy.xlsx
    └── Extracted/
        ├── CPT xxx.csv
        └── CPT yyy.csv

### Key Features:

- **Choose Project Path**: Select the directory containing your CPT data.
- **Select Cluster**: Choose a specific cluster of data to analyze.
- **Visualization Panels**: View location, main data, and export data plots. Navigate through data points using the provided controls.
- **Edit Data**: Use the rectangle selector tools to clear or recover data points. Submit depth ranges for precise editing.
- **Export Data**: Export edited data to a MATLAB-compatible `.mat` file for further analysis.

## Contributing

Contributions to the CPT Data Editor are welcome. Please refer to the contributing guidelines for more information on how to contribute to the development.

## License

Specify the license under which your tool is released, and include a `LICENSE` file in your repository.
