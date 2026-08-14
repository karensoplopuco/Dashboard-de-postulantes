
# ============================================================
# scripts/constructor.py
# CONSTRUCTOR ROBUSTO DEL DASHBOARD DE POSTULANTES
# ============================================================

import os
import re
import unicodedata

import numpy as np
import pandas as pd

from app import ROOT
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
communities = cargar_cache("communities")
quizzes = cargar_cache("quizzes")
quizresults = cargar_cache("quizresults")
userquizdatas = cargar_cache("userquizdatas")
questions = cargar_cache("questions")

# ============================================================
# INSPECCIÓN DE DATOS DE QUIZZES
# ============================================================

print("\n========== INSPECCIÓN DE QUIZZES ==========")

# ------------------------------------------------------------
# USERQUIZDATAS
# ------------------------------------------------------------

print("\n--- USERQUIZDATAS ---")

print("Cantidad de registros:", len(userquizdatas))

if "data" in userquizdatas.columns:

    print("\nEjemplos de userquizdatas.data:")

    for i, valor in enumerate(
        userquizdatas["data"].dropna().head(5)
    ):
        print(f"\nRegistro {i + 1}:")
        print(valor)

else:

    print("⚠️ No existe la columna 'data'")


# ------------------------------------------------------------
# QUIZRESULTS
# ------------------------------------------------------------

print("\n--- QUIZRESULTS ---")

print("Cantidad de resultados:", len(quizresults))


if "items" in quizresults.columns:

    print("\nEjemplos de quizresults.items:")

    for i, valor in enumerate(
        quizresults["items"].dropna().head(5)
    ):
        print(f"\nResultado {i + 1}:")
        print(valor)

else:

    print("⚠️ No existe la columna 'items'")


if "report" in quizresults.columns:

    print("\nEjemplos de quizresults.report:")

    for i, valor in enumerate(
        quizresults["report"].dropna().head(5)
    ):
        print(f"\nReporte {i + 1}:")
        print(valor)

else:

    print("⚠️ No existe la columna 'report'")


# ------------------------------------------------------------
# INFORMACIÓN GENERAL
# ------------------------------------------------------------

print("\n--- TIPOS DE DATOS ---")

if "data" in userquizdatas.columns:

    print(
        "Tipo de userquizdatas.data:",
        userquizdatas["data"].dropna().map(type).value_counts()
    )

if "items" in quizresults.columns:

    print(
        "Tipo de quizresults.items:",
        quizresults["items"].dropna().map(type).value_counts()
    )

if "report" in quizresults.columns:

    print(
        "Tipo de quizresults.report:",
        quizresults["report"].dropna().map(type).value_counts()
    )


print("\n========== FIN INSPECCIÓN QUIZZES ==========")



# ============================================================
# INTERÉS EN CURSOS
# ============================================================

print("\n========== INTERÉS EN CURSOS ==========")

cursos_interes = pd.DataFrame()
cursos_interes_validos = pd.DataFrame()
cursos_resumen_usuario = pd.DataFrame()

# ------------------------------------------------------------
# VALIDAR COURSEENROLLMENTS
# ------------------------------------------------------------

if not courseenrollments.empty:

    print("Analizando courseenrollments...")

    ce = courseenrollments.copy()

    print("Columnas courseenrollments:")
    print(ce.columns.tolist())

    # --------------------------------------------------------
    # BUSCAR ID DEL USUARIO
    # --------------------------------------------------------

    posibles_user = [
        "userId",
        "user_id",
        "userid",
        "user",
        "_id_user"
    ]

    columna_user = None

    for col in posibles_user:
        if col in ce.columns:
            columna_user = col
            break

    # --------------------------------------------------------
    # BUSCAR ID DEL CURSO
    # --------------------------------------------------------

    posibles_curso = [
        "courseId",
        "course_id",
        "courseid",
        "course",
        "_id_course"
    ]

    columna_curso = None

    for col in posibles_curso:
        if col in ce.columns:
            columna_curso = col
            break

    print(f"Columna usuario encontrada: {columna_user}")
    print(f"Columna curso encontrada: {columna_curso}")

    # --------------------------------------------------------
    # SI ENCONTRAMOS AMBOS CAMPOS
    # --------------------------------------------------------

    if columna_user and columna_curso:

        cursos_interes = ce[
            [columna_user, columna_curso]
        ].copy()

        cursos_interes = cursos_interes.rename(
            columns={
                columna_user: "_id_user",
                columna_curso: "_id_course"
            }
        )

        # ----------------------------------------------------
        # NORMALIZAR IDs
        # ----------------------------------------------------

        cursos_interes["_id_user"] = (
            cursos_interes["_id_user"]
            .astype(str)
            .str.strip()
        )

        cursos_interes["_id_course"] = (
            cursos_interes["_id_course"]
            .astype(str)
            .str.strip()
        )

        # ----------------------------------------------------
        # ELIMINAR IDS VACÍOS
        # ----------------------------------------------------

        cursos_interes = cursos_interes[
            (cursos_interes["_id_user"] != "") &
            (cursos_interes["_id_course"] != "") &
            (cursos_interes["_id_user"] != "nan") &
            (cursos_interes["_id_course"] != "nan") &
            (cursos_interes["_id_user"] != "None") &
            (cursos_interes["_id_course"] != "None")
        ].copy()

        # ----------------------------------------------------
        # CRUZAR CON COURSES
        # ----------------------------------------------------

        if not courses.empty:

            cursos = courses.copy()

            # Normalizar ID del curso
            if "_id" in cursos.columns:

                cursos["_id_course"] = (
                    cursos["_id"]
                    .astype(str)
                    .str.strip()
                )

            elif "id" in cursos.columns:

                cursos["_id_course"] = (
                    cursos["id"]
                    .astype(str)
                    .str.strip()
                )

            else:

                cursos["_id_course"] = ""

            # ------------------------------------------------
            # BUSCAR NOMBRE DEL CURSO
            # ------------------------------------------------

            posibles_nombre = [
                "name",
                "title",
                "courseName",
                "course_name",
                "nombre",
                "nombreCurso"
            ]

            columna_nombre = None

            for col in posibles_nombre:

                if col in cursos.columns:
                    columna_nombre = col
                    break

            print(
                f"Columna nombre curso encontrada: "
                f"{columna_nombre}"
            )

            if columna_nombre:

                cursos_nombre = cursos[
                    ["_id_course", columna_nombre]
                ].copy()

                cursos_nombre = cursos_nombre.rename(
                    columns={
                        columna_nombre: "curso"
                    }
                )

                cursos_nombre = (
                    cursos_nombre
                    .drop_duplicates(
                        subset="_id_course"
                    )
                )

                cursos_interes = cursos_interes.merge(
                    cursos_nombre,
                    on="_id_course",
                    how="left"
                )

            else:

                cursos_interes["curso"] = (
                    cursos_interes["_id_course"]
                )

            # ------------------------------------------------
            # BUSCAR CATEGORÍA DEL CURSO
            # ------------------------------------------------

            posibles_categoria = [
                "type",
                "category",
                "categoria",
                "courseType",
                "course_type"
            ]

            columna_categoria = None

            for col in posibles_categoria:

                if col in cursos.columns:
                    columna_categoria = col
                    break

            print(
                f"Columna categoría encontrada: "
                f"{columna_categoria}"
            )

            if columna_categoria:

                cursos_categoria = cursos[
                    ["_id_course", columna_categoria]
                ].copy()

                cursos_categoria = cursos_categoria.rename(
                    columns={
                        columna_categoria: "categoria_curso"
                    }
                )

                cursos_categoria = (
                    cursos_categoria
                    .drop_duplicates(
                        subset="_id_course"
                    )
                )

                cursos_interes = cursos_interes.merge(
                    cursos_categoria,
                    on="_id_course",
                    how="left"
                )

            else:

                cursos_interes[
                    "categoria_curso"
                ] = "Sin categoría"

        else:

            cursos_interes["curso"] = (
                cursos_interes["_id_course"]
            )

            cursos_interes[
                "categoria_curso"
            ] = "Sin categoría"

        # ----------------------------------------------------
        # CRUZAR CON USERS
        # ----------------------------------------------------

        if not users.empty and "_id" in users.columns:

            usuarios = users.copy()

            usuarios["_id_user"] = (
                usuarios["_id"]
                .astype(str)
                .str.strip()
            )

            columnas_usuario = [
                "_id_user"
            ]

            for col in [
                "firstName",
                "lastName",
                "email"
            ]:

                if col in usuarios.columns:
                    columnas_usuario.append(col)

            usuarios_info = (
                usuarios[
                    columnas_usuario
                ]
                .drop_duplicates(
                    subset="_id_user"
                )
            )

            cursos_interes = cursos_interes.merge(
                usuarios_info,
                on="_id_user",
                how="left"
            )

        # ----------------------------------------------------
        # ELIMINAR DUPLICADOS
        # ----------------------------------------------------

        cursos_interes = (
            cursos_interes
            .drop_duplicates()
            .reset_index(drop=True)
        )

        # ----------------------------------------------------
        # VALIDAR REGISTROS
        # ----------------------------------------------------

        cursos_interes_validos = cursos_interes[
            cursos_interes["_id_user"].notna() &
            cursos_interes["_id_course"].notna()
        ].copy()

        print(
            f"Registros de interés en cursos: "
            f"{len(cursos_interes_validos)}"
        )

        print(
            f"Usuarios únicos: "
            f"{cursos_interes_validos['_id_user'].nunique()}"
        )

        print(
            f"Cursos únicos: "
            f"{cursos_interes_validos['_id_course'].nunique()}"
        )

        # ----------------------------------------------------
        # CURSOS MÁS INTERESADOS
        # ----------------------------------------------------

        if "curso" in cursos_interes_validos.columns:

            print("\n========== CURSOS DE INTERÉS ==========")

            print(
                cursos_interes_validos[
                    "curso"
                ]
                .value_counts()
                .head(20)
            )

        # ----------------------------------------------------
        # RESUMEN POR USUARIO
        # ----------------------------------------------------

        cursos_resumen_usuario = (
            cursos_interes_validos
            .groupby("_id_user")
            .agg(
                cantidad_cursos=(
                    "_id_course",
                    "nunique"
                ),
                total_registros_curso=(
                    "_id_course",
                    "count"
                )
            )
            .reset_index()
        )

        # ----------------------------------------------------
        # CATEGORÍA MÁS INTERESADA POR USUARIO
        # ----------------------------------------------------

        if "categoria_curso" in cursos_interes_validos.columns:

            categoria_usuario = (
                cursos_interes_validos[
                    [
                        "_id_user",
                        "categoria_curso"
                    ]
                ]
                .copy()
            )

            categoria_usuario[
                "categoria_curso"
            ] = (
                categoria_usuario[
                    "categoria_curso"
                ]
                .fillna("Sin categoría")
                .astype(str)
                .str.strip()
            )

            conteo_categoria = (
                categoria_usuario
                .groupby(
                    [
                        "_id_user",
                        "categoria_curso"
                    ]
                )
                .size()
                .reset_index(
                    name="cantidad"
                )
            )

            # Categoría con mayor cantidad por usuario
            categoria_mayor = (
                conteo_categoria
                .sort_values(
                    [
                        "_id_user",
                        "cantidad",
                        "categoria_curso"
                    ],
                    ascending=[
                        True,
                        False,
                        True
                    ]
                )
                .drop_duplicates(
                    subset="_id_user"
                )
            )

            categoria_mayor = categoria_mayor.rename(
                columns={
                    "categoria_curso":
                        "categoria_curso_mas_interesada"
                }
            )

            categoria_mayor = categoria_mayor[
                [
                    "_id_user",
                    "categoria_curso_mas_interesada"
                ]
            ]

            cursos_resumen_usuario = (
                cursos_resumen_usuario
                .merge(
                    categoria_mayor,
                    on="_id_user",
                    how="left"
                )
            )

            # ------------------------------------------------
            # CANTIDAD DE CATEGORÍAS POR USUARIO
            # ------------------------------------------------

            total_categorias = (
                categoria_usuario
                .groupby("_id_user")[
                    "categoria_curso"
                ]
                .nunique()
                .reset_index(
                    name="total_categorias_curso"
                )
            )

            cursos_resumen_usuario = (
                cursos_resumen_usuario
                .merge(
                    total_categorias,
                    on="_id_user",
                    how="left"
                )
            )

        else:

            cursos_resumen_usuario[
                "categoria_curso_mas_interesada"
            ] = np.nan

            cursos_resumen_usuario[
                "total_categorias_curso"
            ] = 0

        # ----------------------------------------------------
        # CANTIDAD DE POSTULANTES POR CATEGORÍA
        # ----------------------------------------------------

        if "categoria_curso" in cursos_interes_validos.columns:

            postulantes_categoria = (
                cursos_interes_validos[
                    [
                        "_id_user",
                        "categoria_curso"
                    ]
                ]
                .drop_duplicates()
                .groupby(
                    "categoria_curso"
                )["_id_user"]
                .nunique()
                .reset_index(
                    name="postulantes_categoria_curso"
                )
            )

            cursos_resumen_usuario = (
                cursos_resumen_usuario
                .merge(
                    postulantes_categoria,
                    left_on=
                        "categoria_curso_mas_interesada",
                    right_on=
                        "categoria_curso",
                    how="left"
                )
            )

            cursos_resumen_usuario = (
                cursos_resumen_usuario
                .drop(
                    columns=[
                        "categoria_curso"
                    ],
                    errors="ignore"
                )
                .rename(
                    columns={
                        "postulantes_categoria_curso":
                            "postulantes_categoria_curso_mas_interesada"
                    }
                )
            )

        else:

            cursos_resumen_usuario[
                "postulantes_categoria_curso_mas_interesada"
            ] = 0

        # ----------------------------------------------------
        # ASEGURAR COLUMNAS
        # ----------------------------------------------------

        for col in [
            "cantidad_cursos",
            "total_registros_curso",
            "total_categorias_curso",
            "postulantes_categoria_curso_mas_interesada"
        ]:

            if col not in cursos_resumen_usuario.columns:

                cursos_resumen_usuario[col] = 0

        # ----------------------------------------------------
        # MOSTRAR RESUMEN
        # ----------------------------------------------------

        print("\n========== RESUMEN POR USUARIO ==========")

        print(
            cursos_resumen_usuario.head(20).to_string(
                index=False
            )
        )

    else:

        print(
            "⚠️ No se encontraron automáticamente "
            "las columnas user/course."
        )

else:

    print(
        "⚠️ courseenrollments está vacío."
    )

# ============================================================
# GUARDAR DETALLE DE CURSOS
# ============================================================

if not cursos_interes.empty:

    cursos_interes.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "cursos_interes_dashboard.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print(
        "💾 Cursos de interés guardados:"
    )

    print(
        "   data/cache/cursos_interes_dashboard.csv"
    )

else:

    print(
        "\n⚠️ No existen registros de cursos_interes."
    )
# ============================================================
# CÓDIGOS DE ALIADOS Y LABORAL HEROS
# ============================================================

print()
print(
    "========== CÓDIGOS ALIADOS / LABORAL HEROS =========="
)


def normalizar_codigo(valor):

    if valor is None:
        return ""

    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass

    return (
        str(valor)
        .strip()
        .upper()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )


# ------------------------------------------------------------
# PREPARAR CÓDIGOS DE COMMUNITIES
# ------------------------------------------------------------

codigos_aliados = set()

if not communities.empty:

    columna_code = buscar_columna(
        communities,
        [
            "code",
            "Code",
            "CODE",
        ],
    )

    if columna_code:

        codigos_aliados = set(
            communities[
                columna_code
            ]
            .apply(normalizar_codigo)
            .loc[
                lambda s: s != ""
            ]
            .unique()
        )

        print(
            f"Códigos Aliados encontrados: "
            f"{len(codigos_aliados)}"
        )

    else:

        print(
            "⚠️ communities no contiene "
            "la columna code."
        )

else:

    print(
        "⚠️ communities está vacío."
    )


# ------------------------------------------------------------
# PREPARAR USERS
# ------------------------------------------------------------

columna_codigo_user = buscar_columna(
    users,
    [
        "usedInvitationCode",
        "used_invitation_code",
    ],
)

if columna_codigo_user:

    usuarios_codigos = users.copy()

    usuarios_codigos[
        "_codigo_normalizado"
    ] = (
        usuarios_codigos[
            columna_codigo_user
        ]
        .apply(normalizar_codigo)
    )

else:

    usuarios_codigos = users.copy()

    usuarios_codigos[
        "_codigo_normalizado"
    ] = ""

    print(
        "⚠️ users no contiene "
        "usedInvitationCode."
    )


# ------------------------------------------------------------
# CLASIFICAR CÓDIGOS UTILIZADOS
# ------------------------------------------------------------

usuarios_con_codigo = (
    usuarios_codigos[
        usuarios_codigos[
            "_codigo_normalizado"
        ] != ""
    ]
    .copy()
)


usuarios_con_codigo[
    "_origen_codigo"
] = np.where(
    usuarios_con_codigo[
        "_codigo_normalizado"
    ].isin(
        codigos_aliados
    ),
    "Aliados",
    "Laboral Heros",
)


# ============================================================
# DATASET DE CÓDIGOS
# ============================================================

codigos_laboral_heros_aliados = (
    usuarios_con_codigo
    .groupby(
        [
            "_codigo_normalizado",
            "_origen_codigo",
        ],
        as_index=False,
    )
    .size()
    .rename(
        columns={
            "_codigo_normalizado":
                "codigo",

            "_origen_codigo":
                "origen",

            "size":
                "counter",
        }
    )
)


# Ordenar para facilitar lectura
codigos_laboral_heros_aliados = (
    codigos_laboral_heros_aliados
    .sort_values(
        [
            "origen",
            "counter",
        ],
        ascending=[
            True,
            False,
        ],
    )
    .reset_index(
        drop=True
    )
)


# ============================================================
# USUARIOS INVITADOS POR ALIADOS
# ============================================================

usuarios_invitados_aliados = (
    usuarios_con_codigo[
        usuarios_con_codigo[
            "_origen_codigo"
        ] == "Aliados"
    ]
    .copy()
)


columna_first = buscar_columna(
    usuarios_invitados_aliados,
    [
        "firstName",
        "firstname",
        "first_name",
    ],
)

columna_last = buscar_columna(
    usuarios_invitados_aliados,
    [
        "lastName",
        "lastname",
        "last_name",
    ],
)


if columna_first:

    usuarios_invitados_aliados[
        "firstName"
    ] = usuarios_invitados_aliados[
        columna_first
    ]

else:

    usuarios_invitados_aliados[
        "firstName"
    ] = np.nan


if columna_last:

    usuarios_invitados_aliados[
        "lastName"
    ] = usuarios_invitados_aliados[
        columna_last
    ]

else:

    usuarios_invitados_aliados[
        "lastName"
    ] = np.nan


if "isActive" not in usuarios_invitados_aliados.columns:

    usuarios_invitados_aliados[
        "isActive"
    ] = False


usuarios_invitados_aliados = (
    usuarios_invitados_aliados[
        [
            "_id",
            "firstName",
            "lastName",
            "_codigo_normalizado",
            "isActive",
        ]
    ]
    .rename(
        columns={
            "_id":
                "usuario_id",

            "_codigo_normalizado":
                "codigo_aliado",
        }
    )
)


# ============================================================
# USUARIOS INVITADOS POR LABORAL HEROS
# ============================================================

usuarios_invitados_laboral_heros = (
    usuarios_con_codigo[
        usuarios_con_codigo[
            "_origen_codigo"
        ] == "Laboral Heros"
    ]
    .copy()
)


if columna_first:

    usuarios_invitados_laboral_heros[
        "firstName"
    ] = usuarios_invitados_laboral_heros[
        columna_first
    ]

else:

    usuarios_invitados_laboral_heros[
        "firstName"
    ] = np.nan


if columna_last:

    usuarios_invitados_laboral_heros[
        "lastName"
    ] = usuarios_invitados_laboral_heros[
        columna_last
    ]

else:

    usuarios_invitados_laboral_heros[
        "lastName"
    ] = np.nan


if "isActive" not in usuarios_invitados_laboral_heros.columns:

    usuarios_invitados_laboral_heros[
        "isActive"
    ] = False


usuarios_invitados_laboral_heros = (
    usuarios_invitados_laboral_heros[
        [
            "_id",
            "firstName",
            "lastName",
            "_codigo_normalizado",
            "isActive",
        ]
    ]
    .rename(
        columns={
            "_id":
                "usuario_id",

            "_codigo_normalizado":
                "codigo_LaboralHeros",
        }
    )
)


# ============================================================
# VALIDACIÓN CÓDIGOS
# ============================================================

print()
print(
    "========== VALIDACIÓN CÓDIGOS =========="
)

print(
    "Usuarios con código:",
    len(usuarios_con_codigo),
)

print(
    "Usuarios invitados por Aliados:",
    len(usuarios_invitados_aliados),
)

print(
    "Usuarios invitados por Laboral Heros:",
    len(usuarios_invitados_laboral_heros),
)

print(
    "Códigos únicos:",
    len(codigos_laboral_heros_aliados),
)

print()
print(
    codigos_laboral_heros_aliados
)


# ============================================================
# GUARDAR DATASETS DE CÓDIGOS
# ============================================================

ruta_codigos = os.path.join(
    OUTPUT_DIR,
    "codigos_laboral_heros_aliados.csv",
)

ruta_usuarios_aliados = os.path.join(
    OUTPUT_DIR,
    "usuarios_invitados_aliados.csv",
)

ruta_usuarios_laboral_heros = os.path.join(
    OUTPUT_DIR,
    "usuarios_invitados_laboral_heros.csv",
)


codigos_laboral_heros_aliados.to_csv(
    ruta_codigos,
    index=False,
    encoding="utf-8-sig",
)


usuarios_invitados_aliados.to_csv(
    ruta_usuarios_aliados,
    index=False,
    encoding="utf-8-sig",
)


usuarios_invitados_laboral_heros.to_csv(
    ruta_usuarios_laboral_heros,
    index=False,
    encoding="utf-8-sig",
)


print()
print(
    "💾 Códigos guardados:"
)

print(
    ruta_codigos
)

print(
    ruta_usuarios_aliados
)

print(
    ruta_usuarios_laboral_heros
)

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
    "communities": communities,
     "quizzes": quizzes,
    "quizresults": quizresults,
    "userquizdatas": userquizdatas,
    "questions": questions,
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

    # --------------------------------------------------------
    # COLUMNAS DE EVENTGUESTS
    # --------------------------------------------------------

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
        f"Columna ID evento: "
        f"{columna_evento}"
    )

    # --------------------------------------------------------
    # GUARDAR ID ORIGINAL DEL EVENTGUEST
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

    # --------------------------------------------------------
    # NORMALIZAR ID DEL EVENTO
    # --------------------------------------------------------

    if columna_evento:

        eventos["_id_evento"] = (
            eventos[columna_evento]
            .apply(limpiar_id)
        )

    else:

        eventos["_id_evento"] = np.nan

    # ========================================================
    # OBTENER TÍTULO DESDE LA COLECCIÓN EVENTS
    # ========================================================

    if (
        not events.empty
        and "_id" in events.columns
        and "title" in events.columns
        and columna_evento
    ):

        eventos_catalogo = events.copy()

        eventos_catalogo["_id"] = (
            eventos_catalogo["_id"]
            .apply(limpiar_id)
        )

        eventos_catalogo = (
            eventos_catalogo[
                [
                    "_id",
                    "title",
                ]
            ]
            .dropna(
                subset=[
                    "_id",
                ]
            )
            .drop_duplicates(
                subset=[
                    "_id",
                ]
            )
            .rename(
                columns={
                    "_id":
                        "_id_evento_catalogo",
                    "title":
                        "titulo_evento",
                }
            )
        )

        eventos = eventos.merge(
            eventos_catalogo,
            left_on="_id_evento",
            right_on="_id_evento_catalogo",
            how="left",
        )

        eventos = eventos.drop(
            columns=[
                "_id_evento_catalogo",
            ],
            errors="ignore",
        )

        print(
            "✅ Títulos de eventos vinculados."
        )

    else:

        eventos["titulo_evento"] = np.nan

        print(
            "⚠️ No se pudo obtener el título "
            "desde la colección events."
        )

    # ========================================================
    # CLASIFICAR TIPO DE EVENTO
    # ========================================================

    def clasificar_evento(titulo):

        if pd.isna(titulo):

            return "Sin clasificar"

        titulo = normalizar_texto(
            titulo
        )

        if not titulo:

            return "Sin clasificar"

        if "taller" in titulo:

            return "Taller"

        elif "despega" in titulo:

            return "Feria laboral"

        elif "hub" in titulo:

            return "Networking"

        elif "webinar" in titulo:

            return "Webinar"

        else:

            return "Sin clasificar"

    eventos["tipo_evento"] = (
        eventos[
            "titulo_evento"
        ]
        .apply(
            clasificar_evento
        )
    )

    # --------------------------------------------------------
    # CRUCE POR EMAIL
    # --------------------------------------------------------

    eventos["_id_usuario_evento"] = np.nan

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

    # ========================================================
    # GUARDAR DETALLE
    # ========================================================

    eventos_detalle = eventos.copy()

    eventos_detalle[
        "_id_postulante"
    ] = (
        eventos_detalle[
            "_id_usuario_evento"
        ]
        .apply(
            limpiar_id
        )
    )

    eventos_detalle = (
        eventos_detalle
        .dropna(
            subset=[
                "_id_postulante",
            ]
        )
    )

    # ========================================================
    # PARTICIPACIÓN POR USUARIO
    # ========================================================

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


# ============================================================
# ASEGURAR CANTIDAD DE EVENTOS
# ============================================================

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
# VALIDACIÓN EVENTOS
# ============================================================

print()
print(
    "========== VALIDACIÓN EVENTOS =========="
)

if not eventos_detalle.empty:

    print(
        "Participantes vinculados:",
        eventos_detalle[
            "_id_postulante"
        ].nunique()
    )

    print(
        "Total participaciones:",
        len(eventos_detalle)
    )

    print()
    print(
        "Títulos de eventos:"
    )

    print(
        eventos_detalle[
            "titulo_evento"
        ]
        .value_counts(
            dropna=False
        )
        .head(15)
    )

    print()
    print(
        "Tipos de eventos:"
    )

    print(
        eventos_detalle[
            "tipo_evento"
        ]
        .value_counts(
            dropna=False
        )
    )

else:

    print(
        "⚠️ No se encontraron "
        "participaciones vinculadas."
    )

# ============================================================
# CÓDIGOS DE INVITACIÓN
# ALIADOS + LABORAL HEROS
# ============================================================

print()
print(
    "========== CRUCE CÓDIGOS DE INVITACIÓN =========="
)


def normalizar_codigo(valor):

    if valor is None:
        return ""

    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass

    return (
        str(valor)
        .strip()
        .upper()
        .replace(" ", "")
        .replace("-", "")
        .replace("_", "")
    )


# ============================================================
# VALIDAR COMMUNITIES
# ============================================================

if "code" not in communities.columns:

    raise ValueError(
        "❌ La colección communities no contiene la columna 'code'."
    )


if "usedInvitationCode" not in users.columns:

    raise ValueError(
        "❌ La colección users no contiene 'usedInvitationCode'."
    )


# ============================================================
# NORMALIZAR CÓDIGOS
# ============================================================

users["_codigo_invitacion_normalizado"] = (
    users["usedInvitationCode"]
    .apply(normalizar_codigo)
)

communities["_codigo_aliado_normalizado"] = (
    communities["code"]
    .apply(normalizar_codigo)
)


# ============================================================
# CÓDIGOS DE ALIADOS
# ============================================================

codigos_aliados = set(
    communities.loc[
        communities[
            "_codigo_aliado_normalizado"
        ] != "",
        "_codigo_aliado_normalizado"
    ]
    .unique()
)


# ============================================================
# CÓDIGOS UTILIZADOS POR USERS
# ============================================================

users_con_codigo = users[
    users[
        "_codigo_invitacion_normalizado"
    ] != ""
].copy()


codigos_users = set(
    users_con_codigo[
        "_codigo_invitacion_normalizado"
    ]
    .unique()
)


# ============================================================
# CLASIFICAR CÓDIGOS
# ============================================================

codigos_aliados_usados = (
    codigos_users
    .intersection(
        codigos_aliados
    )
)


codigos_laboral_heros = (
    codigos_users
    - codigos_aliados
)


print(
    f"🤝 Códigos de Aliados: "
    f"{len(codigos_aliados)}"
)

print(
    f"👤 Códigos utilizados por users: "
    f"{len(codigos_users)}"
)

print(
    f"✅ Códigos de Aliados utilizados: "
    f"{len(codigos_aliados_usados)}"
)

print(
    f"🦸 Códigos Laboral Heros: "
    f"{len(codigos_laboral_heros)}"
)


# ============================================================
# TABLA DE CÓDIGOS
# ============================================================

conteo_usuarios_codigo = (
    users_con_codigo
    .groupby(
        "_codigo_invitacion_normalizado"
    )
    .size()
    .reset_index(
        name="counter"
    )
)


# ============================================================
# ALIADOS
# ============================================================

df_aliados = pd.DataFrame(
    {
        "codigo_normalizado":
            list(codigos_aliados)
    }
)


df_aliados = df_aliados.merge(
    conteo_usuarios_codigo,
    left_on="codigo_normalizado",
    right_on="_codigo_invitacion_normalizado",
    how="left",
)


df_aliados["counter"] = (
    df_aliados["counter"]
    .fillna(0)
    .astype(int)
)


# Código original de communities

codigos_originales = (
    communities.loc[
        communities[
            "_codigo_aliado_normalizado"
        ] != "",
        [
            "_codigo_aliado_normalizado",
            "code",
        ],
    ]
    .drop_duplicates(
        subset=[
            "_codigo_aliado_normalizado"
        ]
    )
)


df_aliados = df_aliados.merge(
    codigos_originales,
    left_on="codigo_normalizado",
    right_on="_codigo_aliado_normalizado",
    how="left",
)


df_aliados["codigo"] = (
    df_aliados["code"]
)


df_aliados["origen"] = "Aliados"


df_aliados = df_aliados[
    [
        "codigo",
        "origen",
        "counter",
    ]
]


# ============================================================
# LABORAL HEROS
# ============================================================

df_laboral_heros = (
    conteo_usuarios_codigo[
        conteo_usuarios_codigo[
            "_codigo_invitacion_normalizado"
        ].isin(
            codigos_laboral_heros
        )
    ]
    .copy()
)


df_laboral_heros["codigo"] = (
    df_laboral_heros[
        "_codigo_invitacion_normalizado"
    ]
)


df_laboral_heros["origen"] = (
    "Laboral Heros"
)


df_laboral_heros = df_laboral_heros[
    [
        "codigo",
        "origen",
        "counter",
    ]
]


# ============================================================
# UNIR TABLA DE CÓDIGOS
# ============================================================

df_codigos = pd.concat(
    [
        df_aliados,
        df_laboral_heros,
    ],
    ignore_index=True,
)


df_codigos = (
    df_codigos
    .drop_duplicates(
        subset=[
            "codigo"
        ]
    )
    .sort_values(
        by=[
            "origen",
            "codigo",
        ]
    )
    .reset_index(
        drop=True
    )
)


# ============================================================
# USUARIOS INVITADOS POR ALIADOS
# ============================================================

df_usuarios_aliados = users[
    users[
        "_codigo_invitacion_normalizado"
    ].isin(
        codigos_aliados
    )
].copy()


df_usuarios_aliados[
    "codigo_aliado"
] = (
    df_usuarios_aliados[
        "usedInvitationCode"
    ]
    .astype(str)
    .str.strip()
)


df_usuarios_aliados = df_usuarios_aliados[
    [
        "_id",
        "firstName",
        "lastName",
        "codigo_aliado",
        "isActive",
    ]
].copy()


df_usuarios_aliados = (
    df_usuarios_aliados
    .rename(
        columns={
            "_id": "usuario_id"
        }
    )
    .drop_duplicates(
        subset=[
            "usuario_id"
        ]
    )
    .reset_index(
        drop=True
    )
)


# ============================================================
# USUARIOS INVITADOS POR LABORAL HEROS
# ============================================================

df_usuarios_heros = users[
    users[
        "_codigo_invitacion_normalizado"
    ].isin(
        codigos_laboral_heros
    )
].copy()


df_usuarios_heros[
    "codigo_LaboralHeros"
] = (
    df_usuarios_heros[
        "usedInvitationCode"
    ]
    .astype(str)
    .str.strip()
)


df_usuarios_heros = df_usuarios_heros[
    [
        "_id",
        "firstName",
        "lastName",
        "codigo_LaboralHeros",
        "isActive",
    ]
].copy()


df_usuarios_heros = (
    df_usuarios_heros
    .rename(
        columns={
            "_id": "usuario_id"
        }
    )
    .drop_duplicates(
        subset=[
            "usuario_id"
        ]
    )
    .reset_index(
        drop=True
    )
)


# ============================================================
# MARCAR ORIGEN EN EL DATASET PRINCIPAL
# ============================================================

df_users_cv[
    "origen_invitacion"
] = "Sin código"


df_users_cv[
    "codigo_invitacion"
] = np.nan


df_users_cv[
    "cantidad_invitados"
] = 0


# Mapa usuario → código/origen

mapa_invitaciones = users[
    [
        "_id",
        "usedInvitationCode",
        "_codigo_invitacion_normalizado",
    ]
].copy()


mapa_invitaciones = (
    mapa_invitaciones
    .rename(
        columns={
            "_id":
                "_id_postulante"
        }
    )
)


mapa_invitaciones[
    "_id_postulante"
] = (
    mapa_invitaciones[
        "_id_postulante"
    ]
    .apply(limpiar_id)
)


mapa_invitaciones[
    "codigo_invitacion"
] = (
    mapa_invitaciones[
        "usedInvitationCode"
    ]
    .replace(
        [
            "",
            "nan",
            "None",
            "null",
        ],
        np.nan,
    )
)


mapa_invitaciones[
    "origen_invitacion"
] = np.where(
    mapa_invitaciones[
        "_codigo_invitacion_normalizado"
    ].isin(
        codigos_aliados
    ),
    "Aliados",
    np.where(
        mapa_invitaciones[
            "_codigo_invitacion_normalizado"
        ].isin(
            codigos_laboral_heros
        ),
        "Laboral Heros",
        "Sin código",
    ),
)


df_users_cv = df_users_cv.merge(
    mapa_invitaciones[
        [
            "_id_postulante",
            "codigo_invitacion",
            "origen_invitacion",
        ]
    ],
    on="_id_postulante",
    how="left",
    suffixes=(
        "",
        "_invitacion",
    ),
)


df_users_cv[
    "codigo_invitacion"
] = (
    df_users_cv[
        "codigo_invitacion_invitacion"
    ]
    .combine_first(
        df_users_cv[
            "codigo_invitacion"
        ]
    )
)


df_users_cv[
    "origen_invitacion"
] = (
    df_users_cv[
        "origen_invitacion_invitacion"
    ]
    .combine_first(
        df_users_cv[
            "origen_invitacion"
        ]
    )
)


df_users_cv = df_users_cv.drop(
    columns=[
        "codigo_invitacion_invitacion",
        "origen_invitacion_invitacion",
    ],
    errors="ignore",
)


# ============================================================
# VALIDACIÓN
# ============================================================

print()
print(
    "========== VALIDACIÓN CÓDIGOS =========="
)


print(
    "Usuarios invitados por Aliados:",
    len(
        df_usuarios_aliados
    ),
)


print(
    "Usuarios invitados por Laboral Heros:",
    len(
        df_usuarios_heros
    ),
)


print(
    "Usuarios con código:",
    len(
        users_con_codigo
    ),
)


print(
    "Distribución:"
)


print(
    df_codigos[
        "origen"
    ].value_counts()
)


# ============================================================
# GUARDAR CACHE
# ============================================================

df_codigos.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "codigos_laboral_heros_aliados.csv",
    ),
    index=False,
    encoding="utf-8-sig",
)


df_usuarios_aliados.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "usuarios_invitados_aliados.csv",
    ),
    index=False,
    encoding="utf-8-sig",
)


df_usuarios_heros.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "usuarios_invitados_laboral_heros.csv",
    ),
    index=False,
    encoding="utf-8-sig",
)


print()
print(
    "💾 Caches de invitaciones guardados:"
)


print(
    "   data/cache/codigos_laboral_heros_aliados.csv"
)

print(
    "   data/cache/usuarios_invitados_aliados.csv"
)

print(
    "   data/cache/usuarios_invitados_laboral_heros.csv"
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

    "total_registros_curso": 0,

    "categoria_curso_mas_interesada":np.nan,
        

    "postulantes_categoria_curso_mas_interesada":0,

    "total_categorias_curso":0,


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

    "categoria_curso_mas_interesada",

    "postulantes_categoria_curso_mas_interesada",

    "total_categorias_curso",

    "uso_ia",

    "cantidad_quizzes",

    "cantidad_respuestas_quiz",

    "cantidad_resultados_quiz",

    "completo_quiz",

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
# CRUCE QUIZZES
# ============================================================

print("\n========== CRUCE QUIZZES ==========")

# ------------------------------------------------------------
# VALIDAR COLUMNAS
# ------------------------------------------------------------

print("Columnas userquizdatas:")
print(list(userquizdatas.columns))

print("\nColumnas quizzes:")
print(list(quizzes.columns))

print("\nColumnas quizresults:")
print(list(quizresults.columns))


# ------------------------------------------------------------
# NORMALIZAR IDs
# ------------------------------------------------------------

def normalizar_id_quiz(valor):

    if pd.isna(valor):
        return None

    return str(valor).strip()


userquizdatas["_id_user"] = userquizdatas["user"].apply(
    normalizar_id_quiz
)

userquizdatas["_id_quiz"] = userquizdatas["quiz"].apply(
    normalizar_id_quiz
)

quizzes["_id_quiz"] = quizzes["_id"].apply(
    normalizar_id_quiz
)

quizresults["_id_user"] = quizresults["user"].apply(
    normalizar_id_quiz
)

quizresults["_id_quiz"] = quizresults["quiz"].apply(
    normalizar_id_quiz
)


# ------------------------------------------------------------
# MAPA DE QUIZZES
# ------------------------------------------------------------

mapa_quizzes = quizzes[
    [
        "_id_quiz",
        "key",
        "title"
    ]
].copy()

mapa_quizzes = mapa_quizzes.rename(
    columns={
        "key": "quiz_key",
        "title": "quiz_nombre"
    }
)

print(
    f"Quizzes encontrados: {len(mapa_quizzes)}"
)

print(
    mapa_quizzes[
        [
            "_id_quiz",
            "quiz_key",
            "quiz_nombre"
        ]
    ].to_string(index=False)
)


# ------------------------------------------------------------
# CRUZAR USERQUIZDATAS + QUIZZES
# ------------------------------------------------------------

quizzes_detalle = userquizdatas.merge(
    mapa_quizzes,
    on="_id_quiz",
    how="left"
)

print(
    f"\nRegistros userquizdatas: "
    f"{len(userquizdatas)}"
)

print(
    f"Registros después de cruzar quizzes: "
    f"{len(quizzes_detalle)}"
)


# ------------------------------------------------------------
# VALIDAR QUIZZES SIN NOMBRE
# ------------------------------------------------------------

sin_quiz = quizzes_detalle[
    quizzes_detalle["quiz_nombre"].isna()
]

print(
    f"Registros sin información del quiz: "
    f"{len(sin_quiz)}"
)


# ------------------------------------------------------------
# CRUZAR CON USERS
# ------------------------------------------------------------

usuarios_quiz = users[
    [
        "_id",
        "email",
        "firstName",
        "lastName"
    ]
].copy()

usuarios_quiz["_id_user"] = usuarios_quiz[
    "_id"
].apply(normalizar_id_quiz)

usuarios_quiz = usuarios_quiz.drop(
    columns=["_id"]
)

usuarios_quiz = usuarios_quiz.rename(
    columns={
        "email": "email_quiz",
        "firstName": "firstName_quiz",
        "lastName": "lastName_quiz"
    }
)


quizzes_detalle = quizzes_detalle.merge(
    usuarios_quiz,
    on="_id_user",
    how="left"
)


# ------------------------------------------------------------
# CRUZAR RESULTADOS
# ------------------------------------------------------------

resultados_quiz = quizresults[
    [
        "_id_user",
        "_id_quiz",
        "items",
        "report",
        "createdAt"
    ]
].copy()

resultados_quiz = resultados_quiz.rename(
    columns={
        "items": "resultado_items",
        "report": "resultado_quiz",
        "createdAt": "fecha_resultado_quiz"
    }
)


# Un usuario puede tener resultado para un quiz.
# Usamos left para conservar todos los registros
# de userquizdatas.

quizzes_detalle = quizzes_detalle.merge(
    resultados_quiz,
    on=[
        "_id_user",
        "_id_quiz"
    ],
    how="left"
)


# ------------------------------------------------------------
# INDICADORES POR USUARIO
# ------------------------------------------------------------

resumen_quizzes = (
    quizzes_detalle
    .groupby("_id_user")
    .agg(
        cantidad_quizzes=(
            "_id_quiz",
            "nunique"
        ),
        cantidad_respuestas_quiz=(
            "_id",
            "count"
        ),
        cantidad_resultados_quiz=(
            "resultado_quiz",
            lambda x: x.notna().sum()
        )
    )
    .reset_index()
)


# ------------------------------------------------------------
# INDICADOR: COMPLETÓ QUIZ
# ------------------------------------------------------------

resumen_quizzes["completo_quiz"] = (
    resumen_quizzes["cantidad_resultados_quiz"] > 0
)


# ------------------------------------------------------------
# VALIDACIÓN
# ------------------------------------------------------------

print("\n========== VALIDACIÓN QUIZZES ==========")

print(
    "Registros userquizdatas:",
    len(userquizdatas)
)

print(
    "Usuarios con quizzes:",
    resumen_quizzes["_id_user"].nunique()
)

print(
    "Quizzes realizados:",
    resumen_quizzes["cantidad_quizzes"].sum()
)

print(
    "Usuarios con resultado:",
    (
        resumen_quizzes[
            "cantidad_resultados_quiz"
        ] > 0
    ).sum()
)

print(
    "Total resultados:",
    len(quizresults)
)


# ------------------------------------------------------------
# DISTRIBUCIÓN POR QUIZ
# ------------------------------------------------------------

print("\n========== DISTRIBUCIÓN POR QUIZ ==========")

distribucion_quizzes = (
    quizzes_detalle
    .groupby(
        [
            "_id_quiz",
            "quiz_key",
            "quiz_nombre"
        ]
    )
    .agg(
        usuarios=(
            "_id_user",
            "nunique"
        ),
        respuestas=(
            "_id",
            "count"
        )
    )
    .reset_index()
    .sort_values(
        "usuarios",
        ascending=False
    )
)

print(
    distribucion_quizzes.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# GUARDAR DETALLE
# ------------------------------------------------------------

ruta_quizzes_detalle = (
    "data/cache/quizzes_detalle_dashboard.csv"
)

quizzes_detalle.to_csv(
    ruta_quizzes_detalle,
    index=False,
    encoding="utf-8-sig"
)

print(
    f"\n💾 Detalle de quizzes guardado en:"
    f"\n   {ruta_quizzes_detalle}"
)


# ------------------------------------------------------------
# GUARDAR RESUMEN
# ------------------------------------------------------------

ruta_resumen_quizzes = (
    "data/cache/resumen_quizzes_dashboard.csv"
)

resumen_quizzes.to_csv(
    ruta_resumen_quizzes,
    index=False,
    encoding="utf-8-sig"
)

print(
    f"💾 Resumen de quizzes guardado en:"
    f"\n   {ruta_resumen_quizzes}"
)


print("\n========== QUIZZES TERMINADO ==========")

# ============================================================
# INCORPORAR QUIZZES AL DATASET PRINCIPAL
# ============================================================

print()
print(
    "========== INCORPORAR QUIZZES AL DATASET PRINCIPAL =========="
)

# ------------------------------------------------------------
# PREPARAR RESUMEN DE QUIZZES
# ------------------------------------------------------------

if not resumen_quizzes.empty:

    resumen_quizzes_merge = resumen_quizzes.copy()

    resumen_quizzes_merge[
        "_id_postulante"
    ] = (
        resumen_quizzes_merge[
            "_id_user"
        ]
        .apply(limpiar_id)
    )

    resumen_quizzes_merge = (
        resumen_quizzes_merge[
            [
                "_id_postulante",
                "cantidad_quizzes",
                "cantidad_respuestas_quiz",
                "cantidad_resultados_quiz",
                "completo_quiz",
            ]
        ]
        .drop_duplicates(
            subset=[
                "_id_postulante"
            ]
        )
    )

    # --------------------------------------------------------
    # CRUZAR CON DATASET PRINCIPAL
    # --------------------------------------------------------

    df_users_cv = df_users_cv.merge(
        resumen_quizzes_merge,
        on="_id_postulante",
        how="left",
        validate="one_to_one",
    )

else:

    df_users_cv[
        "cantidad_quizzes"
    ] = 0

    df_users_cv[
        "cantidad_respuestas_quiz"
    ] = 0

    df_users_cv[
        "cantidad_resultados_quiz"
    ] = 0

    df_users_cv[
        "completo_quiz"
    ] = False


# ------------------------------------------------------------
# ASEGURAR VALORES
# ------------------------------------------------------------

for columna in [
    "cantidad_quizzes",
    "cantidad_respuestas_quiz",
    "cantidad_resultados_quiz",
]:

    if columna not in df_users_cv.columns:

        df_users_cv[
            columna
        ] = 0

    df_users_cv[
        columna
    ] = (
        pd.to_numeric(
            df_users_cv[
                columna
            ],
            errors="coerce",
        )
        .fillna(0)
        .astype(int)
    )


if "completo_quiz" not in df_users_cv.columns:

    df_users_cv[
        "completo_quiz"
    ] = False


df_users_cv[
    "completo_quiz"
] = (
    df_users_cv[
        "completo_quiz"
    ]
    .fillna(False)
    .astype(bool)
)


# ------------------------------------------------------------
# VALIDACIÓN
# ------------------------------------------------------------

print(
    "Usuarios con quizzes:",
    int(
        (
            df_users_cv[
                "cantidad_quizzes"
            ] > 0
        ).sum()
    ),
)

print(
    "Total quizzes realizados:",
    int(
        df_users_cv[
            "cantidad_quizzes"
        ].sum()
    ),
)

print(
    "Usuarios con resultado:",
    int(
        (
            df_users_cv[
                "cantidad_resultados_quiz"
            ] > 0
        ).sum()
    ),
)

print(
    "Usuarios que completaron quiz:",
    int(
        df_users_cv[
            "completo_quiz"
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
# INTERÉS EN CURSOS
# ============================================================

print("\n========== INTERÉS EN CURSOS ==========")

# DataFrame vacío por defecto
cursos_interes = pd.DataFrame()

if not courseenrollments.empty:

    print("Analizando courseenrollments...")

    ce = courseenrollments.copy()

    # --------------------------------------------------------
    # MOSTRAR COLUMNAS
    # --------------------------------------------------------

    print("Columnas courseenrollments:")
    print(ce.columns.tolist())

    # --------------------------------------------------------
    # BUSCAR USUARIO
    # --------------------------------------------------------

    posibles_user = [
        "userId",
        "user_id",
        "userid",
        "user",
        "_id_user"
    ]

    columna_user = None

    for col in posibles_user:
        if col in ce.columns:
            columna_user = col
            break

    # --------------------------------------------------------
    # BUSCAR CURSO
    # --------------------------------------------------------

    posibles_curso = [
        "courseId",
        "course_id",
        "courseid",
        "course",
        "_id_course"
    ]

    columna_curso = None

    for col in posibles_curso:
        if col in ce.columns:
            columna_curso = col
            break

    print(
        f"Columna usuario encontrada: {columna_user}"
    )

    print(
        f"Columna curso encontrada: {columna_curso}"
    )

    # --------------------------------------------------------
    # PROCESAR SI EXISTEN AMBAS COLUMNAS
    # --------------------------------------------------------

    if columna_user and columna_curso:

        cursos_interes = ce[
            [columna_user, columna_curso]
        ].copy()

        cursos_interes = cursos_interes.rename(
            columns={
                columna_user: "_id_user",
                columna_curso: "_id_course"
            }
        )

        # ----------------------------------------------------
        # NORMALIZAR IDS
        # ----------------------------------------------------

        cursos_interes["_id_user"] = (
            cursos_interes["_id_user"]
            .astype(str)
            .str.strip()
        )

        cursos_interes["_id_course"] = (
            cursos_interes["_id_course"]
            .astype(str)
            .str.strip()
        )

        # ----------------------------------------------------
        # ELIMINAR IDS VACÍOS
        # ----------------------------------------------------

        cursos_interes = cursos_interes[
            (cursos_interes["_id_user"] != "") &
            (cursos_interes["_id_course"] != "") &
            (cursos_interes["_id_user"] != "nan") &
            (cursos_interes["_id_course"] != "nan") &
            (cursos_interes["_id_user"] != "None") &
            (cursos_interes["_id_course"] != "None")
        ].copy()

        # ----------------------------------------------------
        # CRUZAR CON COURSES
        # ----------------------------------------------------

        if not courses.empty:

            cursos = courses.copy()

            if "_id" in cursos.columns:

                cursos["_id_course"] = (
                    cursos["_id"]
                    .astype(str)
                    .str.strip()
                )

            elif "id" in cursos.columns:

                cursos["_id_course"] = (
                    cursos["id"]
                    .astype(str)
                    .str.strip()
                )

            else:

                cursos["_id_course"] = ""

            # ------------------------------------------------
            # BUSCAR NOMBRE DEL CURSO
            # ------------------------------------------------

            posibles_nombre = [
                "name",
                "title",
                "courseName",
                "course_name",
                "nombre",
                "nombreCurso"
            ]

            columna_nombre = None

            for col in posibles_nombre:

                if col in cursos.columns:
                    columna_nombre = col
                    break

            print(
                f"Columna nombre curso encontrada: "
                f"{columna_nombre}"
            )

            if columna_nombre:

                cursos_nombre = cursos[
                    [
                        "_id_course",
                        columna_nombre
                    ]
                ].copy()

                cursos_nombre = cursos_nombre.rename(
                    columns={
                        columna_nombre: "curso"
                    }
                )

                cursos_nombre = (
                    cursos_nombre
                    .drop_duplicates(
                        subset="_id_course"
                    )
                )

                cursos_interes = cursos_interes.merge(
                    cursos_nombre,
                    on="_id_course",
                    how="left"
                )

            else:

                cursos_interes["curso"] = (
                    cursos_interes["_id_course"]
                )

            # ------------------------------------------------
            # BUSCAR CATEGORÍA / TIPO
            # ------------------------------------------------

            posibles_categoria = [
                "type",
                "category",
                "categoria",
                "courseType",
                "course_type"
            ]

            columna_categoria = None

            for col in posibles_categoria:

                if col in cursos.columns:
                    columna_categoria = col
                    break

            print(
                f"Columna categoría encontrada: "
                f"{columna_categoria}"
            )

            if columna_categoria:

                cursos_categoria = cursos[
                    [
                        "_id_course",
                        columna_categoria
                    ]
                ].copy()

                cursos_categoria = cursos_categoria.rename(
                    columns={
                        columna_categoria:
                        "categoria_curso"
                    }
                )

                cursos_categoria = (
                    cursos_categoria
                    .drop_duplicates(
                        subset="_id_course"
                    )
                )

                cursos_interes = cursos_interes.merge(
                    cursos_categoria,
                    on="_id_course",
                    how="left"
                )

            else:

                cursos_interes[
                    "categoria_curso"
                ] = "Sin categoría"

        # ----------------------------------------------------
        # CRUZAR CON USERS
        # ----------------------------------------------------

        if not users.empty and "_id" in users.columns:

            usuarios = users.copy()

            usuarios["_id_user"] = (
                usuarios["_id"]
                .astype(str)
                .str.strip()
            )

            columnas_usuario = [
                "_id_user"
            ]

            for col in [
                "firstName",
                "lastName",
                "email"
            ]:

                if col in usuarios.columns:
                    columnas_usuario.append(col)

            usuarios_info = (
                usuarios[
                    columnas_usuario
                ]
                .drop_duplicates(
                    subset="_id_user"
                )
            )

            cursos_interes = cursos_interes.merge(
                usuarios_info,
                on="_id_user",
                how="left"
            )

        # ----------------------------------------------------
        # ELIMINAR DUPLICADOS
        # ----------------------------------------------------

        cursos_interes = (
            cursos_interes
            .drop_duplicates()
            .reset_index(drop=True)
        )

        # ----------------------------------------------------
        # MOSTRAR RESULTADOS
        # ----------------------------------------------------

        print(
            f"Registros de interés en cursos: "
            f"{len(cursos_interes)}"
        )

        print(
            f"Usuarios únicos: "
            f"{cursos_interes['_id_user'].nunique()}"
        )

        print(
            f"Cursos únicos: "
            f"{cursos_interes['curso'].nunique()}"
        )

        if "curso" in cursos_interes.columns:

            print("\nCursos de interés:")

            print(
                cursos_interes[
                    "curso"
                ]
                .value_counts()
                .head(20)
            )

    else:

        print(
            "⚠️ No se encontraron automáticamente "
            "las columnas user/course."
        )

else:

    print(
        "⚠️ courseenrollments está vacío."
    )


# ============================================================
# GUARDAR DETALLE DE CURSOS
# ============================================================

if not cursos_interes.empty:

    cursos_interes.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "cursos_interes_dashboard.csv"
        ),
        index=False,
        encoding="utf-8-sig"
    )

    print(
        "\n💾 Cursos de interés guardados:"
    )

    print(
        "   data/cache/cursos_interes_dashboard.csv"
    )

else:

    print(
        "\n⚠️ No se generaron registros "
        "de interés en cursos."
    )
# ============================================================
# INCORPORANDO INTERÉS EN CURSOS AL DATASET PRINCIPAL
# ============================================================

print("\n========== INCORPORANDO INTERÉS EN CURSOS ==========")


# ------------------------------------------------------------
# VALIDAR QUE EXISTE EL DATAFRAME DE CURSOS
# ------------------------------------------------------------

if "cursos_interes" not in locals() or cursos_interes is None:

    print("⚠️ No existe cursos_interes.")
    print("Se crearán columnas de cursos con valores 0.")

    # --------------------------------------------------------
    # USAR EL DATAFRAME PRINCIPAL REAL
    # --------------------------------------------------------

    df_users_cv["cantidad_cursos"] = 0
    df_users_cv["total_registros_curso"] = 0
    df_users_cv[
    "categoria_curso_mas_interesada"
    ] = "Sin cursos"

    
    df_users_cv[
    "total_categorias_curso"
    ]  = 0


    df_users_cv[
    "postulantes_categoria_curso_mas_interesada"
    ] = 0

else:

    cursos = cursos_interes.copy()

    # --------------------------------------------------------
    # NORMALIZAR IDS
    # --------------------------------------------------------

    cursos["_id_user"] = (
        cursos["_id_user"]
        .astype(str)
        .str.strip()
    )

    df_users_cv["_id_user"] = (
        df_users_cv["_id_postulante"]
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # ASEGURAR COLUMNA DE CATEGORÍA
    # --------------------------------------------------------

    if "categoria_curso" not in cursos.columns:

        if "categoria" in cursos.columns:

            cursos["categoria_curso"] = (
                cursos["categoria"]
            )

        elif "type" in cursos.columns:

            cursos["categoria_curso"] = (
                cursos["type"]
            )

        else:

            cursos["categoria_curso"] = (
                "Sin categoría"
            )

    cursos["categoria_curso"] = (
        cursos["categoria_curso"]
        .fillna("Sin categoría")
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # 1. RESUMEN DE CURSOS POR USUARIO
    # --------------------------------------------------------

    resumen_cursos_usuario = (
        cursos
        .groupby("_id_user")
        .agg(
            cantidad_cursos=("curso", "nunique"),
            total_registros_curso=("curso", "count"),
            total_categorias_curso=(
                "categoria_curso",
                "nunique"
            )
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # 2. CATEGORÍA MÁS INTERESADA POR USUARIO
    # --------------------------------------------------------

    categoria_usuario = (
        cursos
        .groupby(
            [
                "_id_user",
                "categoria_curso"
            ]
        )
        .size()
        .reset_index(
            name="cantidad_categoria"
        )
    )

    categoria_usuario = (
        categoria_usuario
        .sort_values(
            [
                "_id_user",
                "cantidad_categoria",
                "categoria_curso"
            ],
            ascending=[
                True,
                False,
                True
            ]
        )
    )

    categoria_usuario = (
        categoria_usuario
        .drop_duplicates(
            subset="_id_user",
            keep="first"
        )
        .rename(
            columns={
                "categoria_curso":
                    "categoria_curso_mas_interesada"
            }
        )
    )

    # --------------------------------------------------------
    # 3. CANTIDAD DE POSTULANTES POR CATEGORÍA
    # --------------------------------------------------------

    cantidad_postulantes_categoria = (
        cursos
        .groupby(
            "categoria_curso"
        )["_id_user"]
        .nunique()
        .reset_index(
            name="postulantes_categoria"
        )
    )

    # --------------------------------------------------------
    # 4. UNIR CATEGORÍA + CANTIDAD DE POSTULANTES
    # --------------------------------------------------------

    categoria_usuario = categoria_usuario.merge(
        cantidad_postulantes_categoria,
        left_on="categoria_curso_mas_interesada",
        right_on="categoria_curso",
        how="left"
    )

    if "categoria_curso" in categoria_usuario.columns:

        categoria_usuario = (
            categoria_usuario
            .drop(
                columns=["categoria_curso"]
            )
        )

    categoria_usuario = (
        categoria_usuario
        .rename(
            columns={
                "postulantes_categoria":
                    "postulantes_categoria_curso_mas_interesada"
            }
        )
    )

    # --------------------------------------------------------
    # 5. UNIR RESUMEN + CATEGORÍA
    # --------------------------------------------------------

    resumen_cursos_usuario = (
        resumen_cursos_usuario
        .merge(
            categoria_usuario[
                [
                    "_id_user",
                    "categoria_curso_mas_interesada",
                    "postulantes_categoria_curso_mas_interesada"
                ]
            ],
            on="_id_user",
            how="left"
        )
    )

    # --------------------------------------------------------
    # 6. ELIMINAR COLUMNAS ANTERIORES SI EXISTEN
    # --------------------------------------------------------

    columnas_curso = [
        "cantidad_cursos",
        "total_registros_curso",
        "categoria_curso_mas_interesada",
        "total_categorias_curso",
        "postulantes_categoria_curso_mas_interesada"
    ]

    columnas_existentes = [
        c
        for c in columnas_curso
        if c in df_users_cv.columns
    ]

    if columnas_existentes:

        df_users_cv = df_users_cv.drop(
            columns=columnas_existentes
        )

    # --------------------------------------------------------
    # 7. UNIR AL DATASET PRINCIPAL
    # --------------------------------------------------------

    df_users_cv = df_users_cv.merge(
        resumen_cursos_usuario[
            [
                "_id_user",
                "cantidad_cursos",
                "total_registros_curso",
                "categoria_curso_mas_interesada",
                "total_categorias_curso",
                "postulantes_categoria_curso_mas_interesada"
            ]
        ],
        left_on="_id_postulante",
        right_on="_id_user",
        how="left"
    )

    # --------------------------------------------------------
    # 8. COMPLETAR USUARIOS SIN CURSOS
    # --------------------------------------------------------

    df_users_cv["cantidad_cursos"] = (
        pd.to_numeric(
            df_users_cv["cantidad_cursos"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )

    df_users_cv["total_registros_curso"] = (
        pd.to_numeric(
            df_users_cv["total_registros_curso"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )

    df_users_cv["total_categorias_curso"] = (
        pd.to_numeric(
            df_users_cv["total_categorias_curso"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )

    df_users_cv[
        "categoria_curso_mas_interesada"
    ] = (
        df_users_cv[
            "categoria_curso_mas_interesada"
        ]
        .fillna("Sin cursos")
    )

    df_users_cv[
        "postulantes_categoria_curso_mas_interesada"
    ] = (
        pd.to_numeric(
            df_users_cv[
                "postulantes_categoria_curso_mas_interesada"
            ],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )

    # --------------------------------------------------------
    # 9. VALIDACIÓN
    # --------------------------------------------------------

    print(
        "\n========== VALIDACIÓN INTERÉS EN CURSOS =========="
    )

    print(
        "Usuarios con cursos:",
        (
            df_users_cv["cantidad_cursos"]> 0
        ).sum()
    )

    print(
        "Total matrículas:",
        df_users_cv[
            "total_registros_curso"
        ].sum()
    )

    print(
        "Categorías con interés:",
        (
            df_users_cv[
                "categoria_curso_mas_interesada"
            ] != "Sin cursos"
        ).sum()
    )

    print(
        "\nDistribución de categorías:"
    )

    print(
        df_users_cv[
            "categoria_curso_mas_interesada"
        ]
        .value_counts()
    )

    print(
        "\n✅ Interés en cursos incorporado correctamente."
    )


# ============================================================
# GENERAR DATASET DE INTERÉS EN CURSOS PARA EL DASHBOARD
# ============================================================

print("\n========== GENERANDO DATASET DE INTERÉS EN CURSOS ==========")


# ------------------------------------------------------------
# VALIDAR QUE EXISTE EL DATAFRAME DE CURSOS
# ------------------------------------------------------------

if "cursos" not in locals() or cursos is None:

    print(
        "⚠️ No existe el dataframe cursos."
    )

else:

    cursos_dashboard = cursos.copy()


    # --------------------------------------------------------
    # VALIDAR COLUMNAS NECESARIAS
    # --------------------------------------------------------

    columnas_necesarias = [
        "_id_user",
        "categoria_curso"
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_necesarias
        if columna not in cursos_dashboard.columns
    ]


    if columnas_faltantes:

        print(
            "⚠️ No se puede generar el dataset "
            "de interés en cursos."
        )

        print(
            "Columnas faltantes:",
            columnas_faltantes
        )

    else:

        # ----------------------------------------------------
        # SELECCIONAR SOLO LO NECESARIO
        # ----------------------------------------------------

        cursos_dashboard = cursos_dashboard[
            [
                "_id_user",
                "categoria_curso"
            ]
        ].copy()


        # ----------------------------------------------------
        # RENOMBRAR ID
        # ----------------------------------------------------

        cursos_dashboard = (
            cursos_dashboard
            .rename(
                columns={
                    "_id_user":
                        "_id_postulante"
                }
            )
        )


        # ----------------------------------------------------
        # NORMALIZAR ID
        # ----------------------------------------------------

        cursos_dashboard["_id_postulante"] = (
            cursos_dashboard["_id_postulante"]
            .astype("string")
            .str.strip()
        )


        # ----------------------------------------------------
        # NORMALIZAR CATEGORÍA
        # ----------------------------------------------------

        cursos_dashboard["categoria_curso"] = (
            cursos_dashboard["categoria_curso"]
            .astype("string")
            .str.strip()
        )


        # ----------------------------------------------------
        # ELIMINAR REGISTROS SIN ID
        # ----------------------------------------------------

        cursos_dashboard = (
            cursos_dashboard[
                cursos_dashboard[
                    "_id_postulante"
                ].notna()
            ]
        )


        # ----------------------------------------------------
        # ELIMINAR CATEGORÍAS VACÍAS
        # ----------------------------------------------------

        cursos_dashboard = (
            cursos_dashboard[
                cursos_dashboard[
                    "categoria_curso"
                ].notna()
            ]
        )


        # ----------------------------------------------------
        # ELIMINAR DUPLICADOS
        #
        # Un mismo postulante puede tener varios registros
        # en la misma categoría.
        # ----------------------------------------------------

        cursos_dashboard = (
            cursos_dashboard
            .drop_duplicates(
                subset=[
                    "_id_postulante",
                    "categoria_curso"
                ]
            )
        )


        # ----------------------------------------------------
        # GUARDAR CSV
        # ----------------------------------------------------

        RUTA_CURSOS_INTERES = (
            ROOT
            / "data"
            / "cache"
            / "cursos_interes_dashboard.csv"
        )


        cursos_dashboard.to_csv(
            RUTA_CURSOS_INTERES,
            index=False,
            encoding="utf-8-sig"
        )


        # ----------------------------------------------------
        # VALIDACIÓN
        # ----------------------------------------------------

        print(
            "\n✅ Archivo generado correctamente:"
        )

        print(
            RUTA_CURSOS_INTERES
        )

        print(
            "\nRegistros:",
            len(cursos_dashboard)
        )

        print(
            "Postulantes únicos:",
            cursos_dashboard[
                "_id_postulante"
            ].nunique()
        )

        print(
            "Categorías:",
            cursos_dashboard[
                "categoria_curso"
            ].nunique()
        )

        print(
            "\nColumnas:"
        )

        print(
            cursos_dashboard.columns.tolist()
        )

        print(
            "\nDistribución:"
        )

        print(
            cursos_dashboard[
                "categoria_curso"
            ].value_counts()
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

