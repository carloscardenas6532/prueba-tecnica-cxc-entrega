# Actividad 3. Dashboard e informe ejecutivo

## Objetivo

Presentar el comportamiento de las cuentas por cobrar y los resultados del modelo en una herramienta comprensible para usuarios de negocio.

## Fuente

El dashboard utiliza `data/processed/dashboard_cxc.csv`, con una fila por cuenta por cobrar.

El archivo integra información histórica, probabilidad de pago a 120 días, segmento de riesgo, recuperación esperada y exposición esperada.

## Contenido del dashboard

El dashboard contiene tres páginas:

1. **Resumen ejecutivo:** presenta los principales valores del portafolio, recuperación histórica y estimaciones esperadas.
2. **Riesgo y priorización:** permite identificar segmentos, transacciones y obligaciones con mayor exposición.
3. **Desempeño del modelo:** presenta métricas de clasificación, calibración y comportamiento observado por segmento.

Las métricas de evaluación se calcularon con predicciones fuera de muestra. Las probabilidades utilizadas para la priorización fueron generadas con el modelo final entrenado sobre la población elegible.

## Uso esperado

El dashboard permite pasar de una revisión general del saldo a una priorización que combina riesgo y valor económico.

Debe utilizarse como apoyo para la gestión. El modelo estima pago total dentro de 120 días, no representa de forma específica los pagos parciales y no reemplaza la revisión del equipo operativo.

## Archivos principales

* `powerbi/dashboard_cxc.pbix`
* `data/processed/dashboard_cxc.csv`
* `docs/informe_ejecutivo_cxc.docx`
* `docs/informe_ejecutivo_cxc.pdf`
