"""Construye y exporta la sábana analítica."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.database import SQLiteDatabase


class AnalyticalTableBuilder:
    """Construye la sábana analítica mediante una consulta SQL."""

    def __init__(
        self,
        database: SQLiteDatabase,
        sql_path: Path,
    ) -> None:
        self.database = database
        self.sql_path = sql_path

    def build(self) -> pd.DataFrame:
        """Ejecuta la consulta SQL y devuelve la sábana analítica."""
        if not self.sql_path.exists():
            raise FileNotFoundError(
                f"No se encontró la consulta SQL: {self.sql_path}"
            )

        query = self.sql_path.read_text(encoding="utf-8")

        with self.database.connect() as connection:
            analytical_table = pd.read_sql_query(
                query,
                connection,
            )

        return analytical_table

    @staticmethod
    def validate(
        analytical_table: pd.DataFrame,
    ) -> pd.DataFrame:
        """Ejecuta controles básicos sobre la sábana."""
        return pd.DataFrame(
            {
                "validation": [
                    "total_rows",
                    "unique_cxc_ids",
                    "duplicated_cxc_ids",
                    "inconsistent_amount_rows",
                ],
                "value": [
                    len(analytical_table),
                    analytical_table["cxc_id"].nunique(),
                    analytical_table["cxc_id"].duplicated().sum(),
                    (
                        analytical_table["is_amount_consistent"] == 0
                    ).sum(),
                ],
            }
        )

    @staticmethod
    def export_csv(
        analytical_table: pd.DataFrame,
        output_path: Path,
    ) -> None:
        """Exporta la sábana analítica en formato CSV."""
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        analytical_table.to_csv(
            output_path,
            index=False,
            encoding="utf-8",
        )