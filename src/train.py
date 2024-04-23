import os

import mlflow
import optuna
import pandas as pd
import yaml
from mlflow import MlflowClient
from mlflow.entities import ViewType
from mlflow.models import infer_signature
from numpy import int64
from optuna.samplers import TPESampler
from prefect import flow, task
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error

from dataset import Dataset
from model import WindPredictionModel


@task
def read_data(path):
    df = pd.read_csv(
        f"{path}/input/wind_dataset.csv", storage_options={"profile": "localstack"}
    )
    return df


@task
def process_data(df):
    df["MONTH"] = pd.to_datetime(df["DATE"]).dt.month.astype(str)
    df["DAY"] = pd.to_datetime(df["DATE"]).dt.day.astype(str)
    df["YEAR"] = pd.to_datetime(df["DATE"]).dt.year.astype(int64)

    df["IND"] = df["IND"].astype(str)
    df["IND.1"] = df["IND.1"].astype(str)
    df["IND.2"] = df["IND.2"].astype(str)

    df.dropna(inplace=True)

    categorical_features = ["MONTH", "DAY", "IND", "IND.1", "IND.2"]
    numerical_features = ["RAIN", "T.MAX", "T.MIN", "T.MIN.G"]
    label = "WIND"

    training_dataset = Dataset(
        df[df["YEAR"] < 1978], categorical_features, numerical_features, label
    )
    validation_dataset = Dataset(
        df[df["YEAR"] == 1978],
        categorical_features,
        numerical_features,
        label,
        training_dataset.vectorizer,
    )

    return training_dataset, validation_dataset


def get_trial_params(trial, name, hyperparameter: dict):
    return trial.suggest_int(
        name=name,
        low=hyperparameter["low"],
        high=hyperparameter["high"],
        step=hyperparameter["step"],
    )


def training(params, training_df, validation_df):
    mlflow.log_params(params)
    model = RandomForestRegressor(**params)
    model.fit(training_df.vectorized_features_data, training_df.label_data)
    validation_prediction = model.predict(validation_df.vectorized_features_data)

    rmse = root_mean_squared_error(validation_df.label_data, validation_prediction)
    mlflow.log_metric("rmse", rmse)
    return model, rmse


def log_model(model, dataset, model_name):
    mlflow.pyfunc.log_model(
        python_model=WindPredictionModel(model, dataset.vectorizer),
        artifact_path="model",
        signature=infer_signature(
            dataset.features_data,
            model.predict(dataset.vectorized_features_data),
        ),
        registered_model_name=model_name,
    )


@task
def train_model(training_df, validation_df, config):
    mlflow.set_experiment(config["mlflow"]["experiment_name"])

    def objective(trial):
        with mlflow.start_run():
            hyperparameters = config["hyperparameters"]
            params = {
                "n_estimators": get_trial_params(
                    trial, "n_estimators", hyperparameters["n_estimators"]
                ),
                "max_depth": get_trial_params(
                    trial, "max_depth", hyperparameters["max_depth"]
                ),
                "min_samples_split": get_trial_params(
                    trial, "min_samples_split", hyperparameters["min_samples_split"]
                ),
                "min_samples_leaf": get_trial_params(
                    trial, "min_samples_leaf", hyperparameters["min_samples_leaf"]
                ),
                "random_state": hyperparameters["seed"],
                "n_jobs": -1,
            }

            model, rmse = training(params, training_df, validation_df)
            return rmse

    sampler = TPESampler(seed=config["hyperparameters"]["seed"])
    study = optuna.create_study(direction="minimize", sampler=sampler)
    study.optimize(objective, n_trials=config["hyperparameters"]["n_trials"])


def convert_value_to_int(params):
    return {k: int(v) for k, v in params.items()}


def set_alias(client, alias):
    latest_mv = client.get_latest_versions("wind-prediction-model", stages=["None"])[0]
    client.set_registered_model_alias("wind-prediction-model", alias, latest_mv.version)


@task
def register_model(training_df, validation_df, config):
    client = MlflowClient()

    experiment = client.get_experiment_by_name(config["mlflow"]["experiment_name"])
    best_run = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=1,
        order_by=["metrics.rmse ASC"],
    )[0]

    mlflow.set_experiment(f"{config['mlflow']['experiment_name']}-best-model")
    with mlflow.start_run():
        params = convert_value_to_int(best_run.data.params)
        model, rmse = training(params, training_df, validation_df)
        log_model(model, validation_df, config["mlflow"]["model_name"])
        set_alias(client, "serving")
        training_predict = model.predict(training_df.vectorized_features_data)
        training_df.set_prediction(training_predict)


@task
def read_config(config_path):
    with open(config_path, "rb") as config_file:
        config = yaml.safe_load(config_file)

    return config


@task
def save_training_data(training_dataset: Dataset, path):
    training_dataset.prediction_data.to_parquet(
        f"{path}/training/training_prediction.parquet",
        storage_options={"profile": "localstack"},
    )


@flow(name="Wind Prediction Model Training")
def main(config_path="../config/training_parameters.yaml"):
    config = read_config(config_path)
    mlflow.set_tracking_uri(os.getenv("MLFLOW_URI", config["mlflow"]["tracking_uri"]))

    df = read_data(config["source"]["path"])
    training_df, validation_df = process_data(df)
    train_model(training_df, validation_df, config)
    register_model(training_df, validation_df, config)
    save_training_data(training_df, config["source"]["path"])


if __name__ == "__main__":
    main()
    # main.deploy(
    #     name="Wind Prediction Model Training",
    #     work_pool_name="docker-pool",
    #     image="wind-prediction-training:1.0.0",
    #     job_variables={
    #         "network_mode": "host",
    #     },
    #     build=False
    # )
