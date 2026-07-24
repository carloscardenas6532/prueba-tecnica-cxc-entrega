# Prueba técnica – Cuentas por cobrar

Solución analítica para comprender el comportamiento de las cuentas por cobrar, estimar la probabilidad de pago total a 120 días y apoyar la priorización de la gestión operativa.

## Contenido del proyecto

* `data/`: base de datos original y archivos procesados.
* `notebooks/`: exploración de datos y modelación.
* `src/`: transformación SQL y lógica en Python.
* `tests/`: validaciones principales.
* `docs/`: documentación técnica e informe ejecutivo.
* `powerbi/`: dashboard de Power BI.

## Requisitos

* Python 3.11
* SQLite
* Power BI Desktop para abrir el dashboard

## Instalación

Desde la raíz del proyecto, ejecutar en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecución

Construir la sábana analítica:

```powershell
python -m src.run_activity_1
```

Entrenar el modelo y generar los archivos para Power BI:

```powershell
python -m src.run_activity_2
```

Ejecutar las pruebas:

```powershell
python -m unittest discover -s tests
```

## Resultados generados

La ejecución produce los siguientes archivos:

* `data/processed/sabana_analitica.csv`
* `data/processed/predicciones_cxc.csv`
* `data/processed/dashboard_cxc.csv`
* `src/modelo/modelo_probabilidad_pago.pkl`
* `src/metricas/metricas_modelo.csv`

El dashboard se encuentra en:

* `powerbi/dashboard_cxc.pbix`

El informe ejecutivo se encuentra en:

* `docs/informe_ejecutivo_cxc.pdf`

## Enfoque analítico

La solución parte de una fila por cuenta por cobrar, revisa la calidad de la fuente y construye una sábana analítica mediante SQL.

El modelo estima la probabilidad de pago total dentro de 120 días utilizando únicamente información conocida al crear la obligación. Se compararon una referencia general, una regresión logística y un bosque aleatorio.

La regresión logística fue seleccionada por ofrecer un desempeño similar al bosque aleatorio, probabilidades ligeramente mejor calibradas y una interpretación más sencilla.

Los supuestos, decisiones y limitaciones se encuentran en la carpeta `docs/`.
