import pandas as pd


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def convertir_id(df, columna):
    """
    Convierte una columna ID a texto para evitar
    problemas de comparación entre ObjectId y string.
    """
    df = df.copy()

    if columna in df.columns:
        df[columna] = (
            df[columna]
            .astype(str)
            .str.strip()
        )

    return df


# ============================================================
# CRUCE 1: USERS + CVS
# ============================================================

def cruzar_users_cvs(df_users, df_cvs):

    print("\n🔗 Cruzando USERS + CVS")

    users = df_users.copy()
    cvs = df_cvs.copy()

    # --------------------------------------------------------
    # VALIDAR COLUMNAS
    # --------------------------------------------------------

    if "_id" not in users.columns:
        raise KeyError(
            "df_users no contiene la columna '_id'."
        )

    if "_id" not in cvs.columns:
        raise KeyError(
            "df_cvs no contiene la columna '_id'."
        )

    if "user" not in cvs.columns:
        raise KeyError(
            "df_cvs no contiene la columna 'user'."
        )

    # --------------------------------------------------------
    # NORMALIZAR IDs
    # --------------------------------------------------------

    users = convertir_id(
        users,
        "_id"
    )

    cvs = convertir_id(
        cvs,
        "_id"
    )

    cvs = convertir_id(
        cvs,
        "user"
    )

    # --------------------------------------------------------
    # RENOMBRAR IDs DEL CV
    # --------------------------------------------------------

    cvs = cvs.rename(
        columns={
            "_id": "_id_cv"
        }
    )

    # --------------------------------------------------------
    # SELECCIONAR CV PRINCIPAL
    # --------------------------------------------------------

    if "isMain" in cvs.columns:

        cvs_main = cvs[
            cvs["isMain"] == True
        ].copy()

        # Si no existen CV principales,
        # utilizar todos los CV disponibles.

        if cvs_main.empty:
            cvs_main = cvs.copy()

    else:

        cvs_main = cvs.copy()

    # --------------------------------------------------------
    # UN CV POR USUARIO
    # --------------------------------------------------------

    cvs_main = (
        cvs_main
        .drop_duplicates(
            subset="user"
        )
    )

    # --------------------------------------------------------
    # CRUCE
    # --------------------------------------------------------

    df = pd.merge(
        users,
        cvs_main,
        left_on="_id",
        right_on="user",
        how="left",
        suffixes=(
            "_user",
            "_cv"
        )
    )

    # --------------------------------------------------------
    # INDICADOR DE CV
    # --------------------------------------------------------

    df["tiene_cv"] = (
        df["user"].notna()
    )

    # --------------------------------------------------------
    # GARANTIZAR UN USUARIO POR FILA
    # --------------------------------------------------------

    df = (
        df
        .drop_duplicates(
            subset="_id"
        )
        .reset_index(drop=True)
    )

    print(
        f"✅ Users + CVs: {df.shape}"
    )

    return df


# ============================================================
# CRUCE 2: USERS + CVS + EDUCACIÓN
# ============================================================

def cruzar_users_educacion(
    df_users_cv,
    df_educations
):

    print(
        "\n🔗 Cruzando USERS + EDUCACIÓN mediante CV"
    )

    users_cv = df_users_cv.copy()
    education = df_educations.copy()

    # --------------------------------------------------------
    # VALIDAR
    # --------------------------------------------------------

    if "_id_cv" not in users_cv.columns:
        raise KeyError(
            "df_users_cv no contiene '_id_cv'."
        )

    if "cv" not in education.columns:
        raise KeyError(
            "df_educations no contiene 'cv'."
        )

    # --------------------------------------------------------
    # NORMALIZAR
    # --------------------------------------------------------

    users_cv = convertir_id(
        users_cv,
        "_id_cv"
    )

    education = convertir_id(
        education,
        "cv"
    )

    # --------------------------------------------------------
    # EVITAR DUPLICADOS DE EDUCACIÓN
    # --------------------------------------------------------

    # No eliminamos todas las educaciones aquí porque
    # una persona puede tener varias formaciones.

    # --------------------------------------------------------
    # CRUCE
    # --------------------------------------------------------

    df = pd.merge(
        users_cv,
        education,
        left_on="_id_cv",
        right_on="cv",
        how="left",
        suffixes=(
            "_userscv",
            "_education"
        )
    )

    print(
        f"✅ Users + CVs + Educación: {df.shape}"
    )

    return df


# ============================================================
# CRUCE 3: USERS + EXPERIENCIA
# ============================================================

def cruzar_users_experiencia(
    df_users,
    df_work,
    df_cvs
):

    print(
        "\n🔗 Cruzando USERS + EXPERIENCIA mediante CV"
    )

    users = df_users.copy()
    work = df_work.copy()
    cvs = df_cvs.copy()

    # --------------------------------------------------------
    # VALIDAR
    # --------------------------------------------------------

    if "_id" not in users.columns:
        raise KeyError(
            "df_users no contiene '_id'."
        )

    if "cv" not in work.columns:
        raise KeyError(
            "df_work no contiene la columna 'cv'. "
            "La experiencia debe relacionarse mediante el CV."
        )

    if "_id" not in cvs.columns:
        raise KeyError(
            "df_cvs no contiene '_id'."
        )

    if "user" not in cvs.columns:
        raise KeyError(
            "df_cvs no contiene 'user'."
        )

    # --------------------------------------------------------
    # NORMALIZAR
    # --------------------------------------------------------

    users = convertir_id(
        users,
        "_id"
    )

    work = convertir_id(
        work,
        "cv"
    )

    cvs = convertir_id(
        cvs,
        "_id"
    )

    cvs = convertir_id(
        cvs,
        "user"
    )

    # --------------------------------------------------------
    # CV + USER
    # --------------------------------------------------------

    cvs_user = cvs[
        [
            "_id",
            "user"
        ]
    ].copy()

    cvs_user = cvs_user.rename(
        columns={
            "_id": "_id_cv"
        }
    )

    # --------------------------------------------------------
    # EXPERIENCIA + CV
    # --------------------------------------------------------

    work_cv = pd.merge(
        work,
        cvs_user,
        left_on="cv",
        right_on="_id_cv",
        how="left"
    )

    print(
        f"✅ Experiencia + CV: {work_cv.shape}"
    )

    # --------------------------------------------------------
    # USERS + EXPERIENCIA
    # --------------------------------------------------------

    df = pd.merge(
        users,
        work_cv,
        left_on="_id",
        right_on="user",
        how="left",
        suffixes=(
            "_user",
            "_work"
        )
    )

    print(
        f"✅ Users + Experiencia: {df.shape}"
    )

    return df


# ============================================================
# CRUCE 4: APPLICATIONS + USERS
# ============================================================

def cruzar_applications_users(
    df_applications,
    df_users
):

    print(
        "\n🔗 Cruzando APPLICATIONS + USERS"
    )

    applications = df_applications.copy()
    users = df_users.copy()

    # --------------------------------------------------------
    # VALIDAR
    # --------------------------------------------------------

    if "user" not in applications.columns:
        raise KeyError(
            "df_applications no contiene la columna 'user'."
        )

    if "_id" not in users.columns:
        raise KeyError(
            "df_users no contiene la columna '_id'."
        )

    # --------------------------------------------------------
    # NORMALIZAR
    # --------------------------------------------------------

    applications = convertir_id(
        applications,
        "user"
    )

    users = convertir_id(
        users,
        "_id"
    )

    # --------------------------------------------------------
    # CRUCE
    # --------------------------------------------------------

    df = pd.merge(
        applications,
        users,
        left_on="user",
        right_on="_id",
        how="left",
        suffixes=(
            "_application",
            "_user"
        )
    )

    print(
        f"✅ Applications + Users: {df.shape}"
    )

    return df


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def realizar_cruces(
    df_users,
    df_cvs,
    df_educations,
    df_work,
    df_applications
):

    print("\n" + "=" * 60)
    print("REALIZANDO CRUCES")
    print("=" * 60)

    # ========================================================
    # 1. USERS + CVS
    # ========================================================

    df_users_cv = cruzar_users_cvs(
        df_users,
        df_cvs
    )

    # ========================================================
    # 2. USERS + CVS + EDUCACIÓN
    # ========================================================

    df_users_education = cruzar_users_educacion(
        df_users_cv,
        df_educations
    )

    # ========================================================
    # 3. USERS + EXPERIENCIA
    # ========================================================

    df_users_work = cruzar_users_experiencia(
        df_users,
        df_work,
        df_cvs
    )

    # ========================================================
    # 4. APPLICATIONS + USERS
    # ========================================================

    df_applications_users = cruzar_applications_users(
        df_applications,
        df_users
    )

    # ========================================================
    # RESULTADOS
    # ========================================================

    print("\n" + "=" * 60)
    print("✅ CRUCES COMPLETADOS")
    print("=" * 60)

    print(
        f"Users + CVs: "
        f"{df_users_cv.shape}"
    )

    print(
        f"Users + CVs + Educación: "
        f"{df_users_education.shape}"
    )

    print(
        f"Users + Experiencia: "
        f"{df_users_work.shape}"
    )

    print(
        f"Applications + Users: "
        f"{df_applications_users.shape}"
    )

    return {
        "users_cv": df_users_cv,
        "users_education": df_users_education,
        "users_work": df_users_work,
        "applications_users": df_applications_users
    }