
import pandas as pd


# ============================================================
# KPIs DEL DASHBOARD DE POSTULANTES
# ============================================================

def calcular_kpis_postulantes(df):

    df = df.copy()

    # ========================================================
    # VALIDACIÓN
    # ========================================================

    if "_id_postulante" not in df.columns:

        raise ValueError(
            "El dataset no contiene '_id_postulante'."
        )

    # ========================================================
    # TOTAL POSTULANTES
    # ========================================================

    total = (
        df["_id_postulante"]
        .dropna()
        .astype(str)
        .str.strip()
        .nunique()
    )

    # ========================================================
    # POSTULANTES CON CV
    # ========================================================

    if "tiene_cv" in df.columns:

        con_cv = (
            df["tiene_cv"]
            .fillna(False)
            .astype(bool)
            .sum()
        )

    else:

        con_cv = 0

    # ========================================================
    # POSTULANTES ACTIVOS
    # ========================================================

    if "isActive" in df.columns:

        activos = (
            df["isActive"]
            .fillna(False)
            .astype(bool)
            .sum()
        )

    else:

        activos = 0

    # ========================================================
    # USO DE IA
    # ========================================================

    if "uso_ia" in df.columns:

        uso_ia = (
            df["uso_ia"]
            .fillna(False)
            .astype(bool)
            .sum()
        )

    else:

        uso_ia = 0

    # ========================================================
    # USO DE CURSOS
    # ========================================================

    if "cantidad_cursos" in df.columns:

        cursos = (
            pd.to_numeric(
                df["cantidad_cursos"],
                errors="coerce"
            )
            .fillna(0)
            .gt(0)
            .sum()
        )

    else:

        cursos = 0

    # ========================================================
    # PARTICIPACIÓN EN EVENTOS
    # ========================================================

    if "participo_evento" in df.columns:

        eventos = (
            df["participo_evento"]
            .fillna(False)
            .astype(bool)
            .sum()
        )

    else:

        eventos = 0

    # ========================================================
    # FUNCIÓN PARA PORCENTAJES
    # ========================================================

    def porcentaje(valor):

        if total == 0:
            return 0

        return round(
            valor / total * 100,
            2
        )

    # ========================================================
    # RESULTADO
    # ========================================================

    return {

        "total_postulantes":
            total,

        "postulantes_con_cv":
            int(con_cv),

        "porcentaje_cv":
            porcentaje(con_cv),

        "postulantes_activos":
            int(activos),

        "porcentaje_activos":
            porcentaje(activos),

        "postulantes_uso_ia":
            int(uso_ia),

        "porcentaje_ia":
            porcentaje(uso_ia),

        "postulantes_cursos":
            int(cursos),

        "porcentaje_cursos":
            porcentaje(cursos),

        "postulantes_eventos":
            int(eventos),

        "porcentaje_eventos":
            porcentaje(eventos)
    }
