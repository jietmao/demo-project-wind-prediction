# Wind Prediction Model
This is a project for mlops-zoomcamp homework.  
Objective is to predict the wind speed 


## Pre-requisite
This example is built and executed using the tools below on Windows machine.   
To run the project, please ensure the below tools or their alternatives are installed.  

- Poetry - Python package manager
  - Follow the installation guide from https://python-poetry.org/docs/#installation  
- docker
  - Option #1 (easiest) - Install Docker Desktop 
  - Option #2 - manual installation in WSL (option used for demo)
    - follow guide in https://dev.to/bowmanjd/install-docker-on-windows-wsl-without-docker-desktop-34m9
- docker-compose
  - Option #1 (easiest) - Installed as part of Docker Desktop
  - Option #2 - manual installation in WSL (refer guide on manual docker installation in WSL above)
- Python 
  - Python version 3.11
- Chocolatey - software management automation for Windows
  - Follow installation guide on https://chocolatey.org/install
- Make
  - Install via powershell (with admin privilege)
    ```
    choco install make
    ```
- minikube - Single node Kubernetes cluster for local 
  - Option #1 - If using Docker Desktop   
  Run below command using Powershell (with Admin privilege)
    ```
    choco install minikube
    ```
  - Option #2 - Installation in WSL (option used for demo)
    - Follow installation guide from https://www.linuxbuzz.com/install-minikube-on-ubuntu/
- Kubectl - Kubernetes command-line tool
  - Install with powershell (with admin privilege)
    ```
    choco install kubernetes-cli
    ```
  - If minikube is installed in wsl, kubectl needs to be manual configured to connect to it. (option used for demo)
    ```
    kubectl config set-cluster minikube --server=<minikube url> --certificate-authority=<path of ca.crt store in window host>
    kubectl config set-context minikube --cluster=minikube --user=minikube
    kubectl config set-credentials minikube --client-certificate=<path of client.crt store in window host> --client-key=<path of client.key store in window host>
    ```
    The minikube url and credential certificate path (in wsl) can be found by running below command in wsl console. The certificate files need to be copied over to window host machine. 
    ```
    kubectl config view
    ```
- Helm - Kubernetes Package Manager 
  - Install with powershell (with admin privilege)
    ```
    choco install kubernetes-helm
    ```
- Terraform - Infrastructure as code tool
  - Follow installation guide from https://developer.hashicorp.com/terraform/install?product_intent=terraform

Note: The above commands/steps are for Windows OS (or WSL in Windows) only. 


## Project Technologies
The project is developed using below technologies. 
- Python (scikit-learn, pandas, evidently, fastapi, etc)
- Kubernetes
- Docker
- Mlflow
- Prefect
- Grafana


## Execution 
### Environment Setup
1. Python library installation
   1. **(First time only)** Install dependent python package using Poetry.  
   2. The package version is already "locked" by poetry and tracked in "poetry.lock" file. Hence, there is no need to run the `poetry lock` command before installing the package.   
   3. Execute the below command in the project folder. This will create a new virtual environment with the necessarily locked down python packages version.
      ```
      poetry install --no-root
      ```
2. **(First time only)** Create an AWS profile for localstack.
    1. The demo will be using localstack to simulate the data store on S3.
    2. An AWS profile is require to connect to localstack
        1. Add the localstack profile to .aws folder
3. Start the services (localstack, mlflow server, prefect server, grafana) using docker-compose.
   1. Run the below command in project directory using wsl console. 
      ```
      docker-compose up &
      ```
4. Start Kubernetes service using minikube. 
   1. Run the below command in project directory using wsl console. 
      ```
      minikube start & 
      ```
5. Set up the infra using Make command. 
   1. Create a S3 bucket using Terraform
   2. Upload source data into S3 (localstack) 
   3. Create the postgresql for Grafana  
   Run the command below for the above infra setup.   
   Note: the Makefile is prepared for Windows OS execution only, and it uses manual docker installed in WSL setup. 
      ```
      make setup
      ```

### Training
Training script is containerized using docker and will be deployed to a kubernetes cluster for execution via prefect workflow.
1. Build docker image for training and serving.
   1. Run the command below for image building
      ```
      make build
      ```
2. Deploy training job to Prefect Server. 
   1. Create a kubernetes work pool
   2. Create a training deployment
   3. Create a kubernetes worker  
   Note: Kubernetes worker deployment takes around 1 min to start. Do verify the worker is up from Prefect UI (http://127.0.0.1:4200) before proceeding to start the training job manually. 
   4. Run the below command for the above deployment step
      ```
      make workflow_deployment
      ```
3. Start training job from Prefect server. 
   1. Run the command below to start training job. 
      ```
      make train
      ```
   2. Training job will be executing in minikube. 
4. All the training experiments will be tracked in mlflow server. The best model after training will be registered into mlflow server's model registry. 

### Model Serving
A webservice will be setup on a kubernetes cluster for model serving. The webservice will retrieve the best model from mlflow server for prediction.  
1. Deploy the webservice into a kubernetes cluster. 
   1. Run the below command to deploy serving webservice. 
      ```
      make serve
      ```
2. Forward the port from window host to minikube.  
   1. Run the below command in Window Host CMD/Powershell.  
      ```
      kubectl port-forward service/model-serving 8000:8000
      ```
3. Verify the URL of the expose webservice (e.g. http://127.0.0.1:8000)
   - Access the api document on http://127.0.0.1:8000/docs (fastapi feature)

### Monitoring
Drift monitoring has been set up using evidently and Grafana when each webservice is being triggered for prediction.
1. After calling API (e.g. http://127.0.0.1:8000/predict), datadrift will be evaluated and logged into a postgresql db (logged with UTC time). 
2. A dashboard on Grafana has been built for drift monitoring. 


### Code Linting & Pre-commit Hook
Black is used for code linting. 
1. Run the command below to lint the code before commit. 
   ```
   make lint
   ```
2. A client side pre-commit hook has been set up to run the lint and stop the commit if linting check using black has failed. 
3. Run the command below to set up the client side pre-commit hook. 
   ```
   make hook
   ```

### CI/CD
CI/CD has been setup using Github Action
1. Auto Image build and push to image repository
2. Auto unit test execution to ensure code correctness
