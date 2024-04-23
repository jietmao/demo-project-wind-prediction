.phony: infra input workflow

setup: infra input
tests: unit_test integration_test

# wsl docker-compose up -d
# timeout /t 20
infra:
	terraform -chdir=./terraform apply -auto-approve
	poetry run python ./db/create_database.py

input:
	poetry run python ./data/download_data.py --data_file ./data/wind_dataset.csv

build:
	wsl docker build . -f docker/train/Dockerfile -t wind-prediction-training:1.0.0
	wsl minikube image load wind-prediction-training:1.0.0
	wsl docker build . -f docker/serving/Dockerfile -t model-serving:1.0.0
	wsl minikube image load model-serving:1.0.0

workflow_deployment:
	poetry run prefect work-pool create minikube-pool --type kubernetes
	poetry run prefect deploy -n wind_prediction_model_training --prefect-file ./workflow/prefect.yaml
	helm install prefect-worker prefect/prefect-worker -f ./workflow/values.yaml

train:
	poetry run prefect deployment run 'Wind Prediction Model Training/wind_prediction_model_training'

serve:
	kubectl apply -f ./kubernetes/serving_deployment.yaml
	kubectl apply -f ./kubernetes/serving_service.yaml

lint:
	poetry run black .

deploy_hook:
	copy /Y hook\pre-commit .git\hooks\pre-commit

unit_test:
	wsl docker build . -f docker/train/Dockerfile -t wind-prediction-training:test --target test
	wsl docker build . -f docker/serving/Dockerfile -t model-serving:test --target test

integration_test:
	poetry run pytest test/integration_test.py
