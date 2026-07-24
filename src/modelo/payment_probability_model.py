"""Define el modelo de probabilidad de pago."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class PaymentProbabilityModel:
    """Entrena y aplica una regresión logística de pago."""

    categorical_features = ["cod_apli_prod", "cod_trn"]
    numeric_features = [
        "log_original_amount",
        "creation_year",
        "creation_month",
        "creation_weekday",
    ]
    required_columns = {
        "cod_apli_prod",
        "cod_trn",
        "vlr_original",
        "creation_date",
    }

    def __init__(self, random_state: int = 42) -> None:
        self.pipeline = self._build_pipeline(random_state)

    def _build_pipeline(self, random_state: int) -> Pipeline:
        """Construye las transformaciones y el modelo."""
        categorical_transformer = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore")),
            ]
        )
        numeric_transformer = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
        preprocessor = ColumnTransformer(
            [
                (
                    "categorical",
                    categorical_transformer,
                    self.categorical_features,
                ),
                (
                    "numeric",
                    numeric_transformer,
                    self.numeric_features,
                ),
            ]
        )

        return Pipeline(
            [
                ("preprocessor", preprocessor),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=1000,
                        random_state=random_state,
                    ),
                ),
            ]
        )

    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Construye las variables disponibles al crear la CxC."""
        missing_columns = self.required_columns.difference(data.columns)
        if missing_columns:
            raise ValueError(
                f"Faltan columnas requeridas: {sorted(missing_columns)}"
            )

        features = data.copy()
        features["creation_date"] = pd.to_datetime(
            features["creation_date"],
            errors="coerce",
        )
        features["log_original_amount"] = np.log1p(
            features["vlr_original"]
        )
        features["creation_year"] = features["creation_date"].dt.year
        features["creation_month"] = features["creation_date"].dt.month
        features["creation_weekday"] = (
            features["creation_date"].dt.dayofweek
        )
        features["cod_apli_prod"] = features["cod_apli_prod"].astype(str)
        features["cod_trn"] = features["cod_trn"].astype(str)

        return features[self.categorical_features + self.numeric_features]

    def fit(self, data: pd.DataFrame, target_column: str) -> None:
        """Entrena el modelo con la población elegible."""
        features = self.prepare_features(data)
        target = data[target_column].astype(int)
        self.pipeline.fit(features, target)

    def predict_probability(self, data: pd.DataFrame) -> np.ndarray:
        """Estima la probabilidad individual de pago."""
        features = self.prepare_features(data)
        return self.pipeline.predict_proba(features)[:, 1]

    def predict_out_of_fold(
        self,
        data: pd.DataFrame,
        target_column: str,
        group_column: str,
        n_splits: int = 5,
    ) -> np.ndarray:
        """Genera probabilidades fuera de muestra por cuenta."""
        probabilities = cross_val_predict(
            estimator=self.pipeline,
            X=self.prepare_features(data),
            y=data[target_column].astype(int),
            groups=data[group_column],
            cv=GroupKFold(n_splits=n_splits),
            method="predict_proba",
            n_jobs=-1,
        )
        return probabilities[:, 1]

    def save(self, output_path: Path) -> None:
        """Guarda el modelo entrenado."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, output_path)
