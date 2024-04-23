import pandas as pd
import pytest
from prefect.testing.utilities import prefect_test_harness

from train import main


@pytest.fixture(autouse=True, scope="session")
def prefect_test_fixture():
    with prefect_test_harness():
        yield


def set_up_input_data():
    input_df = pd.DataFrame(
        [
            ["1977-04-01", 100.00, 0, 11.0, 0.0, 15.0, 1.0, 10.0, 8.0],
            ["1978-03-28", 90.00, 0, 10.0, 0.0, 20.0, 1.0, 12.0, 6.0],
        ],
        columns=[
            "DATE",
            "WIND",
            "IND",
            "RAIN",
            "IND.1",
            "T.MAX",
            "IND.2",
            "T.MIN",
            "T.MIN.G",
        ],
    )

    input_df.to_csv(
        "s3://project-bucket/integration_test/input/wind_dataset.csv",
        storage_options={"profile": "localstack"},
        index=False,
    )


def test_integration():
    set_up_input_data()
    main("./test_conf.yaml")
    prediction_df = pd.read_parquet(
        "s3://project-bucket/integration_test/training/training_prediction.parquet",
        storage_options={"profile": "localstack"},
    )

    assert len(prediction_df) == 1
    assert set(prediction_df.columns) == {
        "IND",
        "RAIN",
        "IND.1",
        "T.MAX",
        "IND.2",
        "T.MIN",
        "T.MIN.G",
        "MONTH",
        "DAY",
        "prediction",
    }
