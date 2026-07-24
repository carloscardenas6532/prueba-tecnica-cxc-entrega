"""Ejecuta la construcción de la sábana analítica."""

from pathlib import Path

from src.analytical_table_builder import AnalyticalTableBuilder
from src.database import SQLiteDatabase


def main() -> None:
    """Construye, valida y exporta la sábana analítica."""
    project_path = Path(__file__).resolve().parents[1]

    database = SQLiteDatabase(
        project_path / "data" / "base_datos_historica.db"
    )

    table_builder = AnalyticalTableBuilder(
        database=database,
        sql_path=project_path / "src" / "sql" / "sabana_analitica.sql",
    )

    analytical_table = table_builder.build()
    validation_results = table_builder.validate(analytical_table)

    output_path = (
        project_path
        / "data"
        / "processed"
        / "sabana_analitica.csv"
    )

    table_builder.export_csv(
        analytical_table=analytical_table,
        output_path=output_path,
    )

    print(validation_results.to_string(index=False))
    print(f"Sábana exportada en: {output_path}")


if __name__ == "__main__":
    main()