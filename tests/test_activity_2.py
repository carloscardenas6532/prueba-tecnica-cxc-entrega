"""Valida la preparación y ejecución del modelo de pago."""

from pathlib import Path
import unittest

from src.analytical_table_builder import AnalyticalTableBuilder
from src.database import SQLiteDatabase
from src.modelo.payment_probability_model import (
    PaymentProbabilityModel,
)
from src.run_activity_2 import prepare_modeling_data


class TestActivityTwo(unittest.TestCase):
    """Valida los componentes principales de la Actividad 2."""

    @classmethod
    def setUpClass(cls) -> None:
        """Construye los datos necesarios para las pruebas."""
        project_path = Path(__file__).resolve().parents[1]

        database = SQLiteDatabase(
            project_path / "data" / "base_datos_historica.db"
        )

        table_builder = AnalyticalTableBuilder(
            database=database,
            sql_path=(
                project_path
                / "src"
                / "sql"
                / "sabana_analitica.sql"
            ),
        )

        analytical_table = table_builder.build()

        cls.modeling_data = prepare_modeling_data(
            analytical_table
        )

    def test_expected_eligible_records(self) -> None:
        """Valida la población elegible para modelación."""
        self.assertEqual(
            len(self.modeling_data),
            21276,
        )

    def test_target_is_binary(self) -> None:
        """Valida que la variable objetivo sea binaria."""
        target_values = set(
            self.modeling_data["target_paid_120d"].unique()
        )

        self.assertEqual(
            target_values,
            {0, 1},
        )

    def test_payment_probabilities_are_valid(self) -> None:
        """Valida el rango de las probabilidades estimadas."""
        sample_data = self.modeling_data.sample(
            n=2000,
            random_state=42,
        )

        payment_model = PaymentProbabilityModel()

        payment_model.fit(
            data=sample_data,
            target_column="target_paid_120d",
        )

        probabilities = payment_model.predict_probability(
            sample_data
        )

        self.assertEqual(
            len(probabilities),
            len(sample_data),
        )

        self.assertTrue(
            ((probabilities >= 0) & (probabilities <= 1)).all()
        )


if __name__ == "__main__":
    unittest.main()