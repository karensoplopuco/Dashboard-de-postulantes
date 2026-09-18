# ============================================================
# ANALISIS BCP
# ============================================================
#
# Segunda capa analítica del dashboard BCP.
#
# Usa:
#   constructor_bcp.py
#   indicadores_bcp.py
#
# Analiza:
#   - Ikigai
#   - Fortalezas
#   - Aspectos por desarrollar
#   - Motivaciones / intereses
#   - Dirección profesional
#   - Áreas sugeridas
#   - Ingreso actual y deseado
#   - Hard skills / soft skills
#   - Demanda laboral
#   - Requisitos de empresas
#   - Relación participantes ↔ mercado
#
# IMPORTANTE:
#   - NO modifica MongoDB
#   - NO inventa categorías
#   - Mantiene trazabilidad con datos originales
#
# ============================================================

from pathlib import Path
from datetime import datetime
from collections import Counter
import ast
import json
import re
import unicodedata

import numpy as np
import pandas as pd


# ============================================================
# IMPORTS DEL PROYECTO
# ============================================================

try:
    from conexion import get_db, comprobar_conexion
    from indicadores_bcp import construir_indicadores_bcp

except ImportError:
    from scripts.conexion import get_db, comprobar_conexion
    from scripts.indicadores_bcp import construir_indicadores_bcp


# ============================================================
# CONFIGURACION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

ARCHIVO_SALIDA = DATA_DIR / "analisis_bcp.xlsx"

FECHA_EVENTO_BCP = pd.Timestamp("2026-08-20")


# ============================================================
# UTILIDADES
# ============================================================

def titulo(texto):

    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def normalizar_texto(valor):

    if valor is None:
        return ""

    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass

    texto = str(valor).strip().lower()

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def limpiar_texto_visual(valor):

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

    return re.sub(
        r"\s+",
        " ",
        texto
    )


def convertir_lista(valor):
    """
    Convierte strings/listas/diccionarios en una lista de textos
    sin inventar información.
    """

    if valor is None:
        return []

    if isinstance(valor, list):

        resultado = []

        for elemento in valor:

            resultado.extend(
                convertir_lista(elemento)
            )

        return resultado

    if isinstance(valor, tuple):

        resultado = []

        for elemento in valor:

            resultado.extend(
                convertir_lista(elemento)
            )

        return resultado

    if isinstance(valor, set):

        return convertir_lista(
            list(valor)
        )

    if isinstance(valor, dict):

        resultado = []

        for _, contenido in valor.items():

            resultado.extend(
                convertir_lista(contenido)
            )

        return resultado

    try:

        if pd.isna(valor):
            return []

    except Exception:
        pass

    texto = str(valor).strip()

    if not texto:
        return []

    # --------------------------------------------------------
    # Intentar JSON
    # --------------------------------------------------------

    if (
        texto.startswith("[")
        or texto.startswith("{")
    ):

        try:

            objeto = json.loads(
                texto
            )

            return convertir_lista(
                objeto
            )

        except Exception:
            pass

        try:

            objeto = ast.literal_eval(
                texto
            )

            return convertir_lista(
                objeto
            )

        except Exception:
            pass

    return [texto]


def convertir_numero(valor):
    """
    Intenta extraer un número sin asumir moneda.
    """

    if valor is None:
        return np.nan

    if isinstance(
        valor,
        (int, float, np.number)
    ):

        try:

            if pd.isna(valor):
                return np.nan

        except Exception:
            pass

        return float(valor)

    if isinstance(valor, dict):

        candidatos = [
            "value",
            "amount",
            "salary",
            "income",
            "min",
            "max"
        ]

        for campo in candidatos:

            if campo in valor:

                numero = convertir_numero(
                    valor[campo]
                )

                if not pd.isna(numero):
                    return numero

        return np.nan

    texto = str(valor).strip()

    if not texto:
        return np.nan

    texto = (
        texto
        .replace(",", "")
        .replace("S/", "")
        .replace("s/", "")
        .replace("$", "")
    )

    encontrados = re.findall(
        r"-?\d+(?:\.\d+)?",
        texto
    )

    if not encontrados:
        return np.nan

    try:
        return float(
            encontrados[0]
        )

    except Exception:
        return np.nan


# ============================================================
# ANALISIS DE CAMPOS DE TEXTO
# ============================================================

def explotar_campo_texto(
    df,
    campo,
    nombre_dimension
):
    """
    Convierte un campo de Ikigai en formato largo.

    Mantiene:
        user_id
        dimension
        valor_original
        valor_normalizado
    """

    columnas = [
        "user_id",
        "dimension",
        "valor_original",
        "valor_normalizado"
    ]

    if df.empty:
        return pd.DataFrame(
            columns=columnas
        )

    if campo not in df.columns:
        return pd.DataFrame(
            columns=columnas
        )

    filas = []

    for _, row in df.iterrows():

        user_id = row.get(
            "user_id"
        )

        valores = convertir_lista(
            row.get(campo)
        )

        for valor in valores:

            original = limpiar_texto_visual(
                valor
            )

            normalizado = normalizar_texto(
                valor
            )

            if not normalizado:
                continue

            filas.append(
                {
                    "user_id":
                        user_id,

                    "dimension":
                        nombre_dimension,

                    "valor_original":
                        original,

                    "valor_normalizado":
                        normalizado
                }
            )

    return pd.DataFrame(
        filas,
        columns=columnas
    )


# ============================================================
# FRECUENCIAS EXACTAS
# ============================================================

def crear_frecuencias_texto(df_largo):

    columnas = [
        "dimension",
        "valor",
        "participantes",
        "registros"
    ]

    if df_largo.empty:

        return pd.DataFrame(
            columns=columnas
        )

    frecuencia = (
        df_largo
        .groupby(
            [
                "dimension",
                "valor_normalizado"
            ],
            dropna=False
        )
        .agg(
            participantes=(
                "user_id",
                "nunique"
            ),
            registros=(
                "user_id",
                "size"
            )
        )
        .reset_index()
        .rename(
            columns={
                "valor_normalizado":
                    "valor"
            }
        )
        .sort_values(
            [
                "dimension",
                "participantes",
                "registros"
            ],
            ascending=[
                True,
                False,
                False
            ]
        )
    )

    return frecuencia


# ============================================================
# PALABRAS FRECUENTES
# ============================================================

STOPWORDS = {
    "de", "la", "el", "los", "las",
    "y", "o", "en", "un", "una",
    "unos", "unas", "para", "por",
    "con", "sin", "del", "al",
    "que", "se", "es", "son",
    "como", "su", "sus", "mi",
    "mis", "tu", "tus", "a",
    "e", "lo", "le", "les",
    "me", "te", "nos", "ya",
    "muy", "mas", "más", "ser",
    "tener", "hacer", "esta",
    "este", "estos", "estas"
}


def crear_palabras_frecuentes(
    df_largo,
    minimo_longitud=4
):

    columnas = [
        "dimension",
        "palabra",
        "frecuencia"
    ]

    if df_largo.empty:

        return pd.DataFrame(
            columns=columnas
        )

    resultados = []

    for dimension, grupo in (
        df_largo.groupby(
            "dimension"
        )
    ):

        contador = Counter()

        for texto in grupo[
            "valor_normalizado"
        ].dropna():

            palabras = re.findall(
                r"\b[a-z0-9]+\b",
                texto
            )

            palabras = [
                palabra
                for palabra in palabras
                if (
                    len(palabra)
                    >= minimo_longitud
                    and
                    palabra not in STOPWORDS
                )
            ]

            contador.update(
                palabras
            )

        for palabra, frecuencia in (
            contador.most_common(100)
        ):

            resultados.append(
                {
                    "dimension":
                        dimension,

                    "palabra":
                        palabra,

                    "frecuencia":
                        frecuencia
                }
            )

    return pd.DataFrame(
        resultados,
        columns=columnas
    )


# ============================================================
# IKIGAI
# ============================================================

def analizar_ikigai(
    df_perfil
):

    titulo(
        "BCP | ANALISIS DE IKIGAI"
    )

    if df_perfil.empty:

        print(
            "[AVISO] No hay perfiles "
            "Ikigai para analizar."
        )

        return {
            "ikigai_largo":
                pd.DataFrame(),

            "ikigai_frecuencias":
                pd.DataFrame(),

            "ikigai_palabras":
                pd.DataFrame()
        }

    configuracion = {

        "fortalezas":
            "Fortalezas",

        "mejoras":
            "Aspectos por desarrollar",

        "motivacion":
            "Motivaciones",

        "problemas_interes":
            "Problemas de interés",

        "direccion_profesional":
            "Dirección profesional",

        "areas_trabajo_sugeridas":
            "Áreas de trabajo sugeridas",

        "perfil_profesional":
            "Perfil profesional"
    }

    largos = []

    for campo, dimension in (
        configuracion.items()
    ):

        temp = explotar_campo_texto(
            df_perfil,
            campo,
            dimension
        )

        if not temp.empty:

            largos.append(
                temp
            )

    if largos:

        ikigai_largo = pd.concat(
            largos,
            ignore_index=True
        )

    else:

        ikigai_largo = pd.DataFrame(
            columns=[
                "user_id",
                "dimension",
                "valor_original",
                "valor_normalizado"
            ]
        )

    frecuencias = crear_frecuencias_texto(
        ikigai_largo
    )

    palabras = crear_palabras_frecuentes(
        ikigai_largo
    )

    print(
        f"Perfiles analizados: "
        f"{df_perfil['user_id'].nunique():,}"
    )

    print(
        f"Elementos de introspección: "
        f"{len(ikigai_largo):,}"
    )

    if not frecuencias.empty:

        print(
            "\nPrincipales elementos "
            "por dimensión:"
        )

        for dimension in (
            frecuencias[
                "dimension"
            ].unique()
        ):

            print(
                f"\n--- {dimension} ---"
            )

            muestra = (
                frecuencias[
                    frecuencias[
                        "dimension"
                    ]
                    == dimension
                ]
                .head(5)
            )

            for _, row in muestra.iterrows():

                print(
                    f"{row['valor']} | "
                    f"{int(row['participantes'])} "
                    "participante(s)"
                )

    return {
        "ikigai_largo":
            ikigai_largo,

        "ikigai_frecuencias":
            frecuencias,

        "ikigai_palabras":
            palabras
    }


# ============================================================
# INGRESOS IKIGAI
# ============================================================

def analizar_ingresos(
    df_perfil
):

    titulo(
        "BCP | SITUACION Y EXPECTATIVAS DE INGRESO"
    )

    columnas_salida = [
        "user_id",
        "ingreso_actual_original",
        "ingreso_deseado_original",
        "ingreso_actual_num",
        "ingreso_deseado_num",
        "diferencia_ingreso",
        "variacion_porcentual"
    ]

    if df_perfil.empty:

        return (
            pd.DataFrame(
                columns=columnas_salida
            ),
            pd.DataFrame()
        )

    df = pd.DataFrame()

    df["user_id"] = (
        df_perfil["user_id"]
    )

    df[
        "ingreso_actual_original"
    ] = df_perfil.get(
        "ingreso_actual_estimado"
    )

    df[
        "ingreso_deseado_original"
    ] = df_perfil.get(
        "ingreso_deseado_estimado"
    )

    df["ingreso_actual_num"] = (
        df[
            "ingreso_actual_original"
        ]
        .apply(convertir_numero)
    )

    df["ingreso_deseado_num"] = (
        df[
            "ingreso_deseado_original"
        ]
        .apply(convertir_numero)
    )

    df["diferencia_ingreso"] = (
        df["ingreso_deseado_num"]
        -
        df["ingreso_actual_num"]
    )

    df["variacion_porcentual"] = np.where(
        df["ingreso_actual_num"] > 0,

        (
            df["diferencia_ingreso"]
            /
            df["ingreso_actual_num"]
        ) * 100,

        np.nan
    )

    validos_actual = (
        df["ingreso_actual_num"]
        .dropna()
    )

    validos_deseado = (
        df["ingreso_deseado_num"]
        .dropna()
    )

    ambos = df.dropna(
        subset=[
            "ingreso_actual_num",
            "ingreso_deseado_num"
        ]
    )

    resumen = {
        "participantes_con_ingreso_actual":
            len(validos_actual),

        "participantes_con_ingreso_deseado":
            len(validos_deseado),

        "participantes_con_ambos":
            len(ambos),

        "ingreso_actual_promedio":
            validos_actual.mean()
            if len(validos_actual)
            else np.nan,

        "ingreso_actual_mediana":
            validos_actual.median()
            if len(validos_actual)
            else np.nan,

        "ingreso_deseado_promedio":
            validos_deseado.mean()
            if len(validos_deseado)
            else np.nan,

        "ingreso_deseado_mediana":
            validos_deseado.median()
            if len(validos_deseado)
            else np.nan,

        "diferencia_promedio":
            ambos[
                "diferencia_ingreso"
            ].mean()
            if len(ambos)
            else np.nan
    }

    df_resumen = pd.DataFrame(
        [resumen]
    )

    print(
        "Participantes con ingreso actual "
        f"interpretable: {len(validos_actual):,}"
    )

    print(
        "Participantes con ingreso deseado "
        f"interpretable: {len(validos_deseado):,}"
    )

    print(
        "Participantes con ambos valores: "
        f"{len(ambos):,}"
    )

    print(
        "\n[IMPORTANTE] Los valores se mantienen "
        "sin asumir moneda ni periodicidad."
    )

    return (
        df,
        df_resumen
    )


# ============================================================
# HABILIDADES DE PARTICIPANTES
# ============================================================

def analizar_habilidades(
    df_skills
):

    titulo(
        "BCP | HABILIDADES DE PARTICIPANTES"
    )

    columnas = [
        "tipo",
        "habilidad",
        "participantes",
        "registros"
    ]

    if df_skills.empty:

        return pd.DataFrame(
            columns=columnas
        )

    if "name" not in df_skills.columns:

        print(
            "[AVISO] Skills no contiene "
            "campo name."
        )

        return pd.DataFrame(
            columns=columnas
        )

    df = df_skills.copy()

    if "user_id" not in df.columns:

        print(
            "[AVISO] Skills no tiene user_id."
        )

        return pd.DataFrame(
            columns=columnas
        )

    df["habilidad"] = (
        df["name"]
        .apply(normalizar_texto)
    )

    if "type" in df.columns:

        df["tipo"] = (
            df["type"]
            .fillna("sin_tipo")
            .astype(str)
            .str.strip()
            .str.lower()
        )

    else:

        df["tipo"] = "sin_tipo"

    df = df[
        df["habilidad"] != ""
    ]

    resumen = (
        df
        .groupby(
            [
                "tipo",
                "habilidad"
            ]
        )
        .agg(
            participantes=(
                "user_id",
                "nunique"
            ),
            registros=(
                "user_id",
                "size"
            )
        )
        .reset_index()
        .sort_values(
            [
                "tipo",
                "participantes",
                "registros"
            ],
            ascending=[
                True,
                False,
                False
            ]
        )
    )

    print(
        f"Habilidades registradas: "
        f"{len(df):,}"
    )

    print(
        f"Habilidades normalizadas únicas: "
        f"{df['habilidad'].nunique():,}"
    )

    for tipo in resumen[
        "tipo"
    ].unique():

        print(
            f"\n--- {tipo.upper()} ---"
        )

        muestra = resumen[
            resumen["tipo"] == tipo
        ].head(10)

        for _, row in muestra.iterrows():

            print(
                f"{row['habilidad']} | "
                f"{int(row['participantes'])} "
                "participante(s)"
            )

    return resumen


# ============================================================
# MERCADO LABORAL - JOBS
# ============================================================

def cargar_jobs(
    db
):

    titulo(
        "BCP | MERCADO LABORAL"
    )

    if "jobs" not in (
        db.list_collection_names()
    ):

        print(
            "[AVISO] No existe jobs."
        )

        return pd.DataFrame()

    documentos = list(
        db["jobs"].find({})
    )

    if not documentos:

        return pd.DataFrame()

    df = pd.DataFrame(
        documentos
    )

    print(
        f"Ofertas disponibles en colección jobs: "
        f"{len(df):,}"
    )

    if "status" in df.columns:

        print(
            "\nEstados de las ofertas:"
        )

        print(
            df["status"]
            .fillna("[SIN ESTADO]")
            .astype(str)
            .value_counts()
            .head(20)
            .to_string()
        )

    return df


# ============================================================
# DISTRIBUCION DE OFERTAS
# ============================================================

def analizar_jobs(
    df_jobs
):

    if df_jobs.empty:

        return {
            "jobs_departamentos":
                pd.DataFrame(),

            "jobs_modalidad":
                pd.DataFrame(),

            "jobs_titulos":
                pd.DataFrame()
        }

    # --------------------------------------------------------
    # Departamento
    # --------------------------------------------------------

    if "department" in df_jobs.columns:

        departamentos = (
            df_jobs["department"]
            .fillna("Sin especificar")
            .astype(str)
            .value_counts()
            .rename_axis("departamento")
            .reset_index(
                name="ofertas"
            )
        )

    else:

        departamentos = pd.DataFrame()

    # --------------------------------------------------------
    # Modalidad
    # --------------------------------------------------------

    if "modality" in df_jobs.columns:

        modalidad = (
            df_jobs["modality"]
            .fillna("Sin especificar")
            .astype(str)
            .value_counts()
            .rename_axis("modalidad")
            .reset_index(
                name="ofertas"
            )
        )

    else:

        modalidad = pd.DataFrame()

    # --------------------------------------------------------
    # Títulos
    # --------------------------------------------------------

    if "title" in df_jobs.columns:

        titulos = (
            df_jobs["title"]
            .fillna("")
            .astype(str)
            .apply(normalizar_texto)
        )

        titulos = titulos[
            titulos != ""
        ]

        titulos = (
            titulos
            .value_counts()
            .rename_axis("puesto")
            .reset_index(
                name="ofertas"
            )
        )

    else:

        titulos = pd.DataFrame()

    return {
        "jobs_departamentos":
            departamentos,

        "jobs_modalidad":
            modalidad,

        "jobs_titulos":
            titulos
    }


# ============================================================
# REQUISITOS DEL MERCADO
# ============================================================

def cargar_requisitos(
    db
):

    titulo(
        "BCP | REQUISITOS DEL MERCADO"
    )

    if "jobs_requisitos" not in (
        db.list_collection_names()
    ):

        print(
            "[AVISO] No existe jobs_requisitos."
        )

        return pd.DataFrame()

    documentos = list(
        db["jobs_requisitos"].find({})
    )

    if not documentos:

        return pd.DataFrame()

    df = pd.DataFrame(
        documentos
    )

    print(
        f"Requisitos disponibles: "
        f"{len(df):,}"
    )

    return df


def analizar_requisitos(
    df_requisitos
):

    if df_requisitos.empty:

        return pd.DataFrame()

    if "text" not in df_requisitos.columns:

        return pd.DataFrame()

    df = df_requisitos.copy()

    df["requisito_normalizado"] = (
        df["text"]
        .apply(normalizar_texto)
    )

    df = df[
        df["requisito_normalizado"]
        != ""
    ]

    columnas_agrupacion = [
        "requisito_normalizado"
    ]

    if "type" in df.columns:

        df["tipo"] = (
            df["type"]
            .fillna("sin_tipo")
            .astype(str)
            .str.lower()
            .str.strip()
        )

        columnas_agrupacion = [
            "tipo",
            "requisito_normalizado"
        ]

    resumen = (
        df
        .groupby(
            columnas_agrupacion
        )
        .size()
        .rename("frecuencia")
        .reset_index()
        .sort_values(
            "frecuencia",
            ascending=False
        )
    )

    print(
        f"Requisitos normalizados: "
        f"{len(resumen):,}"
    )

    return resumen


# ============================================================
# PALABRAS DE DEMANDA
# ============================================================

def analizar_palabras_demanda(
    df_requisitos
):

    columnas = [
        "palabra",
        "frecuencia"
    ]

    if df_requisitos.empty:

        return pd.DataFrame(
            columns=columnas
        )

    if "text" not in df_requisitos.columns:

        return pd.DataFrame(
            columns=columnas
        )

    contador = Counter()

    for texto in (
        df_requisitos["text"]
        .dropna()
    ):

        texto = normalizar_texto(
            texto
        )

        palabras = re.findall(
            r"\b[a-z0-9+#.]+\b",
            texto
        )

        palabras = [
            palabra
            for palabra in palabras
            if (
                len(palabra) >= 3
                and
                palabra not in STOPWORDS
            )
        ]

        contador.update(
            palabras
        )

    resultados = [
        {
            "palabra":
                palabra,

            "frecuencia":
                frecuencia
        }

        for palabra, frecuencia
        in contador.most_common(300)
    ]

    return pd.DataFrame(
        resultados,
        columns=columnas
    )


# ============================================================
# PARTICIPANTES VS DEMANDA
# ============================================================

def comparar_skills_demanda(
    df_habilidades,
    df_requisitos
):
    """
    Comparación textual conservadora.

    No afirma que una persona "cumple" o "no cumple".
    Solo identifica si el nombre normalizado de una habilidad
    aparece textualmente en requisitos publicados.
    """

    titulo(
        "BCP | HABILIDADES ↔ DEMANDA LABORAL"
    )

    columnas = [
        "tipo",
        "habilidad",
        "participantes",
        "apariciones_en_requisitos",
        "presente_en_demanda"
    ]

    if (
        df_habilidades.empty
        or
        df_requisitos.empty
    ):

        return pd.DataFrame(
            columns=columnas
        )

    if "text" not in df_requisitos.columns:

        return pd.DataFrame(
            columns=columnas
        )

    textos_requisitos = (
        df_requisitos["text"]
        .dropna()
        .apply(normalizar_texto)
        .tolist()
    )

    resultados = []

    for _, row in (
        df_habilidades.iterrows()
    ):

        habilidad = row.get(
            "habilidad",
            ""
        )

        if not habilidad:
            continue

        apariciones = sum(
            1
            for requisito in textos_requisitos
            if habilidad in requisito
        )

        resultados.append(
            {
                "tipo":
                    row.get("tipo"),

                "habilidad":
                    habilidad,

                "participantes":
                    row.get(
                        "participantes",
                        0
                    ),

                "apariciones_en_requisitos":
                    apariciones,

                "presente_en_demanda":
                    apariciones > 0
            }
        )

    df = pd.DataFrame(
        resultados,
        columns=columnas
    )

    if not df.empty:

        df = df.sort_values(
            [
                "apariciones_en_requisitos",
                "participantes"
            ],
            ascending=[
                False,
                False
            ]
        )

        presentes = int(
            df[
                "presente_en_demanda"
            ].sum()
        )

        print(
            f"Habilidades comparadas: "
            f"{len(df):,}"
        )

        print(
            "Habilidades con coincidencia textual "
            f"en requisitos: {presentes:,}"
        )

    return df


# ============================================================
# RESUMEN PARA DASHBOARD
# ============================================================

def crear_resumen_analitico(
    resultados_indicadores,
    df_perfil_ikigai,
    df_ingresos,
    df_habilidades,
    df_comparacion
):

    maestro = resultados_indicadores.get(
        "Participantes",
        pd.DataFrame()
    )

    resumen = {
        "participantes_bcp":
            len(maestro),

        "perfiles_ikigai_analizados":
            (
                df_perfil_ikigai[
                    "user_id"
                ].nunique()
                if (
                    not df_perfil_ikigai.empty
                    and
                    "user_id"
                    in df_perfil_ikigai.columns
                )
                else 0
            ),

        "participantes_con_ingreso_actual":
            (
                df_ingresos[
                    "ingreso_actual_num"
                ].notna().sum()
                if (
                    not df_ingresos.empty
                    and
                    "ingreso_actual_num"
                    in df_ingresos.columns
                )
                else 0
            ),

        "participantes_con_ingreso_deseado":
            (
                df_ingresos[
                    "ingreso_deseado_num"
                ].notna().sum()
                if (
                    not df_ingresos.empty
                    and
                    "ingreso_deseado_num"
                    in df_ingresos.columns
                )
                else 0
            ),

        "habilidades_unicas":
            (
                df_habilidades[
                    "habilidad"
                ].nunique()
                if (
                    not df_habilidades.empty
                    and
                    "habilidad"
                    in df_habilidades.columns
                )
                else 0
            ),

        "habilidades_con_coincidencia_demanda":
            (
                int(
                    df_comparacion[
                        "presente_en_demanda"
                    ].sum()
                )
                if (
                    not df_comparacion.empty
                    and
                    "presente_en_demanda"
                    in df_comparacion.columns
                )
                else 0
            )
    }

    return pd.DataFrame(
        [resumen]
    )


# ============================================================
# PREPARAR EXCEL
# ============================================================

def preparar_para_excel(df):

    exportar = df.copy()

    for columna in exportar.columns:

        if exportar[columna].dtype != "object":
            continue

        exportar[columna] = (
            exportar[columna]
            .apply(
                lambda valor:
                    json.dumps(
                        valor,
                        ensure_ascii=False,
                        default=str
                    )
                    if isinstance(
                        valor,
                        (
                            dict,
                            list,
                            tuple,
                            set
                        )
                    )
                    else str(valor)
                    if valor is not None
                    else None
            )
        )

    return exportar


# ============================================================
# EXPORTAR
# ============================================================

def exportar_analisis(
    datasets
):

    titulo(
        "BCP | EXPORTANDO ANALISIS"
    )

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with pd.ExcelWriter(
        ARCHIVO_SALIDA,
        engine="openpyxl"
    ) as writer:

        for nombre, df in (
            datasets.items()
        ):

            if not isinstance(
                df,
                pd.DataFrame
            ):
                continue

            hoja = nombre[:31]

            preparado = preparar_para_excel(
                df
            )

            preparado.to_excel(
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
# CONSTRUCTOR GENERAL
# ============================================================

def construir_analisis_bcp():

    inicio = datetime.now()

    print("\n")
    print("#" * 70)
    print("#")
    print("# ANALISIS BCP")
    print("#")
    print("#" * 70)

    # --------------------------------------------------------
    # 1. Ejecutar indicadores
    # --------------------------------------------------------

    resultados_indicadores = (
        construir_indicadores_bcp()
    )

    # --------------------------------------------------------
    # 2. Obtener datasets
    # --------------------------------------------------------

    df_perfil_ikigai = (
        resultados_indicadores.get(
            "Ikigai_Perfil",
            pd.DataFrame()
        )
        .copy()
    )

    df_skills = (
        resultados_indicadores.get(
            "Skills",
            pd.DataFrame()
        )
        .copy()
    )

    # --------------------------------------------------------
    # 3. Ikigai
    # --------------------------------------------------------

    resultado_ikigai = (
        analizar_ikigai(
            df_perfil_ikigai
        )
    )

    df_ikigai_largo = (
        resultado_ikigai[
            "ikigai_largo"
        ]
    )

    df_ikigai_frecuencias = (
        resultado_ikigai[
            "ikigai_frecuencias"
        ]
    )

    df_ikigai_palabras = (
        resultado_ikigai[
            "ikigai_palabras"
        ]
    )

    # --------------------------------------------------------
    # 4. Ingresos
    # --------------------------------------------------------

    (
        df_ingresos,
        df_ingresos_resumen
    ) = analizar_ingresos(
        df_perfil_ikigai
    )

    # --------------------------------------------------------
    # 5. Habilidades
    # --------------------------------------------------------

    df_habilidades = (
        analizar_habilidades(
            df_skills
        )
    )

    # --------------------------------------------------------
    # 6. MongoDB
    # --------------------------------------------------------

    titulo(
    "BCP | REUTILIZANDO CONEXIÓN MONGODB"
      )

    db = get_db()

    print(
    "[OK] Cliente MongoDB reutilizado"
    )

    # --------------------------------------------------------
    # 7. Mercado
    # --------------------------------------------------------

    df_jobs = cargar_jobs(
        db
    )

    resultado_jobs = (
        analizar_jobs(
            df_jobs
        )
    )

    # --------------------------------------------------------
    # 8. Requisitos
    # --------------------------------------------------------

    df_requisitos = cargar_requisitos(
        db
    )

    df_requisitos_resumen = (
        analizar_requisitos(
            df_requisitos
        )
    )

    df_demanda_palabras = (
        analizar_palabras_demanda(
            df_requisitos
        )
    )

    # --------------------------------------------------------
    # 9. Participantes vs mercado
    # --------------------------------------------------------

    df_comparacion = (
        comparar_skills_demanda(
            df_habilidades,
            df_requisitos
        )
    )

    # --------------------------------------------------------
    # 10. Resumen
    # --------------------------------------------------------

    df_resumen = (
        crear_resumen_analitico(
            resultados_indicadores,
            df_perfil_ikigai,
            df_ingresos,
            df_habilidades,
            df_comparacion
        )
    )

    # --------------------------------------------------------
    # 11. Datasets finales
    # --------------------------------------------------------

    datasets = {

        "Resumen_Analitico":
            df_resumen,

        "Ikigai_Perfil":
            df_perfil_ikigai,

        "Ikigai_Detalle":
            df_ikigai_largo,

        "Ikigai_Frecuencias":
            df_ikigai_frecuencias,

        "Ikigai_Palabras":
            df_ikigai_palabras,

        "Ingresos":
            df_ingresos,

        "Ingresos_Resumen":
            df_ingresos_resumen,

        "Habilidades":
            df_habilidades,

        "Jobs":
            df_jobs,

        "Jobs_Departamentos":
            resultado_jobs[
                "jobs_departamentos"
            ],

        "Jobs_Modalidad":
            resultado_jobs[
                "jobs_modalidad"
            ],

        "Jobs_Titulos":
            resultado_jobs[
                "jobs_titulos"
            ],

        "Requisitos":
            df_requisitos,

        "Requisitos_Resumen":
            df_requisitos_resumen,

        "Demanda_Palabras":
            df_demanda_palabras,

        "Skills_vs_Demanda":
            df_comparacion,
    }

    # --------------------------------------------------------
    # 12. Exportar
    # --------------------------------------------------------

    exportar_analisis(
        datasets
    )

    # --------------------------------------------------------
    # 13. Resultado terminal
    # --------------------------------------------------------

    fin = datetime.now()

    duracion = (
        fin - inicio
    ).total_seconds()

    titulo(
        "BCP | RESULTADO DEL ANALISIS"
    )

    print("\n")

    print(
        df_resumen.to_string(
            index=False
        )
    )

    print(
        f"\nDuración total: "
        f"{duracion:.2f} segundos"
    )

    print(
        "\n[OK] ANALISIS BCP "
        "CONSTRUIDO CORRECTAMENTE"
    )

    print(
        "\nArchivo:"
    )

    print(
        ARCHIVO_SALIDA
    )

    return datasets


# ============================================================
# EJECUCION
# ============================================================

if __name__ == "__main__":

    try:

        resultados = (
            construir_analisis_bcp()
        )

    except KeyboardInterrupt:

        print(
            "\n\n[AVISO] Proceso cancelado."
        )

    except Exception as error:

        print("\n")
        print("=" * 70)
        print("ERROR EN ANALISIS BCP")
        print("=" * 70)

        print(
            f"\nTipo: "
            f"{type(error).__name__}"
        )

        print(
            f"\nDetalle:\n{error}"
        )

        print("=" * 70)

        raise