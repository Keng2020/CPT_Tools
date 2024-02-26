# CPT Data Editor

The CPT Data Editor is a sophisticated application tailored for geotechnical engineers and researchers, designed to visualize, analyze, and edit Cone Penetration Test (CPT) data. Leveraging the capabilities of PyQt5 and integrating powerful data processing libraries such as Pandas and NumPy, it offers an intuitive interface for comprehensive CPT data management. This includes functionalities for interactive data plotting, precise data editing, and the exportation of modified datasets for advanced analyses.

## Features

- **Data Visualization**: Seamlessly visualize CPT data through interactive plots. Facilitates comparison of multiple datasets for thorough analysis.
- **Data Editing**: Precisely select and edit specific data regions. Features include clearing or recovering data points to refine your dataset.
- **Export Capabilities**: Enables the export of edited datasets in MATLAB format, allowing for further analysis or use with other analytical tools.
- **Interactive Selection**: Utilize rectangle selectors for interactive data point selection on plots, enhancing user control over data editing.
- **Cluster Management**: Efficiently organize your CPT data into clusters for easier analysis and selection.
- **Customizable Plots**: Offers extensive plot customization options, including adjustment of plot settings and visualization exports.

## Installation

CPT Data Editor is conveniently distributed as an executable file (.exe), streamlining the installation process without the need for manual installation of Python or dependencies.

### Installation Steps:

1. Download `CPTDataEditor.exe` from the latest release.
2. Place the executable file in your preferred directory.
3. Double-click on `CPTDataEditor.exe` to initiate the application.

*Note*: Your Windows security settings may prompt you to allow permissions or create a firewall exception to run the application for the first time.

## Usage

Launching the CPT Data Editor presents a user-friendly interface, segmented into multiple panels for efficient data management and visualization.

### Organizing the Project Folder

The CPT Data Editor structures CPT data into clusters within the project folder. Each cluster comprises individual CPT data files and an `Extracted` subfolder for processed data. For optimal use, structure your project folder as follows:

```
project_folder/
└── Cluster 1/
    ├── CPT xxx.xlsx
    ├── CPT yyy.xlsx
    └── Extracted/
        ├── CPT xxx.csv
        └── CPT yyy.csv
```

### Key Functionalities:

- **Choose Project Path**: Navigate and select the directory containing your CPT data.
- **Select Cluster**: Identify and select a specific cluster of data for detailed analysis.
- **Visualization Panels**: Access location, main data, and export data plots. Utilize navigation controls to sift through data points efficiently.
- **Edit Data**: Engage rectangle selector tools for data clearing or recovery. Input depth ranges for targeted editing.
- **Export Data**: Facilitate the exportation of data in a MATLAB-compatible `.mat` file format for extended analysis.

## Contributing

Your contributions to the CPT Data Editor are highly valued. For guidelines on contributing, please consult the project's contributing documentation.

## License

This tool is released under [SPECIFY LICENSE], with the full text available in the `LICENSE` file located in the repository.
