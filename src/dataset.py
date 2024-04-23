from sklearn.feature_extraction import DictVectorizer


class Dataset:
    def __init__(
        self,
        data,
        categorical_columns,
        numerical_columns,
        label_column,
        vectorizer=None,
    ):
        self.__data = data
        self.__feature_df = None
        self.__vectorized_feature_df = None
        self.__label_df = None
        self.__prediction_df = None
        self.__vectorizer = vectorizer
        self.__slice_data(categorical_columns, numerical_columns, label_column)
        self.__vectorize_feature()

    @property
    def data(self):
        return self.__data

    @property
    def features_data(self):
        return self.__feature_df

    @property
    def vectorized_features_data(self):
        return self.__vectorized_feature_df

    @property
    def label_data(self):
        return self.__label_df

    @property
    def vectorizer(self):
        return self.__vectorizer

    @property
    def prediction_data(self):
        return self.__prediction_df

    def __vectorize_feature(self):
        if not self.__vectorizer:
            self.__vectorizer = DictVectorizer()
            vectorize_func = self.__vectorizer.fit_transform
        else:
            vectorize_func = self.__vectorizer.transform

        vectorize_dict = self.__feature_df.to_dict(orient="records")
        self.__vectorized_feature_df = vectorize_func(vectorize_dict)

    def __slice_data(self, categorical_columns, numerical_columns, label_column):
        self.__feature_columns = categorical_columns + numerical_columns
        self.__label_column = label_column
        self.__feature_df = self.__data[self.__feature_columns]
        self.__label_df = self.__data[self.__label_column]

    def set_prediction(self, prediction):
        self.__prediction_df = self.__feature_df.copy()
        self.__prediction_df["prediction"] = prediction
