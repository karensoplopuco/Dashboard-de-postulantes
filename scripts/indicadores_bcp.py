# ============================================================
# INDICADORES BCP
# ============================================================
#
# Construye los datasets analíticos de los participantes BCP.
#
# Población:
#   51 participantes identificados por constructor_bcp.py
#
# Este script:
#   - NO modifica MongoDB
#   - Lee datos
#   - Cruza participantes
#   - Calcula indicadores verificables
#   - Exporta resultados a Excel
#
# Fecha de referencia:
#   Evento BCP: 20/08/2026
#
# ============================================================

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from bson import ObjectId


# ============================================================
# 1. IMPORTS DEL PROYECTO
# ============================================================

try:
    from conexion import get_db, comprobar_conexion
    from constructor_bcp import construir_bcp

except ImportError:
    from scripts.conexion import get_db, comprobar_conexion
    from scripts.constructor_bcp import construir_bcp


# ============================================================
# 2. CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

ARCHIVO_SALIDA = DATA_DIR / "indicadores_bcp.xlsx"

FECHA_EVENTO_BCP = pd.Timestamp("2026-08-20")


# ============================================================
# 3. UTILIDADES
# ============================================================

def titulo(texto):

    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def normalizar_id(valor):

    if valor is None:
        return None

    try:
        if pd.isna(valor):
            return None
    except Exception:
        pass

    texto = str(valor).strip()

    if not texto:
        return None

    return texto


def normalizar_fecha(serie):

    return pd.to_datetime(
        serie,
        errors="coerce"
    )


def porcentaje(numerador, denominador):

    if not denominador:
        return 0.0

    return round(
        numerador / denominador * 100,
        2
    )


def convertir_a_numero(valor):

    if valor is None:
        return np.nan

    try:
        return float(valor)

    except (TypeError, ValueError):
        return np.nan


# ============================================================
# 4. PREPARAR IDs EN AMBOS FORMATOS
# ============================================================

def preparar_ids_mongo(valores):
    """
    MongoDB contiene relaciones guardadas de distintas maneras:

        "6a..."
        ObjectId("6a...")

    Esta función conserva AMBAS representaciones.
    """

    ids_string = set()

    for valor in valores:

        if valor is None:
            continue

        texto = str(valor).strip()

        if texto:
            ids_string.add(texto)

    ids_objectid = set()

    for texto in ids_string:

        try:

            if ObjectId.is_valid(texto):

                ids_objectid.add(
                    ObjectId(texto)
                )

        except Exception:
            pass

    return (
        list(ids_string)
        +
        list(ids_objectid)
    )


# ============================================================
# 5. DETECTAR CAMPO USUARIO
# ============================================================

def detectar_campo_usuario(documento):

    candidatos = [
        "user",
        "userId",
        "user_id",
        "userid",
        "userID",
        "owner",
        "ownerId",
        "createdBy",
        "candidateId",
        "candidate_id",
        "applicantId",
        "applicant_id",
    ]

    for campo in candidatos:

        if campo in documento:
            return campo

    return None


# ============================================================
# 6. CONSULTA POR USUARIO
# ============================================================

def consultar_por_usuarios(
    db,
    coleccion,
    object_ids,
    user_ids,
    campo_usuario=None
):
    """
    Consulta registros pertenecientes a participantes BCP.

    IMPORTANTE:
    Conserva simultáneamente IDs como string y ObjectId.
    """

    if coleccion not in db.list_collection_names():

        print(
            f"[AVISO] No existe colección: {coleccion}"
        )

        return pd.DataFrame()

    col = db[coleccion]

    muestra = col.find_one()

    if not muestra:

        print(
            f"[AVISO] Colección vacía: {coleccion}"
        )

        return pd.DataFrame()

    if campo_usuario is None:

        campo_usuario = detectar_campo_usuario(
            muestra
        )

    if campo_usuario is None:

        print(
            f"[AVISO] {coleccion}: "
            "no se detectó campo usuario."
        )

        return pd.DataFrame()

    valores_busqueda = preparar_ids_mongo(
        list(user_ids)
        +
        list(object_ids)
    )

    documentos = list(
        col.find(
            {
                campo_usuario: {
                    "$in": valores_busqueda
                }
            }
        )
    )

    if not documentos:

        print(
            f"{coleccion}: 0 registros BCP"
        )

        return pd.DataFrame()

    df = pd.DataFrame(
        documentos
    )

    df["_user_bcp"] = (
        df[campo_usuario]
        .apply(normalizar_id)
    )

    print(
        f"{coleccion}: "
        f"{len(df):,} registros BCP | "
        f"{df['_user_bcp'].nunique():,} participantes"
    )

    return df


# ============================================================
# 7. CONSULTA POR CV
# ============================================================

def consultar_por_cv(
    db,
    coleccion,
    cv_ids,
    campo_cv=None
):
    """
    Cruza colecciones mediante ID del CV.

    Casos confirmados:

        skills.cv              -> str
        educations.cv          -> str
        workexperiences.cv     -> str
        df_matches.cv_id       -> ObjectId
        jobcompatibilityanalyses.cvId -> str
    """

    if not cv_ids:
        return pd.DataFrame()

    if coleccion not in db.list_collection_names():

        print(
            f"[AVISO] No existe colección: {coleccion}"
        )

        return pd.DataFrame()

    col = db[coleccion]

    muestra = col.find_one()

    if not muestra:
        return pd.DataFrame()

    if campo_cv is None:

        candidatos = [
            "cv",
            "cvId",
            "cv_id",
        ]

        for candidato in candidatos:

            if candidato in muestra:

                campo_cv = candidato
                break

    if campo_cv is None:

        print(
            f"[AVISO] {coleccion}: "
            "no se detectó campo CV."
        )

        return pd.DataFrame()

    valores_busqueda = preparar_ids_mongo(
        cv_ids
    )

    documentos = list(
        col.find(
            {
                campo_cv: {
                    "$in": valores_busqueda
                }
            }
        )
    )

    if not documentos:

        print(
            f"{coleccion}: 0 registros BCP"
        )

        return pd.DataFrame()

    df = pd.DataFrame(
        documentos
    )

    df["_cv_id"] = (
        df[campo_cv]
        .apply(normalizar_id)
    )

    print(
        f"{coleccion}: "
        f"{len(df):,} registros BCP"
    )

    return df


# ============================================================
# 8. CREAR BASE DE PARTICIPANTES
# ============================================================

def crear_base_participantes(resultado_bcp):

    titulo(
        "BCP | CREANDO BASE DE PARTICIPANTES"
    )

    df = (
        resultado_bcp[
            "participantes"
        ]
        .copy()
    )

    if "user_id" not in df.columns:

        raise ValueError(
            "No existe user_id en participantes BCP."
        )

    df["user_id"] = (
        df["user_id"]
        .apply(normalizar_id)
    )

    if "createdAt" in df.columns:

        df["fecha_registro"] = (
            normalizar_fecha(
                df["createdAt"]
            )
        )

    else:

        df["fecha_registro"] = pd.NaT

    print(
        f"Participantes BCP: {len(df):,}"
    )

    return df


# ============================================================
# 9. MAPA CV -> USER
# ============================================================

def crear_mapa_cv_usuario(df_cv):

    if df_cv.empty:

        return pd.DataFrame(
            columns=[
                "_cv_id",
                "user_id"
            ]
        )

    mapa = (
        df_cv[
            [
                "_cv_id",
                "_user_bcp"
            ]
        ]
        .dropna()
        .drop_duplicates()
        .rename(
            columns={
                "_user_bcp": "user_id"
            }
        )
    )

    return mapa


# ============================================================
# 10. PROCESAR CV
# ============================================================

def procesar_cv(
    db,
    base,
    object_ids,
    user_ids
):

    titulo("BCP | PERFIL / CV")

    # Confirmado por diagnóstico:
    # cvs.user es STRING.

    df_cv = consultar_por_usuarios(
        db,
        "cvs",
        object_ids,
        user_ids,
        campo_usuario="user"
    )

    resumen = (
        base[["user_id"]]
        .copy()
    )

    resumen["cantidad_cv"] = 0
    resumen["tiene_cv"] = False

    if df_cv.empty:

        print(
            "[AVISO] No se encontraron CV BCP."
        )

        return (
            resumen,
            df_cv,
            []
        )

    df_cv["_cv_id"] = (
        df_cv["_id"]
        .apply(normalizar_id)
    )

    conteo = (
        df_cv
        .groupby("_user_bcp")
        .size()
        .rename("cantidad_cv")
        .reset_index()
        .rename(
            columns={
                "_user_bcp": "user_id"
            }
        )
    )

    resumen = (
        base[["user_id"]]
        .merge(
            conteo,
            on="user_id",
            how="left"
        )
    )

    resumen["cantidad_cv"] = (
        resumen["cantidad_cv"]
        .fillna(0)
        .astype(int)
    )

    resumen["tiene_cv"] = (
        resumen["cantidad_cv"] > 0
    )

    cv_ids = (
        df_cv["_id"]
        .dropna()
        .tolist()
    )

    print(
        f"Participantes con CV: "
        f"{resumen['tiene_cv'].sum():,}"
    )

    print(
        f"CV encontrados: "
        f"{len(df_cv):,}"
    )

    return (
        resumen,
        df_cv,
        cv_ids
    )


# ============================================================
# 11. FUNCIÓN GENERAL CV -> PARTICIPANTE
# ============================================================

def agregar_conteo_cv(
    base,
    df_cv,
    df_detalle,
    nombre_columna
):

    resultado = (
        base[["user_id"]]
        .copy()
    )

    resultado[nombre_columna] = 0

    if (
        df_cv.empty
        or
        df_detalle.empty
    ):

        return resultado

    mapa_cv = crear_mapa_cv_usuario(
        df_cv
    )

    detalle = (
        df_detalle
        .merge(
            mapa_cv,
            on="_cv_id",
            how="left"
        )
    )

    conteo = (
        detalle
        .dropna(
            subset=["user_id"]
        )
        .groupby("user_id")
        .size()
        .rename(nombre_columna)
        .reset_index()
    )

    resultado = (
        base[["user_id"]]
        .merge(
            conteo,
            on="user_id",
            how="left"
        )
    )

    resultado[nombre_columna] = (
        resultado[nombre_columna]
        .fillna(0)
        .astype(int)
    )

    print(
        f"Participantes con {nombre_columna}: "
        f"{(resultado[nombre_columna] > 0).sum():,}"
    )

    return resultado


# ============================================================
# 12. EDUCACIÓN
# ============================================================

def procesar_educacion(
    db,
    base,
    df_cv,
    cv_ids
):

    titulo("BCP | EDUCACIÓN")

    df = consultar_por_cv(
        db,
        "educations",
        cv_ids,
        campo_cv="cv"
    )

    resumen = agregar_conteo_cv(
        base,
        df_cv,
        df,
        "educaciones"
    )

    if not df.empty:

        mapa = crear_mapa_cv_usuario(
            df_cv
        )

        df = df.merge(
            mapa,
            on="_cv_id",
            how="left"
        )

    return resumen, df


# ============================================================
# 13. EXPERIENCIA
# ============================================================

def procesar_experiencia(
    db,
    base,
    df_cv,
    cv_ids
):

    titulo("BCP | EXPERIENCIA")

    df = consultar_por_cv(
        db,
        "workexperiences",
        cv_ids,
        campo_cv="cv"
    )

    resumen = agregar_conteo_cv(
        base,
        df_cv,
        df,
        "experiencias"
    )

    if not df.empty:

        mapa = crear_mapa_cv_usuario(
            df_cv
        )

        df = df.merge(
            mapa,
            on="_cv_id",
            how="left"
        )

    return resumen, df


# ============================================================
# 14. HABILIDADES
# ============================================================

def procesar_habilidades(
    db,
    base,
    df_cv,
    cv_ids
):

    titulo("BCP | HABILIDADES")

    df = consultar_por_cv(
        db,
        "skills",
        cv_ids,
        campo_cv="cv"
    )

    resultado = (
        base[["user_id"]]
        .copy()
    )

    resultado["total_skills"] = 0
    resultado["hard_skills"] = 0
    resultado["soft_skills"] = 0

    if df.empty or df_cv.empty:

        return resultado, df

    mapa_cv = crear_mapa_cv_usuario(
        df_cv
    )

    df = (
        df.merge(
            mapa_cv,
            on="_cv_id",
            how="left"
        )
    )

    if "type" in df.columns:

        df["tipo_normalizado"] = (
            df["type"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

    else:

        df["tipo_normalizado"] = ""

    total = (
        df
        .dropna(
            subset=["user_id"]
        )
        .groupby("user_id")
        .size()
        .rename("total_skills")
    )

    hard = (
        df[
            df["tipo_normalizado"]
            .str.contains(
                "hard|technical|technical skill|tecnica|técnica",
                regex=True,
                na=False
            )
        ]
        .groupby("user_id")
        .size()
        .rename("hard_skills")
    )

    soft = (
        df[
            df["tipo_normalizado"]
            .str.contains(
                "soft|blanda",
                regex=True,
                na=False
            )
        ]
        .groupby("user_id")
        .size()
        .rename("soft_skills")
    )

    conteo = pd.concat(
        [
            total,
            hard,
            soft
        ],
        axis=1
    ).fillna(0)

    conteo = (
        conteo
        .reset_index()
    )

    resultado = (
        base[["user_id"]]
        .merge(
            conteo,
            on="user_id",
            how="left"
        )
    )

    for columna in [
        "total_skills",
        "hard_skills",
        "soft_skills",
    ]:

        resultado[columna] = (
            resultado[columna]
            .fillna(0)
            .astype(int)
        )

    print(
        f"Participantes con habilidades: "
        f"{(resultado['total_skills'] > 0).sum():,}"
    )

    print(
        f"Registros de habilidades: "
        f"{len(df):,}"
    )

    if "type" in df.columns:

        print(
            "\nTipos de habilidad encontrados:"
        )

        print(
            df["type"]
            .fillna("[SIN TIPO]")
            .value_counts()
            .head(20)
            .to_string()
        )

    return resultado, df


# ============================================================
# 15. IKIGAI
# ============================================================

def procesar_ikigai(
    db,
    base,
    object_ids,
    user_ids
):

    titulo(
        "BCP | IKIGAI / INTROSPECCIÓN"
    )

    datos = consultar_por_usuarios(
        db,
        "userikigaidatas",
        object_ids,
        user_ids,
        campo_usuario="user"
    )

    resultados = consultar_por_usuarios(
        db,
        "ikigairesults",
        object_ids,
        user_ids,
        campo_usuario="user"
    )

    resumen = (
        base[["user_id"]]
        .copy()
    )

    resumen["ikigai_registros"] = 0
    resumen["ikigai_iniciado"] = False
    resumen["ikigai_completado"] = False
    resumen["ikigai_resultado"] = False

    # --------------------------------------------------------
    # Registros / iniciado
    # --------------------------------------------------------

    if not datos.empty:

        conteo = (
            datos
            .groupby("_user_bcp")
            .size()
            .rename("ikigai_registros")
            .reset_index()
            .rename(
                columns={
                    "_user_bcp": "user_id"
                }
            )
        )

        resumen = (
            resumen
            .drop(
                columns=[
                    "ikigai_registros"
                ]
            )
            .merge(
                conteo,
                on="user_id",
                how="left"
            )
        )

        resumen["ikigai_registros"] = (
            resumen["ikigai_registros"]
            .fillna(0)
            .astype(int)
        )

        resumen["ikigai_iniciado"] = (
            resumen["ikigai_registros"] > 0
        )

    # --------------------------------------------------------
    # Completado
    # --------------------------------------------------------

    if (
        not datos.empty
        and
        "completed" in datos.columns
    ):

        def es_completado(valor):

            if valor is True:
                return True

            if isinstance(valor, str):

                return (
                    valor.strip().lower()
                    in [
                        "true",
                        "1",
                        "yes",
                        "si",
                        "sí"
                    ]
                )

            if isinstance(
                valor,
                (int, float)
            ):

                return valor == 1

            return False

        mascara = (
            datos["completed"]
            .apply(es_completado)
        )

        completados = datos[
            mascara
        ]

        usuarios_completaron = set(
            completados[
                "_user_bcp"
            ]
            .dropna()
        )

        resumen["ikigai_completado"] = (
            resumen["user_id"]
            .isin(
                usuarios_completaron
            )
        )

    # --------------------------------------------------------
    # Resultado
    # --------------------------------------------------------

    if not resultados.empty:

        usuarios_resultado = set(
            resultados[
                "_user_bcp"
            ]
            .dropna()
        )

        resumen["ikigai_resultado"] = (
            resumen["user_id"]
            .isin(
                usuarios_resultado
            )
        )

    print(
        f"Participantes que iniciaron: "
        f"{resumen['ikigai_iniciado'].sum():,}"
    )

    print(
        f"Participantes marcados como completados: "
        f"{resumen['ikigai_completado'].sum():,}"
    )

    print(
        f"Participantes con resultado generado: "
        f"{resumen['ikigai_resultado'].sum():,}"
    )

    print(
        f"Registros userikigaidatas: "
        f"{len(datos):,}"
    )

    print(
        f"Registros ikigairesults: "
        f"{len(resultados):,}"
    )

    return (
        resumen,
        datos,
        resultados
    )


# ============================================================
# 16. EXTRAER PERFIL IKIGAI
# ============================================================

def procesar_perfil_ikigai(
    resultados
):
    """
    Prepara campos de introspección para análisis posterior.

    NO categoriza todavía textos automáticamente.
    Conserva los valores originales.
    """

    if resultados.empty:

        return pd.DataFrame()

    filas = []

    for _, row in resultados.iterrows():

        profile = row.get(
            "profile",
            {}
        )

        if not isinstance(
            profile,
            dict
        ):

            profile = {}

        fila = {
            "user_id":
                row.get("_user_bcp"),

            "fecha_resultado":
                row.get("createdAt"),

            "fortalezas":
                profile.get("strengths"),

            "mejoras":
                profile.get("improvements"),

            "motivacion":
                profile.get("motivation"),

            "problemas_interes":
                profile.get(
                    "problems_of_interest"
                ),

            "direccion_profesional":
                profile.get(
                    "career_direction"
                ),

            "areas_trabajo_sugeridas":
                profile.get(
                    "suggested_work_areas"
                ),

            "perfil_profesional":
                profile.get(
                    "professional_profile"
                ),

            "nivel_claridad":
                profile.get(
                    "clarity_level"
                ),

            "ingreso_actual_estimado":
                profile.get(
                    "current_income_estimate"
                ),

            "ingreso_deseado_estimado":
                profile.get(
                    "desired_income_estimate"
                ),
        }

        filas.append(
            fila
        )

    df = pd.DataFrame(
        filas
    )

    print(
        f"\nPerfiles Ikigai preparados: "
        f"{len(df):,}"
    )

    return df


# ============================================================
# 17. CURSOS
# ============================================================

def procesar_cursos(
    db,
    base,
    object_ids,
    user_ids
):

    titulo("BCP | CURSOS")

    df = consultar_por_usuarios(
        db,
        "courseenrollments",
        object_ids,
        user_ids,
        campo_usuario="user"
    )

    resultado = (
        base[["user_id"]]
        .copy()
    )

    resultado["cursos_inscritos"] = 0

    if df.empty:

        return resultado, df

    conteo = (
        df
        .groupby("_user_bcp")
        .size()
        .rename("cursos_inscritos")
        .reset_index()
        .rename(
            columns={
                "_user_bcp": "user_id"
            }
        )
    )

    resultado = (
        base[["user_id"]]
        .merge(
            conteo,
            on="user_id",
            how="left"
        )
    )

    resultado["cursos_inscritos"] = (
        resultado["cursos_inscritos"]
        .fillna(0)
        .astype(int)
    )

    print(
        f"Participantes en cursos: "
        f"{(resultado['cursos_inscritos'] > 0).sum():,}"
    )

    print(
        f"Inscripciones BCP: "
        f"{len(df):,}"
    )

    return resultado, df


# ============================================================
# 18. EVALUACIONES
# ============================================================

def procesar_evaluaciones(
    db,
    base,
    object_ids,
    user_ids
):

    titulo("BCP | EVALUACIONES")

    datos = consultar_por_usuarios(
        db,
        "userquizdatas",
        object_ids,
        user_ids,
        campo_usuario="user"
    )

    resultados = consultar_por_usuarios(
        db,
        "quizresults",
        object_ids,
        user_ids,
        campo_usuario="user"
    )

    resumen = (
        base[["user_id"]]
        .copy()
    )

    resumen["evaluaciones_registros"] = 0
    resumen["evaluaciones_resultados"] = 0

    if not datos.empty:

        conteo = (
            datos
            .groupby("_user_bcp")
            .size()
            .rename(
                "evaluaciones_registros"
            )
            .reset_index()
            .rename(
                columns={
                    "_user_bcp": "user_id"
                }
            )
        )

        resumen = (
            resumen
            .drop(
                columns=[
                    "evaluaciones_registros"
                ]
            )
            .merge(
                conteo,
                on="user_id",
                how="left"
            )
        )

    if not resultados.empty:

        conteo = (
            resultados
            .groupby("_user_bcp")
            .size()
            .rename(
                "evaluaciones_resultados"
            )
            .reset_index()
            .rename(
                columns={
                    "_user_bcp": "user_id"
                }
            )
        )

        resumen = (
            resumen
            .drop(
                columns=[
                    "evaluaciones_resultados"
                ]
            )
            .merge(
                conteo,
                on="user_id",
                how="left"
            )
        )

    for columna in [
        "evaluaciones_registros",
        "evaluaciones_resultados",
    ]:

        resumen[columna] = (
            resumen[columna]
            .fillna(0)
            .astype(int)
        )

    print(
        f"Participantes con datos de evaluación: "
        f"{(resumen['evaluaciones_registros'] > 0).sum():,}"
    )

    print(
        f"Participantes con resultado: "
        f"{(resumen['evaluaciones_resultados'] > 0).sum():,}"
    )

    return (
        resumen,
        datos,
        resultados
    )


# ============================================================
# 19. CHATBOT
# ============================================================

def procesar_chatbot(
    db,
    base,
    object_ids,
    user_ids
):

    titulo("BCP | CHATBOT")

    conversaciones = consultar_por_usuarios(
        db,
        "aiconversations",
        object_ids,
        user_ids,
        campo_usuario="user"
    )

    mensajes = consultar_por_usuarios(
        db,
        "aimessages",
        object_ids,
        user_ids,
        campo_usuario="user"
    )

    resultado = (
        base[["user_id"]]
        .copy()
    )

    resultado["chatbot_conversaciones"] = 0
    resultado["chatbot_mensajes"] = 0

    if not conversaciones.empty:

        conteo = (
            conversaciones
            .groupby("_user_bcp")
            .size()
            .rename(
                "chatbot_conversaciones"
            )
            .reset_index()
            .rename(
                columns={
                    "_user_bcp": "user_id"
                }
            )
        )

        resultado = (
            resultado
            .drop(
                columns=[
                    "chatbot_conversaciones"
                ]
            )
            .merge(
                conteo,
                on="user_id",
                how="left"
            )
        )

    if not mensajes.empty:

        conteo = (
            mensajes
            .groupby("_user_bcp")
            .size()
            .rename(
                "chatbot_mensajes"
            )
            .reset_index()
            .rename(
                columns={
                    "_user_bcp": "user_id"
                }
            )
        )

        resultado = (
            resultado
            .drop(
                columns=[
                    "chatbot_mensajes"
                ]
            )
            .merge(
                conteo,
                on="user_id",
                how="left"
            )
        )

    for columna in [
        "chatbot_conversaciones",
        "chatbot_mensajes",
    ]:

        resultado[columna] = (
            resultado[columna]
            .fillna(0)
            .astype(int)
        )

    print(
        f"Participantes con conversación: "
        f"{(resultado['chatbot_conversaciones'] > 0).sum():,}"
    )

    print(
        f"Conversaciones: "
        f"{len(conversaciones):,}"
    )

    print(
        f"Mensajes: "
        f"{len(mensajes):,}"
    )

    return (
        resultado,
        conversaciones,
        mensajes
    )


# ============================================================
# 20. ALERTAS
# ============================================================

def procesar_alertas(
    db,
    base,
    object_ids,
    user_ids
):

    titulo("BCP | ALERTAS DE EMPLEO")

    df = consultar_por_usuarios(
        db,
        "jobalertrequests",
        object_ids,
        user_ids,
        campo_usuario="userId"
    )

    resultado = (
        base[["user_id"]]
        .copy()
    )

    resultado["alertas_empleo"] = 0

    if df.empty:

        return resultado, df

    conteo = (
        df
        .groupby("_user_bcp")
        .size()
        .rename("alertas_empleo")
        .reset_index()
        .rename(
            columns={
                "_user_bcp": "user_id"
            }
        )
    )

    resultado = (
        base[["user_id"]]
        .merge(
            conteo,
            on="user_id",
            how="left"
        )
    )

    resultado["alertas_empleo"] = (
        resultado["alertas_empleo"]
        .fillna(0)
        .astype(int)
    )

    print(
        f"Participantes con alertas: "
        f"{(resultado['alertas_empleo'] > 0).sum():,}"
    )

    print(
        f"Solicitudes de alerta: "
        f"{len(df):,}"
    )

    return resultado, df


# ============================================================
# 21. COMPATIBILIDAD - ANÁLISIS
# ============================================================

def procesar_compatibilidad(
    db,
    base,
    object_ids,
    user_ids
):

    titulo("BCP | COMPATIBILIDAD")

    df = consultar_por_usuarios(
        db,
        "jobcompatibilityanalyses",
        object_ids,
        user_ids,
        campo_usuario="userId"
    )

    resultado = (
        base[["user_id"]]
        .copy()
    )

    resultado["analisis_compatibilidad"] = 0
    resultado["compatibilidad_promedio"] = np.nan

    if df.empty:

        return resultado, df

    conteo = (
        df
        .groupby("_user_bcp")
        .size()
        .rename(
            "analisis_compatibilidad"
        )
    )

    if "compatibilityPercentage" in df.columns:

        df["compatibilityPercentage"] = (
            pd.to_numeric(
                df[
                    "compatibilityPercentage"
                ],
                errors="coerce"
            )
        )

        promedio = (
            df
            .groupby("_user_bcp")[
                "compatibilityPercentage"
            ]
            .mean()
            .rename(
                "compatibilidad_promedio"
            )
        )

    else:

        promedio = pd.Series(
            dtype=float,
            name="compatibilidad_promedio"
        )

    agregado = pd.concat(
        [
            conteo,
            promedio
        ],
        axis=1
    ).reset_index()

    agregado = agregado.rename(
        columns={
            "_user_bcp": "user_id"
        }
    )

    resultado = (
        base[["user_id"]]
        .merge(
            agregado,
            on="user_id",
            how="left"
        )
    )

    resultado["analisis_compatibilidad"] = (
        resultado["analisis_compatibilidad"]
        .fillna(0)
        .astype(int)
    )

    print(
        f"Participantes que utilizaron compatibilidad: "
        f"{(resultado['analisis_compatibilidad'] > 0).sum():,}"
    )

    print(
        f"Análisis realizados: "
        f"{len(df):,}"
    )

    return resultado, df


# ============================================================
# 22. DF_MATCHES
# ============================================================

def procesar_df_matches(
    db,
    base,
    df_cv,
    cv_ids
):

    titulo(
        "BCP | MATCHES CV ↔ OPORTUNIDADES"
    )

    df = consultar_por_cv(
        db,
        "df_matches",
        cv_ids,
        campo_cv="cv_id"
    )

    resultado = (
        base[["user_id"]]
        .copy()
    )

    resultado["matches_disponibles"] = 0
    resultado["score_match_promedio"] = np.nan
    resultado["score_match_maximo"] = np.nan

    if df.empty or df_cv.empty:

        return resultado, df

    mapa_cv = crear_mapa_cv_usuario(
        df_cv
    )

    df = (
        df.merge(
            mapa_cv,
            on="_cv_id",
            how="left"
        )
    )

    df = df.dropna(
        subset=["user_id"]
    )

    if df.empty:

        return resultado, df

    conteo = (
        df
        .groupby("user_id")
        .size()
        .rename(
            "matches_disponibles"
        )
    )

    if "score_total" in df.columns:

        df["score_total"] = (
            pd.to_numeric(
                df["score_total"],
                errors="coerce"
            )
        )

        promedio = (
            df
            .groupby("user_id")[
                "score_total"
            ]
            .mean()
            .rename(
                "score_match_promedio"
            )
        )

        maximo = (
            df
            .groupby("user_id")[
                "score_total"
            ]
            .max()
            .rename(
                "score_match_maximo"
            )
        )

    else:

        promedio = pd.Series(
            dtype=float,
            name="score_match_promedio"
        )

        maximo = pd.Series(
            dtype=float,
            name="score_match_maximo"
        )

    agregado = pd.concat(
        [
            conteo,
            promedio,
            maximo
        ],
        axis=1
    ).reset_index()

    resultado = (
        base[["user_id"]]
        .merge(
            agregado,
            on="user_id",
            how="left"
        )
    )

    resultado["matches_disponibles"] = (
        resultado["matches_disponibles"]
        .fillna(0)
        .astype(int)
    )

    print(
        f"Participantes con matches calculados: "
        f"{(resultado['matches_disponibles'] > 0).sum():,}"
    )

    print(
        f"Matches encontrados: "
        f"{len(df):,}"
    )

    return resultado, df


# ============================================================
# 23. EVENTOS
# ============================================================

def procesar_eventos(
    db,
    base,
    object_ids,
    user_ids
):

    titulo("BCP | EVENTOS")

    df = consultar_por_usuarios(
        db,
        "user_events",
        object_ids,
        user_ids,
        campo_usuario="userId"
    )

    resultado = (
        base[["user_id"]]
        .copy()
    )

    resultado["eventos_registrados"] = 0

    if df.empty:

        return resultado, df

    conteo = (
        df
        .groupby("_user_bcp")
        .size()
        .rename(
            "eventos_registrados"
        )
        .reset_index()
        .rename(
            columns={
                "_user_bcp": "user_id"
            }
        )
    )

    resultado = (
        base[["user_id"]]
        .merge(
            conteo,
            on="user_id",
            how="left"
        )
    )

    resultado["eventos_registrados"] = (
        resultado["eventos_registrados"]
        .fillna(0)
        .astype(int)
    )

    print(
        f"Participantes con registros de eventos: "
        f"{(resultado['eventos_registrados'] > 0).sum():,}"
    )

    print(
        f"Registros user_events: "
        f"{len(df):,}"
    )

    return resultado, df


# ============================================================
# 24. ACTIVIDAD DESDE EL EVENTO
# ============================================================

def crear_actividad(
    datasets
):

    titulo(
        "BCP | ACTIVIDAD DESDE EL EVENTO"
    )

    registros = []

    for funcionalidad, df in datasets.items():

        if df is None or df.empty:
            continue

        if "_user_bcp" not in df.columns:
            continue

        if "createdAt" not in df.columns:
            continue

        temp = df[
            [
                "_user_bcp",
                "createdAt"
            ]
        ].copy()

        temp["fecha"] = (
            pd.to_datetime(
                temp["createdAt"],
                errors="coerce"
            )
        )

        temp = temp.dropna(
            subset=["fecha"]
        )

        temp = temp[
            temp["fecha"]
            >= FECHA_EVENTO_BCP
        ]

        if temp.empty:
            continue

        temp["funcionalidad"] = (
            funcionalidad
        )

        temp = temp.rename(
            columns={
                "_user_bcp": "user_id"
            }
        )

        registros.append(
            temp[
                [
                    "user_id",
                    "fecha",
                    "funcionalidad"
                ]
            ]
        )

    if not registros:

        print(
            "No se encontraron acciones "
            "posteriores al evento."
        )

        return pd.DataFrame(
            columns=[
                "user_id",
                "fecha",
                "funcionalidad",
                "semana"
            ]
        )

    actividad = pd.concat(
        registros,
        ignore_index=True
    )

    actividad["semana"] = (
        actividad["fecha"]
        .dt.to_period("W")
        .astype(str)
    )

    actividad = actividad.sort_values(
        "fecha"
    )

    print(
        f"Acciones verificables desde 20/08/2026: "
        f"{len(actividad):,}"
    )

    print(
        f"Participantes con actividad: "
        f"{actividad['user_id'].nunique():,}"
    )

    return actividad


# ============================================================
# 25. RESUMEN DE ACTIVIDAD POR PARTICIPANTE
# ============================================================

def crear_resumen_actividad(
    base,
    actividad
):

    resultado = (
        base[["user_id"]]
        .copy()
    )

    resultado["actividad_total"] = 0
    resultado["funcionalidades_usadas"] = 0
    resultado["ultima_actividad"] = pd.NaT

    if actividad.empty:

        return resultado

    agregado = (
        actividad
        .groupby("user_id")
        .agg(
            actividad_total=(
                "funcionalidad",
                "size"
            ),
            funcionalidades_usadas=(
                "funcionalidad",
                "nunique"
            ),
            ultima_actividad=(
                "fecha",
                "max"
            )
        )
        .reset_index()
    )

    resultado = (
        base[["user_id"]]
        .merge(
            agregado,
            on="user_id",
            how="left"
        )
    )

    resultado["actividad_total"] = (
        resultado["actividad_total"]
        .fillna(0)
        .astype(int)
    )

    resultado["funcionalidades_usadas"] = (
        resultado["funcionalidades_usadas"]
        .fillna(0)
        .astype(int)
    )

    return resultado


# ============================================================
# 26. TABLA MAESTRA
# ============================================================

def construir_tabla_maestra(
    base,
    datasets_resumen
):

    titulo(
        "BCP | CONSTRUYENDO TABLA MAESTRA"
    )

    maestro = base.copy()

    for _, df in datasets_resumen.items():

        if df is None or df.empty:
            continue

        if "user_id" not in df.columns:
            continue

        columnas_nuevas = [
            columna
            for columna in df.columns
            if (
                columna == "user_id"
                or
                columna not in maestro.columns
            )
        ]

        maestro = maestro.merge(
            df[columnas_nuevas],
            on="user_id",
            how="left"
        )

    print(
        f"Filas tabla maestra: "
        f"{len(maestro):,}"
    )

    if len(maestro) != 51:

        print(
            "[AVISO] La tabla maestra "
            "no tiene exactamente 51 filas."
        )

    return maestro


# ============================================================
# 27. RESUMEN EJECUTIVO
# ============================================================

def crear_resumen_ejecutivo(
    maestro,
    actividad
):

    total = len(maestro)

    def contar_booleano(columna):

        if columna not in maestro.columns:
            return 0

        return int(
            maestro[columna]
            .fillna(False)
            .astype(bool)
            .sum()
        )

    def contar_mayor_cero(columna):

        if columna not in maestro.columns:
            return 0

        serie = pd.to_numeric(
            maestro[columna],
            errors="coerce"
        ).fillna(0)

        return int(
            (serie > 0).sum()
        )

    participantes_activos = (
        actividad["user_id"]
        .nunique()
        if not actividad.empty
        else 0
    )

    resumen = {

        "participantes_bcp":
            total,

        "participantes_con_actividad":
            participantes_activos,

        "porcentaje_con_actividad":
            porcentaje(
                participantes_activos,
                total
            ),

        "participantes_con_cv":
            contar_booleano(
                "tiene_cv"
            ),

        "porcentaje_con_cv":
            porcentaje(
                contar_booleano(
                    "tiene_cv"
                ),
                total
            ),

        "participantes_con_educacion":
            contar_mayor_cero(
                "educaciones"
            ),

        "participantes_con_experiencia":
            contar_mayor_cero(
                "experiencias"
            ),

        "participantes_con_habilidades":
            contar_mayor_cero(
                "total_skills"
            ),

        "ikigai_iniciado":
            contar_booleano(
                "ikigai_iniciado"
            ),

        "ikigai_completado":
            contar_booleano(
                "ikigai_completado"
            ),

        "ikigai_con_resultado":
            contar_booleano(
                "ikigai_resultado"
            ),

        "participantes_en_cursos":
            contar_mayor_cero(
                "cursos_inscritos"
            ),

        "participantes_evaluaciones":
            contar_mayor_cero(
                "evaluaciones_registros"
            ),

        "participantes_chatbot":
            contar_mayor_cero(
                "chatbot_conversaciones"
            ),

        "participantes_alertas":
            contar_mayor_cero(
                "alertas_empleo"
            ),

        "participantes_compatibilidad":
            contar_mayor_cero(
                "analisis_compatibilidad"
            ),

        "participantes_con_matches":
            contar_mayor_cero(
                "matches_disponibles"
            ),

        "participantes_eventos":
            contar_mayor_cero(
                "eventos_registrados"
            ),
    }

    return pd.DataFrame(
        [resumen]
    )


# ============================================================
# 28. EXPORTACIÓN SEGURA A EXCEL
# ============================================================

def preparar_para_excel(df):

    exportar = df.copy()

    for columna in exportar.columns:

        if exportar[columna].dtype != "object":
            continue

        def convertir(valor):

            if isinstance(valor, ObjectId):

                return str(valor)

            if isinstance(
                valor,
                (dict, list, tuple, set)
            ):

                return str(valor)

            return valor

        exportar[columna] = (
            exportar[columna]
            .apply(convertir)
        )

    return exportar


def exportar_resultados(
    resultados
):

    titulo(
        "BCP | EXPORTANDO INDICADORES"
    )

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with pd.ExcelWriter(
        ARCHIVO_SALIDA,
        engine="openpyxl"
    ) as writer:

        for nombre, df in resultados.items():

            if not isinstance(
                df,
                pd.DataFrame
            ):
                continue

            hoja = nombre[:31]

            exportar = preparar_para_excel(
                df
            )

            exportar.to_excel(
                writer,
                sheet_name=hoja,
                index=False
            )

    print(
        "\n[OK] Archivo generado:"
    )

    print(
        ARCHIVO_SALIDA
    )


# ============================================================
# 29. CONSTRUCTOR GENERAL
# ============================================================

def construir_indicadores_bcp():

    inicio = datetime.now()

    print("\n")
    print("#" * 70)
    print("#")
    print("# INDICADORES BCP")
    print("#")
    print("#" * 70)

    # --------------------------------------------------------
    # A. Participantes BCP
    # --------------------------------------------------------

    resultado_bcp = construir_bcp(
        exportar=False
    )

    base = crear_base_participantes(
        resultado_bcp
    )

    user_ids = resultado_bcp[
        "user_ids"
    ]

    object_ids = resultado_bcp[
        "user_object_ids"
    ]

    # --------------------------------------------------------
    # B. MongoDB
    # --------------------------------------------------------

    comprobar_conexion()

    db = get_db()

    # --------------------------------------------------------
    # C. CV
    # --------------------------------------------------------

    (
        resumen_cv,
        df_cv,
        cv_ids
    ) = procesar_cv(
        db,
        base,
        object_ids,
        user_ids
    )

    # --------------------------------------------------------
    # D. Educación
    # --------------------------------------------------------

    (
        resumen_educacion,
        df_educacion
    ) = procesar_educacion(
        db,
        base,
        df_cv,
        cv_ids
    )

    # --------------------------------------------------------
    # E. Experiencia
    # --------------------------------------------------------

    (
        resumen_experiencia,
        df_experiencia
    ) = procesar_experiencia(
        db,
        base,
        df_cv,
        cv_ids
    )

    # --------------------------------------------------------
    # F. Skills
    # --------------------------------------------------------

    (
        resumen_skills,
        df_skills
    ) = procesar_habilidades(
        db,
        base,
        df_cv,
        cv_ids
    )

    # --------------------------------------------------------
    # G. Ikigai
    # --------------------------------------------------------

    (
        resumen_ikigai,
        df_ikigai,
        df_ikigai_resultados
    ) = procesar_ikigai(
        db,
        base,
        object_ids,
        user_ids
    )

    df_perfil_ikigai = (
        procesar_perfil_ikigai(
            df_ikigai_resultados
        )
    )

    # --------------------------------------------------------
    # H. Cursos
    # --------------------------------------------------------

    (
        resumen_cursos,
        df_cursos
    ) = procesar_cursos(
        db,
        base,
        object_ids,
        user_ids
    )

    # --------------------------------------------------------
    # I. Evaluaciones
    # --------------------------------------------------------

    (
        resumen_evaluaciones,
        df_evaluaciones,
        df_quiz_resultados
    ) = procesar_evaluaciones(
        db,
        base,
        object_ids,
        user_ids
    )

    # --------------------------------------------------------
    # J. Chatbot
    # --------------------------------------------------------

    (
        resumen_chatbot,
        df_conversaciones,
        df_mensajes
    ) = procesar_chatbot(
        db,
        base,
        object_ids,
        user_ids
    )

    # --------------------------------------------------------
    # K. Alertas
    # --------------------------------------------------------

    (
        resumen_alertas,
        df_alertas
    ) = procesar_alertas(
        db,
        base,
        object_ids,
        user_ids
    )

    # --------------------------------------------------------
    # L. Compatibilidad
    # --------------------------------------------------------

    (
        resumen_compatibilidad,
        df_compatibilidad
    ) = procesar_compatibilidad(
        db,
        base,
        object_ids,
        user_ids
    )

    # --------------------------------------------------------
    # M. Matches
    # --------------------------------------------------------

    (
        resumen_matches,
        df_matches
    ) = procesar_df_matches(
        db,
        base,
        df_cv,
        cv_ids
    )

    # --------------------------------------------------------
    # N. Eventos
    # --------------------------------------------------------

    (
        resumen_eventos,
        df_eventos
    ) = procesar_eventos(
        db,
        base,
        object_ids,
        user_ids
    )

    # --------------------------------------------------------
    # O. Actividad desde evento
    # --------------------------------------------------------

    actividad = crear_actividad(
        {
            "ikigai":
                df_ikigai,

            "ikigai_resultado":
                df_ikigai_resultados,

            "cursos":
                df_cursos,

            "evaluaciones":
                df_evaluaciones,

            "chatbot_conversaciones":
                df_conversaciones,

            "chatbot_mensajes":
                df_mensajes,

            "alertas":
                df_alertas,

            "compatibilidad":
                df_compatibilidad,

            "eventos":
                df_eventos,
        }
    )

    resumen_actividad = (
        crear_resumen_actividad(
            base,
            actividad
        )
    )

    # --------------------------------------------------------
    # P. Tabla maestra
    # --------------------------------------------------------

    maestro = construir_tabla_maestra(
        base,
        {
            "cv":
                resumen_cv,

            "educacion":
                resumen_educacion,

            "experiencia":
                resumen_experiencia,

            "skills":
                resumen_skills,

            "ikigai":
                resumen_ikigai,

            "cursos":
                resumen_cursos,

            "evaluaciones":
                resumen_evaluaciones,

            "chatbot":
                resumen_chatbot,

            "alertas":
                resumen_alertas,

            "compatibilidad":
                resumen_compatibilidad,

            "matches":
                resumen_matches,

            "eventos":
                resumen_eventos,

            "actividad":
                resumen_actividad,
        }
    )

    # --------------------------------------------------------
    # Q. Resumen ejecutivo
    # --------------------------------------------------------

    resumen = crear_resumen_ejecutivo(
        maestro,
        actividad
    )

    # --------------------------------------------------------
    # R. Datasets de salida
    # --------------------------------------------------------

    resultados = {

        "Resumen":
            resumen,

        "Participantes":
            maestro,

        "Actividad":
            actividad,

        "CV":
            df_cv,

        "Educacion":
            df_educacion,

        "Experiencia":
            df_experiencia,

        "Skills":
            df_skills,

        "Ikigai":
            df_ikigai,

        "Ikigai_Resultados":
            df_ikigai_resultados,

        "Ikigai_Perfil":
            df_perfil_ikigai,

        "Cursos":
            df_cursos,

        "Evaluaciones":
            df_evaluaciones,

        "Quiz_Resultados":
            df_quiz_resultados,

        "Chatbot_Conversaciones":
            df_conversaciones,

        "Chatbot_Mensajes":
            df_mensajes,

        "Alertas":
            df_alertas,

        "Compatibilidad":
            df_compatibilidad,

        "Matches":
            df_matches,

        "Eventos":
            df_eventos,
    }

    # --------------------------------------------------------
    # S. Exportación
    # --------------------------------------------------------

    exportar_resultados(
        resultados
    )

    # --------------------------------------------------------
    # T. Resultado final
    # --------------------------------------------------------

    fin = datetime.now()

    duracion = (
        fin - inicio
    ).total_seconds()

    titulo(
        "BCP | RESULTADO DE INDICADORES"
    )

    print("\n")

    print(
        resumen.to_string(
            index=False
        )
    )

    print(
        f"\n\nDuración: "
        f"{duracion:.2f} segundos"
    )

    print(
        "\n[OK] INDICADORES BCP "
        "CONSTRUIDOS CORRECTAMENTE"
    )

    print(
        "\nArchivo:"
    )

    print(
        ARCHIVO_SALIDA
    )

    return resultados


# ============================================================
# 30. EJECUCIÓN
# ============================================================

if __name__ == "__main__":

    try:

        resultados = (
            construir_indicadores_bcp()
        )

    except KeyboardInterrupt:

        print(
            "\n\n[AVISO] Proceso cancelado "
            "por el usuario."
        )

    except Exception as error:

        print("\n")
        print("=" * 70)
        print("ERROR EN INDICADORES BCP")
        print("=" * 70)

        print(
            f"\nTipo: "
            f"{type(error).__name__}"
        )

        print(
            f"\nDetalle:\n{error}"
        )

        print("\n")
        print(
            "Revisa el traceback mostrado "
            "a continuación."
        )

        print("=" * 70)

        raise