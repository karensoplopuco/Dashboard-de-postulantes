import pandas as pd
import numpy as np


# ==========================================
# RESUMEN TIPO DE EXPERIENCIA
# ==========================================

def resumen_tipo_experiencia(df):

    df_experiencia_laboral = df[
        df["type"] == "work_experience"
    ]

    df_practicas = df[
        df["position_clean"]
        .str.contains(
            "practicante|práctica|practica",
            case=False,
            na=False
        )
    ]

    experiencia_tipo = pd.DataFrame({
        "Tipo_experiencia": [
            "Experiencia laboral",
            "Prácticas",
            "Proyectos"
        ],

        "Cantidad_postulantes": [
            df_experiencia_laboral["_id_user"].nunique(),
            df_practicas["_id_user"].nunique(),
            df[
                df["type"] == "project"
            ]["_id_user"].nunique()
        ]
    })

    return experiencia_tipo


# ==========================================
# CALCULAR AÑOS DE EXPERIENCIA
# ==========================================

def calcular_experiencia(df):

    df = df.copy()

    df["meses_experiencia"] = np.where(
        df["startYear"].notna() &
        df["endYear"].notna(),

        (
            (df["endYear"] - df["startYear"]) * 12
            + (12 - df["startMonth"])
        ),

        0
    )

    df["años_experiencia"] = (
        df["meses_experiencia"] / 12
    )

    df = df.drop_duplicates(
        subset=[
            "_id_user",
            "position_clean",
            "startMonth",
            "startYear",
            "endYear"
        ]
    )

    experiencia_postulantes = (
        df
        .groupby("_id_user")["años_experiencia"]
        .sum()
        .reset_index()
    )

    experiencia_postulantes.columns = [
        "_id_user",
        "años_experiencia"
    ]

    experiencia_postulantes["Rango_experiencia"] = (
        experiencia_postulantes["años_experiencia"]
        .apply(rango_experiencia)
    )

    return experiencia_postulantes


# ==========================================
# RANGO DE EXPERIENCIA
# ==========================================

def rango_experiencia(años):

    if años == 0:
        return "Sin experiencia registrada"

    elif años < 1:
        return "Menos de 1 año"

    elif años < 3:
        return "1 a 3 años"

    elif años < 5:
        return "3 a 5 años"

    else:
        return "Más de 5 años"


# ==========================================
# RANGO DE PRÁCTICAS
# ==========================================

def rango_practica(x):

    if pd.isna(x):
        return "Sin registro"

    elif x < 1:
        return "Menos de 1 año"

    elif x <= 2:
        return "1 a 2 años"

    else:
        return "Más de 2 años"