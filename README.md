# Pixxel CLI

A cli to dynamically create data pipelines for Sentinel-2

## Introduction

* A command with the path of sentinal-2a images has to be passed
* CLI program will dynamically create another program from a template based on the parameters
* This program is automatically upload to Airflow and is scheduled for download
* Any number of pipelines can be created

## Important Folders and Files

```
pixxel-cli
│   README.md
|   .gitignore
│
└───bin - Python executable for running the program, cleaning the logs
|
|
└───logs - Folder which will contain the logs for every run (Automatically created)
|
|
└───src
    |
    └───pixxel - Python libraries annd classes (Solution)
    |
    └───tests - Test cases for the libraries and its classes
    |
    └───main.py - Start of the program
```

## Dependencies

- Python 3.7 >= or =< Python 3.8
- Pytest >= 5.x.x
- rasterio
- boto3
- google-cloud-storage
- gcloud cli tool
- aws cli tool

## Installation

It is recommended to create a virtual environment using **VirtualEnv** or **Anaconda**. Below is an example for VirtualEnv

### Install Python 3.7

```sudo apt install python3.7```
```sudo apt install python3-pip```

#### Install virtualenv for creating virtual environments

```sudo apt install virtualenv```
```python3 -m pip install virtualenv --user```

#### Create a virtual environment with name **env** and activate it

```virtualenv venv --python=python3.7```
```source venv/bin/activate```

#### Verify installation and working of virtual environment

```which python```

#### Install pytest

```pip install pytest --user```

## Usage

- Make ./bin/pixxel as executable by running ```chmod +x ./bin/pixxel```
- Make ./bin/clean_logs as executable by running ```chmod +x ./bin/clean_logs```

### Command Syntax

- Create a pipeline: 
  - Syntax: ```bin/pixxel <normalize_method> <bucket_name> <utm_code> <latitude_band> <square> <year> <month> <day> <sequence> <resolution>```
  - Example: ```bin/pixxel ndvi sentinel-s2-l2a 10 S DG 2018 12 31 0 R60m```

- Listing all pipelines: ```bin/pixxel list```
- Deleting a pipeline: ```bin/pixxel delete```

## Testing

**Note:** Running tests will delete all of ```./logs```

**Note:** There are breaking changes in Python 3.6 and 3.7 subprocesses. Test cases won't work in 3.6 or below. Please use 3.7 and above

- **Normal:** ```python3 -m pytest -v -s```
- **Verbose:** ```python3 -m pytest -v -s -rA```

## Logs

- Logs can be cleaned by running ```./bin/clean_logs``` . This will remove all the contents of the logs directory
  
## Author

- [Sudhanva Narayana](https://sudhanva.me)