import os
from abc import ABC, abstractmethod
from datetime import datetime
from functools import lru_cache
from typing import Annotated, Any

import mlflow
import pandas as pd
import psycopg
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric
from evidently.report import Report
from fastapi import FastAPI, Depends
from pandas import DataFrame
from pydantic import BaseModel

serving = FastAPI()


class Input(BaseModel):
    month: str
    day: str
    ind: str
    rain: float
    ind_1: str
    t_max: float
    ind_2: str
    t_min: float
    t_min_g: float


@lru_cache
def get_model():
    print(f"MLFLOW_URI Environment Value: {os.getenv('MLFLOW_URI')}")
    mlflow_uri = os.getenv("MLFLOW_URI", "http://127.0.0.1:5000")
    mlflow.set_tracking_uri(mlflow_uri)
    model_name = "wind-prediction-model"
    return mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}@serving")


class Monitor(ABC):
    @abstractmethod
    def log_prediction(self, prediction: DataFrame):
        pass


class SimpleMonitor(Monitor):
    def __init__(self):
        self.__report = None
        self.__column_mapping = None
        self.__reference_data = self.__read_reference()
        self.__setup_monitor_report()

    def __read_reference(self):
        return pd.read_parquet(
            "s3://project-bucket/training/training_prediction.parquet",
            storage_options={"profile": "localstack"},
        )

    def __setup_monitor_report(self):
        num_features = ["RAIN", "T.MAX", "T.MIN", "T.MIN.G"]
        cat_features = ["MONTH", "DAY", "IND", "IND.1", "IND.2"]

        self.__column_mapping = ColumnMapping(
            prediction="prediction",
            numerical_features=num_features,
            categorical_features=cat_features,
            target=None,
        )

        self.__report = Report(
            metrics=[
                ColumnDriftMetric(column_name="prediction"),
                DatasetDriftMetric(),
            ]
        )

    def log_prediction(self, prediction):
        self.__report.run(
            reference_data=self.__reference_data,
            current_data=prediction,
            column_mapping=self.__column_mapping,
        )

        result = self.__report.as_dict()

        prediction_drift = result["metrics"][0]["result"]["drift_score"]
        num_drifted_columns = result["metrics"][1]["result"][
            "number_of_drifted_columns"
        ]

        postgresql_host = os.getenv("POSTGRESQL_HOST", "localhost")
        with psycopg.connect(
            f"host={postgresql_host} port=5432 dbname=test user=postgres password=example",
            autocommit=True,
        ) as conn:
            with conn.cursor() as curr:
                curr.execute(
                    "insert into dummy_metrics(timestamp, prediction_drift, num_drifted_columns) values (%s, %s, %s)",
                    (
                        datetime.now(),
                        prediction_drift,
                        num_drifted_columns,
                    ),
                )


@serving.post("/predict")
def predict(
    body: Input,
    model: Annotated[Any, Depends(get_model)],
    monitoring: Annotated[Monitor, Depends(SimpleMonitor)],
):
    df = pd.DataFrame([body.dict()])
    df.columns = [column.upper().replace("_", ".") for column in df.columns]

    result = model.predict(df)
    df["prediction"] = result
    monitoring.log_prediction(df)
    return {"prediction": result[0]}
