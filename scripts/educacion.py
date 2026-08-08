import pandas as pd


# ==========================================
# CLASIFICAR CARRERAS
# ==========================================

def clasificar_carrera(x):

    if pd.isna(x):
        return "Sin registro"

    x = str(x).lower().strip()

    if "administr" in x or "marketing" in x:
        return "Administración y Marketing"

    elif "software" in x or "sistema" in x or "tecnolog" in x:
        return "Tecnología / Sistemas"

    elif "industrial" in x:
        return "Ingeniería Industrial"

    elif "comunicación" in x or "comunicadora" in x or "publicidad" in x:
        return "Comunicación y Publicidad"

    elif "econom" in x:
        return "Economía"

    elif "psicolog" in x:
        return "Psicología"

    elif "diseñ" in x:
        return "Diseño"

    elif "big data" in x or "datos" in x:
        return "Big Data y Ciencia de Datos"

    else:
        return "Otros"


# ==========================================
# ÁREA DE CARRERA
# ==========================================

def crear_area_carrera(df):

    df = df.copy()

    df["area_carrera"] = (
        df["profession"]
        .apply(clasificar_carrera)
    )

    return df


# ==========================================
# RESUMEN DE CARRERAS
# ==========================================

def resumen_carreras(df):

    carreras = (
        df["area_carrera"]
        .value_counts()
        .reset_index()
    )

    carreras.columns = [
        "Carrera",
        "Cantidad_postulantes"
    ]

    return carreras


# ==========================================
# NIVEL EDUCATIVO
# ==========================================

def resumen_nivel_educativo(df):

    nivel_educativo = (
        df[
            (df["type"] != "Certificate") &
            (df["type"].notna()) &
            (df["type"] != "")
        ]["type"]
        .replace({
            "Bachelor": "Bachiller",
            "Student": "Estudiante",
            "Other": "Otros",
            "Diploma": "Diplomado",
            "Master": "Maestría"
        })
        .value_counts()
        .reset_index()
    )

    nivel_educativo.columns = [
        "Nivel_educativo",
        "Cantidad_postulantes"
    ]

    return nivel_educativo