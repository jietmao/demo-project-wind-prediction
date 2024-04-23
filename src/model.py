from typing import Optional, Dict, Any

import pandas as pd
from mlflow.pyfunc import PythonModel


class WindPredictionModel(PythonModel):
    def __init__(self, model, vectorizer):
        self.__model = model
        self.__vectorizer = vectorizer

    def __process_input(self, model_input):
        model_input_dict = model_input.to_dict(orient="records")
        vectorized_df = self.__vectorizer.transform(model_input_dict)
        return vectorized_df

    def predict(self, context, model_input, params: Optional[Dict[str, Any]] = None):
        processed_input = self.__process_input(model_input)
        prediction = self.__model.predict(processed_input)

        return prediction
