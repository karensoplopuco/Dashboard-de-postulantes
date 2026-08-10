import pandas as pd


# ============================================================
# RESUMEN DE POSTULACIONES
# ============================================================

def resumen_postulaciones(df):

    if df.empty:
        return pd.DataFrame(
            columns=[
                "Indicador",
                "Cantidad"
            ]
        )

    total_postulaciones = len(df)

    usuarios_unicos = (
        df["user"]
        .nunique()
        if "user" in df.columns
        else 0
    )

    empleos_unicos = (
        df["job"]
        .nunique()
        if "job" in df.columns
        else 0
    )

    return pd.DataFrame({
        "Indicador": [
            "Postulaciones totales",
            "Postulantes con postulación",
            "Empleos con postulaciones"
        ],

        "Cantidad": [
            total_postulaciones,
            usuarios_unicos,
            empleos_unicos
        ]
    })


# ============================================================
# POSTULACIONES POR ESTADO
# ============================================================

def resumen_estado_postulacion(df):

    if "status" not in df.columns:
        return pd.DataFrame(
            columns=[
                "Estado",
                "Cantidad"
            ]
        )

    estados = (
        df["status"]
        .fillna("Sin registro")
        .astype(str)
        .str.strip()
        .replace("", "Sin registro")
        .value_counts()
        .reset_index()
    )

    estados.columns = [
        "Estado",
        "Cantidad"
    ]

    return estados


# ============================================================
# POSTULACIONES POR MES
# ============================================================

def resumen_postulaciones_mes(df):

    posibles_fechas = [
        "createdAt",
        "created_at",
        "appliedAt",
        "applicationDate"
    ]

    columna_fecha = None

    for columna in posibles_fechas:

        if columna in df.columns:
            columna_fecha = columna
            break

    if columna_fecha is None:

        return pd.DataFrame(
            columns=[
                "Mes",
                "Cantidad"
            ]
        )

    x = df.copy()

    x[columna_fecha] = pd.to_datetime(
        x[columna_fecha],
        errors="coerce"
    )

    x = x[
        x[columna_fecha].notna()
    ].copy()

    if x.empty:

        return pd.DataFrame(
            columns=[
                "Mes",
                "Cantidad"
            ]
        )

    x["Mes"] = (
        x[columna_fecha]
        .dt.to_period("M")
        .astype(str)
    )

    resultado = (
        x["Mes"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    resultado.columns = [
        "Mes",
        "Cantidad"
    ]

    return resultado


# ============================================================
# POSTULACIONES POR USUARIO
# ============================================================

def resumen_postulaciones_usuario(df):

    if "user" not in df.columns:

        return pd.DataFrame(
            columns=[
                "user",
                "cantidad_postulaciones"
            ]
        )

    resultado = (
        df
        .dropna(subset=["user"])
        .groupby("user")
        .size()
        .reset_index(
            name="cantidad_postulaciones"
        )
    )

    return resultado