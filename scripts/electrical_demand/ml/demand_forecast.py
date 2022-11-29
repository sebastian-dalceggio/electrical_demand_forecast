import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder, SplineTransformer, MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_validate
from sklearn.kernel_approximation import Nystroem
from sklearn.linear_model import RidgeCV
import numpy as np

def train_and_predictions(dataset):
    dataset.drop(columns=["id", "demand_forecast"], inplace=True)
    dataset['month'] = dataset.index.month
    dataset['hour'] = dataset.index.hour
    dataset["weekday"] = dataset.index.weekday
    max_demand = dataset["demand"].max()
    dataset["demand"] = dataset["demand"] / max_demand
    dataset["temperature"].fillna(dataset["temperature_forecast"], inplace=True)
    dataset["temperature"] = dataset["temperature"].interpolate(method='linear').ffill()
    dataset.drop(columns=["temperature_forecast"], inplace=True)
    predict_dataset = dataset[dataset["demand"].isnull()]
    train_dataset = dataset[~dataset["demand"].isnull()]
    model = train_model(train_dataset)
    predictions = predict(predict_dataset, model, max_demand)
    return predictions

def train_model(dataset):
    X = dataset.drop("demand", axis="columns")
    y = dataset["demand"]
    ts_cv = TimeSeriesSplit(
        n_splits=5,
        gap=48,
        max_train_size=10000,
        test_size=1000,
    )
    ts_cv.split(X, y)
    categorical_columns = [
        "day_type",
    ]
    categories = [
        ["holiday", "working_day"],
    ]
    one_hot_encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)
    alphas = np.logspace(-6, 6, 25)
    def periodic_spline_transformer(period, n_splines=None, degree=3):
        if n_splines is None:
            n_splines = period
        n_knots = n_splines + 1
        return SplineTransformer(
            degree=degree,
            n_knots=n_knots,
            knots=np.linspace(0, period, n_knots).reshape(n_knots, 1),
            extrapolation="periodic",
            include_bias=True,
        )
    cyclic_spline_transformer = ColumnTransformer(
    transformers=[
        ("categorical", one_hot_encoder, categorical_columns),
        ("cyclic_month", periodic_spline_transformer(12, n_splines=6), ["month"]),
        ("cyclic_weekday", periodic_spline_transformer(7, n_splines=3), ["weekday"]),
        ("cyclic_hour", periodic_spline_transformer(24, n_splines=12), ["hour"]),
    ],
    remainder=MinMaxScaler(),
)

    cyclic_spline_poly_pipeline = make_pipeline(
        cyclic_spline_transformer,
        Nystroem(kernel="poly", degree=2, n_components=300, random_state=0),
        RidgeCV(alphas=alphas),
    )

    cyclic_spline_poly_pipeline.fit(X, y)
    return cyclic_spline_poly_pipeline

def evaluate(model, X, y, cv):
        cv_results = cross_validate(
            model,
            X,
            y,
            cv=cv,
            scoring=["neg_mean_absolute_error", "neg_root_mean_squared_error"],
        )
        mae = -cv_results["test_neg_mean_absolute_error"]
        rmse = -cv_results["test_neg_root_mean_squared_error"]
        print(
            f"Mean Absolute Error:     {mae.mean():.3f} +/- {mae.std():.3f}\n"
            f"Root Mean Squared Error: {rmse.mean():.3f} +/- {rmse.std():.3f}"
            )

def predict(dataset, model, max_demand):
    dataset["demand_forecast"] = dataset[["day_type", "temperature", "month", "hour", "weekday"]].apply(
        lambda s: model.predict(pd.DataFrame([s]))[0], axis=1
    )
    dataset.drop(columns=["month", "hour", "weekday", "day_type", "temperature", "demand"], inplace=True)
    dataset["demand_forecast"] = dataset["demand_forecast"] * max_demand
    return dataset