import json

import mlflow
import pandas as pd
import requests
from fastapi import FastAPI
from pydantic import BaseModel


def get_model():
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    model_name = "wind-prediction-model"
    return mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}@latest")


# @serving.post('predict')
def predict():
    model = get_model()

    df = pd.DataFrame(
        [["10", "6", "0", 10.0, "0", 13.0, "0", 8.0, 2.0]],
        columns=[
            "MONTH",
            "DAY",
            "IND",
            "RAIN",
            "IND.1",
            "T.MAX",
            "IND.2",
            "T.MIN",
            "T.MIN.G",
        ],
    )

    result = model.predict(df)
    print(type(result))
    print(result[0])
    return {"prediction": result[0]}


def request():
    url = "http://127.0.0.1:38431/predict"
    # url = 'http://127.0.0.1:8000/predict'

    data = {
        "month": "4",
        "day": "1",
        "ind": "0",
        "rain": 33.0,
        "ind_1": "1",
        "t_max": 20.0,
        "ind_2": "2",
        "t_min": 15.0,
        "t_min_g": 10.0,
    }

    response = requests.post(url, data=json.dumps(data))
    print(response.status_code)
    print(response.json())


def read():
    df = pd.read_parquet(
        "s3://project-bucket/training/training_prediction.parquet",
        storage_options={"profile": "localstack"},
    )
    print(df.info())
    print(len(df))
    print(df.head(10))


if __name__ == "__main__":
    # predict()
    request()
    # read()

    # expected_columns = [
    #     "DATE",
    #     "WIND",
    #     "IND",
    #     "RAIN",
    #     "IND.1",
    #     "T.MAX",
    #     "IND.2",
    #     "T.MIN",
    #     "T.MIN.G",
    #     "MONTH",
    #     "DAY",
    #     "YEAR",
    # ]
    # expected_validation_df = pd.DataFrame(
    #     [
    #         ['1978-03-28', 90.00, '0', 10.0, '0.0', 20.0, '1.0', 12.0, 6.0, '3', '28', 1978],
    #     ],
    #     columns=expected_columns
    # )
    #
    # print(list(expected_validation_df.dtypes))
