"""Valida la construcción de la sábana analítica."""

from pathlib import Path
import unittest

from src.analytical_table_builder import AnalyticalTableBuilder
from src.database import SQLiteDatabase


class TestActivityOne(unittest.TestCase):
    """Valida los controles principales de la Actividad 1."""

    @classmethod
    def setUpClass(cls) -> None:
        """Construye la sábana una vez para todas las pruebas."""
        project_path = Path(__file__).resolve().parents[1]

        database = SQLiteDatabase(
            project_path / "data" / "base_datos_historica.db"
        )

        table_builder = AnalyticalTableBuilder(
            database=database,
            sql_path=project_path / "src" / "sql" / "sabana_analitica.sql",
        )

        cls.analytical_table = table_builder.build()

    def test_expected_row_count(self) -> None:
        """Valida la cantidad esperada de registros."""
        self.assertEqual(len(self.analytical_table), 21739)

    def test_cxc_id_is_unique(self) -> None:
        """Valida que el identificador de CxC sea único."""
        duplicated_ids = (
            self.analytical_table["cxc_id"]
            .duplicated()
            .sum()
        )

        self.assertEqual(duplicated_ids, 0)

    def test_amounts_are_consistent(self) -> None:
        """Valida la consistencia monetaria de los registros."""
        inconsistent_rows = (
            self.analytical_table["is_amount_consistent"] == 0
        ).sum()

        self.assertEqual(inconsistent_rows, 0)


if __name__ == "__main__":
    unittest.main()