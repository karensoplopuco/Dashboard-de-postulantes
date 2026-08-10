
import pandas as pd
import numpy as np


# ============================================================
# RESUMEN TIPO DE EXPERIENCIA
# ============================================================

def resumen_tipo_experiencia(df):

    df = df.copy()

    # --------------------------------------------------------
    # Experiencia laboral
    # --------------------------------------------------------

    if "type" in df.columns:

        df_experiencia_laboral = df[
            df["type"]
            .astype(str)
            .str.lower()
            .eq("work_experience")
        ]

    else:

        df_experiencia_laboral = pd.DataFrame()


    # --------------------------------------------------------
    # Prácticas
    # --------------------------------------------------------

    if "position_clean" in df.columns:

        df_practicas = df[
            df["position_clean"]
            .fillna("")
            .astype(str)
            .str.contains(
                "practicante|práctica|practica",
                case=False,
                na=False
            )
        ]

    else:

        df_practicas = pd.DataFrame()


    # --------------------------------------------------------
    # Proyectos
    # --------------------------------------------------------

    if "type" in df.columns:

        df_proyectos = df[
            df["type"]
            .astype(str)
            .str.lower()
            .eq("project")
        ]

    else:

        df_proyectos = pd.DataFrame()


    # --------------------------------------------------------
    # ID DE USUARIO
    # --------------------------------------------------------

    def usuarios_unicos(data):

        if (
            not data.empty
            and "_id_user" in data.columns
        ):

            return (
                data["_id_user"]
                .dropna()
                .astype(str)
                .str.strip()
                .replace("", pd.NA)
                .dropna()
                .nunique()
            )

        return 0


    return pd.DataFrame({

        "Tipo_experiencia": [
            "Experiencia laboral",
            "Prácticas",
            "Proyectos"
        ],

        "Cantidad_postulantes": [
            usuarios_unicos(
                df_experiencia_laboral
            ),

            usuarios_unicos(
                df_practicas
            ),

            usuarios_unicos(
                df_proyectos
            )
        ]
    })


# ============================================================
# CALCULAR AÑOS DE EXPERIENCIA
# ============================================================

def calcular_experiencia(df):

    df = df.copy()

    columnas_necesarias = [
        "_id_user",
        "startYear",
        "startMonth"
    ]

    for columna in columnas_necesarias:

        if columna not in df.columns:

            return pd.DataFrame(
                columns=[
                    "_id_user",
                    "años_experiencia",
                    "Rango_experiencia"
                ]
            )


    # --------------------------------------------------------
    # Convertir fechas a numérico
    # --------------------------------------------------------

    df["startYear"] = pd.to_numeric(
        df["startYear"],
        errors="coerce"
    )

    df["startMonth"] = pd.to_numeric(
        df["startMonth"],
        errors="coerce"
    )

    if "endYear" in df.columns:

        df["endYear"] = pd.to_numeric(
            df["endYear"],
            errors="coerce"
        )

    else:

        df["endYear"] = np.nan


    if "endMonth" in df.columns:

        df["endMonth"] = pd.to_numeric(
            df["endMonth"],
            errors="coerce"
        )

    else:

        df["endMonth"] = np.nan


    # --------------------------------------------------------
    # Mes de inicio
    # --------------------------------------------------------

    df["startMonth"] = (
        df["startMonth"]
        .fillna(1)
        .clip(1, 12)
    )


    # --------------------------------------------------------
    # Experiencias terminadas
    # --------------------------------------------------------

    experiencia_terminada = (
        df["startYear"].notna()
        & df["endYear"].notna()
    )


    df["meses_experiencia"] = 0.0


    df.loc[
        experiencia_terminada,
        "meses_experiencia"
    ] = (

        (
            df.loc[
                experiencia_terminada,
                "endYear"
            ]

            -

            df.loc[
                experiencia_terminada,
                "startYear"
            ]
        )
        * 12

        +

        (
            df.loc[
                experiencia_terminada,
                "endMonth"
            ]
            .fillna(12)

            -

            df.loc[
                experiencia_terminada,
                "startMonth"
            ]

            + 1
        )
    )


    # --------------------------------------------------------
    # Experiencias actuales
    #
    # Si no existe endYear, calculamos hasta hoy.
    # --------------------------------------------------------

    experiencia_actual = (
        df["startYear"].notna()
        & df["endYear"].isna()
    )

    if experiencia_actual.any():

        hoy = pd.Timestamp.today()

        df.loc[
            experiencia_actual,
            "meses_experiencia"
        ] = (

            (
                hoy.year
                -
                df.loc[
                    experiencia_actual,
                    "startYear"
                ]
            )
            * 12

            +

            (
                hoy.month
                -
                df.loc[
                    experiencia_actual,
                    "startMonth"
                ]
                + 1
            )
        )


    # --------------------------------------------------------
    # Evitar valores negativos
    # --------------------------------------------------------

    df["meses_experiencia"] = (
        df["meses_experiencia"]
        .clip(lower=0)
    )


    # --------------------------------------------------------
    # Convertir a años
    # --------------------------------------------------------

    df["años_experiencia"] = (
        df["meses_experiencia"] / 12
    )


    # --------------------------------------------------------
    # Eliminar experiencias duplicadas
    # --------------------------------------------------------

    columnas_dedupe = [
        "_id_user",
        "position_clean",
        "startMonth",
        "startYear",
        "endMonth",
        "endYear"
    ]

    columnas_dedupe = [
        c for c in columnas_dedupe
        if c in df.columns
    ]

    df = (
        df
        .drop_duplicates(
            subset=columnas_dedupe
        )
    )


    # --------------------------------------------------------
    # SUMAR EXPERIENCIA POR USUARIO
    # --------------------------------------------------------

    experiencia_postulantes = (
        df
        .groupby(
            "_id_user",
            as_index=False
        )
        .agg(
            años_experiencia=(
                "años_experiencia",
                "sum"
            )
        )
    )


    # --------------------------------------------------------
    # RANGO
    # --------------------------------------------------------

    experiencia_postulantes[
        "Rango_experiencia"
    ] = (
        experiencia_postulantes[
            "años_experiencia"
        ]
        .apply(
            rango_experiencia
        )
    )


    return experiencia_postulantes


# ============================================================
# RANGO DE EXPERIENCIA
# ============================================================

def rango_experiencia(años):

    if pd.isna(años) or años <= 0:

        return "Sin experiencia registrada"

    elif años < 1:

        return "Menos de 1 año"

    elif años < 3:

        return "1 a 3 años"

    elif años < 5:

        return "3 a 5 años"

    else:

        return "Más de 5 años"


# ============================================================
# RANGO DE PRÁCTICAS
# ============================================================

def rango_practica(x):

    if pd.isna(x):

        return "Sin registro"

    elif x < 1:

        return "Menos de 1 año"

    elif x <= 2:

        return "1 a 2 años"

    else:

        return "Más de 2 años"

