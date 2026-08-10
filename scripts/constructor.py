
# ============================================================
# scripts/constructor.py
# CONSTRUCTOR ROBUSTO DEL DASHBOARD DE POSTULANTES
# ============================================================

import os
import re
import unicodedata

import numpy as np
import pandas as pd

from scripts.conexion import db


# ============================================================
# CONFIGURACIÓN
# ============================================================

CACHE_DIR = "data/cache"
OUTPUT_DIR = "data/cache"

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# FUNCIONES GENERALES
# ============================================================

def normalizar_texto(valor):
    """
    Normaliza texto:
    - convierte a string
    - elimina espacios innecesarios
    - elimina tildes
    - convierte a minúsculas
    """

    if valor is None:
        return ""

    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass

    valor = str(valor).strip().lower()

    valor = unicodedata.normalize("NFKD", valor)

    valor = "".join(
        c for c in valor
        if not unicodedata.combining(c)
    )

    valor = re.sub(r"\s+", " ", valor)

    return valor


def limpiar_id(valor):
    """
    Convierte ObjectId, diccionarios, números y strings
    a un identificador comparable.
    """

    if valor is None:
        return np.nan

    try:
        if pd.isna(valor):
            return np.nan
    except Exception:
        pass

    # Mongo exportado como:
    # {"$oid": "..."}
    if isinstance(valor, dict):

        for key in ["$oid", "_id", "id"]:

            if key in valor:

                valor = valor[key]

                if isinstance(valor, dict):
                    continue

                texto = str(valor).strip()

                if texto:
                    return texto

    texto = str(valor).strip()

    if texto.lower() in [
        "",
        "nan",
        "none",
        "null",
        "nat",
    ]:
        return np.nan

    return texto


def normalizar_columna_id(df, columna):

    if columna in df.columns:

        df[columna] = (
            df[columna]
            .apply(limpiar_id)
        )

    return df


def buscar_columna(df, candidatas):

    for columna in candidatas:

        if columna in df.columns:
            return columna

    return None


def convertir_bool(serie):

    return (
        serie
        .fillna(False)
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(
            [
                "true",
                "1",
                "yes",
                "si",
                "sí",
                "y",
            ]
        )
    )


def normalizar_email(valor):

    if valor is None:
        return np.nan

    try:
        if pd.isna(valor):
            return np.nan
    except Exception:
        pass

    texto = str(valor).strip().lower()

    if texto in [
        "",
        "nan",
        "none",
        "null",
    ]:
        return np.nan

    return texto


def normalizar_telefono(valor):

    if valor is None:
        return np.nan

    try:
        if pd.isna(valor):
            return np.nan
    except Exception:
        pass

    texto = re.sub(
        r"\D",
        "",
        str(valor),
    )

    if not texto:
        return np.nan

    return texto


# ============================================================
# CACHE
# ============================================================

def cargar_cache(nombre):

    ruta = os.path.join(
        CACHE_DIR,
        f"{nombre}.csv",
    )

    # --------------------------------------------------------
    # LEER CACHE
    # --------------------------------------------------------

    if os.path.exists(ruta):

        print(
            f"📂 Leyendo cache {nombre}..."
        )

        try:

            df = pd.read_csv(
                ruta,
                low_memory=False,
            )

            print(
                f"{nombre}: {df.shape}"
            )

            return df

        except Exception as e:

            print(
                f"⚠️ No se pudo leer cache {nombre}: {e}"
            )

    # --------------------------------------------------------
    # LEER MONGODB
    # --------------------------------------------------------

    print(
        f"⚠️ Cache no encontrado: {nombre}"
    )

    try:

        datos = list(
            db[nombre].find()
        )

        df = pd.DataFrame(datos)

        if "_id" in df.columns:

            df["_id"] = (
                df["_id"]
                .apply(limpiar_id)
            )

        df.to_csv(
            ruta,
            index=False,
            encoding="utf-8-sig",
        )

        print(
            f"💾 Cache creado: {ruta}"
        )

        print(
            f"{nombre}: {df.shape}"
        )

        return df

    except Exception as e:

        print(
            f"❌ Error cargando {nombre}: {e}"
        )

        return pd.DataFrame()


# ============================================================
# CARGAR COLECCIONES
# ============================================================

users = cargar_cache("users")
cvs = cargar_cache("cvs")
educations = cargar_cache("educations")
workexperiences = cargar_cache("workexperiences")
companies = cargar_cache("companies")
jobs = cargar_cache("jobs")
applications = cargar_cache("applications")
courseenrollments = cargar_cache("courseenrollments")
courses = cargar_cache("courses")
aiconversations = cargar_cache("aiconversations")
aimessages = cargar_cache("aimessages")
events = cargar_cache("events")
eventguests = cargar_cache("eventguests")


# ============================================================
# VALIDACIÓN DE COLECCIONES
# ============================================================

print()
print(
    "========== VALIDACIÓN DE COLECCIONES =========="
)

colecciones = {
    "users": users,
    "cvs": cvs,
    "educations": educations,
    "workexperiences": workexperiences,
    "companies": companies,
    "jobs": jobs,
    "applications": applications,
    "courseenrollments": courseenrollments,
    "courses": courses,
    "aiconversations": aiconversations,
    "aimessages": aimessages,
    "events": events,
    "eventguests": eventguests,
}

for nombre, df in colecciones.items():

    print(
        f"{nombre}: {df.shape}"
    )


# ============================================================
# VALIDAR USERS
# ============================================================

if "_id" not in users.columns:

    raise ValueError(
        "❌ La colección users no contiene _id."
    )

users = users.copy()

users["_id"] = (
    users["_id"]
    .apply(limpiar_id)
)


# ============================================================
# NORMALIZAR USERS
# ============================================================

columna_email_users = buscar_columna(
    users,
    [
        "email",
        "emailAddress",
    ],
)

if columna_email_users:

    users["_email_normalizado"] = (
        users[columna_email_users]
        .apply(normalizar_email)
    )

else:

    users["_email_normalizado"] = np.nan


columna_phone_users = buscar_columna(
    users,
    [
        "phone",
        "phoneNumber",
        "mobile",
        "cellphone",
    ],
)

if columna_phone_users:

    users["_telefono_normalizado"] = (
        users[columna_phone_users]
        .apply(normalizar_telefono)
    )

else:

    users["_telefono_normalizado"] = np.nan


columna_first_users = buscar_columna(
    users,
    [
        "firstName",
        "firstname",
        "first_name",
    ],
)

columna_last_users = buscar_columna(
    users,
    [
        "lastName",
        "lastname",
        "last_name",
    ],
)


if columna_first_users:

    users["_nombre_normalizado"] = (
        users[columna_first_users]
        .apply(normalizar_texto)
    )

else:

    users["_nombre_normalizado"] = ""


if columna_last_users:

    users["_apellido_normalizado"] = (
        users[columna_last_users]
        .apply(normalizar_texto)
    )

else:

    users["_apellido_normalizado"] = ""


# ============================================================
# DATASET BASE
# ============================================================

df_users_cv = users.copy()

df_users_cv["_id_postulante"] = (
    df_users_cv["_id"]
    .apply(limpiar_id)
)


# ============================================================
# CREAR MAPA CV → USUARIO
# ============================================================

print()
print(
    "========== CREANDO MAPA CV → USUARIO =========="
)

mapa_cv_usuario = pd.DataFrame(
    columns=[
        "_id_cv_mapa",
        "_id_usuario_mapa",
    ]
)


if not cvs.empty:

    cvs = cvs.copy()

    if "_id" in cvs.columns:

        cvs["_id"] = (
            cvs["_id"]
            .apply(limpiar_id)
        )

    columna_cv_user = buscar_columna(
        cvs,
        [
            "user",
            "userId",
            "user_id",
            "candidate",
            "candidateId",
        ],
    )

    print(
        f"Columna usuario CV: "
        f"{columna_cv_user}"
    )

    if columna_cv_user:

        cvs[columna_cv_user] = (
            cvs[columna_cv_user]
            .apply(limpiar_id)
        )

        if "_id" in cvs.columns:

            mapa_cv_usuario = cvs[
                [
                    "_id",
                    columna_cv_user,
                ]
            ].copy()

            mapa_cv_usuario.columns = [
                "_id_cv_mapa",
                "_id_usuario_mapa",
            ]

            mapa_cv_usuario = (
                mapa_cv_usuario
                .dropna(
                    subset=[
                        "_id_cv_mapa",
                        "_id_usuario_mapa",
                    ]
                )
                .drop_duplicates(
                    subset=[
                        "_id_cv_mapa",
                    ]
                )
            )

            print(
                f"Mapa CV → usuario: "
                f"{len(mapa_cv_usuario)} registros"
            )


# ============================================================
# USERS + CV
# ============================================================

print()
print(
    "========== CRUCE USERS + CVS =========="
)

if (
    not cvs.empty
    and columna_cv_user
):

    cvs_aux = cvs.copy()

    # --------------------------------------------------------
    # PRIORIZAR CV PRINCIPAL
    # --------------------------------------------------------

    if "isMain" in cvs_aux.columns:

        cvs_aux["_isMain_sort"] = (
            convertir_bool(
                cvs_aux["isMain"]
            )
            .astype(int)
        )

        cvs_aux = (
            cvs_aux
            .sort_values(
                "_isMain_sort",
                ascending=False,
            )
            .drop_duplicates(
                subset=[
                    columna_cv_user,
                ],
                keep="first",
            )
            .drop(
                columns=[
                    "_isMain_sort",
                ],
                errors="ignore",
            )
        )

    else:

        cvs_aux = (
            cvs_aux
            .drop_duplicates(
                subset=[
                    columna_cv_user,
                ],
                keep="first",
            )
        )

    df_users_cv = pd.merge(
        df_users_cv,
        cvs_aux,
        left_on="_id_postulante",
        right_on=columna_cv_user,
        how="left",
        suffixes=(
            "_user",
            "_cv",
        ),
    )


# ============================================================
# TIENE CV
# ============================================================

if "user" in df_users_cv.columns:

    df_users_cv["tiene_cv"] = (
        df_users_cv["user"]
        .notna()
    )

elif "_id_cv" in df_users_cv.columns:

    df_users_cv["tiene_cv"] = (
        df_users_cv["_id_cv"]
        .notna()
    )

else:

    # Como respaldo, buscamos cualquier
    # columna del CV que permita determinar
    # que hubo coincidencia.
    df_users_cv["tiene_cv"] = False


# ============================================================
# EDUCACIÓN
# ============================================================

print()
print(
    "========== EDUCACIÓN =========="
)


def clasificar_nivel(valor):

    texto = normalizar_texto(valor)

    if not texto:
        return np.nan

    if any(
        palabra in texto
        for palabra in [
            "student",
            "estudiante",
            "universitario",
            "undergraduate",
            "college student",
        ]
    ):
        return "Estudiante"

    if any(
        palabra in texto
        for palabra in [
            "bachiller",
            "bachelor",
        ]
    ):
        return "Bachiller"

    if any(
        palabra in texto
        for palabra in [
            "licenciatura",
            "licenciado",
            "licentiate",
        ]
    ):
        return "Licenciatura"

    if any(
        palabra in texto
        for palabra in [
            "maestria",
            "master",
            "magister",
        ]
    ):
        return "Maestría"

    if any(
        palabra in texto
        for palabra in [
            "doctorado",
            "doctor",
            "phd",
        ]
    ):
        return "Doctorado"

    if any(
        palabra in texto
        for palabra in [
            "diplomado",
            "diploma",
        ]
    ):
        return "Diplomado"

    if any(
        palabra in texto
        for palabra in [
            "certificado",
            "certificate",
            "certification",
        ]
    ):
        return "Certificado"

    return "Otros"


def limpiar_carrera(valor):

    if valor is None:
        return np.nan

    try:

        if pd.isna(valor):
            return np.nan

    except Exception:
        pass

    texto_original = str(
        valor
    ).strip()

    if not texto_original:
        return np.nan

    texto = normalizar_texto(
        texto_original
    )

    if texto in [
        "nan",
        "none",
        "null",
    ]:
        return np.nan

    if (
        "secundaria" in texto
        or "secondary" in texto
    ):
        return "Educación Secundaria"

    return texto_original


def clasificar_area(carrera):

    texto = normalizar_texto(
        carrera
    )

    if not texto:
        return np.nan

    grupos = {

        "Ingeniería y Tecnología": [
            "ingenieria",
            "engineering",
            "sistemas",
            "software",
            "informatica",
            "computacion",
            "industrial",
            "mecatronica",
            "ambiental",
            "electronica",
            "civil",
            "tecnologia",
            "data science",
            "ciencia de datos",
            "telecomunicaciones",
            "redes",
        ],

        "Administración y Negocios": [
            "administracion",
            "negocios",
            "marketing",
            "mercadeo",
            "gestion",
            "comercial",
            "management",
            "ventas",
            "recursos humanos",
        ],

        "Economía y Finanzas": [
            "economia",
            "finanzas",
            "contabilidad",
            "economics",
            "finance",
            "accounting",
        ],

        "Ciencias Sociales y Humanidades": [
            "psicologia",
            "derecho",
            "sociologia",
            "comunicacion",
            "educacion",
            "historia",
            "humanidades",
            "periodismo",
            "ingles",
            "literatura",
        ],

        "Arquitectura y Diseño": [
            "arquitectura",
            "diseno",
            "design",
        ],

        "Salud": [
            "medicina",
            "enfermeria",
            "odontologia",
            "salud",
            "farmacia",
            "nutricion",
        ],

        "Ciencias": [
            "matematica",
            "fisica",
            "quimica",
            "biologia",
            "estadistica",
        ],
    }

    for area, palabras in grupos.items():

        if any(
            palabra in texto
            for palabra in palabras
        ):
            return area

    return "Otros"


educacion_detalle = pd.DataFrame()


if not educations.empty:

    edu = educations.copy()

    columna_carrera = buscar_columna(
        edu,
        [
            "degree",
            "degree_clean",
            "career",
            "careerName",
            "carrera",
            "program",
            "programName",
        ],
    )

    columna_nivel = buscar_columna(
        edu,
        [
            "level",
            "educationLevel",
            "education_level",
            "degreeLevel",
            "levelName",
            "nivel",
            "nivelEducativo",
            "educationType",
            "type",
        ],
    )

    columna_user_edu = buscar_columna(
        edu,
        [
            "user",
            "userId",
            "user_id",
            "candidate",
            "candidateId",
        ],
    )

    columna_cv_edu = buscar_columna(
        edu,
        [
            "cv",
            "cvId",
            "cv_id",
            "curriculum",
            "curriculumId",
        ],
    )

    print(
        f"Columna carrera: "
        f"{columna_carrera}"
    )

    print(
        f"Columna nivel: "
        f"{columna_nivel}"
    )

    print(
        f"Columna usuario educación: "
        f"{columna_user_edu}"
    )

    print(
        f"Columna CV educación: "
        f"{columna_cv_edu}"
    )

    edu["_id_usuario_edu"] = np.nan

    if columna_user_edu:

        edu["_id_usuario_edu"] = (
            edu[columna_user_edu]
            .apply(limpiar_id)
        )

    if (
        columna_cv_edu
        and not mapa_cv_usuario.empty
    ):

        edu["_id_cv_edu"] = (
            edu[columna_cv_edu]
            .apply(limpiar_id)
        )

        edu = edu.merge(
            mapa_cv_usuario,
            left_on="_id_cv_edu",
            right_on="_id_cv_mapa",
            how="left",
        )

        edu["_id_usuario_edu"] = (
            edu["_id_usuario_edu"]
            .fillna(
                edu["_id_usuario_mapa"]
            )
        )

    if columna_carrera:

        edu["carrera_principal"] = (
            edu[columna_carrera]
            .apply(limpiar_carrera)
        )

    else:

        edu["carrera_principal"] = np.nan

    if columna_nivel:

        edu["nivel_educativo"] = (
            edu[columna_nivel]
            .apply(clasificar_nivel)
        )

    else:

        edu["nivel_educativo"] = np.nan

    edu["area_profesional"] = (
        edu["carrera_principal"]
        .apply(clasificar_area)
    )

    educacion_detalle = edu[
        [
            "_id_usuario_edu",
            "carrera_principal",
            "area_profesional",
            "nivel_educativo",
        ]
    ].copy()

    educacion_detalle = (
        educacion_detalle
        .rename(
            columns={
                "_id_usuario_edu":
                    "_id_postulante",
            }
        )
    )

    educacion_detalle[
        "_id_postulante"
    ] = (
        educacion_detalle[
            "_id_postulante"
        ]
        .apply(limpiar_id)
    )

    educacion_detalle = (
        educacion_detalle
        .dropna(
            subset=[
                "_id_postulante",
            ]
        )
    )

    print(
        f"Educación vinculada: "
        f"{len(educacion_detalle)}"
    )


# ============================================================
# EDUCACIÓN POR USUARIO
# ============================================================

print()
print(
    "========== CRUCE EDUCACIÓN =========="
)

if not educacion_detalle.empty:

    def primer_valor_valido(serie):

        valores = (
            serie
            .dropna()
            .astype(str)
            .str.strip()
        )

        valores = valores[
            valores != ""
        ]

        if len(valores) == 0:
            return np.nan

        return valores.iloc[0]


    educacion_usuario = (
        educacion_detalle
        .groupby(
            "_id_postulante"
        )
        .agg(
            carrera_principal=(
                "carrera_principal",
                primer_valor_valido,
            ),
            area_profesional=(
                "area_profesional",
                primer_valor_valido,
            ),
            nivel_educativo=(
                "nivel_educativo",
                primer_valor_valido,
            ),
        )
        .reset_index()
    )

    educacion_usuario[
        "_id_postulante"
    ] = (
        educacion_usuario[
            "_id_postulante"
        ]
        .apply(limpiar_id)
    )

    df_users_cv = pd.merge(
        df_users_cv,
        educacion_usuario,
        on="_id_postulante",
        how="left",
        validate="one_to_one",
    )

else:

    df_users_cv[
        "carrera_principal"
    ] = np.nan

    df_users_cv[
        "area_profesional"
    ] = np.nan

    df_users_cv[
        "nivel_educativo"
    ] = np.nan


df_users_cv[
    "tiene_educacion"
] = (
    df_users_cv[
        "nivel_educativo"
    ].notna()
)


df_users_cv[
    "tiene_carrera"
] = (
    df_users_cv[
        "carrera_principal"
    ].notna()
)


# ============================================================
# EXPERIENCIA LABORAL
# ============================================================

print()
print(
    "========== CRUCE EXPERIENCIA =========="
)

experiencia_detalle = pd.DataFrame()


if not workexperiences.empty:

    exp = workexperiences.copy()

    columna_user_exp = buscar_columna(
        exp,
        [
            "user",
            "userId",
            "user_id",
            "candidate",
            "candidateId",
        ],
    )

    columna_cv_exp = buscar_columna(
        exp,
        [
            "cv",
            "cvId",
            "cv_id",
            "curriculum",
            "curriculumId",
        ],
    )

    print(
        f"Columna usuario experiencia: "
        f"{columna_user_exp}"
    )

    print(
        f"Columna CV experiencia: "
        f"{columna_cv_exp}"
    )

    exp["_id_usuario_exp"] = np.nan

    # --------------------------------------------------------
    # USER DIRECTO
    # --------------------------------------------------------

    if columna_user_exp:

        exp["_id_usuario_exp"] = (
            exp[columna_user_exp]
            .apply(limpiar_id)
        )

    # --------------------------------------------------------
    # CV → USER
    # --------------------------------------------------------

    if (
        columna_cv_exp
        and not mapa_cv_usuario.empty
    ):

        exp["_id_cv_exp"] = (
            exp[columna_cv_exp]
            .apply(limpiar_id)
        )

        exp = exp.merge(
            mapa_cv_usuario,
            left_on="_id_cv_exp",
            right_on="_id_cv_mapa",
            how="left",
        )

        exp["_id_usuario_exp"] = (
            exp["_id_usuario_exp"]
            .fillna(
                exp["_id_usuario_mapa"]
            )
        )

    # --------------------------------------------------------
    # FECHAS
    # --------------------------------------------------------

    columna_inicio = buscar_columna(
        exp,
        [
            "startDate",
            "start_date",
            "startedAt",
            "dateStart",
        ],
    )

    columna_fin = buscar_columna(
        exp,
        [
            "endDate",
            "end_date",
            "endedAt",
            "dateEnd",
        ],
    )

    if columna_inicio:

        exp["_fecha_inicio"] = pd.to_datetime(
            exp[columna_inicio],
            errors="coerce",
            format="mixed",
        )

    else:

        exp["_fecha_inicio"] = pd.NaT

    if columna_fin:

        exp["_fecha_fin"] = pd.to_datetime(
            exp[columna_fin],
            errors="coerce",
            format="mixed",
        )

    else:

        exp["_fecha_fin"] = pd.NaT

    # --------------------------------------------------------
    # EXPERIENCIA ACTIVA
    # --------------------------------------------------------

    if "inProgress" in exp.columns:

        activa = convertir_bool(
            exp["inProgress"]
        )

    else:

        activa = pd.Series(
            False,
            index=exp.index,
        )

    hoy = pd.Timestamp.now().normalize()

    exp["_fecha_fin"] = (
        exp["_fecha_fin"]
        .where(
            ~activa,
            hoy,
        )
    )

    # --------------------------------------------------------
    # CALCULAR DÍAS
    # --------------------------------------------------------

    exp["_dias"] = (
        exp["_fecha_fin"]
        - exp["_fecha_inicio"]
    ).dt.days

    exp["_dias"] = (
        pd.to_numeric(
            exp["_dias"],
            errors="coerce",
        )
        .clip(lower=0)
    )

    exp["_años"] = (
        exp["_dias"]
        / 365.25
    )

    # --------------------------------------------------------
    # DETECTAR PRÁCTICAS
    # --------------------------------------------------------

    columnas_texto_practica = [
        "type",
        "position",
        "title",
        "jobTitle",
        "description",
        "descriptionExperience",
    ]

    columnas_texto_practica = [
        c
        for c in columnas_texto_practica
        if c in exp.columns
    ]

    if columnas_texto_practica:

        texto_exp = (
            exp[
                columnas_texto_practica
            ]
            .fillna("")
            .astype(str)
            .agg(
                " ".join,
                axis=1,
            )
            .apply(
                normalizar_texto
            )
        )

    else:

        texto_exp = pd.Series(
            "",
            index=exp.index,
        )

    palabras_practica = [
        "practica",
        "practicante",
        "intern",
        "internship",
        "trainee",
        "pasantia",
        "becario",
        "becaria",
    ]

    exp["_es_practica"] = (
        texto_exp
        .apply(
            lambda x:
            any(
                palabra in x
                for palabra in palabras_practica
            )
        )
    )

    # --------------------------------------------------------
    # SOLO EXPERIENCIAS VÁLIDAS
    # --------------------------------------------------------

    exp = exp[
        exp["_id_usuario_exp"].notna()
        & exp["_fecha_inicio"].notna()
        & exp["_fecha_fin"].notna()
        & (exp["_dias"] > 0)
    ].copy()

    experiencia_detalle = pd.DataFrame(
        {
            "_id_postulante":
                exp["_id_usuario_exp"],

            "fecha_inicio":
                exp["_fecha_inicio"],

            "fecha_fin":
                exp["_fecha_fin"],

            "años":
                exp["_años"],

            "es_practica":
                exp["_es_practica"],
        }
    )

    experiencia_detalle[
        "_id_postulante"
    ] = (
        experiencia_detalle[
            "_id_postulante"
        ]
        .apply(limpiar_id)
    )

    experiencia_detalle = (
        experiencia_detalle
        .dropna(
            subset=[
                "_id_postulante",
            ]
        )
    )

    print(
        f"Experiencias válidas vinculadas: "
        f"{len(experiencia_detalle)}"
    )


# ============================================================
# CALCULAR DÍAS SIN SUPERPOSICIÓN
# ============================================================

def calcular_dias_sin_superposicion(grupo):

    if grupo.empty:
        return 0

    intervalos = (
        grupo[
            [
                "fecha_inicio",
                "fecha_fin",
            ]
        ]
        .dropna()
        .sort_values(
            "fecha_inicio"
        )
    )

    if intervalos.empty:
        return 0

    total_dias = 0

    inicio_actual = None
    fin_actual = None

    for fila in intervalos.itertuples(
        index=False
    ):

        inicio = pd.Timestamp(
            fila.fecha_inicio
        )

        fin = pd.Timestamp(
            fila.fecha_fin
        )

        if pd.isna(inicio) or pd.isna(fin):
            continue

        if fin <= inicio:
            continue

        if inicio_actual is None:

            inicio_actual = inicio
            fin_actual = fin

            continue

        # ----------------------------------------------------
        # INTERVALOS SUPERPUESTOS
        # ----------------------------------------------------

        if inicio <= fin_actual:

            if fin > fin_actual:
                fin_actual = fin

        # ----------------------------------------------------
        # INTERVALOS SEPARADOS
        # ----------------------------------------------------

        else:

            diferencia = (
                fin_actual
                - inicio_actual
            )

            # Importante:
            # usamos total_seconds() y NO .days
            # sobre numpy.timedelta64.

            dias = (
                diferencia.total_seconds()
                / 86400
            )

            total_dias += dias

            inicio_actual = inicio
            fin_actual = fin

    # --------------------------------------------------------
    # ÚLTIMO INTERVALO
    # --------------------------------------------------------

    if (
        inicio_actual is not None
        and fin_actual is not None
    ):

        diferencia = (
            fin_actual
            - inicio_actual
        )

        dias = (
            diferencia.total_seconds()
            / 86400
        )

        total_dias += dias

    return max(
        total_dias,
        0,
    )


# ============================================================
# AGREGAR EXPERIENCIA POR USUARIO
# ============================================================

if not experiencia_detalle.empty:

    registros = []

    for usuario, grupo_usuario in (
        experiencia_detalle
        .groupby(
            "_id_postulante"
        )
    ):

        laborales = grupo_usuario[
            ~grupo_usuario[
                "es_practica"
            ]
        ].copy()

        practicas = grupo_usuario[
            grupo_usuario[
                "es_practica"
            ]
        ].copy()

        dias_laborales = (
            calcular_dias_sin_superposicion(
                laborales
            )
        )

        dias_practicas = (
            calcular_dias_sin_superposicion(
                practicas
            )
        )

        registros.append(
            {
                "_id_postulante":
                    usuario,

                "años_experiencia":
                    dias_laborales / 365.25,

                "años_practica":
                    dias_practicas / 365.25,

                "cantidad_experiencias":
                    len(laborales),

                "cantidad_practicas":
                    len(practicas),
            }
        )

    experiencia_usuario = pd.DataFrame(
        registros
    )

    experiencia_usuario[
        "_id_postulante"
    ] = (
        experiencia_usuario[
            "_id_postulante"
        ]
        .apply(limpiar_id)
    )

    df_users_cv = pd.merge(
        df_users_cv,
        experiencia_usuario,
        on="_id_postulante",
        how="left",
        validate="one_to_one",
    )

else:

    df_users_cv[
        "años_experiencia"
    ] = 0.0

    df_users_cv[
        "años_practica"
    ] = 0.0

    df_users_cv[
        "cantidad_experiencias"
    ] = 0

    df_users_cv[
        "cantidad_practicas"
    ] = 0


# ============================================================
# LIMPIAR EXPERIENCIA
# ============================================================

for columna in [
    "años_experiencia",
    "años_practica",
]:

    df_users_cv[columna] = (
        pd.to_numeric(
            df_users_cv[columna],
            errors="coerce",
        )
        .fillna(0)
        .clip(lower=0)
    )


for columna in [
    "cantidad_experiencias",
    "cantidad_practicas",
]:

    df_users_cv[columna] = (
        pd.to_numeric(
            df_users_cv[columna],
            errors="coerce",
        )
        .fillna(0)
        .astype(int)
    )


df_users_cv[
    "tiene_experiencia"
] = (
    df_users_cv[
        "cantidad_experiencias"
    ] > 0
)


df_users_cv[
    "tiene_practicas"
] = (
    df_users_cv[
        "cantidad_practicas"
    ] > 0
)


# ============================================================
# TIPO DE EXPERIENCIA
# ============================================================

def clasificar_tipo_experiencia(row):

    laboral = bool(
        row["tiene_experiencia"]
    )

    practica = bool(
        row["tiene_practicas"]
    )

    if laboral and practica:
        return "Experiencia laboral y prácticas"

    if laboral:
        return "Experiencia laboral"

    if practica:
        return "Prácticas"

    return "Sin experiencia"


df_users_cv[
    "tipo_experiencia"
] = (
    df_users_cv
    .apply(
        clasificar_tipo_experiencia,
        axis=1,
    )
)


# ============================================================
# RANGOS DE EXPERIENCIA
# ============================================================

def rango_experiencia(años):

    if pd.isna(años):
        return "Sin experiencia registrada"

    if años <= 0:
        return "Sin experiencia registrada"

    if años < 1:
        return "Menos de 1 año"

    if años <= 3:
        return "1 a 3 años"

    if años <= 5:
        return "3 a 5 años"

    return "Más de 5 años"


def rango_practica(años):

    if pd.isna(años):
        return "Sin prácticas registradas"

    if años <= 0:
        return "Sin prácticas registradas"

    if años < 1:
        return "Menos de 1 año"

    if años <= 3:
        return "1 a 3 años"

    return "Más de 3 años"


df_users_cv[
    "Rango_experiencia"
] = (
    df_users_cv[
        "años_experiencia"
    ]
    .apply(rango_experiencia)
)


df_users_cv[
    "Rango_practica"
] = (
    df_users_cv[
        "años_practica"
    ]
    .apply(rango_practica)
)


# ============================================================
# CURSOS
# ============================================================

print()
print(
    "========== CRUCE CURSOS =========="
)

if not courseenrollments.empty:

    cursos = courseenrollments.copy()

    columna_user_curso = buscar_columna(
        cursos,
        [
            "user",
            "userId",
            "user_id",
            "candidate",
            "candidateId",
        ],
    )

    columna_cv_curso = buscar_columna(
        cursos,
        [
            "cv",
            "cvId",
            "cv_id",
        ],
    )

    print(
        f"Columna usuario cursos: "
        f"{columna_user_curso}"
    )

    print(
        f"Columna CV cursos: "
        f"{columna_cv_curso}"
    )

    cursos[
        "_id_usuario_curso"
    ] = np.nan

    if columna_user_curso:

        cursos[
            "_id_usuario_curso"
        ] = (
            cursos[
                columna_user_curso
            ]
            .apply(limpiar_id)
        )

    if (
        columna_cv_curso
        and not mapa_cv_usuario.empty
    ):

        cursos[
            "_id_cv_curso"
        ] = (
            cursos[
                columna_cv_curso
            ]
            .apply(limpiar_id)
        )

        cursos = cursos.merge(
            mapa_cv_usuario,
            left_on="_id_cv_curso",
            right_on="_id_cv_mapa",
            how="left",
        )

        cursos[
            "_id_usuario_curso"
        ] = (
            cursos[
                "_id_usuario_curso"
            ]
            .fillna(
                cursos[
                    "_id_usuario_mapa"
                ]
            )
        )

    cursos_usuario = (
        cursos
        .dropna(
            subset=[
                "_id_usuario_curso",
            ]
        )
        .groupby(
            "_id_usuario_curso"
        )
        .size()
        .reset_index(
            name="cantidad_cursos"
        )
        .rename(
            columns={
                "_id_usuario_curso":
                    "_id_postulante",
            }
        )
    )

    cursos_usuario[
        "_id_postulante"
    ] = (
        cursos_usuario[
            "_id_postulante"
        ]
        .apply(limpiar_id)
    )

    if not cursos_usuario.empty:

        df_users_cv = pd.merge(
            df_users_cv,
            cursos_usuario,
            on="_id_postulante",
            how="left",
            validate="one_to_one",
        )

else:

    df_users_cv[
        "cantidad_cursos"
    ] = 0


if "cantidad_cursos" not in df_users_cv.columns:

    df_users_cv[
        "cantidad_cursos"
    ] = 0


df_users_cv[
    "cantidad_cursos"
] = (
    pd.to_numeric(
        df_users_cv[
            "cantidad_cursos"
        ],
        errors="coerce",
    )
    .fillna(0)
    .astype(int)
)


# ============================================================
# INTELIGENCIA ARTIFICIAL
# ============================================================

print()
print(
    "========== CRUCE IA =========="
)

if not aiconversations.empty:

    ia = aiconversations.copy()

    columna_user_ia = buscar_columna(
        ia,
        [
            "user",
            "userId",
            "user_id",
            "candidate",
            "candidateId",
        ],
    )

    columna_cv_ia = buscar_columna(
        ia,
        [
            "cv",
            "cvId",
            "cv_id",
        ],
    )

    print(
        f"Columna usuario IA: "
        f"{columna_user_ia}"
    )

    print(
        f"Columna CV IA: "
        f"{columna_cv_ia}"
    )

    ia[
        "_id_usuario_ia"
    ] = np.nan

    if columna_user_ia:

        ia[
            "_id_usuario_ia"
        ] = (
            ia[
                columna_user_ia
            ]
            .apply(limpiar_id)
        )

    if (
        columna_cv_ia
        and not mapa_cv_usuario.empty
    ):

        ia[
            "_id_cv_ia"
        ] = (
            ia[
                columna_cv_ia
            ]
            .apply(limpiar_id)
        )

        ia = ia.merge(
            mapa_cv_usuario,
            left_on="_id_cv_ia",
            right_on="_id_cv_mapa",
            how="left",
        )

        ia[
            "_id_usuario_ia"
        ] = (
            ia[
                "_id_usuario_ia"
            ]
            .fillna(
                ia[
                    "_id_usuario_mapa"
                ]
            )
        )

    ia_usuario = (
        ia
        .dropna(
            subset=[
                "_id_usuario_ia",
            ]
        )
        .groupby(
            "_id_usuario_ia"
        )
        .size()
        .reset_index(
            name="cantidad_conversaciones"
        )
        .rename(
            columns={
                "_id_usuario_ia":
                    "_id_postulante",
            }
        )
    )

    ia_usuario[
        "_id_postulante"
    ] = (
        ia_usuario[
            "_id_postulante"
        ]
        .apply(limpiar_id)
    )

    if not ia_usuario.empty:

        df_users_cv = pd.merge(
            df_users_cv,
            ia_usuario,
            on="_id_postulante",
            how="left",
            validate="one_to_one",
        )

else:

    df_users_cv[
        "cantidad_conversaciones"
    ] = 0


if (
    "cantidad_conversaciones"
    not in df_users_cv.columns
):

    df_users_cv[
        "cantidad_conversaciones"
    ] = 0


df_users_cv[
    "cantidad_conversaciones"
] = (
    pd.to_numeric(
        df_users_cv[
            "cantidad_conversaciones"
        ],
        errors="coerce",
    )
    .fillna(0)
    .astype(int)
)


df_users_cv[
    "uso_ia"
] = (
    df_users_cv[
        "cantidad_conversaciones"
    ] > 0
)


# ============================================================
# EVENTOS
# ============================================================

print()
print(
    "========== CRUCE EVENTOS =========="
)

eventos_detalle = pd.DataFrame()


if not eventguests.empty:

    eventos = eventguests.copy()

    print(
        "Columnas eventguests:"
    )

    print(
        eventos.columns.tolist()
    )

    columna_email_evento = buscar_columna(
        eventos,
        [
            "userEmail",
            "email",
            "emailUser",
            "guestEmail",
        ],
    )

    columna_phone_evento = buscar_columna(
        eventos,
        [
            "userPhone",
            "phone",
            "phoneNumber",
            "guestPhone",
        ],
    )

    columna_nombre_evento = buscar_columna(
        eventos,
        [
            "userName",
            "name",
            "guestName",
        ],
    )

    columna_evento = buscar_columna(
        eventos,
        [
            "event",
            "eventId",
            "event_id",
        ],
    )

    print(
        f"Columna email evento: "
        f"{columna_email_evento}"
    )

    print(
        f"Columna teléfono evento: "
        f"{columna_phone_evento}"
    )

    print(
        f"Columna nombre evento: "
        f"{columna_nombre_evento}"
    )

    print(
        f"Columna evento: "
        f"{columna_evento}"
    )

    # --------------------------------------------------------
    # IMPORTANTE:
    # Guardamos el _id ORIGINAL del eventguest
    # antes de hacer merges.
    # --------------------------------------------------------

    if "_id" in eventos.columns:

        eventos["_id_eventguest"] = (
            eventos["_id"]
            .apply(limpiar_id)
        )

    else:

        eventos["_id_eventguest"] = (
            pd.Series(
                np.nan,
                index=eventos.index,
            )
        )

    eventos[
        "_id_usuario_evento"
    ] = np.nan

    # --------------------------------------------------------
    # CRUCE POR EMAIL
    # --------------------------------------------------------

    if columna_email_evento:

        eventos[
            "_email_evento"
        ] = (
            eventos[
                columna_email_evento
            ]
            .apply(
                normalizar_email
            )
        )

        mapa_email = (
            users[
                [
                    "_id",
                    "_email_normalizado",
                ]
            ]
            .dropna(
                subset=[
                    "_email_normalizado",
                ]
            )
            .drop_duplicates(
                subset=[
                    "_email_normalizado",
                ]
            )
            .rename(
                columns={
                    "_id":
                        "_id_usuario_email",
                }
            )
        )

        eventos = eventos.merge(
            mapa_email,
            left_on="_email_evento",
            right_on="_email_normalizado",
            how="left",
        )

        eventos[
            "_id_usuario_evento"
        ] = (
            eventos[
                "_id_usuario_evento"
            ]
            .fillna(
                eventos[
                    "_id_usuario_email"
                ]
            )
        )

        eventos = eventos.drop(
            columns=[
                "_id_usuario_email",
                "_email_normalizado",
            ],
            errors="ignore",
        )

    # --------------------------------------------------------
    # CRUCE POR TELÉFONO
    # --------------------------------------------------------

    if columna_phone_evento:

        eventos[
            "_telefono_evento"
        ] = (
            eventos[
                columna_phone_evento
            ]
            .apply(
                normalizar_telefono
            )
        )

        mapa_phone = (
            users[
                [
                    "_id",
                    "_telefono_normalizado",
                ]
            ]
            .dropna(
                subset=[
                    "_telefono_normalizado",
                ]
            )
            .drop_duplicates(
                subset=[
                    "_telefono_normalizado",
                ]
            )
            .rename(
                columns={
                    "_id":
                        "_id_usuario_phone",
                }
            )
        )

        eventos = eventos.merge(
            mapa_phone,
            left_on="_telefono_evento",
            right_on="_telefono_normalizado",
            how="left",
        )

        eventos[
            "_id_usuario_evento"
        ] = (
            eventos[
                "_id_usuario_evento"
            ]
            .fillna(
                eventos[
                    "_id_usuario_phone"
                ]
            )
        )

        eventos = eventos.drop(
            columns=[
                "_id_usuario_phone",
                "_telefono_normalizado",
            ],
            errors="ignore",
        )

    # --------------------------------------------------------
    # GUARDAR DETALLE
    # --------------------------------------------------------

    eventos_detalle = eventos.copy()

    eventos_detalle[
        "_id_postulante"
    ] = (
        eventos_detalle[
            "_id_usuario_evento"
        ]
        .apply(limpiar_id)
    )

    eventos_detalle = (
        eventos_detalle
        .dropna(
            subset=[
                "_id_postulante",
            ]
        )
    )

    if not eventos_detalle.empty:

        eventos_usuario = (
            eventos_detalle
            .groupby(
                "_id_postulante"
            )
            .size()
            .reset_index(
                name="cantidad_eventos"
            )
        )

        df_users_cv = pd.merge(
            df_users_cv,
            eventos_usuario,
            on="_id_postulante",
            how="left",
            validate="one_to_one",
        )

    else:

        df_users_cv[
            "cantidad_eventos"
        ] = 0

else:

    df_users_cv[
        "cantidad_eventos"
    ] = 0


if (
    "cantidad_eventos"
    not in df_users_cv.columns
):

    df_users_cv[
        "cantidad_eventos"
    ] = 0


df_users_cv[
    "cantidad_eventos"
] = (
    pd.to_numeric(
        df_users_cv[
            "cantidad_eventos"
        ],
        errors="coerce",
    )
    .fillna(0)
    .astype(int)
)


df_users_cv[
    "participo_evento"
] = (
    df_users_cv[
        "cantidad_eventos"
    ] > 0
)


# ============================================================
# MODALIDAD LABORAL
# ============================================================

print()
print(
    "========== MODALIDAD LABORAL =========="
)

columna_modalidad = buscar_columna(
    df_users_cv,
    [
        "workMode",
        "workModality",
        "modality",
        "modalidadLaboral",
        "employmentModality",
    ],
)

if columna_modalidad:

    df_users_cv[
        "modalidad_laboral"
    ] = (
        df_users_cv[
            columna_modalidad
        ]
        .fillna(
            "Sin registro"
        )
        .astype(str)
        .str.strip()
    )

else:

    df_users_cv[
        "modalidad_laboral"
    ] = "Sin registro"


df_users_cv[
    "modalidad_laboral"
] = (
    df_users_cv[
        "modalidad_laboral"
    ]
    .replace(
        [
            "",
            "nan",
            "None",
            "null",
        ],
        "Sin registro",
    )
)


# ============================================================
# FECHA DE REGISTRO
# ============================================================

columna_fecha_registro = buscar_columna(
    df_users_cv,
    [
        "createdAt_user",
        "createdAt",
    ],
)

if columna_fecha_registro:

    df_users_cv[
        "createdAt_user"
    ] = pd.to_datetime(
        df_users_cv[
            columna_fecha_registro
        ],
        errors="coerce",
        format="mixed",
    )

    df_users_cv[
        "año"
    ] = (
        df_users_cv[
            "createdAt_user"
        ]
        .dt.year
    )

    df_users_cv[
        "mes_num"
    ] = (
        df_users_cv[
            "createdAt_user"
        ]
        .dt.month
    )

    meses = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }

    df_users_cv[
        "mes"
    ] = (
        df_users_cv[
            "mes_num"
        ]
        .map(meses)
    )

else:

    df_users_cv[
        "año"
    ] = np.nan

    df_users_cv[
        "mes_num"
    ] = np.nan

    df_users_cv[
        "mes"
    ] = np.nan


# ============================================================
# ASEGURAR COLUMNAS PRINCIPALES
# ============================================================

columnas_base = {

    "_id_postulante": np.nan,

    "email_postulante": np.nan,

    "firstName_postulante": np.nan,

    "lastName_postulante": np.nan,

    "tiene_cv": False,

    "cantidad_cursos": 0,

    "uso_ia": False,

    "cantidad_conversaciones": 0,

    "cantidad_eventos": 0,

    "participo_evento": False,

    "carrera_principal": np.nan,

    "area_profesional": np.nan,

    "nivel_educativo": np.nan,

    "tiene_educacion": False,

    "tiene_carrera": False,

    "años_experiencia": 0.0,

    "cantidad_experiencias": 0,

    "años_practica": 0.0,

    "cantidad_practicas": 0,

    "tiene_experiencia": False,

    "tiene_practicas": False,

    "tipo_experiencia": "Sin experiencia",

    "Rango_experiencia":
        "Sin experiencia registrada",

    "Rango_practica":
        "Sin prácticas registradas",

    "año": np.nan,

    "mes_num": np.nan,

    "mes": np.nan,

    "modalidad_laboral":
        "Sin registro",
}


for columna, valor_default in (
    columnas_base.items()
):

    if columna not in df_users_cv.columns:

        df_users_cv[
            columna
        ] = valor_default


# ============================================================
# NOMBRES ESTÁNDAR
# ============================================================

renombrar = {

    "email_user":
        "email_postulante",

    "firstName_user":
        "firstName_postulante",

    "lastName_user":
        "lastName_postulante",
}


for origen, destino in (
    renombrar.items()
):

    if (
        destino in df_users_cv.columns
        and origen in df_users_cv.columns
    ):

        df_users_cv[
            destino
        ] = (
            df_users_cv[
                destino
            ]
            .fillna(
                df_users_cv[
                    origen
                ]
            )
        )


# ============================================================
# SI LOS NOMBRES NO EXISTEN, BUSCAR COLUMNAS ORIGINALES
# ============================================================

if (
    df_users_cv[
        "email_postulante"
    ].isna().all()
):

    columna_email = buscar_columna(
        df_users_cv,
        [
            "email",
            "emailAddress",
        ],
    )

    if columna_email:

        df_users_cv[
            "email_postulante"
        ] = (
            df_users_cv[
                columna_email
            ]
            .apply(
                normalizar_email
            )
        )


if (
    df_users_cv[
        "firstName_postulante"
    ].isna().all()
):

    columna_nombre = buscar_columna(
        df_users_cv,
        [
            "firstName",
            "firstname",
            "first_name",
        ],
    )

    if columna_nombre:

        df_users_cv[
            "firstName_postulante"
        ] = df_users_cv[
            columna_nombre
        ]


if (
    df_users_cv[
        "lastName_postulante"
    ].isna().all()
):

    columna_apellido = buscar_columna(
        df_users_cv,
        [
            "lastName",
            "lastname",
            "last_name",
        ],
    )

    if columna_apellido:

        df_users_cv[
            "lastName_postulante"
        ] = df_users_cv[
            columna_apellido
        ]


# ============================================================
# LIMPIAR CATEGORÍAS
# ============================================================

df_users_cv[
    "area_profesional"
] = (
    df_users_cv[
        "area_profesional"
    ]
    .replace(
        [
            "",
            "nan",
            "None",
            "Sin registro",
        ],
        np.nan,
    )
)


# ============================================================
# ELIMINAR COLUMNAS SENSIBLES
# ============================================================

columnas_sensibles = [
    "password",
    "passwordHash",
    "hashedPassword",
]

df_users_cv = df_users_cv.drop(
    columns=columnas_sensibles,
    errors="ignore",
)


# ============================================================
# ORDENAR COLUMNAS IMPORTANTES
# ============================================================

columnas_importantes = [

    "_id_postulante",

    "email_postulante",

    "firstName_postulante",

    "lastName_postulante",

    "tiene_cv",

    "cantidad_cursos",

    "uso_ia",

    "cantidad_conversaciones",

    "cantidad_eventos",

    "participo_evento",

    "carrera_principal",

    "area_profesional",

    "nivel_educativo",

    "tiene_educacion",

    "tiene_carrera",

    "años_experiencia",

    "cantidad_experiencias",

    "años_practica",

    "cantidad_practicas",

    "tiene_experiencia",

    "tiene_practicas",

    "tipo_experiencia",

    "Rango_experiencia",

    "Rango_practica",

    "año",

    "mes_num",

    "mes",

    "modalidad_laboral",
]


columnas_importantes = [
    c
    for c in columnas_importantes
    if c in df_users_cv.columns
]


otras_columnas = [
    c
    for c in df_users_cv.columns
    if c not in columnas_importantes
]


df_users_cv = df_users_cv[
    columnas_importantes
    + otras_columnas
]


# ============================================================
# ELIMINAR DUPLICADOS
# ============================================================

df_users_cv = (
    df_users_cv
    .drop_duplicates(
        subset=[
            "_id_postulante",
        ],
        keep="first",
    )
    .reset_index(
        drop=True
    )
)


# ============================================================
# VALIDACIÓN POSTULANTES
# ============================================================

print()
print(
    "========== VALIDACIÓN POSTULANTES =========="
)

filas = len(
    df_users_cv
)

usuarios_unicos = (
    df_users_cv[
        "_id_postulante"
    ]
    .nunique()
)

duplicados = (
    filas
    - usuarios_unicos
)

print(
    f"Filas: {filas}"
)

print(
    f"Usuarios únicos: "
    f"{usuarios_unicos}"
)

print(
    f"Duplicados: "
    f"{duplicados}"
)

if filas == usuarios_unicos:

    print(
        "✅ VALIDACIÓN OK: "
        "1 fila = 1 usuario"
    )

else:

    print(
        "⚠️ ATENCIÓN: "
        "existen duplicados"
    )


# ============================================================
# VALIDACIÓN EXPERIENCIA
# ============================================================

print()
print(
    "========== VALIDACIÓN EXPERIENCIA =========="
)

conteo_tipo = (
    df_users_cv[
        "tipo_experiencia"
    ]
    .value_counts()
)

for categoria in [
    "Experiencia laboral",
    "Experiencia laboral y prácticas",
    "Prácticas",
    "Sin experiencia",
]:

    print(
        f"{categoria}: "
        f"{conteo_tipo.get(categoria, 0)}"
    )


print(
    f"Total categorías: "
    f"{conteo_tipo.sum()}"
)


if (
    conteo_tipo.sum()
    == len(df_users_cv)
):

    print(
        "✅ Las categorías son excluyentes"
    )


# ============================================================
# EXPERIENCIA SEPARADA
# ============================================================

print()
print(
    "========== EXPERIENCIA SEPARADA =========="
)

print(
    "Años experiencia laboral "
    "(sin prácticas): "
    f"{df_users_cv['años_experiencia'].sum():.2f}"
)

print(
    "Años prácticas: "
    f"{df_users_cv['años_practica'].sum():.2f}"
)

print(
    "Promedio experiencia laboral: "
    f"{df_users_cv['años_experiencia'].mean():.2f}"
)

print(
    "Promedio prácticas: "
    f"{df_users_cv['años_practica'].mean():.2f}"
)


# ============================================================
# DATOS PARA GRÁFICOS
# ============================================================

print()
print(
    "========== DATOS PARA GRÁFICOS =========="
)

print(
    "Postulantes:",
    len(df_users_cv),
)

print(
    "Con CV:",
    int(
        df_users_cv[
            "tiene_cv"
        ].sum()
    ),
)

print(
    "Usuarios IA:",
    int(
        df_users_cv[
            "uso_ia"
        ].sum()
    ),
)

print(
    "Participaron en eventos:",
    int(
        df_users_cv[
            "participo_evento"
        ].sum()
    ),
)

print(
    "Con experiencia laboral:",
    int(
        df_users_cv[
            "tiene_experiencia"
        ].sum()
    ),
)

print(
    "Con prácticas:",
    int(
        df_users_cv[
            "tiene_practicas"
        ].sum()
    ),
)

print(
    "Sin experiencia:",
    int(
        (
            df_users_cv[
                "tipo_experiencia"
            ]
            == "Sin experiencia"
        ).sum()
    ),
)

print(
    "Con área profesional:",
    int(
        df_users_cv[
            "area_profesional"
        ]
        .notna()
        .sum()
    ),
)

print(
    "Con carrera:",
    int(
        df_users_cv[
            "tiene_carrera"
        ].sum()
    ),
)

print(
    "Con nivel educativo:",
    int(
        df_users_cv[
            "tiene_educacion"
        ].sum()
    ),
)


# ============================================================
# DISTRIBUCIÓN EXPERIENCIA
# ============================================================

print()
print(
    "========== DISTRIBUCIÓN EXPERIENCIA =========="
)

print(
    df_users_cv[
        "tipo_experiencia"
    ]
    .value_counts()
)

print()
print(
    "Rangos experiencia laboral:"
)

print(
    df_users_cv[
        "Rango_experiencia"
    ]
    .value_counts()
)

print()
print(
    "Rangos prácticas:"
)

print(
    df_users_cv[
        "Rango_practica"
    ]
    .value_counts()
)


# ============================================================
# EDUCACIÓN
# ============================================================

print()
print(
    "========== EDUCACIÓN =========="
)

print(
    "Áreas profesionales:"
)

print(
    df_users_cv[
        "area_profesional"
    ]
    .value_counts()
)

print()
print(
    "Carreras:"
)

print(
    df_users_cv[
        "carrera_principal"
    ]
    .value_counts()
    .head(15)
)

print()
print(
    "Niveles educativos:"
)

print(
    df_users_cv[
        "nivel_educativo"
    ]
    .value_counts()
)


# ============================================================
# IA
# ============================================================

print()
print(
    "========== IA =========="
)

print(
    "Usuarios que utilizaron IA:",
    int(
        df_users_cv[
            "uso_ia"
        ].sum()
    ),
)

print(
    "Total conversaciones:",
    int(
        df_users_cv[
            "cantidad_conversaciones"
        ].sum()
    ),
)


# ============================================================
# CURSOS
# ============================================================

print()
print(
    "========== CURSOS =========="
)

print(
    "Usuarios con cursos:",
    int(
        (
            df_users_cv[
                "cantidad_cursos"
            ] > 0
        ).sum()
    ),
)

print(
    "Total matrículas:",
    int(
        df_users_cv[
            "cantidad_cursos"
        ].sum()
    ),
)


# ============================================================
# EVENTOS
# ============================================================

print()
print(
    "========== EVENTOS =========="
)

print(
    "Usuarios participantes:",
    int(
        df_users_cv[
            "participo_evento"
        ].sum()
    ),
)

print(
    "Total participaciones:",
    int(
        df_users_cv[
            "cantidad_eventos"
        ].sum()
    ),
)


# ============================================================
# VALIDACIONES ANALÍTICAS
# ============================================================

print()
print(
    "========== VALIDACIONES ANALÍTICAS =========="
)

total = len(
    df_users_cv
)

print(
    f"CV: "
    f"{int(df_users_cv['tiene_cv'].sum())}"
    f" / {total}"
)

print(
    f"Educación: "
    f"{int(df_users_cv['tiene_educacion'].sum())}"
    f" / {total}"
)

print(
    f"Carrera: "
    f"{int(df_users_cv['tiene_carrera'].sum())}"
    f" / {total}"
)

print(
    f"Experiencia: "
    f"{int(df_users_cv['tiene_experiencia'].sum())}"
    f" / {total}"
)

print(
    f"Prácticas: "
    f"{int(df_users_cv['tiene_practicas'].sum())}"
    f" / {total}"
)

print(
    f"IA: "
    f"{int(df_users_cv['uso_ia'].sum())}"
    f" / {total}"
)

print(
    f"Cursos: "
    f"{int((df_users_cv['cantidad_cursos'] > 0).sum())}"
    f" / {total}"
)

print(
    f"Eventos: "
    f"{int(df_users_cv['participo_evento'].sum())}"
    f" / {total}"
)


# ============================================================
# GUARDAR DASHBOARD
# ============================================================

ruta_dashboard = os.path.join(
    OUTPUT_DIR,
    "postulantes_dashboard.csv",
)

df_users_cv.to_csv(
    ruta_dashboard,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# GUARDAR DATASETS AUXILIARES
# ============================================================

if not educacion_detalle.empty:

    educacion_detalle.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "educacion_dashboard.csv",
        ),
        index=False,
        encoding="utf-8-sig",
    )


if not experiencia_detalle.empty:

    experiencia_detalle.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "experiencia_dashboard.csv",
        ),
        index=False,
        encoding="utf-8-sig",
    )


if not eventos_detalle.empty:

    eventos_detalle.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "eventos_dashboard.csv",
        ),
        index=False,
        encoding="utf-8-sig",
    )


# ============================================================
# RESULTADOS
# ============================================================

print()
print(
    "========== RESULTADOS =========="
)

print(
    "Usuarios:",
    users.shape,
)

print(
    "Usuarios + CV:",
    df_users_cv.shape,
)

print(
    "Educación detalle:",
    educacion_detalle.shape,
)

print(
    "Experiencia detalle:",
    experiencia_detalle.shape,
)

print(
    "Eventos detalle:",
    eventos_detalle.shape,
)

print(
    "IA:",
    aiconversations.shape,
)

print(
    "Cursos:",
    courseenrollments.shape,
)


# ============================================================
# VALIDACIÓN FINAL
# ============================================================

print()
print(
    "========== VALIDACIÓN FINAL =========="
)

print(
    f"Dimensiones: "
    f"{df_users_cv.shape}"
)

print(
    "Usuarios únicos:",
    df_users_cv[
        "_id_postulante"
    ].nunique(),
)

print(
    "Duplicados:",
    df_users_cv[
        "_id_postulante"
    ]
    .duplicated()
    .sum(),
)


# ============================================================
# COLUMNAS FINALES
# ============================================================

print()
print(
    "========== COLUMNAS FINALES =========="
)

print(
    df_users_cv.columns.tolist()
)


# ============================================================
# MENSAJE FINAL
# ============================================================

print()
print(
    f"💾 Dashboard guardado en: "
    f"{ruta_dashboard}"
)

print()
print(
    "✅ CONSTRUCTOR TERMINADO CORRECTAMENTE"
)

