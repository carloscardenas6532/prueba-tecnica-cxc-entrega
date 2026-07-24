# Actividad 2. Modelo de probabilidad de pago

## Objetivo

Estimar la probabilidad de que una cuenta por cobrar alcance el pago total durante los primeros 120 días desde su creación.

## Población y variable objetivo

El objetivo toma el valor 1 cuando la obligación fue pagada totalmente dentro de 120 días y 0 cuando no alcanzó el pago total en ese periodo.

Se utilizaron 21.276 registros. Se excluyeron 463 obligaciones no pagadas que todavía no habían completado los 120 días de observación.

La tasa de pago dentro del horizonte fue de 48,53 %.

## Variables y control de fuga

Se utilizaron variables conocidas al crear la obligación:

* producto;
* código de transacción;
* valor original;
* año y mes de creación;
* día de la semana.

Se excluyeron el valor pagado, el saldo pendiente, la fecha del último pago, el estado final y las métricas de recuperación porque contienen información posterior al momento de predicción.

`num_cta` se utilizó para separar entrenamiento y validación, evitando que obligaciones de una misma cuenta aparecieran en ambos grupos.

## Comparación y selección

Se compararon una probabilidad general de referencia, una regresión logística y un bosque aleatorio.

La regresión logística obtuvo en validación agrupada:

* ROC-AUC: 0,7028;
* Average Precision: 0,7186;
* Brier Score: 0,2180.

El bosque aleatorio mostró una mejora pequeña en clasificación, pero no mejoró la calidad de las probabilidades y añadió complejidad. Se seleccionó la regresión logística por ofrecer un desempeño similar y una interpretación más sencilla.

## Segmentación

Las probabilidades se agruparon en cuatro segmentos:

* alto riesgo: menor a 0,40;
* riesgo medio: entre 0,40 y 0,60;
* probable pago: entre 0,60 y 0,80;
* alta probabilidad de pago: superior a 0,80.

La tasa observada aumenta entre los segmentos, lo que permite utilizarlos para priorizar la gestión.

## Limitaciones

El horizonte de 120 días es un supuesto analítico. La fecha del último pago se utilizó como aproximación del momento del pago total.

El modelo no incluye información sobre vencimientos, perfil del cliente, condiciones contractuales ni gestiones de cobranza. Sus resultados representan asociaciones y deben monitorearse antes de utilizarlos de manera recurrente.

## Archivos principales

* `notebooks/02_actividad_2_modelo.ipynb`
* `src/modelo/payment_probability_model.py`
* `src/metricas/metricas_modelo.csv`
* `data/processed/predicciones_cxc.csv`
