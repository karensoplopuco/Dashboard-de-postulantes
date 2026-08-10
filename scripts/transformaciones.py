import pandas as pd


# ============================================================
# LIMPIEZA GENERAL DE TEXTO
# ============================================================

def limpiar_texto(df, columnas):
    """
    Limpia columnas de texto:
    - Reemplaza nulos por ""
    - Convierte a string
    - Elimina espacios innecesarios
    """

    df = df.copy()

    for columna in columnas:

        if columna in df.columns:

            df[columna] = (
                df[columna]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    return df


# ============================================================
# CONVERTIR OBJECTID A STRING
# ============================================================

def convertir_ids_a_string(df):
    """
    Convierte columnas _id y referencias relacionadas
    a string para facilitar los cruces entre DataFrames.
    """

    df = df.copy()

    columnas_id = [
        "_id",
        "user",
        "cv",
        "job",
        "applicant",
        "company",
        "companyId",
        "course",
        "event",
        "conversation"
    ]

    for columna in columnas_id:

        if columna in df.columns:

            df[columna] = df[columna].astype(str)

    return df


# ============================================================
# LIMPIAR USERS
# ============================================================

def transformar_users(df):

    df = df.copy()

    df = convertir_ids_a_string(df)

    df = limpiar_texto(
        df,
        [
            "email",
            "firstName",
            "lastName",
            "phone",
            "location",
            "modalidad",
            "disponibilidad",
            "role"
        ]
    )

    return df


# ============================================================
# LIMPIAR CVS
# ============================================================

def transformar_cvs(df):

    df = df.copy()

    df = convertir_ids_a_string(df)

    df = limpiar_texto(
        df,
        [
            "name",
            "email",
            "firstName",
            "lastName",
            "profession",
            "summary",
            "location"
        ]
    )

    return df


# ============================================================
# TRANSFORMAR EDUCACIÓN
# ============================================================

def transformar_educacion(df):

    df = df.copy()

    # ==========================================
    # NORMALIZAR ID DE USUARIO
    # ==========================================

    if "user" in df.columns:
        df["user"] = df["user"].astype(str)

    # ==========================================
    # LIMPIAR DEGREE
    # ==========================================

    if "degree" in df.columns:
        df["degree_clean"] = (
            df["degree"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

    # ==========================================
    # LIMPIAR INSTITUCIÓN
    # ==========================================

    if "institution" in df.columns:
        df["institution"] = (
            df["institution"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # ==========================================
    # NIVEL DE FORMACIÓN
    # ==========================================

    if "degree_clean" in df.columns:

        df["nivel_formacion"] = "Otros"

        df.loc[
            df["degree_clean"].str.contains(
                "estudiante|student",
                na=False
            ),
            "nivel_formacion"
        ] = "Estudiante"

        df.loc[
            df["degree_clean"].str.contains(
                "bachiller|bachelor",
                na=False
            ),
            "nivel_formacion"
        ] = "Bachiller"

        df.loc[
            df["degree_clean"].str.contains(
                "licenci|ingenier|título|titulo",
                na=False
            ),
            "nivel_formacion"
        ] = "Licenciatura"

        df.loc[
            df["degree_clean"].str.contains(
                "maestr|master|magister",
                na=False
            ),
            "nivel_formacion"
        ] = "Maestría"

    print(
        "Educación transformada:",
        df.shape,
        "| columnas:",
        df.columns.tolist()
    )

    return df

    # --------------------------------------------
    # Fechas
    # --------------------------------------------

    for columna in ["startDate", "endDate"]:

        if columna in df.columns:

            df[columna] = pd.to_datetime(
                df[columna],
                errors="coerce"
            )

    # --------------------------------------------
    # Duplicados
    # --------------------------------------------

    if "_id" in df.columns:

        df = df.drop_duplicates(
            subset="_id"
        )

    return df


# ============================================================
# TRANSFORMAR EXPERIENCIA LABORAL
# ============================================================

def transformar_experiencia(df):

    df = df.copy()

    df = convertir_ids_a_string(df)

    df = limpiar_texto(
        df,
        [
            "company",
            "position",
            "type",
            "description"
        ]
    )

    # --------------------------------------------
    # Fechas
    # --------------------------------------------

    for columna in ["startDate", "endDate"]:

        if columna in df.columns:

            df[columna] = pd.to_datetime(
                df[columna],
                errors="coerce"
            )

    # --------------------------------------------
    # Experiencia actual
    # --------------------------------------------

    if "inProgress" in df.columns:

        df["inProgress"] = (
            df["inProgress"]
            .fillna(False)
            .astype(bool)
        )

    # --------------------------------------------
    # Eliminar duplicados
    # --------------------------------------------

    if "_id" in df.columns:

        df = df.drop_duplicates(
            subset="_id"
        )

    return df