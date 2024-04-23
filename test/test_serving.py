from unittest.mock import Mock

from pandas import DataFrame

from serving import serving, get_model, SimpleMonitor, Monitor
from fastapi.testclient import TestClient


client = TestClient(serving)


# def get_mock_model():
#     mock_model = Mock()
#     mock_model.predict.return_value = [8]
#     return mock_model


class FakeMonitor(Monitor):
    def log_prediction(self, prediction: DataFrame):
        pass


serving.dependency_overrides[SimpleMonitor] = FakeMonitor


def test_serving():
    mock_model = Mock()

    def get_mock_model():
        mock_model.predict.return_value = [8]
        return mock_model

    serving.dependency_overrides[get_model] = get_mock_model

    body = {
        "month": "1",
        "day": "1",
        "ind": "1",
        "rain": 0.0,
        "ind_1": "1",
        "t_max": 0.0,
        "ind_2": "1",
        "t_min": 0.0,
        "t_min_g": 0.0,
    }
    response = client.post("/predict", json=body)

    assert response.status_code == 200
    assert response.json() == {"prediction": 8}
    mock_model.predict.assert_called_once()
