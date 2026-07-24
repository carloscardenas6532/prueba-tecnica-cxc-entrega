# Actividad 1. Exploración y sábana analítica

## Objetivo

Comprender la fuente, revisar su calidad y construir una sábana con una fila por cuenta por cobrar para el análisis y la modelación.

## Fuente y granularidad

La tabla original contiene 21.739 registros asociados a 800 cuentas, 2 productos y 71 códigos de transacción.

Cada fila representa una cuenta por cobrar. Como la fuente no incluye un identificador único de la obligación, se creó `cxc_id` a partir del `rowid` de SQLite. `num_cta` identifica la cuenta asociada, pero puede repetirse.

## Validaciones y reglas

Se revisaron valores nulos, duplicados, fechas, montos negativos y consistencia monetaria.

Se definieron tres estados:

* pagada: saldo pendiente menor o igual a 0,01;
* pago parcial: presenta pagos, pero conserva saldo;
* sin pago: valor pagado menor o igual a 0,01.

También se validó que el valor original correspondiera a la suma del valor pagado y el saldo pendiente.

La transformación principal se realizó en SQL y su ejecución se integró con Python.

## Hallazgos

El 79,69 % de las obligaciones está totalmente pagado, el 12,28 % presenta pago parcial y el 8,04 % no presenta pagos. La recuperación histórica ponderada es de 84,33 %.

Las obligaciones de mayor valor muestran menor recuperación. La antigüedad, calculada desde la fecha de creación, no presenta una relación creciente clara con el pago.

## Supuestos y limitaciones

La fuente no contiene fecha de vencimiento, identificador original de la obligación ni diccionario de datos. La antigüedad representa tiempo desde la creación, no días de mora.

El producto AHORRO concentra casi todos los registros, por lo que las comparaciones con CORRIENTE deben interpretarse con precaución.

## Archivos principales

* `src/sql/sabana_analitica.sql`
* `data/processed/sabana_analitica.csv`
* `notebooks/01_actividad_1_exploracion.ipynb`
