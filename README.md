# Apple Watch Exploratory Data Analysis
> Preliminary Exploratory Data Analysis of 1 Year of Apple Watch Data

**Goal and Outcome:** The goal of this project was to do some preliminary exploratory data analysis of one persons apple watch data over the course of 2023. Basic findings can be found in /src/frontend/Visualizations.ipynb and the associated png's within /src/frontend

## Extracting Apple Watch Data from the Apple ecosystem:
1. Open the Health app on the iPhone/iPad
2. Navigate to the settings of the Health app (found in the top right of the application, available from Summary or Browse)
3. Scroll to the bottom of the settings page and locate "Export All Health Data"
4. Select the "Export All Health Data" button and wait (5-20 seconds) for compilation of Health data to complete
5. Save the returned "extract.zip" folder or send to a computer via the share options available on the device
6. Extract (unzip) the "extract.zip" folder

### Overall Impression: 
- Apple Watch data can be easily extracted from the originating iOS/iPadOS Health app, as demonstrated in /src/main.py
- From the zip folder compiled from the Health app, export.xml is easier to parse, if no knowledge/previous experience working with clinical document architecture (CDA) is present.


## Installation/ Usage

### OS X & Linux:

#### First: Environment Setup
1. Setup python3 virtual environment (for Vizualizations):
    - Open shell at root of the project
    - Create virtual environment:
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        ```
    - Note: Step 2 and the "Second" section in this instruction list must be completed to successfully run the Visualizations. 

2. Setup miniconda virtual environment (for data extraction, cleaning, and descriptive statistics)
    - Open shell at root of the project
    - Activate current miniconda base environment (if not already active):
    ```sh
    cd ..
    source ~/miniconda3/bin/activate
    ```
    - Note: if miniconda is installed in a different location, please navtivate to that location to activate conda base
    - Create conda environment from conda.yml
    ```sh
    conda env create -f conda.yml
    conda activate apple_watch_eda
    ```

#### Second: Generate data files

1. Clone or download the repository
2. Open the repository in the desired IDE
3. To run the project with an available Apple Watch dataset:
    - Follow "Extracting Apple Watch Data from the Apple ecosystem" steps above
    - Copy/ move the unzipped "export.zip" folder into the root of this project (APPLEWATCHEDA/<personal exported data folder>)
4. Open shell/terminal at root of the project
5. Change directory to /src/backend:
```sh
cd /src/backend
```
6. Run main.py and examine datatype files located in /src/data:
```sh
python3 main.py
```

#### Third: Visualize data

1. Navigate to the /src/frontend directory
2. Refer to "First: Environment Setup" section for initial environment setup
3. Navigate to the Visualizations.ipynb file and open
4. Important: Select the local venv at the kernel for the notebook.
5. Run all

Troubleshooting:
- The plotly library might have issues in loading the nbformat dependency, if this occurs please follow these steps:
    - In the current shell, deactivate the conda environment. The current shell environment should now be on the venv environment.
    - In the venv environment:
    ```sh
    pip install nbformat
    pip list
    ```
    - Verify that nbformat is at 4.5.0 or higher
    - Restart the Jupyter notebook kernel
    - Re-run all cells

## Requirements

* Python miniconda base environment
    * [miniconda download](https://docs.anaconda.com/free/miniconda/index.html)
* Python version 3 or higher
    * [Python3 download](https://www.python.org/downloads/release/python-3110/)

