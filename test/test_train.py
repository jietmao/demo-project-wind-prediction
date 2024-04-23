import pandas as pd
from prefect.logging import disable_run_logger

from train import process_data


def test_process_data():
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

    with disable_run_logger():
        training_result, validation_result = process_data.fn(input_df)

    expected_columns = [
        "DATE",
        "WIND",
        "IND",
        "RAIN",
        "IND.1",
        "T.MAX",
        "IND.2",
        "T.MIN",
        "T.MIN.G",
        "MONTH",
        "DAY",
        "YEAR",
    ]
    expected_training_df = pd.DataFrame(
        [
            [
                "1977-04-01",
                100.00,
                "0",
                11.0,
                "0.0",
                15.0,
                "1.0",
                10.0,
                8.0,
                "4",
                "1",
                1977,
            ],
        ],
        columns=expected_columns,
    )

    expected_validation_df = pd.DataFrame(
        [
            [
                "1978-03-28",
                90.00,
                "0",
                10.0,
                "0.0",
                20.0,
                "1.0",
                12.0,
                6.0,
                "3",
                "28",
                1978,
            ],
        ],
        columns=expected_columns,
        index=[1],
    )

    assert training_result.data.equals(expected_training_df)
    assert validation_result.data.equals(expected_validation_df)
