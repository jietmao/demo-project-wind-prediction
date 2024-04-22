# Wind Prediction Model
This is a project for mlops-zoomcamp homework.  
Objective is to predict the wind 


## Pre-requisite
This example is build using the development tools below.   
To run the project, please ensure the below tools or their alternatives are installed.  

- Poetry
  - Follow the installation guide from https://python-poetry.org/docs/#installation  
- docker
  - Option #1 (easiest) - Install Docker Desktop 
  - Option #2 - manual installation in WSL 
    - follow guide in https://dev.to/bowmanjd/install-docker-on-windows-wsl-without-docker-desktop-34m9
- docker-compose
  - Option #1 (easiest) - Installed as part of Docker Desktop
  - Option #2 - manual installation in WSL
- Python 
  - Python version 3.11
- Chocolatey
  - Follow installation guide on https://chocolatey.org/install
- Make
  - Install via powershell (with admin privilege)
  - ```choco install make```
- minikube
  - Option #1 - If using Docker Desktop   
  Run below command using Powershell (with Admin privilege)
    ```
    choco install minikube
    ```
    - Option #2 - Installation in WSL

Note: The above command is for Windows OS only. 


## Project Architecture
The project is developed using below technologies. 


## Execution 
### Environment Setup
1. Python library installation
   1. (First time only) Install dependent python package using Poetry.  
   Execute the below command in the project root. This will create a new virtual environment with the necessarily python packages.
        ```
        poetry install --no-root
        ```
   2. s


