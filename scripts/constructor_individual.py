# ============================================================
# CONSTRUCTOR INDIVIDUAL - LABORAL.AI
# ============================================================
#
# Genera:
#   data/cache/postulantes_individual.csv
#
# Ejecución normal:
#   python scripts/constructor_individual.py
#
# Diagnóstico:
#   python scripts/constructor_individual.py --diagnostico
#
# ============================================================

import os
import re
import json
import argparse
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

warnings.filterwarnings("ignore")


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ENV_PATH = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(
    ENV_PATH,
    override=True
)

MONGODB_URI = os.getenv(
    "MONGODB_URI"
)

MONGODB_DB = os.getenv(
    "MONGODB_DB"
)

SAMPLE_SIZE = os.getenv(
    "SAMPLE_SIZE"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "cache",
    "postulantes_individual.csv"
)


# ============================================================
# COLECCIONES
# ============================================================

COLECCIONES = [
    "users",
    "cvs",
    "educations",
    "workexperiences",
    "cvs_skills",
    "skills",
    "languages",
    "applications",
    "courseenrollments",
    "aiconversations",
    "aimessages",
    "eventguests",
    "employabilities",
    "jobcompatibilityanalyses",
    "usercredits",
    "creditoperations",
    "credits",
]


# ============================================================
# FUNCIONES GENERALES
# ============================================================

def convertir_id(valor):

    if valor is None:
        return None

    try:
        return str(valor)

    except Exception:
        return None


def limpiar_texto(valor):

    if valor is None:
        return ""

    try:

        if pd.isna(valor):
            return ""

    except Exception:
        pass

    texto = str(valor).strip()

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto


def serie_vacia(
    index,
    valor=""
):

    return pd.Series(
        valor,
        index=index
    )


def obtener_columna(
    df,
    candidatos
):

    for columna in candidatos:

        if columna in df.columns:
            return columna

    return None


def obtener_valor_row(
    row,
    candidatos
):

    for columna in candidatos:

        if columna in row.index:

            valor = row[columna]

            if limpiar_texto(valor):
                return valor

    return None


def unir_lista(
    valores,
    separador=" | "
):

    resultado = []
    vistos = set()

    for valor in valores:

        texto = limpiar_texto(
            valor
        )

        if not texto:
            continue

        clave = texto.lower()

        if clave not in vistos:

            vistos.add(
                clave
            )

            resultado.append(
                texto
            )

    return separador.join(
        resultado
    )


def lista_a_json(
    valores
):

    try:

        return json.dumps(
            valores,
            ensure_ascii=False
        )

    except Exception:

        return "[]"


def convertir_entero(
    valor
):

    if valor is None:
        return None

    try:

        if pd.isna(valor):
            return None

    except Exception:
        pass

    try:

        texto = str(
            valor
        ).strip()

        if not texto:
            return None

        return int(
            float(texto)
        )

    except Exception:

        return None


def convertir_fecha(
    valor
):

    if valor is None:
        return pd.NaT

    if isinstance(
        valor,
        pd.Timestamp
    ):
        return valor

    if isinstance(
        valor,
        datetime
    ):
        return pd.Timestamp(
            valor
        )

    try:

        if pd.isna(valor):
            return pd.NaT

    except Exception:
        pass

    texto = str(
        valor
    ).strip()

    if not texto:
        return pd.NaT

    formatos = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]

    for formato in formatos:

        try:

            return pd.Timestamp(
                datetime.strptime(
                    texto,
                    formato
                )
            )

        except Exception:
            pass

    try:

        return pd.to_datetime(
            texto,
            errors="coerce"
        )

    except Exception:

        return pd.NaT


# ============================================================
# CONEXIÓN
# ============================================================

def conectar_mongodb():

    print("\n" + "=" * 70)
    print(
        "VERIFICACIÓN DE CONFIGURACIÓN"
    )
    print("=" * 70)

    print(
        f"Ruta .env: {ENV_PATH}"
    )

    print(
        "Archivo .env encontrado: "
        f"{os.path.exists(ENV_PATH)}"
    )

    print(
        "MONGODB_URI cargada: "
        f"{'SÍ' if MONGODB_URI else 'NO'}"
    )

    print(
        "MONGODB_DB cargada: "
        f"{MONGODB_DB if MONGODB_DB else 'NO'}"
    )

    print(
        "SAMPLE_SIZE: "
        f"{SAMPLE_SIZE if SAMPLE_SIZE else 'NO'}"
    )

    if not MONGODB_URI:

        raise ValueError(
            "No se encontró MONGODB_URI en:\n"
            f"{ENV_PATH}"
        )

    if not MONGODB_DB:

        raise ValueError(
            "No se encontró MONGODB_DB en:\n"
            f"{ENV_PATH}"
        )

    print("\n" + "=" * 70)
    print(
        "CONEXIÓN A MONGODB"
    )
    print("=" * 70)

    cliente = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=15000
    )

    cliente.admin.command(
        "ping"
    )

    db = cliente[
        MONGODB_DB
    ]

    print(
        "✓ Conexión correcta"
    )

    print(
        f"✓ Base de datos: "
        f"{MONGODB_DB}"
    )

    return cliente, db


# ============================================================
# CARGA DE COLECCIONES
# ============================================================

def cargar_colecciones(
    db
):

    datos = {}

    print("\n" + "=" * 70)
    print(
        "CARGANDO COLECCIONES"
    )
    print("=" * 70)

    for nombre in COLECCIONES:

        df = pd.DataFrame()

        for intento in range(
            1,
            4
        ):

            try:

                cursor = (
                    db[nombre]
                    .find({})
                    .batch_size(500)
                )

                registros = []

                for documento in cursor:

                    registros.append(
                        documento
                    )

                if registros:

                    df = pd.DataFrame(
                        registros
                    )

                else:

                    df = pd.DataFrame()

                print(
                    f"{nombre:<32} -> "
                    f"{len(df):>6} registros"
                )

                break

            except Exception as error:

                print(
                    f"{nombre:<32} -> "
                    f"intento {intento}/3 fallido"
                )

                print(
                    f"   {error}"
                )

                if intento == 3:

                    print(
                        f"   ⚠ No se pudo cargar "
                        f"{nombre}"
                    )

                    df = pd.DataFrame()

        datos[
            nombre
        ] = df

    return datos


# ============================================================
# USERS
# ============================================================

def procesar_usuarios(
    df_users
):

    if df_users.empty:
        return pd.DataFrame()

    df = df_users.copy()

    df[
        "_id_postulante"
    ] = (
        df[
            "_id"
        ]
        .apply(convertir_id)
    )

    df[
        "nombre_completo"
    ] = (
        df.get(
            "firstName",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)

        + " "

        + df.get(
            "lastName",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    ).str.strip()

    df[
        "email"
    ] = (
        df.get(
            "email",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    df[
        "telefono"
    ] = (
        df.get(
            "phone",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    df[
        "fecha_registro"
    ] = (
        df.get(
            "createdAt",
            serie_vacia(
                df.index,
                pd.NaT
            )
        )
        .apply(convertir_fecha)
    )

    df[
        "estado_empleo"
    ] = (
        df.get(
            "employmentStatus",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    df[
        "creditos_disponibles"
    ] = pd.to_numeric(
        df.get(
            "credits",
            serie_vacia(
                df.index,
                0
            )
        ),
        errors="coerce"
    ).fillna(0)

    df[
        "linkedin"
    ] = (
        df.get(
            "linkedin",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    df[
        "linkedin_profile"
    ] = (
        df.get(
            "linkedinProfile",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    df[
        "ubicacion"
    ] = (
        df.get(
            "location",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    df[
        "modalidad"
    ] = (
        df.get(
            "modalidad",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    df[
        "disponibilidad"
    ] = (
        df.get(
            "disponibilidad",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    # --------------------------------------------------------
    # TIPO DE POSTULANTE
    # --------------------------------------------------------

    def clasificar_tipo(
        estado
    ):

        texto = (
            limpiar_texto(
                estado
            )
            .lower()
        )

        if not texto:
            return "No especificado"

        if "estudiante" in texto:
            return "Estudiante"

        if "practic" in texto:
            return "Practicante"

        if "egres" in texto:
            return "Egresado"

        if (
            "profesional" in texto
            or "trabaj" in texto
            or "empleado" in texto
        ):

            return "Profesional"

        return (
            limpiar_texto(
                estado
            )
            or "No especificado"
        )

    df[
        "tipo_postulante"
    ] = (
        df[
            "estado_empleo"
        ]
        .apply(
            clasificar_tipo
        )
    )

    columnas = [
        "_id_postulante",
        "nombre_completo",
        "email",
        "telefono",
        "fecha_registro",
        "estado_empleo",
        "tipo_postulante",
        "creditos_disponibles",
        "linkedin",
        "linkedin_profile",
        "ubicacion",
        "modalidad",
        "disponibilidad",
    ]

    return df[
        columnas
    ].copy()


# ============================================================
# CV
# ============================================================

def procesar_cvs(
    df_cvs
):

    columnas = [
        "_id_postulante",
        "_id_cv",
        "tiene_cv",
        "profesion",
        "resumen",
        "cv_nombre",
        "cv_tipo",
        "cv_paginas",
    ]

    if df_cvs.empty:

        return pd.DataFrame(
            columns=columnas
        )

    df = df_cvs.copy()

    df[
        "_id_cv"
    ] = (
        df[
            "_id"
        ]
        .apply(convertir_id)
    )

    df[
        "_id_postulante"
    ] = (
        df[
            "user"
        ]
        .apply(convertir_id)
    )

    df[
        "createdAt"
    ] = (
        df.get(
            "createdAt",
            serie_vacia(
                df.index,
                pd.NaT
            )
        )
        .apply(convertir_fecha)
    )

    if "isMain" in df.columns:

        df[
            "_es_principal"
        ] = (
            df[
                "isMain"
            ]
            .fillna(False)
            .astype(bool)
            .astype(int)
        )

    else:

        df[
            "_es_principal"
        ] = 0

    df = df.sort_values(
        [
            "_id_postulante",
            "_es_principal",
            "createdAt",
        ],
        ascending=[
            True,
            False,
            False,
        ]
    )

    df = df.drop_duplicates(
        subset="_id_postulante",
        keep="first"
    )

    resultado = pd.DataFrame(
        index=df.index
    )

    resultado[
        "_id_postulante"
    ] = df[
        "_id_postulante"
    ]

    resultado[
        "_id_cv"
    ] = df[
        "_id_cv"
    ]

    resultado[
        "tiene_cv"
    ] = True

    resultado[
        "profesion"
    ] = (
        df.get(
            "profession",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    resultado[
        "resumen"
    ] = (
        df.get(
            "summary",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    resultado[
        "cv_nombre"
    ] = (
        df.get(
            "name",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    resultado[
        "cv_tipo"
    ] = (
        df.get(
            "cvType",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    resultado[
        "cv_paginas"
    ] = pd.to_numeric(
        df.get(
            "pageCount",
            serie_vacia(
                df.index,
                0
            )
        ),
        errors="coerce"
    ).fillna(0)

    return resultado.reset_index(
        drop=True
    )


# ============================================================
# EDUCACIÓN
# ============================================================

def procesar_educacion(
    df_educations,
    df_cvs
):

    columnas = [
        "_id_postulante",
        "cantidad_formaciones",
        "formaciones_detalle",
        "nivel_educativo",
        "instituciones",
    ]

    if (
        df_educations.empty
        or df_cvs.empty
    ):

        return pd.DataFrame(
            columns=columnas
        )

    cvs = df_cvs[
        [
            "_id",
            "user",
        ]
    ].copy()

    cvs[
        "_id_cv"
    ] = (
        cvs[
            "_id"
        ]
        .apply(convertir_id)
    )

    cvs[
        "_id_postulante"
    ] = (
        cvs[
            "user"
        ]
        .apply(convertir_id)
    )

    educ = (
        df_educations.copy()
    )

    educ[
        "_id_cv"
    ] = (
        educ[
            "cv"
        ]
        .apply(convertir_id)
    )

    educ = educ.merge(
        cvs[
            [
                "_id_cv",
                "_id_postulante",
            ]
        ],
        on="_id_cv",
        how="left"
    )

    educ = educ[
        educ[
            "_id_postulante"
        ].notna()
    ].copy()

    registros = []

    for (
        user_id,
        grupo
    ) in educ.groupby(
        "_id_postulante"
    ):

        detalles = []
        niveles = []
        instituciones = []

        for _, fila in grupo.iterrows():

            escuela = limpiar_texto(
                fila.get(
                    "school",
                    ""
                )
            )

            grado = limpiar_texto(
                fila.get(
                    "degree",
                    ""
                )
            )

            tipo = limpiar_texto(
                fila.get(
                    "type",
                    ""
                )
            )

            inicio = limpiar_texto(
                fila.get(
                    "startYear",
                    ""
                )
            )

            fin = limpiar_texto(
                fila.get(
                    "endYear",
                    ""
                )
            )

            en_curso = bool(
                fila.get(
                    "inProgress",
                    False
                )
            )

            if en_curso:

                periodo = (
                    f"{inicio} - En curso"
                    if inicio
                    else "En curso"
                )

            elif inicio or fin:

                periodo = (
                    f"{inicio} - {fin}"
                    if inicio and fin
                    else inicio or fin
                )

            else:

                periodo = ""

            detalle = " | ".join(
                p
                for p in [
                    escuela,
                    grado,
                    tipo,
                    periodo,
                ]
                if p
            )

            if detalle:
                detalles.append(
                    detalle
                )

            if grado:
                niveles.append(
                    grado
                )

            if escuela:
                instituciones.append(
                    escuela
                )

        registros.append(
            {
                "_id_postulante": user_id,
                "cantidad_formaciones": len(
                    grupo
                ),
                "formaciones_detalle": unir_lista(
                    detalles
                ),
                "nivel_educativo": unir_lista(
                    niveles
                ),
                "instituciones": unir_lista(
                    instituciones
                ),
            }
        )

    return pd.DataFrame(
        registros
    )


# ============================================================
# EXPERIENCIA
# ============================================================

def construir_fecha_mes(
    year,
    month,
    default_month=1
):

    year = convertir_entero(
        year
    )

    month = convertir_entero(
        month
    )

    if year is None:
        return None

    if month is None:
        month = default_month

    if (
        month < 1
        or month > 12
    ):

        month = default_month

    try:

        return pd.Timestamp(
            year=year,
            month=month,
            day=1
        )

    except Exception:

        return None


def obtener_fecha_inicio_experiencia(
    fila
):

    inicio = construir_fecha_mes(
        fila.get(
            "startYear"
        ),
        fila.get(
            "startMonth"
        ),
        default_month=1
    )

    if inicio is not None:
        return inicio

    fecha = convertir_fecha(
        fila.get(
            "startDate"
        )
    )

    if not pd.isna(
        fecha
    ):

        return pd.Timestamp(
            year=fecha.year,
            month=fecha.month,
            day=1
        )

    return None


def obtener_fecha_fin_experiencia(
    fila,
    fecha_actual
):

    en_curso = bool(
        fila.get(
            "inProgress",
            False
        )
    )

    if en_curso:

        return pd.Timestamp(
            year=fecha_actual.year,
            month=fecha_actual.month,
            day=1
        )

    fin = construir_fecha_mes(
        fila.get(
            "endYear"
        ),
        fila.get(
            "endMonth"
        ),
        default_month=12
    )

    if fin is not None:
        return fin

    fecha = convertir_fecha(
        fila.get(
            "endDate"
        )
    )

    if not pd.isna(
        fecha
    ):

        return pd.Timestamp(
            year=fecha.year,
            month=fecha.month,
            day=1
        )

    return None


def calcular_meses_experiencia(
    grupo
):

    intervalos = []

    fecha_actual = (
        pd.Timestamp.now()
        .normalize()
    )

    for _, fila in grupo.iterrows():

        inicio = (
            obtener_fecha_inicio_experiencia(
                fila
            )
        )

        fin = (
            obtener_fecha_fin_experiencia(
                fila,
                fecha_actual
            )
        )

        if inicio is None:
            continue

        if fin is None:
            continue

        if fin < inicio:
            continue

        intervalos.append(
            (
                inicio,
                fin
            )
        )

    if not intervalos:
        return 0

    intervalos.sort(
        key=lambda x: x[0]
    )

    unidos = []

    inicio_actual, fin_actual = (
        intervalos[0]
    )

    for inicio, fin in intervalos[1:]:

        if inicio <= fin_actual:

            if fin > fin_actual:
                fin_actual = fin

        else:

            unidos.append(
                (
                    inicio_actual,
                    fin_actual
                )
            )

            inicio_actual = inicio
            fin_actual = fin

    unidos.append(
        (
            inicio_actual,
            fin_actual
        )
    )

    meses_totales = 0

    for inicio, fin in unidos:

        meses_totales += (
            (
                fin.year
                - inicio.year
            )
            * 12
            + (
                fin.month
                - inicio.month
            )
            + 1
        )

    return int(
        meses_totales
    )


def formatear_experiencia(
    meses
):

    meses = (
        convertir_entero(
            meses
        )
        or 0
    )

    if meses <= 0:
        return "Sin experiencia"

    años = (
        meses // 12
    )

    meses_restantes = (
        meses % 12
    )

    partes = []

    if años > 0:

        if años == 1:
            partes.append(
                "1 año"
            )

        else:
            partes.append(
                f"{años} años"
            )

    if meses_restantes > 0:

        if meses_restantes == 1:
            partes.append(
                "1 mes"
            )

        else:
            partes.append(
                f"{meses_restantes} meses"
            )

    return " y ".join(
        partes
    )


def clasificar_experiencia(
    meses
):

    meses = (
        convertir_entero(
            meses
        )
        or 0
    )

    if meses <= 0:
        return "Sin experiencia"

    if meses < 12:
        return "Menos de 1 año"

    if meses < 36:
        return "1 a 3 años"

    if meses < 60:
        return "3 a 5 años"

    return "Más de 5 años"


def procesar_experiencia(
    df_work,
    df_cvs
):

    columnas = [
        "_id_postulante",
        "cantidad_experiencias",
        "meses_experiencia",
        "años_experiencia",
        "experiencia_formato",
        "experiencia_tipo",
        "experiencia_detalle",
    ]

    if (
        df_work.empty
        or df_cvs.empty
    ):

        return pd.DataFrame(
            columns=columnas
        )

    cvs = df_cvs[
        [
            "_id",
            "user",
        ]
    ].copy()

    cvs[
        "_id_cv"
    ] = (
        cvs[
            "_id"
        ]
        .apply(convertir_id)
    )

    cvs[
        "_id_postulante"
    ] = (
        cvs[
            "user"
        ]
        .apply(convertir_id)
    )

    work = (
        df_work.copy()
    )

    work[
        "_id_cv"
    ] = (
        work[
            "cv"
        ]
        .apply(convertir_id)
    )

    work = work.merge(
        cvs[
            [
                "_id_cv",
                "_id_postulante",
            ]
        ],
        on="_id_cv",
        how="left"
    )

    work = work[
        work[
            "_id_postulante"
        ].notna()
    ].copy()

    registros = []

    for (
        user_id,
        grupo
    ) in work.groupby(
        "_id_postulante"
    ):

        detalles = []
        tipos = []

        for _, fila in grupo.iterrows():

            empresa = limpiar_texto(
                fila.get(
                    "company",
                    ""
                )
            )

            cargo = limpiar_texto(
                fila.get(
                    "position",
                    ""
                )
            )

            tipo = limpiar_texto(
                fila.get(
                    "type",
                    ""
                )
            )

            inicio = limpiar_texto(
                fila.get(
                    "startYear",
                    ""
                )
            )

            fin = limpiar_texto(
                fila.get(
                    "endYear",
                    ""
                )
            )

            en_curso = bool(
                fila.get(
                    "inProgress",
                    False
                )
            )

            if en_curso:

                periodo = (
                    f"{inicio} - En curso"
                    if inicio
                    else "En curso"
                )

            elif inicio or fin:

                periodo = (
                    f"{inicio} - {fin}"
                    if inicio and fin
                    else inicio or fin
                )

            else:

                fecha_inicio = convertir_fecha(
                    fila.get(
                        "startDate"
                    )
                )

                fecha_fin = convertir_fecha(
                    fila.get(
                        "endDate"
                    )
                )

                año_inicio = ""
                año_fin = ""

                if not pd.isna(
                    fecha_inicio
                ):

                    año_inicio = str(
                        fecha_inicio.year
                    )

                if not pd.isna(
                    fecha_fin
                ):

                    año_fin = str(
                        fecha_fin.year
                    )

                if año_inicio or año_fin:

                    periodo = (
                        f"{año_inicio} - {año_fin}"
                        if año_inicio
                        and año_fin
                        else (
                            año_inicio
                            or año_fin
                        )
                    )

                else:

                    periodo = ""

            detalle = " | ".join(
                p
                for p in [
                    empresa,
                    cargo,
                    tipo,
                    periodo,
                ]
                if p
            )

            if detalle:

                detalles.append(
                    detalle
                )

            if tipo:

                tipos.append(
                    tipo
                )

        meses = (
            calcular_meses_experiencia(
                grupo
            )
        )

        años = round(
            meses / 12,
            2
        )

        registros.append(
            {
                "_id_postulante": user_id,
                "cantidad_experiencias": len(
                    grupo
                ),
                "meses_experiencia": meses,
                "años_experiencia": años,
                "experiencia_formato": (
                    formatear_experiencia(
                        meses
                    )
                ),
                "experiencia_tipo": (
                    unir_lista(
                        tipos
                    )
                    if tipos
                    else clasificar_experiencia(
                        meses
                    )
                ),
                "experiencia_detalle": unir_lista(
                    detalles
                ),
            }
        )

    return pd.DataFrame(
        registros
    )


# ============================================================
# HABILIDADES
# ============================================================

def detectar_tipo_habilidad(
    valor
):

    texto = (
        limpiar_texto(
            valor
        )
        .lower()
    )

    if not texto:
        return "No especificada"

    hard_keywords = [
        "hard",
        "technical",
        "técnica",
        "tecnica",
        "technical skill",
        "technical skills",
        "hard skill",
        "hard skills",
    ]

    soft_keywords = [
        "soft",
        "behavioral",
        "interpersonal",
        "blanda",
        "habilidad blanda",
        "soft skill",
        "soft skills",
    ]

    if any(
        palabra in texto
        for palabra in hard_keywords
    ):

        return "Hard"

    if any(
        palabra in texto
        for palabra in soft_keywords
    ):

        return "Soft"

    return "No especificada"


def procesar_habilidades(
    df_cvs_skills,
    df_skills,
    df_cvs
):

    columnas = [
        "_id_postulante",
        "cantidad_habilidades",
        "cantidad_hard_skills",
        "cantidad_soft_skills",
        "hard_skills_detalle",
        "soft_skills_detalle",
        "habilidades_detalle",
        "habilidades_no_especificadas",
    ]

    if (
        df_cvs_skills.empty
        or df_skills.empty
        or df_cvs.empty
    ):

        return pd.DataFrame(
            columns=columnas
        )

    relaciones = (
        df_cvs_skills.copy()
    )

    habilidades = (
        df_skills.copy()
    )

    cvs = df_cvs[
        [
            "_id",
            "user",
        ]
    ].copy()

    relaciones[
        "_id_cvs"
    ] = (
        relaciones[
            "id_cvs"
        ]
        .apply(convertir_id)
    )

    relaciones[
        "_id_skills"
    ] = (
        relaciones[
            "id_skills"
        ]
        .apply(convertir_id)
    )

    habilidades[
        "_id_skills"
    ] = (
        habilidades[
            "_id"
        ]
        .apply(convertir_id)
    )

    cvs[
        "_id_cvs"
    ] = (
        cvs[
            "_id"
        ]
        .apply(convertir_id)
    )

    cvs[
        "_id_postulante"
    ] = (
        cvs[
            "user"
        ]
        .apply(convertir_id)
    )

    relaciones = relaciones.merge(
        cvs[
            [
                "_id_cvs",
                "_id_postulante",
            ]
        ],
        on="_id_cvs",
        how="left"
    )

    relaciones = relaciones.merge(
        habilidades,
        on="_id_skills",
        how="left",
        suffixes=(
            "",
            "_skill"
        )
    )

    relaciones = relaciones[
        relaciones[
            "_id_postulante"
        ].notna()
    ].copy()

    candidatos_nombre = [
        "name",
        "nombre",
        "skillName",
        "skill_name",
        "title",
        "label",
    ]

    candidatos_tipo = [
        "type",
        "skillType",
        "skill_type",
        "category",
        "categoryName",
        "categoria",
        "kind",
        "tipo",
    ]

    relaciones[
        "habilidad_nombre"
    ] = relaciones.apply(
        lambda row:
        limpiar_texto(
            obtener_valor_row(
                row,
                candidatos_nombre
            )
        ),
        axis=1
    )

    relaciones[
        "habilidad_tipo"
    ] = relaciones.apply(
        lambda row:
        detectar_tipo_habilidad(
            obtener_valor_row(
                row,
                candidatos_tipo
            )
        ),
        axis=1
    )

    registros = []

    for (
        user_id,
        grupo
    ) in relaciones.groupby(
        "_id_postulante"
    ):

        hard = []
        soft = []
        otros = []
        todas = []

        for _, fila in grupo.iterrows():

            nombre = limpiar_texto(
                fila[
                    "habilidad_nombre"
                ]
            )

            tipo = fila[
                "habilidad_tipo"
            ]

            if not nombre:
                continue

            if nombre not in todas:

                todas.append(
                    nombre
                )

            if tipo == "Hard":

                if nombre not in hard:
                    hard.append(
                        nombre
                    )

            elif tipo == "Soft":

                if nombre not in soft:
                    soft.append(
                        nombre
                    )

            else:

                if nombre not in otros:
                    otros.append(
                        nombre
                    )

        registros.append(
            {
                "_id_postulante": user_id,
                "cantidad_habilidades": len(
                    todas
                ),
                "cantidad_hard_skills": len(
                    hard
                ),
                "cantidad_soft_skills": len(
                    soft
                ),
                "hard_skills_detalle": unir_lista(
                    hard
                ),
                "soft_skills_detalle": unir_lista(
                    soft
                ),
                "habilidades_detalle": unir_lista(
                    todas
                ),
                "habilidades_no_especificadas": unir_lista(
                    otros
                ),
            }
        )

    return pd.DataFrame(
        registros
    )


# ============================================================
# IDIOMAS
# ============================================================

def procesar_idiomas(
    df_languages
):

    columnas = [
        "_id_postulante",
        "cantidad_idiomas",
        "idiomas_detalle",
    ]

    if df_languages.empty:

        return pd.DataFrame(
            columns=columnas
        )

    if "user" not in df_languages.columns:

        return pd.DataFrame(
            columns=columnas
        )

    df = (
        df_languages.copy()
    )

    df[
        "_id_postulante"
    ] = (
        df[
            "user"
        ]
        .apply(convertir_id)
    )

    registros = []

    for (
        user_id,
        grupo
    ) in df.groupby(
        "_id_postulante"
    ):

        idiomas = []

        for _, fila in grupo.iterrows():

            idioma = limpiar_texto(
                fila.get(
                    "language",
                    ""
                )
            )

            nivel = limpiar_texto(
                fila.get(
                    "level",
                    ""
                )
            )

            if not idioma:
                continue

            nombre = (
                f"{idioma} ({nivel})"
                if nivel
                else idioma
            )

            if nombre not in idiomas:

                idiomas.append(
                    nombre
                )

        registros.append(
            {
                "_id_postulante": user_id,
                "cantidad_idiomas": len(
                    idiomas
                ),
                "idiomas_detalle": unir_lista(
                    idiomas
                ),
            }
        )

    return pd.DataFrame(
        registros
    )


# ============================================================
# POSTULACIONES
# ============================================================

def procesar_postulaciones(
    df_applications
):

    columnas = [
        "_id_postulante",
        "cantidad_postulaciones",
        "postulaciones_pendientes",
        "postulaciones_revision",
        "postulaciones_aceptadas",
        "postulaciones_rechazadas",
        "postulaciones_estado_detalle",
    ]

    if df_applications.empty:

        return pd.DataFrame(
            columns=columnas
        )

    df = (
        df_applications.copy()
    )

    columna_usuario = obtener_columna(
        df,
        [
            "user",
            "userId",
            "user_id",
            "applicant",
        ]
    )

    if columna_usuario is None:

        return pd.DataFrame(
            columns=columnas
        )

    df[
        "_id_postulante"
    ] = (
        df[
            columna_usuario
        ]
        .apply(convertir_id)
    )

    df[
        "estado"
    ] = (
        df.get(
            "applicationStatus",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
        .str.lower()
    )

    registros = []

    for (
        user_id,
        grupo
    ) in df.groupby(
        "_id_postulante"
    ):

        estados = grupo[
            "estado"
        ]

        pendientes = (
            estados.str.contains(
                "pending|pendiente",
                regex=True
            )
            .sum()
        )

        revision = (
            estados.str.contains(
                "review|revisi|process|proceso",
                regex=True
            )
            .sum()
        )

        aceptadas = (
            estados.str.contains(
                "accept|acept|hired|contrat",
                regex=True
            )
            .sum()
        )

        rechazadas = (
            estados.str.contains(
                "reject|rechaz",
                regex=True
            )
            .sum()
        )

        detalle = []

        for (
            estado,
            cantidad
        ) in (
            estados
            .value_counts()
            .items()
        ):

            if estado:

                detalle.append(
                    f"{estado}: {cantidad}"
                )

        registros.append(
            {
                "_id_postulante": user_id,
                "cantidad_postulaciones": len(
                    grupo
                ),
                "postulaciones_pendientes": int(
                    pendientes
                ),
                "postulaciones_revision": int(
                    revision
                ),
                "postulaciones_aceptadas": int(
                    aceptadas
                ),
                "postulaciones_rechazadas": int(
                    rechazadas
                ),
                "postulaciones_estado_detalle": unir_lista(
                    detalle
                ),
            }
        )

    return pd.DataFrame(
        registros
    )


# ============================================================
# CURSOS
# ============================================================

def procesar_cursos(
    df_courseenrollments
):

    columnas = [
        "_id_postulante",
        "cantidad_cursos",
    ]

    if df_courseenrollments.empty:

        return pd.DataFrame(
            columns=columnas
        )

    df = (
        df_courseenrollments.copy()
    )

    columna_usuario = obtener_columna(
        df,
        [
            "user",
            "userId",
            "user_id",
        ]
    )

    if columna_usuario is None:

        return pd.DataFrame(
            columns=columnas
        )

    df[
        "_id_postulante"
    ] = (
        df[
            columna_usuario
        ]
        .apply(convertir_id)
    )

    return (
        df[
            df[
                "_id_postulante"
            ].notna()
        ]
        .groupby(
            "_id_postulante"
        )
        .size()
        .reset_index(
            name="cantidad_cursos"
        )
    )


# ============================================================
# IA
# ============================================================

def procesar_ia(
    df_conversations,
    df_messages
):

    columnas = [
        "_id_postulante",
        "cantidad_conversaciones",
        "cantidad_mensajes_ia",
        "uso_ia",
    ]

    resultados = {}

    # --------------------------------------------------------
    # CONVERSACIONES
    # --------------------------------------------------------

    if not df_conversations.empty:

        conv = (
            df_conversations.copy()
        )

        columna_usuario = obtener_columna(
            conv,
            [
                "user",
                "userId",
                "user_id",
            ]
        )

        if columna_usuario:

            conv[
                "_id_postulante"
            ] = (
                conv[
                    columna_usuario
                ]
                .apply(convertir_id)
            )

            conv = conv[
                conv[
                    "_id_postulante"
                ].notna()
            ]

            for (
                user_id,
                grupo
            ) in conv.groupby(
                "_id_postulante"
            ):

                resultados.setdefault(
                    user_id,
                    {}
                )

                resultados[
                    user_id
                ][
                    "cantidad_conversaciones"
                ] = len(
                    grupo
                )

    # --------------------------------------------------------
    # MENSAJES
    # --------------------------------------------------------

    if not df_messages.empty:

        msg = (
            df_messages.copy()
        )

        columna_usuario = obtener_columna(
            msg,
            [
                "user",
                "userId",
                "user_id",
            ]
        )

        if columna_usuario:

            msg[
                "_id_postulante"
            ] = (
                msg[
                    columna_usuario
                ]
                .apply(convertir_id)
            )

            msg = msg[
                msg[
                    "_id_postulante"
                ].notna()
            ]

            for (
                user_id,
                grupo
            ) in msg.groupby(
                "_id_postulante"
            ):

                resultados.setdefault(
                    user_id,
                    {}
                )

                resultados[
                    user_id
                ][
                    "cantidad_mensajes_ia"
                ] = len(
                    grupo
                )

    if not resultados:

        return pd.DataFrame(
            columns=columnas
        )

    registros = []

    for (
        user_id,
        valores
    ) in resultados.items():

        conversaciones = valores.get(
            "cantidad_conversaciones",
            0
        )

        mensajes = valores.get(
            "cantidad_mensajes_ia",
            0
        )

        registros.append(
            {
                "_id_postulante": user_id,
                "cantidad_conversaciones": conversaciones,
                "cantidad_mensajes_ia": mensajes,
                "uso_ia": (
                    conversaciones > 0
                    or mensajes > 0
                ),
            }
        )

    return pd.DataFrame(
        registros
    )


# ============================================================
# EVENTOS
# ============================================================

def procesar_eventos(
    df_eventguests,
    df_users
):
    """
    eventguests no tiene userId.

    Relación:

        eventguests.userEmail
                ↓
        users.email
                ↓
        users._id
    """

    columnas = [
        "_id_postulante",
        "cantidad_eventos",
        "participo_evento",
    ]

    if (
        df_eventguests.empty
        or df_users.empty
    ):

        return pd.DataFrame(
            columns=columnas
        )

    if "userEmail" not in df_eventguests.columns:

        print(
            "\n⚠ eventguests no contiene userEmail."
        )

        return pd.DataFrame(
            columns=columnas
        )

    if "email" not in df_users.columns:

        print(
            "\n⚠ users no contiene email."
        )

        return pd.DataFrame(
            columns=columnas
        )

    eventos = (
        df_eventguests.copy()
    )

    eventos[
        "_email"
    ] = (
        eventos[
            "userEmail"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    eventos = eventos[
        eventos[
            "_email"
        ] != ""
    ].copy()

    usuarios = (
        df_users.copy()
    )

    usuarios[
        "_email"
    ] = (
        usuarios[
            "email"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    usuarios[
        "_id_postulante"
    ] = (
        usuarios[
            "_id"
        ]
        .apply(convertir_id)
    )

    usuarios_email = (
        usuarios[
            [
                "_email",
                "_id_postulante",
            ]
        ]
        .drop_duplicates(
            subset="_email",
            keep="first"
        )
    )

    eventos = eventos.merge(
        usuarios_email,
        on="_email",
        how="inner"
    )

    if eventos.empty:

        print(
            "\n⚠ No hubo coincidencias "
            "entre eventguests.userEmail "
            "y users.email."
        )

        return pd.DataFrame(
            columns=columnas
        )

    resultado = (
        eventos
        .groupby(
            "_id_postulante"
        )
        .size()
        .reset_index(
            name="cantidad_eventos"
        )
    )

    resultado[
        "participo_evento"
    ] = True

    print(
        "Campo utilizado: "
        "eventguests.userEmail → users.email"
    )

    print(
        "Registros de eventos relacionados: "
        f"{len(eventos)}"
    )

    print(
        "Usuarios con eventos: "
        f"{len(resultado)}"
    )

    return resultado


# ============================================================
# EMPLEABILIDAD
# ============================================================

def procesar_empleabilidad(
    df_employabilities
):

    columnas = [
        "_id_postulante",
        "nivel_empleabilidad",
        "score_empleabilidad",
        "rol_sugerido",
        "fortalezas_empleabilidad",
        "debilidades_empleabilidad",
        "mejoras_empleabilidad",
    ]

    if df_employabilities.empty:

        return pd.DataFrame(
            columns=columnas
        )

    df = (
        df_employabilities.copy()
    )

    columna_usuario = obtener_columna(
        df,
        [
            "user",
            "userId",
            "user_id",
        ]
    )

    if columna_usuario is None:

        return pd.DataFrame(
            columns=columnas
        )

    df[
        "_id_postulante"
    ] = (
        df[
            columna_usuario
        ]
        .apply(convertir_id)
    )

    df[
        "_fecha_eval"
    ] = (
        df.get(
            "createdAt",
            serie_vacia(
                df.index,
                pd.NaT
            )
        )
        .apply(convertir_fecha)
    )

    df = df.sort_values(
        "_fecha_eval",
        ascending=False
    )

    df = df.drop_duplicates(
        "_id_postulante",
        keep="first"
    )

    resultado = pd.DataFrame(
        index=df.index
    )

    resultado[
        "_id_postulante"
    ] = df[
        "_id_postulante"
    ]

    resultado[
        "nivel_empleabilidad"
    ] = (
        df.get(
            "level",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    resultado[
        "score_empleabilidad"
    ] = pd.to_numeric(
        df.get(
            "score",
            serie_vacia(
                df.index,
                0
            )
        ),
        errors="coerce"
    ).fillna(0)

    resultado[
        "rol_sugerido"
    ] = (
        df.get(
            "suggested_role",
            serie_vacia(
                df.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
    )

    resultado[
        "fortalezas_empleabilidad"
    ] = (
        df.get(
            "strengths",
            serie_vacia(
                df.index
            )
        )
        .apply(limpiar_texto)
    )

    resultado[
        "debilidades_empleabilidad"
    ] = (
        df.get(
            "weaknesses",
            serie_vacia(
                df.index
            )
        )
        .apply(limpiar_texto)
    )

    resultado[
        "mejoras_empleabilidad"
    ] = (
        df.get(
            "improvements",
            serie_vacia(
                df.index
            )
        )
        .apply(limpiar_texto)
    )

    return resultado.reset_index(
        drop=True
    )


# ============================================================
# COMPATIBILIDAD
# ============================================================

def procesar_compatibilidad(
    df_jobcompatibilityanalyses,
    df_cvs
):
    """
    Relación correcta:

        jobcompatibilityanalyses.cvId
                    ↓
                 cvs._id
                    ↓
                 cvs.user
                    ↓
              users._id

    Genera por postulante:

        cantidad_analisis_compatibilidad
        score_compatibilidad_promedio
        ultimo_score_compatibilidad
        ultimo_nivel_compatibilidad
    """

    columnas = [
        "_id_postulante",
        "cantidad_analisis_compatibilidad",
        "score_compatibilidad_promedio",
        "ultimo_score_compatibilidad",
        "ultimo_nivel_compatibilidad",
    ]

    if (
        df_jobcompatibilityanalyses.empty
        or df_cvs.empty
    ):

        print(
            "\n⚠ No hay datos suficientes "
            "para procesar compatibilidades."
        )

        return pd.DataFrame(
            columns=columnas
        )

    compat = (
        df_jobcompatibilityanalyses.copy()
    )

    cvs = (
        df_cvs.copy()
    )

    # --------------------------------------------------------
    # VALIDAR COLUMNAS
    # --------------------------------------------------------

    if "cvId" not in compat.columns:

        print(
            "\n⚠ jobcompatibilityanalyses "
            "no contiene cvId."
        )

        print(
            "Columnas encontradas:"
        )

        print(
            list(
                compat.columns
            )
        )

        return pd.DataFrame(
            columns=columnas
        )

    if "_id" not in cvs.columns:

        print(
            "\n⚠ cvs no contiene _id."
        )

        return pd.DataFrame(
            columns=columnas
        )

    if "user" not in cvs.columns:

        print(
            "\n⚠ cvs no contiene user."
        )

        return pd.DataFrame(
            columns=columnas
        )

    # --------------------------------------------------------
    # NORMALIZAR IDS
    # --------------------------------------------------------

    compat[
        "_id_cv"
    ] = (
        compat[
            "cvId"
        ]
        .apply(convertir_id)
    )

    cvs[
        "_id_cv"
    ] = (
        cvs[
            "_id"
        ]
        .apply(convertir_id)
    )

    cvs[
        "_id_postulante"
    ] = (
        cvs[
            "user"
        ]
        .apply(convertir_id)
    )

    # --------------------------------------------------------
    # MAPA CV -> USUARIO
    # --------------------------------------------------------

    mapa_cv_usuario = (
        cvs[
            [
                "_id_cv",
                "_id_postulante",
            ]
        ]
        .dropna(
            subset=[
                "_id_cv",
                "_id_postulante",
            ]
        )
        .drop_duplicates(
            subset="_id_cv",
            keep="first"
        )
    )

    # --------------------------------------------------------
    # UNIR COMPATIBILIDAD CON CV
    # --------------------------------------------------------

    compat = compat.merge(
        mapa_cv_usuario,
        on="_id_cv",
        how="left"
    )

    # --------------------------------------------------------
    # MOSTRAR RELACIÓN EN CONSOLA
    # --------------------------------------------------------

    total_analisis = len(
        compat
    )

    analisis_con_usuario = int(
        compat[
            "_id_postulante"
        ]
        .notna()
        .sum()
    )

    print(
        "\njobcompatibilityanalyses → cvs → users"
    )

    print(
        "Análisis encontrados: "
        f"{total_analisis}"
    )

    print(
        "Análisis relacionados con usuario: "
        f"{analisis_con_usuario}"
    )

    # --------------------------------------------------------
    # ELIMINAR SIN USUARIO
    # --------------------------------------------------------

    compat = compat[
        compat[
            "_id_postulante"
        ].notna()
    ].copy()

    if compat.empty:

        print(
            "⚠ No se pudo relacionar "
            "ningún análisis con un postulante."
        )

        return pd.DataFrame(
            columns=columnas
        )

    # --------------------------------------------------------
    # FECHA
    # --------------------------------------------------------

    columna_fecha = obtener_columna(
        compat,
        [
            "createdAt",
            "updatedAt",
            "created_at",
            "updated_at",
        ]
    )

    if columna_fecha:

        compat[
            "_fecha"
        ] = (
            compat[
                columna_fecha
            ]
            .apply(convertir_fecha)
        )

    else:

        compat[
            "_fecha"
        ] = pd.NaT

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    columna_score = obtener_columna(
        compat,
        [
            "compatibilityPercentage",
            "compatibility_percentage",
            "compatibilityScore",
            "compatibility_score",
            "score",
        ]
    )

    if columna_score:

        compat[
            "_score"
        ] = pd.to_numeric(
            compat[
                columna_score
            ],
            errors="coerce"
        )

    else:

        compat[
            "_score"
        ] = np.nan

        print(
            "⚠ No se encontró columna "
            "de score de compatibilidad."
        )

    # --------------------------------------------------------
    # NIVEL
    # --------------------------------------------------------

    columna_nivel = obtener_columna(
        compat,
        [
            "compatibilityLevel",
            "compatibility_level",
            "level",
        ]
    )

    if columna_nivel:

        compat[
            "_nivel"
        ] = (
            compat[
                columna_nivel
            ]
            .fillna("")
            .apply(limpiar_texto)
        )

    else:

        compat[
            "_nivel"
        ] = ""

    # --------------------------------------------------------
    # ORDENAR
    # --------------------------------------------------------

    if columna_fecha:

        compat = compat.sort_values(
            [
                "_id_postulante",
                "_fecha",
            ],
            ascending=[
                True,
                True,
            ],
            na_position="first"
        )

    # --------------------------------------------------------
    # AGRUPAR
    # --------------------------------------------------------

    registros = []

    for (
        user_id,
        grupo
    ) in compat.groupby(
        "_id_postulante"
    ):

        cantidad = int(
            len(
                grupo
            )
        )

        scores = (
            grupo[
                "_score"
            ]
            .dropna()
        )

        if not scores.empty:

            promedio = float(
                scores.mean()
            )

            ultimo_score = float(
                grupo[
                    "_score"
                ]
                .dropna()
                .iloc[-1]
            )

        else:

            promedio = 0.0
            ultimo_score = 0.0

        niveles = (
            grupo[
                "_nivel"
            ]
            .dropna()
        )

        niveles = [
            limpiar_texto(
                nivel
            )
            for nivel in niveles
            if limpiar_texto(
                nivel
            )
        ]

        ultimo_nivel = (
            niveles[-1]
            if niveles
            else "No disponible"
        )

        registros.append(
            {
                "_id_postulante": user_id,
                "cantidad_analisis_compatibilidad": cantidad,
                "score_compatibilidad_promedio": round(
                    promedio,
                    2
                ),
                "ultimo_score_compatibilidad": round(
                    ultimo_score,
                    2
                ),
                "ultimo_nivel_compatibilidad": (
                    ultimo_nivel
                ),
            }
        )

    resultado = pd.DataFrame(
        registros
    )

    print(
        "Usuarios con compatibilidad: "
        f"{len(resultado)}"
    )

    if not resultado.empty:

        print(
            "Total de análisis contabilizados: "
            f"{int(resultado['cantidad_analisis_compatibilidad'].sum())}"
        )

    return resultado


# ============================================================
# CATÁLOGO DE CRÉDITOS
# ============================================================

def preparar_catalogo_creditos(
    df_credits
):

    columnas = [
        "event",
        "nombre_credito",
        "costo_creditos",
    ]

    if df_credits.empty:

        return pd.DataFrame(
            columns=columnas
        )

    df = (
        df_credits.copy()
    )

    evento_columna = obtener_columna(
        df,
        [
            "event",
            "eventName",
        ]
    )

    if evento_columna is None:

        return pd.DataFrame(
            columns=columnas
        )

    df[
        "event"
    ] = (
        df[
            evento_columna
        ]
        .fillna("")
        .apply(limpiar_texto)
    )

    if "name" in df.columns:

        df[
            "nombre_credito"
        ] = (
            df[
                "name"
            ]
            .fillna("")
            .apply(limpiar_texto)
        )

    else:

        df[
            "nombre_credito"
        ] = df[
            "event"
        ]

    if "multiplier" in df.columns:

        df[
            "costo_creditos"
        ] = pd.to_numeric(
            df[
                "multiplier"
            ],
            errors="coerce"
        )

    else:

        df[
            "costo_creditos"
        ] = np.nan

    if "version" in df.columns:

        df[
            "_version_num"
        ] = pd.to_numeric(
            df[
                "version"
            ],
            errors="coerce"
        )

        df = df.sort_values(
            "_version_num",
            ascending=False
        )

    df = df.drop_duplicates(
        "event",
        keep="first"
    )

    return df[
        columnas
    ].copy()


# ============================================================
# CRÉDITOS
# ============================================================

def procesar_creditos(
    df_users,
    df_creditoperations,
    df_credits
):

    columnas = [
        "_id_postulante",
        "creditos_disponibles",
        "creditos_utilizados",
        "cantidad_operaciones_creditos",
        "ultima_operacion_creditos",
        "funcionalidad_mas_usada",
        "creditos_funcionalidad_mas_usada",
        "uso_creditos_detalle",
    ]

    if df_users.empty:

        return pd.DataFrame(
            columns=columnas
        )

    usuarios = (
        df_users.copy()
    )

    usuarios[
        "_id_postulante"
    ] = (
        usuarios[
            "_id"
        ]
        .apply(convertir_id)
    )

    usuarios[
        "creditos_disponibles"
    ] = pd.to_numeric(
        usuarios.get(
            "credits",
            serie_vacia(
                usuarios.index,
                0
            )
        ),
        errors="coerce"
    ).fillna(0)

    disponibles = usuarios[
        [
            "_id_postulante",
            "creditos_disponibles",
        ]
    ].copy()

    # --------------------------------------------------------
    # SIN OPERACIONES
    # --------------------------------------------------------

    if df_creditoperations.empty:

        disponibles[
            "creditos_utilizados"
        ] = 0

        disponibles[
            "cantidad_operaciones_creditos"
        ] = 0

        disponibles[
            "ultima_operacion_creditos"
        ] = pd.NaT

        disponibles[
            "funcionalidad_mas_usada"
        ] = ""

        disponibles[
            "creditos_funcionalidad_mas_usada"
        ] = 0

        disponibles[
            "uso_creditos_detalle"
        ] = "[]"

        return disponibles[
            columnas
        ]

    ops = (
        df_creditoperations.copy()
    )

    if "userId" not in ops.columns:

        disponibles[
            "creditos_utilizados"
        ] = 0

        disponibles[
            "cantidad_operaciones_creditos"
        ] = 0

        disponibles[
            "ultima_operacion_creditos"
        ] = pd.NaT

        disponibles[
            "funcionalidad_mas_usada"
        ] = ""

        disponibles[
            "creditos_funcionalidad_mas_usada"
        ] = 0

        disponibles[
            "uso_creditos_detalle"
        ] = "[]"

        return disponibles[
            columnas
        ]

    ops[
        "_id_postulante"
    ] = (
        ops[
            "userId"
        ]
        .apply(convertir_id)
    )

    ops[
        "_fecha"
    ] = (
        ops.get(
            "createdAt",
            serie_vacia(
                ops.index,
                pd.NaT
            )
        )
        .apply(convertir_fecha)
    )

    ops[
        "_status"
    ] = (
        ops.get(
            "status",
            serie_vacia(
                ops.index
            )
        )
        .fillna("")
        .apply(limpiar_texto)
        .str.lower()
    )

    # --------------------------------------------------------
    # COMPLETED
    # --------------------------------------------------------

    ops = ops[
        ops[
            "_status"
        ] == "completed"
    ].copy()

    ops[
        "_credits"
    ] = pd.to_numeric(
        ops.get(
            "credits",
            serie_vacia(
                ops.index,
                0
            )
        ),
        errors="coerce"
    ).fillna(0)

    ops = ops[
        ops[
            "_credits"
        ] > 0
    ].copy()

    if ops.empty:

        disponibles[
            "creditos_utilizados"
        ] = 0

        disponibles[
            "cantidad_operaciones_creditos"
        ] = 0

        disponibles[
            "ultima_operacion_creditos"
        ] = pd.NaT

        disponibles[
            "funcionalidad_mas_usada"
        ] = ""

        disponibles[
            "creditos_funcionalidad_mas_usada"
        ] = 0

        disponibles[
            "uso_creditos_detalle"
        ] = "[]"

        return disponibles[
            columnas
        ]

    # --------------------------------------------------------
    # CATÁLOGO
    # --------------------------------------------------------

    catalogo = (
        preparar_catalogo_creditos(
            df_credits
        )
    )

    if not catalogo.empty:

        evento_columna_ops = obtener_columna(
            ops,
            [
                "event",
                "eventName",
            ]
        )

        if evento_columna_ops:

            if evento_columna_ops != "event":

                ops[
                    "event"
                ] = (
                    ops[
                        evento_columna_ops
                    ]
                    .fillna("")
                    .apply(
                        limpiar_texto
                    )
                )

            ops = ops.merge(
                catalogo,
                on="event",
                how="left"
            )

        else:

            ops[
                "nombre_credito"
            ] = "No especificado"

    else:

        evento_columna_ops = obtener_columna(
            ops,
            [
                "event",
                "eventName",
            ]
        )

        if evento_columna_ops:

            ops[
                "nombre_credito"
            ] = (
                ops[
                    evento_columna_ops
                ]
                .fillna("")
                .apply(limpiar_texto)
            )

        else:

            ops[
                "nombre_credito"
            ] = "No especificado"

    ops[
        "nombre_credito"
    ] = (
        ops[
            "nombre_credito"
        ]
        .fillna("")
        .apply(
            limpiar_texto
        )
    )

    # --------------------------------------------------------
    # AGRUPAR
    # --------------------------------------------------------

    registros = []

    for (
        user_id,
        grupo
    ) in ops.groupby(
        "_id_postulante"
    ):

        total_utilizado = (
            grupo[
                "_credits"
            ]
            .sum()
        )

        cantidad_operaciones = (
            len(
                grupo
            )
        )

        ultima_operacion = (
            grupo[
                "_fecha"
            ]
            .max()
        )

        uso = (
            grupo
            .groupby(
                "nombre_credito"
            )[
                "_credits"
            ]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        funcionalidad_mas_usada = ""

        creditos_mas_usada = 0

        if not uso.empty:

            funcionalidad_mas_usada = (
                str(
                    uso.index[0]
                )
            )

            creditos_mas_usada = (
                float(
                    uso.iloc[0]
                )
            )

        detalle = []

        for (
            funcionalidad,
            creditos
        ) in uso.items():

            veces = grupo[
                grupo[
                    "nombre_credito"
                ]
                == funcionalidad
            ].shape[0]

            detalle.append(
                {
                    "funcionalidad": (
                        funcionalidad
                    ),
                    "veces": int(
                        veces
                    ),
                    "creditos": float(
                        creditos
                    ),
                }
            )

        registros.append(
            {
                "_id_postulante": user_id,
                "creditos_utilizados": round(
                    float(
                        total_utilizado
                    ),
                    2
                ),
                "cantidad_operaciones_creditos": int(
                    cantidad_operaciones
                ),
                "ultima_operacion_creditos": (
                    ultima_operacion
                ),
                "funcionalidad_mas_usada": (
                    funcionalidad_mas_usada
                ),
                "creditos_funcionalidad_mas_usada": (
                    round(
                        creditos_mas_usada,
                        2
                    )
                ),
                "uso_creditos_detalle": (
                    lista_a_json(
                        detalle
                    )
                ),
            }
        )

    consumo = pd.DataFrame(
        registros
    )

    resultado = disponibles.merge(
        consumo,
        on="_id_postulante",
        how="left"
    )

    resultado[
        "creditos_utilizados"
    ] = pd.to_numeric(
        resultado[
            "creditos_utilizados"
        ],
        errors="coerce"
    ).fillna(0)

    resultado[
        "cantidad_operaciones_creditos"
    ] = pd.to_numeric(
        resultado[
            "cantidad_operaciones_creditos"
        ],
        errors="coerce"
    ).fillna(0)

    resultado[
        "creditos_funcionalidad_mas_usada"
    ] = pd.to_numeric(
        resultado[
            "creditos_funcionalidad_mas_usada"
        ],
        errors="coerce"
    ).fillna(0)

    resultado[
        "ultima_operacion_creditos"
    ] = (
        resultado[
            "ultima_operacion_creditos"
        ]
        .apply(convertir_fecha)
    )

    resultado[
        "funcionalidad_mas_usada"
    ] = (
        resultado[
            "funcionalidad_mas_usada"
        ]
        .fillna("")
        .apply(limpiar_texto)
    )

    resultado[
        "uso_creditos_detalle"
    ] = (
        resultado[
            "uso_creditos_detalle"
        ]
        .fillna("[]")
    )

    return resultado[
        columnas
    ].copy()


# ============================================================
# DIAGNÓSTICO
# ============================================================

def diagnostico_relaciones(
    datos
):

    print("\n" + "=" * 70)
    print(
        "DIAGNÓSTICO DE RELACIONES"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    users = datos[
        "users"
    ]

    users_ids = set()

    if not users.empty:

        users_ids = set(
            users[
                "_id"
            ]
            .apply(convertir_id)
            .dropna()
        )

    print(
        f"\nusers: "
        f"{len(users_ids)}"
    )

    # --------------------------------------------------------
    # CVS
    # --------------------------------------------------------

    cvs = datos[
        "cvs"
    ]

    if not cvs.empty:

        cvs_user_ids = set(
            cvs[
                "user"
            ]
            .apply(convertir_id)
            .dropna()
        )

        print(
            "\ncvs → users"
        )

        print(
            f"CVs: "
            f"{len(cvs)}"
        )

        print(
            "Usuarios relacionados: "
            f"{len(cvs_user_ids & users_ids)}"
        )

    # --------------------------------------------------------
    # EDUCACIÓN
    # --------------------------------------------------------

    educ = datos[
        "educations"
    ]

    if (
        not educ.empty
        and not cvs.empty
    ):

        mapa_cv_usuario = dict(
            zip(
                cvs[
                    "_id"
                ]
                .apply(convertir_id),
                cvs[
                    "user"
                ]
                .apply(convertir_id)
            )
        )

        educ_users = set()

        if "cv" in educ.columns:

            for cv_id in educ[
                "cv"
            ]:

                user_id = (
                    mapa_cv_usuario.get(
                        convertir_id(
                            cv_id
                        )
                    )
                )

                if user_id:
                    educ_users.add(
                        user_id
                    )

        print(
            "\neducations → cvs → users"
        )

        print(
            f"Educaciones: "
            f"{len(educ)}"
        )

        print(
            "Usuarios relacionados: "
            f"{len(educ_users)}"
        )

    # --------------------------------------------------------
    # EXPERIENCIA
    # --------------------------------------------------------

    work = datos[
        "workexperiences"
    ]

    if (
        not work.empty
        and not cvs.empty
    ):

        mapa_cv_usuario = dict(
            zip(
                cvs[
                    "_id"
                ]
                .apply(convertir_id),
                cvs[
                    "user"
                ]
                .apply(convertir_id)
            )
        )

        work_users = set()

        if "cv" in work.columns:

            for cv_id in work[
                "cv"
            ]:

                user_id = (
                    mapa_cv_usuario.get(
                        convertir_id(
                            cv_id
                        )
                    )
                )

                if user_id:
                    work_users.add(
                        user_id
                    )

        print(
            "\nworkexperiences → cvs → users"
        )

        print(
            f"Experiencias: "
            f"{len(work)}"
        )

        print(
            "Usuarios relacionados: "
            f"{len(work_users)}"
        )

        exp_df = procesar_experiencia(
            work,
            cvs
        )

        if not exp_df.empty:

            print(
                "Usuarios con experiencia "
                "calculable: "
                f"{int((exp_df['meses_experiencia'] > 0).sum())}"
            )

            print(
                "Promedio meses experiencia: "
                f"{exp_df['meses_experiencia'].mean():.2f}"
            )

    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    cvs_skills = datos[
        "cvs_skills"
    ]

    skills = datos[
        "skills"
    ]

    if (
        not cvs_skills.empty
        and not skills.empty
        and not cvs.empty
    ):

        skills_df = procesar_habilidades(
            cvs_skills,
            skills,
            cvs
        )

        print(
            "\ncvs_skills → skills → cvs → users"
        )

        print(
            f"Relaciones: "
            f"{len(cvs_skills)}"
        )

        print(
            "Usuarios relacionados: "
            f"{len(skills_df)}"
        )

    # --------------------------------------------------------
    # IDIOMAS
    # --------------------------------------------------------

    languages = datos[
        "languages"
    ]

    if not languages.empty:

        if "user" in languages.columns:

            language_users = set(
                languages[
                    "user"
                ]
                .apply(convertir_id)
                .dropna()
            )

            print(
                "\nlanguages → users"
            )

            print(
                f"Idiomas: "
                f"{len(languages)}"
            )

            print(
                "Usuarios relacionados: "
                f"{len(language_users & users_ids)}"
            )

    # --------------------------------------------------------
    # POSTULACIONES
    # --------------------------------------------------------

    applications = datos[
        "applications"
    ]

    if not applications.empty:

        apps_df = procesar_postulaciones(
            applications
        )

        print(
            "\napplications → users"
        )

        print(
            f"Postulaciones: "
            f"{len(applications)}"
        )

        print(
            "Usuarios relacionados: "
            f"{len(apps_df)}"
        )

    # --------------------------------------------------------
    # EVENTOS
    # --------------------------------------------------------

    events = datos[
        "eventguests"
    ]

    if not events.empty:

        events_df = procesar_eventos(
            events,
            datos[
                "users"
            ]
        )

        print(
            "\neventguests → users"
        )

        print(
            f"Registros: "
            f"{len(events)}"
        )

        print(
            "Usuarios relacionados: "
            f"{len(events_df)}"
        )

    # --------------------------------------------------------
    # EMPLEABILIDAD
    # --------------------------------------------------------

    employability = datos[
        "employabilities"
    ]

    if not employability.empty:

        employability_df = (
            procesar_empleabilidad(
                employability
            )
        )

        print(
            "\nemployabilities → users"
        )

        print(
            f"Evaluaciones: "
            f"{len(employability)}"
        )

        print(
            "Usuarios relacionados: "
            f"{len(employability_df)}"
        )

    # --------------------------------------------------------
    # COMPATIBILIDADES
    # --------------------------------------------------------

    compatibility = datos[
        "jobcompatibilityanalyses"
    ]

    if not compatibility.empty:

        compatibility_df = (
            procesar_compatibilidad(
                compatibility,
                datos[
                    "cvs"
                ]
            )
        )

        print(
            "\njobcompatibilityanalyses → cvs → users"
        )

        print(
            f"Análisis de compatibilidad: "
            f"{len(compatibility)}"
        )

        print(
            "Usuarios relacionados: "
            f"{len(compatibility_df)}"
        )

        if not compatibility_df.empty:

            print(
                "Análisis contabilizados: "
                f"{int(compatibility_df['cantidad_analisis_compatibilidad'].sum())}"
            )

    # --------------------------------------------------------
    # CRÉDITOS
    # --------------------------------------------------------

    operations = datos[
        "creditoperations"
    ]

    if not operations.empty:

        if "userId" in operations.columns:

            credit_users = set(
                operations[
                    "userId"
                ]
                .apply(convertir_id)
                .dropna()
            )

            print(
                "\ncreditoperations → users"
            )

            print(
                f"Operaciones: "
                f"{len(operations)}"
            )

            print(
                "Usuarios relacionados: "
                f"{len(credit_users & users_ids)}"
            )

    print(
        "\n" + "=" * 70
    )

    print(
        "FIN DEL DIAGNÓSTICO"
    )

    print(
        "=" * 70
    )


# ============================================================
# CONSTRUCCIÓN DEL DATASET
# ============================================================

def construir_dataset(
    datos
):

    print("\n" + "=" * 70)
    print(
        "PROCESANDO INFORMACIÓN"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    df_users = procesar_usuarios(
        datos[
            "users"
        ]
    )

    print(
        f"Usuarios procesados: "
        f"{len(df_users)}"
    )

    # --------------------------------------------------------
    # CV
    # --------------------------------------------------------

    df_cv = procesar_cvs(
        datos[
            "cvs"
        ]
    )

    print(
        f"CV procesados: "
        f"{len(df_cv)}"
    )

    # --------------------------------------------------------
    # EDUCACIÓN
    # --------------------------------------------------------

    df_educacion = procesar_educacion(
        datos[
            "educations"
        ],
        datos[
            "cvs"
        ]
    )

    print(
        f"Usuarios con formación: "
        f"{len(df_educacion)}"
    )

    # --------------------------------------------------------
    # EXPERIENCIA
    # --------------------------------------------------------

    df_experiencia = procesar_experiencia(
        datos[
            "workexperiences"
        ],
        datos[
            "cvs"
        ]
    )

    print(
        f"Usuarios con experiencia: "
        f"{len(df_experiencia)}"
    )

    # --------------------------------------------------------
    # HABILIDADES
    # --------------------------------------------------------

    df_habilidades = procesar_habilidades(
        datos[
            "cvs_skills"
        ],
        datos[
            "skills"
        ],
        datos[
            "cvs"
        ]
    )

    print(
        f"Usuarios con habilidades: "
        f"{len(df_habilidades)}"
    )

    # --------------------------------------------------------
    # IDIOMAS
    # --------------------------------------------------------

    df_idiomas = procesar_idiomas(
        datos[
            "languages"
        ]
    )

    print(
        f"Usuarios con idiomas: "
        f"{len(df_idiomas)}"
    )

    # --------------------------------------------------------
    # POSTULACIONES
    # --------------------------------------------------------

    df_postulaciones = (
        procesar_postulaciones(
            datos[
                "applications"
            ]
        )
    )

    print(
        f"Usuarios con postulaciones: "
        f"{len(df_postulaciones)}"
    )

    # --------------------------------------------------------
    # CURSOS
    # --------------------------------------------------------

    df_cursos = procesar_cursos(
        datos[
            "courseenrollments"
        ]
    )

    print(
        f"Usuarios con cursos: "
        f"{len(df_cursos)}"
    )

    # --------------------------------------------------------
    # IA
    # --------------------------------------------------------

    df_ia = procesar_ia(
        datos[
            "aiconversations"
        ],
        datos[
            "aimessages"
        ]
    )

    print(
        f"Usuarios con uso de IA: "
        f"{len(df_ia)}"
    )

    # --------------------------------------------------------
    # EVENTOS
    # --------------------------------------------------------

    df_eventos = procesar_eventos(
        datos[
            "eventguests"
        ],
        datos[
            "users"
        ]
    )

    print(
        f"Usuarios con eventos: "
        f"{len(df_eventos)}"
    )

    # --------------------------------------------------------
    # EMPLEABILIDAD
    # --------------------------------------------------------

    df_empleabilidad = (
        procesar_empleabilidad(
            datos[
                "employabilities"
            ]
        )
    )

    print(
        f"Usuarios con evaluación: "
        f"{len(df_empleabilidad)}"
    )

    # --------------------------------------------------------
    # COMPATIBILIDAD
    # --------------------------------------------------------

    df_compatibilidad = (
        procesar_compatibilidad(
            datos[
                "jobcompatibilityanalyses"
            ],
            datos[
                "cvs"
            ]
        )
    )

    print(
        f"Usuarios con compatibilidad: "
        f"{len(df_compatibilidad)}"
    )

    if not df_compatibilidad.empty:

        print(
            "Análisis de compatibilidad "
            "contabilizados: "
            f"{int(df_compatibilidad['cantidad_analisis_compatibilidad'].sum())}"
        )

    # --------------------------------------------------------
    # CRÉDITOS
    # --------------------------------------------------------

    df_creditos = procesar_creditos(
        datos[
            "users"
        ],
        datos[
            "creditoperations"
        ],
        datos[
            "credits"
        ]
    )

    print(
        f"Usuarios con información "
        f"de créditos: "
        f"{len(df_creditos)}"
    )

    # ========================================================
    # DATASET BASE
    # ========================================================

    df_final = (
        df_users.copy()
    )

    # ========================================================
    # MERGES
    # ========================================================

    datasets = [
        df_cv,
        df_educacion,
        df_experiencia,
        df_habilidades,
        df_idiomas,
        df_postulaciones,
        df_cursos,
        df_ia,
        df_eventos,
        df_empleabilidad,
        df_compatibilidad,
        df_creditos,
    ]

    for df in datasets:

        if (
            df is None
            or df.empty
            or "_id_postulante"
            not in df.columns
        ):

            continue

        df_final = df_final.merge(
            df,
            on="_id_postulante",
            how="left",
            suffixes=(
                "",
                "_extra"
            )
        )

    # ========================================================
    # NUMÉRICOS
    # ========================================================

    columnas_numericas = [
        "cantidad_formaciones",
        "cantidad_experiencias",
        "meses_experiencia",
        "años_experiencia",
        "cantidad_habilidades",
        "cantidad_hard_skills",
        "cantidad_soft_skills",
        "cantidad_idiomas",
        "cantidad_postulaciones",
        "postulaciones_pendientes",
        "postulaciones_revision",
        "postulaciones_aceptadas",
        "postulaciones_rechazadas",
        "cantidad_cursos",
        "cantidad_conversaciones",
        "cantidad_mensajes_ia",
        "cantidad_eventos",
        "score_empleabilidad",
        "cantidad_analisis_compatibilidad",
        "score_compatibilidad_promedio",
        "ultimo_score_compatibilidad",
        "creditos_disponibles",
        "creditos_utilizados",
        "cantidad_operaciones_creditos",
        "creditos_funcionalidad_mas_usada",
        "cv_paginas",
    ]

    for columna in columnas_numericas:

        if columna in df_final.columns:

            df_final[
                columna
            ] = (
                pd.to_numeric(
                    df_final[
                        columna
                    ],
                    errors="coerce"
                )
                .fillna(0)
            )

    # ========================================================
    # BOOLEANOS
    # ========================================================

    columnas_booleanas = [
        "tiene_cv",
        "uso_ia",
        "participo_evento",
        "tiene_experiencia",
        "perfil_completo",
    ]

    for columna in columnas_booleanas:

        if columna in df_final.columns:

            df_final[
                columna
            ] = (
                df_final[
                    columna
                ]
                .fillna(False)
                .astype(bool)
            )

    # ========================================================
    # TEXTO
    # ========================================================

    columnas_texto = [
        "profesion",
        "resumen",
        "cv_nombre",
        "cv_tipo",
        "nivel_educativo",
        "instituciones",
        "formaciones_detalle",
        "experiencia_formato",
        "experiencia_tipo",
        "experiencia_detalle",
        "hard_skills_detalle",
        "soft_skills_detalle",
        "habilidades_detalle",
        "habilidades_no_especificadas",
        "idiomas_detalle",
        "postulaciones_estado_detalle",
        "nivel_empleabilidad",
        "rol_sugerido",
        "fortalezas_empleabilidad",
        "debilidades_empleabilidad",
        "mejoras_empleabilidad",
        "ultimo_nivel_compatibilidad",
        "funcionalidad_mas_usada",
        "uso_creditos_detalle",
    ]

    for columna in columnas_texto:

        if columna in df_final.columns:

            df_final[
                columna
            ] = (
                df_final[
                    columna
                ]
                .fillna("")
                .apply(
                    limpiar_texto
                )
            )

    # ========================================================
    # FECHAS
    # ========================================================

    columnas_fecha = [
        "fecha_registro",
        "ultima_operacion_creditos",
    ]

    for columna in columnas_fecha:

        if columna in df_final.columns:

            df_final[
                columna
            ] = (
                df_final[
                    columna
                ]
                .apply(
                    convertir_fecha
                )
            )

    # ========================================================
    # EXPERIENCIA
    # ========================================================

    if "meses_experiencia" in df_final.columns:

        df_final[
            "tiene_experiencia"
        ] = (
            df_final[
                "meses_experiencia"
            ]
            > 0
        )

    else:

        df_final[
            "tiene_experiencia"
        ] = False

    # ========================================================
    # POSTULACIONES
    # ========================================================

    if "cantidad_postulaciones" in df_final.columns:

        df_final[
            "tiene_postulaciones"
        ] = (
            df_final[
                "cantidad_postulaciones"
            ]
            > 0
        )

    else:

        df_final[
            "tiene_postulaciones"
        ] = False

    # ========================================================
    # PERFIL COMPLETO
    # ========================================================

    tiene_cv = (
        df_final.get(
            "tiene_cv",
            serie_vacia(
                df_final.index,
                False
            )
        )
        .fillna(False)
        .astype(bool)
    )

    tiene_formacion = (
        pd.to_numeric(
            df_final.get(
                "cantidad_formaciones",
                serie_vacia(
                    df_final.index,
                    0
                )
            ),
            errors="coerce"
        )
        .fillna(0)
        > 0
    )

    tiene_habilidades = (
        pd.to_numeric(
            df_final.get(
                "cantidad_habilidades",
                serie_vacia(
                    df_final.index,
                    0
                )
            ),
            errors="coerce"
        )
        .fillna(0)
        > 0
    )

    df_final[
        "perfil_completo"
    ] = (
        tiene_cv
        & tiene_formacion
        & tiene_habilidades
    )

    # ========================================================
    # PORCENTAJE DE PERFIL
    # ========================================================

    criterios_perfil = (
        tiene_cv.astype(int)
        + tiene_formacion.astype(int)
        + tiene_habilidades.astype(int)
    )

    df_final[
        "perfil_completado_pct"
    ] = (
        criterios_perfil
        / 3
        * 100
    ).round(
        0
    )

    # ========================================================
    # ELIMINAR DUPLICADOS
    # ========================================================

    df_final = (
        df_final
        .drop_duplicates(
            subset="_id_postulante",
            keep="first"
        )
    )

    # ========================================================
    # ORDEN DE COLUMNAS
    # ========================================================

    columnas_preferidas = [

        "_id_postulante",
        "nombre_completo",
        "email",
        "telefono",
        "fecha_registro",
        "tipo_postulante",
        "estado_empleo",

        "tiene_cv",
        "_id_cv",
        "cv_nombre",
        "profesion",
        "resumen",
        "cv_tipo",
        "cv_paginas",

        "cantidad_formaciones",
        "nivel_educativo",
        "instituciones",
        "formaciones_detalle",

        "cantidad_experiencias",
        "meses_experiencia",
        "años_experiencia",
        "experiencia_formato",
        "tiene_experiencia",
        "experiencia_tipo",
        "experiencia_detalle",

        "cantidad_habilidades",
        "cantidad_hard_skills",
        "cantidad_soft_skills",
        "hard_skills_detalle",
        "soft_skills_detalle",
        "habilidades_detalle",
        "habilidades_no_especificadas",

        "cantidad_idiomas",
        "idiomas_detalle",

        "cantidad_postulaciones",
        "tiene_postulaciones",
        "postulaciones_pendientes",
        "postulaciones_revision",
        "postulaciones_aceptadas",
        "postulaciones_rechazadas",
        "postulaciones_estado_detalle",

        "cantidad_cursos",

        "uso_ia",
        "cantidad_conversaciones",
        "cantidad_mensajes_ia",

        "participo_evento",
        "cantidad_eventos",

        "nivel_empleabilidad",
        "score_empleabilidad",
        "rol_sugerido",
        "fortalezas_empleabilidad",
        "debilidades_empleabilidad",
        "mejoras_empleabilidad",

        "cantidad_analisis_compatibilidad",
        "score_compatibilidad_promedio",
        "ultimo_score_compatibilidad",
        "ultimo_nivel_compatibilidad",

        "creditos_disponibles",
        "creditos_utilizados",
        "cantidad_operaciones_creditos",
        "ultima_operacion_creditos",
        "funcionalidad_mas_usada",
        "creditos_funcionalidad_mas_usada",
        "uso_creditos_detalle",

        "linkedin",
        "linkedin_profile",
        "ubicacion",
        "modalidad",
        "disponibilidad",

        "perfil_completo",
        "perfil_completado_pct",
    ]

    columnas_existentes = [
        columna
        for columna in columnas_preferidas
        if columna in df_final.columns
    ]

    otras_columnas = [
        columna
        for columna in df_final.columns
        if columna not in columnas_existentes
    ]

    df_final = df_final[
        columnas_existentes
        + otras_columnas
    ]

    return df_final


# ============================================================
# VALIDACIÓN
# ============================================================

def validar_dataset(
    df
):

    print("\n" + "=" * 70)
    print(
        "VALIDACIÓN FINAL"
    )
    print("=" * 70)

    print(
        f"Postulantes: "
        f"{len(df)}"
    )

    if "_id_postulante" in df.columns:

        unicos = (
            df[
                "_id_postulante"
            ]
            .nunique()
        )

        duplicados = (
            df[
                "_id_postulante"
            ]
            .duplicated()
            .sum()
        )

        print(
            f"Usuarios únicos: "
            f"{unicos}"
        )

        print(
            f"Duplicados: "
            f"{duplicados}"
        )

    if "tiene_cv" in df.columns:

        print(
            f"Con CV: "
            f"{int(df['tiene_cv'].sum())}"
        )

    if "cantidad_habilidades" in df.columns:

        print(
            "Con habilidades: "
            f"{int((df['cantidad_habilidades'] > 0).sum())}"
        )

    if "cantidad_hard_skills" in df.columns:

        print(
            "Con Hard Skills: "
            f"{int((df['cantidad_hard_skills'] > 0).sum())}"
        )

    if "cantidad_soft_skills" in df.columns:

        print(
            "Con Soft Skills: "
            f"{int((df['cantidad_soft_skills'] > 0).sum())}"
        )

    if "cantidad_idiomas" in df.columns:

        print(
            "Con idiomas: "
            f"{int((df['cantidad_idiomas'] > 0).sum())}"
        )

    if "meses_experiencia" in df.columns:

        usuarios_exp = int(
            (
                df[
                    "meses_experiencia"
                ] > 0
            ).sum()
        )

        promedio_meses = (
            df[
                "meses_experiencia"
            ]
            .mean()
        )

        promedio_años = (
            df[
                "años_experiencia"
            ]
            .mean()
        )

        print(
            f"Con experiencia: "
            f"{usuarios_exp}"
        )

        print(
            "Promedio meses experiencia: "
            f"{promedio_meses:.2f}"
        )

        print(
            "Promedio años experiencia: "
            f"{promedio_años:.2f}"
        )

        print(
            "\nEjemplos de experiencia:"
        )

        columnas_ejemplo = [
            "nombre_completo",
            "meses_experiencia",
            "años_experiencia",
            "experiencia_formato",
        ]

        ejemplo = (
            df[
                df[
                    "meses_experiencia"
                ] > 0
            ][
                columnas_ejemplo
            ]
            .head(10)
        )

        if not ejemplo.empty:

            print(
                ejemplo.to_string(
                    index=False
                )
            )

    if "uso_ia" in df.columns:

        print(
            f"\nUsuarios IA: "
            f"{int(df['uso_ia'].sum())}"
        )

    if "participo_evento" in df.columns:

        print(
            "Participaron en eventos: "
            f"{int(df['participo_evento'].sum())}"
        )

    if "cantidad_postulaciones" in df.columns:

        print(
            "Con postulaciones: "
            f"{int((df['cantidad_postulaciones'] > 0).sum())}"
        )

    # --------------------------------------------------------
    # COMPATIBILIDADES
    # --------------------------------------------------------

    if (
        "cantidad_analisis_compatibilidad"
        in df.columns
    ):

        print(
            "Usuarios con compatibilidades: "
            f"{int((df['cantidad_analisis_compatibilidad'] > 0).sum())}"
        )

        print(
            "Análisis de compatibilidad "
            "totales: "
            f"{int(df['cantidad_analisis_compatibilidad'].sum())}"
        )

        if (
            "score_compatibilidad_promedio"
            in df.columns
        ):

            scores_validos = (
                pd.to_numeric(
                    df[
                        "score_compatibilidad_promedio"
                    ],
                    errors="coerce"
                )
            )

            scores_validos = scores_validos[
                scores_validos > 0
            ]

            if not scores_validos.empty:

                print(
                    "Promedio score compatibilidad: "
                    f"{scores_validos.mean():.2f}"
                )

    # --------------------------------------------------------
    # CRÉDITOS
    # --------------------------------------------------------

    if "creditos_disponibles" in df.columns:

        print(
            "Créditos disponibles "
            "totales: "
            f"{df['creditos_disponibles'].sum():.2f}"
        )

    if "creditos_utilizados" in df.columns:

        print(
            "Créditos utilizados "
            "totales: "
            f"{df['creditos_utilizados'].sum():.2f}"
        )

        print(
            "Usuarios que utilizaron "
            "créditos: "
            f"{int((df['creditos_utilizados'] > 0).sum())}"
        )

    if "perfil_completo" in df.columns:

        print(
            "Perfil completo: "
            f"{int(df['perfil_completo'].sum())}"
        )

    if "perfil_completado_pct" in df.columns:

        print(
            "Promedio perfil completado: "
            f"{df['perfil_completado_pct'].mean():.2f}%"
        )

    print(
        f"Columnas finales: "
        f"{len(df.columns)}"
    )


# ============================================================
# GUARDAR
# ============================================================

def guardar_dataset(
    df
):

    os.makedirs(
        os.path.dirname(
            OUTPUT_PATH
        ),
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 70)
    print(
        "ARCHIVO GENERADO"
    )
    print("=" * 70)

    print(
        f"✓ {OUTPUT_PATH}"
    )

    print(
        f"✓ Registros: "
        f"{len(df)}"
    )

    print(
        f"✓ Columnas: "
        f"{len(df.columns)}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Constructor individual "
            "de Laboral.AI"
        )
    )

    parser.add_argument(
        "--diagnostico",
        action="store_true",
        help=(
            "Muestra diagnóstico de "
            "relaciones y termina."
        )
    )

    args = parser.parse_args()

    cliente = None

    print("\n")
    print("=" * 70)
    print(
        "CONSTRUCTOR INDIVIDUAL - LABORAL.AI"
    )
    print("=" * 70)

    try:

        # ----------------------------------------------------
        # CONEXIÓN
        # ----------------------------------------------------

        cliente, db = (
            conectar_mongodb()
        )

        # ----------------------------------------------------
        # CARGAR
        # ----------------------------------------------------

        datos = cargar_colecciones(
            db
        )

        # ----------------------------------------------------
        # DIAGNÓSTICO
        # ----------------------------------------------------

        if args.diagnostico:

            diagnostico_relaciones(
                datos
            )

            return

        # ----------------------------------------------------
        # CONSTRUIR
        # ----------------------------------------------------

        df_final = construir_dataset(
            datos
        )

        # ----------------------------------------------------
        # VALIDAR
        # ----------------------------------------------------

        validar_dataset(
            df_final
        )

        # ----------------------------------------------------
        # GUARDAR
        # ----------------------------------------------------

        guardar_dataset(
            df_final
        )

        print("\n" + "=" * 70)
        print(
            "✓ PROCESO COMPLETADO CORRECTAMENTE"
        )
        print("=" * 70)

    except Exception as error:

        print("\n" + "=" * 70)
        print(
            "ERROR"
        )
        print("=" * 70)

        print(
            f"{type(error).__name__}: "
            f"{error}"
        )

        raise

    finally:

        if cliente is not None:

            cliente.close()

            print(
                "\n✓ Conexión MongoDB cerrada"
            )


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":

    main()