
import pandas as pd


# ============================================================
# CLASIFICAR CARRERAS
# ============================================================

def clasificar_carrera(x):

    if pd.isna(x):
        return "Sin registro"

    x = str(x).lower().strip()

    if "administr" in x or "marketing" in x:
        return "Administración y Marketing"

    elif (
        "software" in x
        or "sistema" in x
        or "tecnolog" in x
        or "comput" in x
        or "informát" in x
        or "informat" in x
    ):
        return "Tecnología / Sistemas"

    elif "industrial" in x:
        return "Ingeniería Industrial"

    elif (
        "comunicación" in x
        or "comunicacion" in x
        or "comunicadora" in x
        or "publicidad" in x
    ):
        return "Comunicación y Publicidad"

    elif "econom" in x:
        return "Economía"

    elif "psicolog" in x:
        return "Psicología"

    elif "diseñ" in x or "disen" in x:
        return "Diseño"

    elif (
        "big data" in x
        or "ciencia de datos" in x
        or "ciencia datos" in x
        or "datos" in x
    ):
        return "Big Data y Ciencia de Datos"

    else:
        return "Otros"


# ============================================================
# CREAR ÁREA DE CARRERA
# ============================================================

def crear_area_carrera(df):

    df = df.copy()

    posibles_columnas = [
        "profession",
        "profession_postulante",
        "profesion",
        "carrera",
        "degree_clean"
    ]

    columna_profesion = None

    for columna in posibles_columnas:

        if columna in df.columns:
            columna_profesion = columna
            break

    if columna_profesion is None:

        df["area_carrera"] = "Sin registro"

        return df

    df["area_carrera"] = (
        df[columna_profesion]
        .apply(clasificar_carrera)
    )

    return df


# ============================================================
# RESUMEN DE CARRERAS
# ============================================================

def resumen_carreras(df):

    df = crear_area_carrera(df)

    carreras = (
        df[
            [
                "_id_postulante",
                "area_carrera"
            ]
        ]
        .drop_duplicates(
            subset=["_id_postulante"]
        )
        .groupby(
            "area_carrera"
        )
        .size()
        .reset_index(
            name="Cantidad_postulantes"
        )
        .rename(
            columns={
                "area_carrera": "Carrera"
            }
        )
        .sort_values(
            "Cantidad_postulantes",
            ascending=False
        )
        .reset_index(drop=True)
    )

    return carreras


# ============================================================
# NIVEL EDUCATIVO
# ============================================================

def resumen_nivel_educativo(df):

    if "type" not in df.columns:

        return pd.DataFrame(
            columns=[
                "Nivel_educativo",
                "Cantidad_postulantes"
            ]
        )

    datos = df.copy()

    # --------------------------------------------------------
    # Limpiar tipo de educación
    # --------------------------------------------------------

    datos["type"] = (
        datos["type"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # Excluir certificados y registros vacíos
    # --------------------------------------------------------

    datos = datos[
        (datos["type"] != "") &
        (datos["type"].str.lower() != "certificate")
    ].copy()

    # --------------------------------------------------------
    # Homologar niveles
    # --------------------------------------------------------

    datos["Nivel_educativo"] = (
        datos["type"]
        .replace({
            "Bachelor": "Bachiller",
            "Student": "Estudiante",
            "Other": "Otros",
            "Diploma": "Diplomado",
            "Master": "Maestría",
            "Master's": "Maestría",
            "Masters": "Maestría",
            "Licentiate": "Licenciatura"
        })
    )

    # --------------------------------------------------------
    # Contar postulantes, NO registros educativos
    # --------------------------------------------------------

    if "_id_user" in datos.columns:

        nivel_educativo = (
            datos[
                [
                    "_id_user",
                    "Nivel_educativo"
                ]
            ]
            .drop_duplicates()
            .groupby(
                "Nivel_educativo"
            )
            .size()
            .reset_index(
                name="Cantidad_postulantes"
            )
        )

    elif "_id_postulante" in datos.columns:

        nivel_educativo = (
            datos[
                [
                    "_id_postulante",
                    "Nivel_educativo"
                ]
            ]
            .drop_duplicates()
            .groupby(
                "Nivel_educativo"
            )
            .size()
            .reset_index(
                name="Cantidad_postulantes"
            )
        )

    else:

        nivel_educativo = (
            datos["Nivel_educativo"]
            .value_counts()
            .reset_index()
        )

        nivel_educativo.columns = [
            "Nivel_educativo",
            "Cantidad_postulantes"
        ]

    return (
        nivel_educativo
        .sort_values(
            "Cantidad_postulantes",
            ascending=False
        )
        .reset_index(drop=True)
    )

