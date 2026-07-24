"""Entrena el modelo y genera los archivos de la Actividad 2."""

from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.analytical_table_builder import AnalyticalTableBuilder
from src.database import SQLiteDatabase
from src.modelo.payment_probability_model import PaymentProbabilityModel


HORIZON_DAYS = 120
RISK_BINS = [0.0, 0.40, 0.60, 0.80, 1.0]
RISK_LABELS = [
    "alto_riesgo",
    "riesgo_medio",
    "probable_pago",
    "alta_probabilidad_pago",
]


def prepare_modeling_data(analytical_table: pd.DataFrame) -> pd.DataFrame:
    """Define la población elegible y el objetivo de pago a 120 días."""
    data = analytical_table.copy()

    for column_name in [
        "creation_date",
        "last_payment_date",
        "reference_date",
    ]:
        data[column_name] = pd.to_datetime(
            data[column_name],
            errors="coerce",
        )

    paid_within_horizon = data["is_fully_paid"].eq(1) & data[
        "days_creation_to_last_payment"
    ].between(0, HORIZON_DAYS, inclusive="both")

    eligible_mask = paid_within_horizon | data["age_days"].ge(
        HORIZON_DAYS
    )
    modeling_data = data.loc[eligible_mask].copy()
    modeling_data["target_paid_120d"] = paid_within_horizon.loc[
        eligible_mask
    ].astype(int)

    return modeling_data


def add_probability_results(
    data: pd.DataFrame,
    probability_column: str,
    segment_column: str,
) -> pd.DataFrame:
    """Agrega segmento, recuperación esperada y exposición esperada."""
    result = data.copy()
    probability = result[probability_column]

    result[segment_column] = pd.cut(
        probability,
        bins=RISK_BINS,
        labels=RISK_LABELS,
        include_lowest=True,
    )
    result["expected_full_recovery_120d"] = (
        result["vlr_original"] * probability
    )
    result["expected_non_full_recovery_exposure_120d"] = (
        result["vlr_original"] * (1 - probability)
    )

    return result


def calculate_metrics(
    target: pd.Series,
    probability: pd.Series,
) -> pd.DataFrame:
    """Calcula las métricas sobre probabilidades fuera de muestra."""
    predicted_class = probability.ge(0.50).astype(int)

    return pd.DataFrame(
        [
            {
                "model": "logistic_regression",
                "horizon_days": HORIZON_DAYS,
                "records": len(target),
                "positive_rate": target.mean(),
                "roc_auc": roc_auc_score(target, probability),
                "average_precision": average_precision_score(
                    target,
                    probability,
                ),
                "brier_score": brier_score_loss(target, probability),
                "accuracy": accuracy_score(target, predicted_class),
                "precision": precision_score(
                    target,
                    predicted_class,
                    zero_division=0,
                ),
                "recall": recall_score(
                    target,
                    predicted_class,
                    zero_division=0,
                ),
                "f1_score": f1_score(
                    target,
                    predicted_class,
                    zero_division=0,
                ),
            }
        ]
    )


def build_dashboard_data(
    analytical_table: pd.DataFrame,
    modeling_data: pd.DataFrame,
    payment_model: PaymentProbabilityModel,
) -> pd.DataFrame:
    """Construye la fuente consolidada utilizada por Power BI."""
    dashboard_data = analytical_table.copy()
    dashboard_data["payment_probability_120d"] = (
        payment_model.predict_probability(dashboard_data)
    )
    dashboard_data = add_probability_results(
        data=dashboard_data,
        probability_column="payment_probability_120d",
        segment_column="operational_risk_segment",
    )

    historical_results = modeling_data[
        [
            "cxc_id",
            "target_paid_120d",
            "payment_probability_120d_oof",
            "risk_segment",
        ]
    ].rename(columns={"risk_segment": "historical_risk_segment"})

    dashboard_data = dashboard_data.merge(
        historical_results,
        on="cxc_id",
        how="left",
    )
    dashboard_data["is_target_evaluable_120d"] = (
        dashboard_data["target_paid_120d"].notna().astype(int)
    )

    return dashboard_data


def export_results(
    project_path: Path,
    payment_model: PaymentProbabilityModel,
    metrics: pd.DataFrame,
    modeling_data: pd.DataFrame,
    dashboard_data: pd.DataFrame,
) -> dict[str, Path]:
    """Guarda el modelo y los archivos utilizados por el análisis."""
    output_paths = {
        "model": project_path
        / "src"
        / "modelo"
        / "modelo_probabilidad_pago.pkl",
        "metrics": project_path
        / "src"
        / "metricas"
        / "metricas_modelo.csv",
        "predictions": project_path
        / "data"
        / "processed"
        / "predicciones_cxc.csv",
        "dashboard": project_path
        / "data"
        / "processed"
        / "dashboard_cxc.csv",
    }

    for output_path in output_paths.values():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    payment_model.save(output_paths["model"])
    metrics.to_csv(output_paths["metrics"], index=False, encoding="utf-8")

    prediction_columns = [
        "cxc_id",
        "num_cta",
        "cod_apli_prod",
        "descri_cod_apli_prod",
        "cod_trn",
        "descri_cod_trn",
        "creation_date",
        "reference_date",
        "vlr_original",
        "target_paid_120d",
        "payment_probability_120d_oof",
        "risk_segment",
        "expected_full_recovery_120d",
        "expected_non_full_recovery_exposure_120d",
    ]
    modeling_data[prediction_columns].to_csv(
        output_paths["predictions"],
        index=False,
        encoding="utf-8",
    )
    dashboard_data.to_csv(
        output_paths["dashboard"],
        index=False,
        encoding="utf-8",
    )

    return output_paths


def main() -> None:
    """Ejecuta la preparación, validación y exportación del modelo."""
    project_path = Path(__file__).resolve().parents[1]
    table_builder = AnalyticalTableBuilder(
        database=SQLiteDatabase(
            project_path / "data" / "base_datos_historica.db"
        ),
        sql_path=project_path / "src" / "sql" / "sabana_analitica.sql",
    )
    analytical_table = table_builder.build()
    modeling_data = prepare_modeling_data(analytical_table)

    payment_model = PaymentProbabilityModel()
    modeling_data["payment_probability_120d_oof"] = (
        payment_model.predict_out_of_fold(
            data=modeling_data,
            target_column="target_paid_120d",
            group_column="num_cta",
        )
    )
    modeling_data = add_probability_results(
        data=modeling_data,
        probability_column="payment_probability_120d_oof",
        segment_column="risk_segment",
    )

    metrics = calculate_metrics(
        target=modeling_data["target_paid_120d"],
        probability=modeling_data["payment_probability_120d_oof"],
    )

    payment_model.fit(
        data=modeling_data,
        target_column="target_paid_120d",
    )
    dashboard_data = build_dashboard_data(
        analytical_table=analytical_table,
        modeling_data=modeling_data,
        payment_model=payment_model,
    )
    output_paths = export_results(
        project_path=project_path,
        payment_model=payment_model,
        metrics=metrics,
        modeling_data=modeling_data,
        dashboard_data=dashboard_data,
    )

    print("\nMétricas del modelo")
    print(metrics.round(4).to_string(index=False))
    print("\nArchivos generados")
    for output_name, output_path in output_paths.items():
        print(f"{output_name}: {output_path}")
    print(f"\nRegistros de modelación: {len(modeling_data):,}")
    print(f"Registros del dashboard: {len(dashboard_data):,}")


if __name__ == "__main__":
    main()
