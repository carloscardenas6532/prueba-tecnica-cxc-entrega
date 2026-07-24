WITH normalized_source AS (
    SELECT
        rowid AS source_row_id,
        printf('CXC_%06d', rowid) AS cxc_id,
        cod_apli_prod,
        descri_cod_apli_prod,
        num_cta,
        cod_trn,
        descri_cod_trn,

        date(
            substr(CAST(f_creacion AS TEXT), 1, 4) || '-' ||
            substr(CAST(f_creacion AS TEXT), 5, 2) || '-' ||
            substr(CAST(f_creacion AS TEXT), 7, 2)
        ) AS creation_date,

        date(
            substr(CAST(f_ultimo_pago AS TEXT), 1, 4) || '-' ||
            substr(CAST(f_ultimo_pago AS TEXT), 5, 2) || '-' ||
            substr(CAST(f_ultimo_pago AS TEXT), 7, 2)
        ) AS last_payment_date,

        date(
            printf(
                '%04d-%02d-%02d',
                year,
                month,
                day
            )
        ) AS reference_date,

        vlr_original,
        vlr_pagado,
        vlr_pendiente_pago

    FROM tabla1
),

derived_features AS (
    SELECT
        *,

        CAST(
            julianday(reference_date)
            - julianday(creation_date)
            AS INTEGER
        ) AS age_days,

        CAST(
            julianday(reference_date)
            - julianday(last_payment_date)
            AS INTEGER
        ) AS days_since_last_payment,

        CAST(
            julianday(last_payment_date)
            - julianday(creation_date)
            AS INTEGER
        ) AS days_creation_to_last_payment,

        ROUND(
            vlr_pagado / NULLIF(vlr_original, 0),
            6
        ) AS recovery_rate,

        ROUND(
            vlr_pendiente_pago / NULLIF(vlr_original, 0),
            6
        ) AS pending_rate,

        CASE
            WHEN vlr_pendiente_pago <= 0.01
                THEN 'pagada_total'
            WHEN vlr_pagado <= 0.01
                THEN 'sin_pago'
            ELSE 'pago_parcial'
        END AS payment_status,

        CASE
            WHEN vlr_pendiente_pago <= 0.01 THEN 1
            ELSE 0
        END AS is_fully_paid,

        CASE
            WHEN vlr_pagado > 0.01
             AND vlr_pendiente_pago > 0.01 THEN 1
            ELSE 0
        END AS is_partially_paid,

        CASE
            WHEN vlr_pagado <= 0.01 THEN 1
            ELSE 0
        END AS is_unpaid,

        CASE
            WHEN ABS(
                vlr_original
                - vlr_pagado
                - vlr_pendiente_pago
            ) <= 0.01 THEN 1
            ELSE 0
        END AS is_amount_consistent,

        CASE
            WHEN vlr_pagado <= 0.01
             AND last_payment_date IS NOT NULL THEN 1
            ELSE 0
        END AS has_payment_date_without_paid_amount

    FROM normalized_source
)

SELECT
    *,

    CASE
        WHEN age_days <= 30 THEN '00_30_dias'
        WHEN age_days <= 60 THEN '31_60_dias'
        WHEN age_days <= 90 THEN '61_90_dias'
        WHEN age_days <= 180 THEN '91_180_dias'
        WHEN age_days <= 360 THEN '181_360_dias'
        ELSE '361_mas_dias'
    END AS age_bucket

FROM derived_features
ORDER BY source_row_id;