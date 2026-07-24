"""Administra el acceso de solo lectura a bases SQLite."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class SQLiteDatabase:
    """Administra conexiones de solo lectura a una base SQLite."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def _build_uri(self) -> str:
        """Construye la URI de conexión en modo de solo lectura."""
        return f"file:{self.database_path.as_posix()}?mode=ro"

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Abre y cierra una conexión SQLite."""
        if not self.database_path.exists():
            raise FileNotFoundError(
                f"No se encontró la base: {self.database_path}"
            )

        connection = sqlite3.connect(
            self._build_uri(),
            uri=True,
        )

        try:
            yield connection
        finally:
            connection.close()