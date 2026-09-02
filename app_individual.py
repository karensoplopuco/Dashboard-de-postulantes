import os
import json
from datetime import date, timedelta

import pandas as pd
import streamlit as st
import altair as alt


# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================

st.set_page_config(
    page_title="Dashboard Individual",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PALETA DE COLORES
# ============================================================

COLOR_SIDEBAR = "#3D8290"

COLOR_YELLOW = "#ffde59"
COLOR_GREEN = "#cbeba3"
COLOR_BLUE = "#68b7ea"
COLOR_ORANGE = "#ffbd59"
COLOR_PURPLE = "#966fb4"
COLOR_AC = "#addfcd"
COLOR_ROSA = "#e0a2c5"

COLOR_TEXT = "#1F2933"
COLOR_SECONDARY = "#6B7280"
COLOR_BACKGROUND = "#F7F8FA"


# ============================================================
# ESTILOS CSS
# ============================================================

st.markdown(
    f"""
    <style>

    /* ========================================================
       CONFIGURACIÓN GENERAL
    ======================================================== */

    html,
    body,
    [class*="css"] {{
        font-family:
            "Trebuchet MS",
            "Segoe UI",
            sans-serif;
    }}

    .stApp {{
        background-color: {COLOR_BACKGROUND};
        color: {COLOR_TEXT};
    }}

    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }}


    /* ========================================================
       SIDEBAR
    ======================================================== */

    [data-testid="stSidebar"] {{
        background-color: {COLOR_SIDEBAR};
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p {{
        color: #FFFFFF !important;
    }}


    /* ========================================================
       INPUT BUSCADOR
    ======================================================== */

    [data-testid="stSidebar"] input {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 7px !important;
    }}

    [data-testid="stSidebar"] input::placeholder {{
        color: #6B7280 !important;
    }}


    /* ========================================================
       SELECTBOX
    ======================================================== */

    [data-testid="stSidebar"] [data-baseweb="select"] {{
        background-color: #FFFFFF !important;
        border-radius: 7px !important;
    }}

    [data-testid="stSidebar"] [data-baseweb="select"] * {{
        color: #000000 !important;
    }}


    /* ========================================================
       DATE INPUT
    ======================================================== */

    [data-testid="stSidebar"] .stDateInput input {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }}

    [data-testid="stSidebar"] .stDateInput > div > div {{
        background-color: #FFFFFF !important;
        border-radius: 7px !important;
    }}


    /* ========================================================
       BOTONES
    ======================================================== */

    [data-testid="stSidebar"] .stButton > button {{
        width: 100% !important;
        min-height: 42px !important;

        background-color: #FFFFFF !important;
        color: #000000 !important;

        border: 1px solid #FFFFFF !important;
        border-radius: 7px !important;

        font-weight: 700 !important;
        opacity: 1 !important;
    }}

    [data-testid="stSidebar"] .stButton > button p {{
        color: #000000 !important;
    }}

    [data-testid="stSidebar"] .stButton > button span {{
        color: #000000 !important;
    }}

    [data-testid="stSidebar"] .stButton > button:hover {{
        background-color: #F1F1F1 !important;
        color: #000000 !important;
        border-color: #FFFFFF !important;
    }}


    /* ========================================================
       TÍTULOS
    ======================================================== */

    .dashboard-title {{
        font-size: 34px;
        font-weight: 800;
        color: {COLOR_TEXT};
        margin-bottom: 4px;
    }}

    .dashboard-subtitle {{
        font-size: 15px;
        color: {COLOR_SECONDARY};
        margin-bottom: 25px;
    }}

    .section-title {{
        font-size: 22px;
        font-weight: 750;
        color: {COLOR_TEXT};
        margin-top: 22px;
        margin-bottom: 12px;
    }}

    .section-line {{
        height: 3px;
        background-color: {COLOR_YELLOW};
        border-radius: 4px;
        margin-bottom: 18px;
    }}


    /* ========================================================
       KPI
    ======================================================== */

    [data-testid="stMetric"] {{
        background-color: #D1E2E8;
        border: 1px solid #C6D9E0;
        border-radius: 10px;
        padding: 11px 14px;
        min-height: 88px;
        box-sizing: border-box;
    }}

    [data-testid="stMetricLabel"] {{
        color: #6B7280 !important;
        font-size: 12px !important;
        font-weight: 700 !important;
    }}

    [data-testid="stMetricValue"] {{
        color: #1F2933 !important;
        font-size: 23px !important;
        font-weight: 500 !important;
    }}


    /* ========================================================
       EXPANDERS
    ======================================================== */

    [data-testid="stExpander"] {{
        border: 1px solid #D9DEE3 !important;
        border-radius: 9px !important;
        background-color: #FFFFFF !important;
    }}


    /* ========================================================
       INFORMACIÓN DEL POSTULANTE
    ======================================================== */

    .plain-label {{
        font-size: 12px;
        color: #6B7280;
        margin-bottom: 3px;
        font-weight: 600;
    }}

    .plain-value {{
        font-size: 15px;
        color: #1F2933;
        font-weight: 400;
        word-break: break-word;
    }}


    /* ========================================================
       MARCOS DE GRÁFICOS
       
       IMPORTANTE:
       YA NO usamos:
       [data-testid="stVerticalBlockBorderWrapper"]
       
       porque ese selector afecta contenedores de Streamlit
       de manera global.
    ======================================================== */

    .st-key-grafico_postulaciones,
    .st-key-grafico_empleabilidad,
    .st-key-grafico_actividad,
    .st-key-grafico_creditos {{

        width: 100% !important;

        box-sizing: border-box !important;

        margin-top: 8px !important;
        margin-bottom: 20px !important;

        padding: 0 !important;

        background: #FFFFFF !important;

        border: 1.5px solid #C9CED4 !important;

        border-radius: 12px !important;

        overflow: hidden !important;

        box-shadow: none !important;
    }}


    /* ========================================================
       QUITAR ESPACIOS INTERNOS DEL CONTENEDOR
    ======================================================== */

    .st-key-grafico_postulaciones > div,
    .st-key-grafico_empleabilidad > div,
    .st-key-grafico_actividad > div,
    .st-key-grafico_creditos > div {{

        padding: 0 !important;
        margin: 0 !important;

        border: none !important;
        box-shadow: none !important;

        width: 100% !important;
    }}


    /* ========================================================
       CONTENEDOR DEL ALTAIR
    ======================================================== */

    .st-key-grafico_postulaciones [data-testid="stAltairChart"],
    .st-key-grafico_empleabilidad [data-testid="stAltairChart"],
    .st-key-grafico_actividad [data-testid="stAltairChart"],
    .st-key-grafico_creditos [data-testid="stAltairChart"] {{

        width: 100% !important;

        margin: 0 !important;
        padding: 0 !important;

        background: transparent !important;
    }}


    /* ========================================================
       IFRAME / CANVAS DEL GRÁFICO
    ======================================================== */

    .st-key-grafico_postulaciones iframe,
    .st-key-grafico_empleabilidad iframe,
    .st-key-grafico_actividad iframe,
    .st-key-grafico_creditos iframe {{

        display: block !important;

        width: 100% !important;

        margin: 0 !important;
        padding: 0 !important;

        border: none !important;

        background: transparent !important;
    }}


    /* ========================================================
       AYUDA TABLA
    ======================================================== */

    .table-help {{
        color: #6B7280;
        font-size: 13px;
        margin-top: -6px;
        margin-bottom: 12px;
    }}


    /* ========================================================
       DATAFRAME
    ======================================================== */

    [data-testid="stDataFrame"] {{
        border-radius: 9px;
        overflow: hidden;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_entero(valor, default=0):

    try:

        if pd.isna(valor):
            return default

        return int(float(valor))

    except Exception:

        return default


def obtener_decimal(valor, default=None):

    try:

        if valor is None:
            return default

        if pd.isna(valor):
            return default

        return float(valor)

    except Exception:

        return default


def obtener_texto(valor, default="No disponible"):

    if valor is None:
        return default

    try:

        if pd.isna(valor):
            return default

    except Exception:
        pass

    texto = str(valor).strip()

    if texto == "":
        return default

    if texto.lower() in [
        "nan",
        "none",
        "null"
    ]:

        return default

    return texto


def obtener_booleano(valor):

    if isinstance(valor, bool):
        return valor

    if valor is None:
        return False

    try:

        if pd.isna(valor):
            return False

    except Exception:
        pass

    return (
        str(valor)
        .strip()
        .lower()
        in [
            "true",
            "1",
            "yes",
            "si",
            "sí"
        ]
    )


def capitalizar_nombre(valor):

    texto = obtener_texto(
        valor,
        ""
    )

    if not texto:
        return ""

    return texto.strip().title()


def formatear_lista(valor):

    texto = obtener_texto(
        valor,
        ""
    )

    if not texto:
        return []

    try:

        contenido = json.loads(texto)

        if isinstance(contenido, list):

            resultado = []

            for item in contenido:

                if isinstance(item, dict):

                    nombre = (
                        item.get("nombre")
                        or item.get("name")
                        or item.get("skill")
                        or item.get("idioma")
                        or item.get("language")
                    )

                    if nombre:

                        resultado.append(
                            str(nombre).strip()
                        )

                else:

                    item_texto = str(item).strip()

                    if item_texto:

                        resultado.append(
                            item_texto
                        )

            return resultado

    except Exception:
        pass

    for separador in [
        "|",
        ";",
        "\n"
    ]:

        if separador in texto:

            return [
                item.strip()
                for item in texto.split(separador)
                if item.strip()
            ]

    return [texto]


# ============================================================
# BUSCAR VALOR FLEXIBLE
# ============================================================

def buscar_valor_flexible(
    registro,
    columnas_posibles
):

    for columna in columnas_posibles:

        if columna in registro.index:

            valor = registro[columna]

            if valor is None:
                continue

            try:

                if pd.isna(valor):
                    continue

            except Exception:
                pass

            texto = str(valor).strip()

            if texto.lower() in [
                "",
                "nan",
                "none",
                "null"
            ]:

                continue

            return valor


    def normalizar_columna(texto):

        return (
            str(texto)
            .lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
        )


    columnas_normalizadas = {
        normalizar_columna(columna): columna
        for columna in registro.index
    }


    for columna in columnas_posibles:

        clave = normalizar_columna(
            columna
        )

        if clave in columnas_normalizadas:

            columna_real = (
                columnas_normalizadas[clave]
            )

            valor = registro[
                columna_real
            ]

            if valor is None:
                continue

            try:

                if pd.isna(valor):
                    continue

            except Exception:
                pass

            texto = str(valor).strip()

            if texto.lower() not in [
                "",
                "nan",
                "none",
                "null"
            ]:

                return valor

    return None


# ============================================================
# SCORE DE EMPLEABILIDAD
# ============================================================

def obtener_score_empleabilidad(registro):

    columnas_posibles = [

        "score_empleabilidad",
        "score_employability",
        "employability_score",
        "employabilityScore",
        "scoreEmployability",

        "puntaje_empleabilidad",
        "puntajeEmployability",

        "puntaje",
        "score",

        "percentage",
        "porcentaje",

        "porcentaje_empleabilidad",
        "employabilityPercentage",

        "score_total",
        "puntaje_total"

    ]

    valor = buscar_valor_flexible(
        registro,
        columnas_posibles
    )

    return obtener_decimal(
        valor,
        None
    )


# ============================================================
# NIVEL DE EMPLEABILIDAD
# ============================================================

def obtener_nivel_empleabilidad(registro):

    columnas_posibles = [

        "nivel_empleabilidad",
        "nivel_employability",

        "employability_level",
        "employabilityLevel",

        "level",
        "nivel",

        "categoria_empleabilidad",
        "categoria",

        "category",

        "employabilityCategory"

    ]

    valor = buscar_valor_flexible(
        registro,
        columnas_posibles
    )

    if valor is None:
        return "No evaluado"

    texto = obtener_texto(
        valor,
        "No evaluado"
    )

    if texto.lower() in [
        "0",
        "0.0",
        "nan",
        "none",
        "null",
        ""
    ]:

        return "No evaluado"

    return texto


# ============================================================
# MOSTRAR KPI
# ============================================================

def mostrar_kpi(
    titulo,
    valor
):

    st.metric(
        label=titulo,
        value=valor
    )


# ============================================================
# MOSTRAR SECCIÓN
# ============================================================

def mostrar_seccion(
    titulo
):

    st.markdown(
        f"""
        <div class="section-title">
            {titulo}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-line"></div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MOSTRAR INFORMACIÓN
# ============================================================

def mostrar_info_simple(
    etiqueta,
    valor
):

    st.markdown(
        f"""
        <div class="plain-label">
            {etiqueta}
        </div>

        <div class="plain-value">
            {valor}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# CONTENEDOR DE GRÁFICO
#
# AQUÍ ESTÁ EL CAMBIO PRINCIPAL
# ============================================================

def mostrar_grafico_enmarcado(
    grafico,
    key
):

    with st.container(
        key=key
    ):

        st.altair_chart(
            grafico,
            use_container_width=True
        )


# ============================================================
# CARGAR DATOS
# ============================================================

@st.cache_data
def cargar_datos():

    ruta = (
        "data/cache/"
        "postulantes_individual.csv"
    )

    if not os.path.exists(ruta):

        st.error(
            f"No se encontró el archivo: {ruta}"
        )

        return pd.DataFrame()

    df = pd.read_csv(
        ruta,
        low_memory=False
    )


    # ========================================================
    # ID
    # ========================================================

    if "_id_postulante" in df.columns:

        df[
            "_id_postulante"
        ] = (
            df[
                "_id_postulante"
            ]
            .astype(str)
            .str.strip()
        )


    # ========================================================
    # FECHA
    # ========================================================

    if "fecha_registro" in df.columns:

        df[
            "fecha_registro"
        ] = pd.to_datetime(
            df[
                "fecha_registro"
            ],
            errors="coerce"
        )

    else:

        df["fecha_registro"] = pd.NaT


    # ========================================================
    # EDAD
    # ========================================================

    if "edad_dashboard" in df.columns:

        df[
            "edad_dashboard"
        ] = pd.to_numeric(
            df[
                "edad_dashboard"
            ],
            errors="coerce"
        )

    elif "edad" in df.columns:

        df[
            "edad_dashboard"
        ] = pd.to_numeric(
            df[
                "edad"
            ],
            errors="coerce"
        )

    else:

        df[
            "edad_dashboard"
        ] = None


    # ========================================================
    # NOMBRE
    # ========================================================

    if "nombre_completo" not in df.columns:

        if "nombre" not in df.columns:
            df["nombre"] = ""

        if "apellido" not in df.columns:
            df["apellido"] = ""

        df[
            "nombre"
        ] = (
            df[
                "nombre"
            ]
            .fillna("")
            .astype(str)
        )

        df[
            "apellido"
        ] = (
            df[
                "apellido"
            ]
            .fillna("")
            .astype(str)
        )

        df[
            "nombre_completo"
        ] = (
            df["nombre"]
            .str.strip()
            + " "
            + df["apellido"]
            .str.strip()
        ).str.strip()

    else:

        df[
            "nombre_completo"
        ] = (
            df[
                "nombre_completo"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
        )


    # ========================================================
    # TIPO DE POSTULANTE
    # ========================================================

    if "tipo_postulante" in df.columns:

        df[
            "tipo_postulante_dashboard"
        ] = (
            df[
                "tipo_postulante"
            ]
            .fillna(
                "No especificado"
            )
            .astype(str)
            .str.strip()
        )

    else:

        df[
            "tipo_postulante_dashboard"
        ] = "No especificado"


    # ========================================================
    # NORMALIZAR TIPO
    # ========================================================

    def normalizar_tipo(valor):

        texto = (
            str(valor)
            .strip()
            .lower()
        )

        if texto in [
            "estudiante",
            "estudiantes"
        ]:

            return "Estudiante"

        if texto in [
            "practicante",
            "practicantes",
            "prácticante",
            "prácticantes"
        ]:

            return "Practicante"

        if texto in [
            "egresado",
            "egresados"
        ]:

            return "Egresado"

        if texto in [
            "profesional",
            "profesionales"
        ]:

            return "Profesional"

        return "No especificado"


    df[
        "tipo_postulante_dashboard"
    ] = (
        df[
            "tipo_postulante_dashboard"
        ]
        .apply(normalizar_tipo)
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

        "cantidad_analisis_compatibilidad",
        "score_compatibilidad_promedio",
        "ultimo_score_compatibilidad",

        "creditos_disponibles",
        "creditos_utilizados",
        "cantidad_operaciones_creditos",

        "creditos_funcionalidad_mas_usada",

        "perfil_completado_pct"

    ]


    for columna in columnas_numericas:

        if columna in df.columns:

            df[
                columna
            ] = pd.to_numeric(
                df[
                    columna
                ],
                errors="coerce"
            ).fillna(0)


    # ========================================================
    # SCORE EMPLEABILIDAD
    # ========================================================

    if "score_empleabilidad" in df.columns:

        df[
            "score_empleabilidad"
        ] = pd.to_numeric(
            df[
                "score_empleabilidad"
            ],
            errors="coerce"
        )


    # ========================================================
    # BOOLEANOS
    # ========================================================

    columnas_booleanas = [

        "tiene_cv",
        "tiene_postulaciones",
        "uso_ia",
        "participo_evento",
        "tiene_experiencia",
        "perfil_completo"

    ]


    for columna in columnas_booleanas:

        if columna in df.columns:

            df[columna] = (
                df[columna]
                .apply(obtener_booleano)
            )


    # ========================================================
    # DUPLICADOS
    # ========================================================

    if "_id_postulante" in df.columns:

        df = df.drop_duplicates(
            subset=[
                "_id_postulante"
            ],
            keep="first"
        )


    # ========================================================
    # ORDEN
    # ========================================================

    df = df.sort_values(
        by=[
            "nombre_completo"
        ],
        ascending=True
    )

    return df.reset_index(
        drop=True
    )


# ============================================================
# CARGAR DATASET
# ============================================================

df = cargar_datos()

if df.empty:
    st.stop()


# ============================================================
# FECHAS DISPONIBLES
# ============================================================

fechas_validas = (
    df[
        "fecha_registro"
    ]
    .dropna()
)

if fechas_validas.empty:

    fecha_min_data = (
        date.today()
        - timedelta(days=365)
    )

    fecha_max_data = date.today()

else:

    fecha_min_data = (
        fechas_validas
        .min()
        .date()
    )

    fecha_max_data = (
        fechas_validas
        .max()
        .date()
    )


# ============================================================
# ESTADOS INICIALES
# ============================================================

if "tipo_filtro" not in st.session_state:

    st.session_state[
        "tipo_filtro"
    ] = "Todos"


if "experiencia_filtro" not in st.session_state:

    st.session_state[
        "experiencia_filtro"
    ] = "Todas"


if "periodo_filtro" not in st.session_state:

    st.session_state[
        "periodo_filtro"
    ] = "Completo"


if "fecha_personalizada" not in st.session_state:

    st.session_state[
        "fecha_personalizada"
    ] = (
        fecha_min_data,
        fecha_max_data
    )


if "buscar_postulante" not in st.session_state:

    st.session_state[
        "buscar_postulante"
    ] = ""


if "postulante_seleccionado" not in st.session_state:

    st.session_state[
        "postulante_seleccionado"
    ] = None


# ============================================================
# LIMPIAR FILTROS
# ============================================================

def limpiar_filtros():

    st.session_state[
        "tipo_filtro"
    ] = "Todos"

    st.session_state[
        "experiencia_filtro"
    ] = "Todas"

    st.session_state[
        "periodo_filtro"
    ] = "Completo"

    st.session_state[
        "fecha_personalizada"
    ] = (
        fecha_min_data,
        fecha_max_data
    )

    st.session_state[
        "buscar_postulante"
    ] = ""


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        ## Filtros

        Filtra y busca postulantes.
        """
    )

    st.text_input(
        "Buscar postulante",
        placeholder="Nombre o ID...",
        key="buscar_postulante"
    )


    tipos_disponibles = [

        "Todos",
        "Estudiante",
        "Practicante",
        "Egresado",
        "Profesional",
        "No especificado"

    ]


    st.selectbox(
        "Tipo de postulante",
        tipos_disponibles,
        key="tipo_filtro"
    )


    rangos_experiencia = [

        "Todas",
        "Sin experiencia",
        "Menos de 1 año",
        "1 a 3 años",
        "3 a 5 años",
        "Más de 5 años"

    ]


    st.selectbox(
        "Experiencia laboral",
        rangos_experiencia,
        key="experiencia_filtro"
    )


    periodos = [

        "Últimos 7 días",
        "Últimos 30 días",
        "Últimos 3 meses",
        "Último año",
        "Completo",
        "Personalizado"

    ]


    st.selectbox(
        "Periodo de registro",
        periodos,
        key="periodo_filtro"
    )


    if (
        st.session_state[
            "periodo_filtro"
        ]
        == "Personalizado"
    ):

        st.date_input(
            "Rango personalizado",
            min_value=fecha_min_data,
            max_value=fecha_max_data,
            key="fecha_personalizada"
        )


    st.markdown("")


    st.button(
        "Limpiar filtros",
        key="btn_limpiar_filtros",
        on_click=limpiar_filtros
    )


    st.markdown(
        "<div style='height:5px;'></div>",
        unsafe_allow_html=True
    )


    if st.button(
        "Recargar datos",
        key="btn_recargar"
    ):

        cargar_datos.clear()

        st.rerun()


# ============================================================
# APLICAR FILTROS
# ============================================================

df_filtrado = df.copy()


# ============================================================
# FILTRO TIPO
# ============================================================

tipo_seleccionado = (
    st.session_state[
        "tipo_filtro"
    ]
)

if tipo_seleccionado != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado[
            "tipo_postulante_dashboard"
        ]
        == tipo_seleccionado
    ]


# ============================================================
# FILTRO EXPERIENCIA
# ============================================================

experiencia_seleccionada = (
    st.session_state[
        "experiencia_filtro"
    ]
)

if experiencia_seleccionada != "Todas":

    meses_experiencia = pd.to_numeric(
        df_filtrado[
            "meses_experiencia"
        ],
        errors="coerce"
    ).fillna(0)


    if experiencia_seleccionada == "Sin experiencia":

        df_filtrado = df_filtrado[
            meses_experiencia <= 0
        ]


    elif experiencia_seleccionada == "Menos de 1 año":

        df_filtrado = df_filtrado[
            (meses_experiencia > 0)
            &
            (meses_experiencia < 12)
        ]


    elif experiencia_seleccionada == "1 a 3 años":

        df_filtrado = df_filtrado[
            (meses_experiencia >= 12)
            &
            (meses_experiencia < 36)
        ]


    elif experiencia_seleccionada == "3 a 5 años":

        df_filtrado = df_filtrado[
            (meses_experiencia >= 36)
            &
            (meses_experiencia < 60)
        ]


    elif experiencia_seleccionada == "Más de 5 años":

        df_filtrado = df_filtrado[
            meses_experiencia >= 60
        ]


# ============================================================
# FILTRO PERIODO
# ============================================================

periodo_seleccionado = (
    st.session_state[
        "periodo_filtro"
    ]
)

if periodo_seleccionado != "Completo":

    if not fechas_validas.empty:

        fecha_max_filtro = (
            fechas_validas.max()
        )

    else:

        fecha_max_filtro = (
            pd.Timestamp.today()
        )


    if periodo_seleccionado == "Últimos 7 días":

        fecha_inicio = (
            fecha_max_filtro
            - pd.Timedelta(days=7)
        )

        fecha_fin = fecha_max_filtro


    elif periodo_seleccionado == "Últimos 30 días":

        fecha_inicio = (
            fecha_max_filtro
            - pd.Timedelta(days=30)
        )

        fecha_fin = fecha_max_filtro


    elif periodo_seleccionado == "Últimos 3 meses":

        fecha_inicio = (
            fecha_max_filtro
            - pd.DateOffset(months=3)
        )

        fecha_fin = fecha_max_filtro


    elif periodo_seleccionado == "Último año":

        fecha_inicio = (
            fecha_max_filtro
            - pd.DateOffset(years=1)
        )

        fecha_fin = fecha_max_filtro


    elif periodo_seleccionado == "Personalizado":

        rango = (
            st.session_state[
                "fecha_personalizada"
            ]
        )

        fecha_inicio = pd.Timestamp(
            rango[0]
        )

        fecha_fin = (
            pd.Timestamp(
                rango[1]
            )
            + pd.Timedelta(days=1)
            - pd.Timedelta(seconds=1)
        )


    df_filtrado = df_filtrado[
        df_filtrado[
            "fecha_registro"
        ].notna()
        &
        (
            df_filtrado[
                "fecha_registro"
            ]
            >= fecha_inicio
        )
        &
        (
            df_filtrado[
                "fecha_registro"
            ]
            <= fecha_fin
        )
    ]


# ============================================================
# BUSCADOR
# ============================================================

texto_busqueda = (
    st.session_state[
        "buscar_postulante"
    ]
    .strip()
    .lower()
)

if texto_busqueda:

    coincide_nombre = (
        df_filtrado[
            "nombre_completo"
        ]
        .str.lower()
        .str.contains(
            texto_busqueda,
            na=False,
            regex=False
        )
    )


    coincide_id = (
        df_filtrado[
            "_id_postulante"
        ]
        .astype(str)
        .str.lower()
        .str.contains(
            texto_busqueda,
            na=False,
            regex=False
        )
    )


    df_filtrado = df_filtrado[
        coincide_nombre
        |
        coincide_id
    ]


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
    """
    <div class="dashboard-title">
        Dashboard Individual
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="dashboard-subtitle">
        Análisis individual del perfil y actividad de los postulantes
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# VALIDAR RESULTADOS
# ============================================================

if df_filtrado.empty:

    st.warning(
        "No se encontraron postulantes con los filtros seleccionados."
    )

    st.info(
        "Prueba cambiando los filtros seleccionados."
    )

    st.stop()


# ============================================================
# SELECCIÓN AUTOMÁTICA
# ============================================================

ids_filtrados = (
    df_filtrado[
        "_id_postulante"
    ]
    .tolist()
)

if (
    st.session_state[
        "postulante_seleccionado"
    ]
    not in ids_filtrados
):

    st.session_state[
        "postulante_seleccionado"
    ] = ids_filtrados[0]


id_seleccionado = (
    st.session_state[
        "postulante_seleccionado"
    ]
)


# ============================================================
# OBTENER POSTULANTE
# ============================================================

postulante_df = df[
    df[
        "_id_postulante"
    ]
    == id_seleccionado
]

if postulante_df.empty:

    st.error(
        "No se encontró el postulante seleccionado."
    )

    st.stop()


postulante = (
    postulante_df
    .iloc[0]
)


# ============================================================
# DATOS BÁSICOS
# ============================================================

nombre_completo = capitalizar_nombre(
    postulante.get(
        "nombre_completo",
        "Postulante"
    )
)


email = obtener_texto(
    postulante.get(
        "email"
    ),
    "No registrado"
)


fecha_registro = postulante.get(
    "fecha_registro"
)


if pd.notna(fecha_registro):

    fecha_registro_texto = (
        pd.to_datetime(
            fecha_registro
        )
        .strftime(
            "%d/%m/%Y"
        )
    )

else:

    fecha_registro_texto = "No registrada"


# ============================================================
# TIPO
# ============================================================

tipo_postulante = obtener_texto(
    postulante.get(
        "tipo_postulante_dashboard"
    ),
    "No especificado"
)


# ============================================================
# CARRERA
# ============================================================

carrera = obtener_texto(
    postulante.get(
        "profesion"
    ),
    "No especificada"
)


# ============================================================
# INFORMACIÓN DEL POSTULANTE
# ============================================================

mostrar_seccion(
    "Información del postulante"
)


i1, i2, i3, i4, i5 = st.columns(5)


with i1:

    mostrar_info_simple(
        "Nombre",
        nombre_completo
    )


with i2:

    mostrar_info_simple(
        "Correo",
        email
    )


with i3:

    mostrar_info_simple(
        "Fecha de registro",
        fecha_registro_texto
    )


with i4:

    mostrar_info_simple(
        "Tipo de postulante",
        tipo_postulante
    )


with i5:

    mostrar_info_simple(
        "Carrera",
        carrera
    )


# ============================================================
# RESUMEN DEL POSTULANTE
# ============================================================

mostrar_seccion(
    "Resumen del postulante"
)


perfil_pct = obtener_decimal(
    postulante.get(
        "perfil_completado_pct"
    ),
    0
)


total_postulaciones = obtener_entero(
    postulante.get(
        "cantidad_postulaciones"
    )
)


nivel_empleabilidad = obtener_nivel_empleabilidad(
    postulante
)


creditos_disponibles = obtener_decimal(
    postulante.get(
        "creditos_disponibles"
    ),
    0
)


r1, r2, r3, r4 = st.columns(4)


with r1:

    mostrar_kpi(
        "Perfil completado",
        f"{perfil_pct:.0f}%"
    )


with r2:

    mostrar_kpi(
        "Postulaciones",
        total_postulaciones
    )


with r3:

    mostrar_kpi(
        "Empleabilidad",
        nivel_empleabilidad
    )


with r4:

    mostrar_kpi(
        "Créditos disponibles",
        f"{creditos_disponibles:g}"
    )


# ============================================================
# PERFIL PROFESIONAL
# ============================================================

mostrar_seccion(
    "Perfil profesional"
)


cantidad_habilidades = obtener_entero(
    postulante.get(
        "cantidad_habilidades"
    )
)


cantidad_idiomas = obtener_entero(
    postulante.get(
        "cantidad_idiomas"
    )
)


p1, p2 = st.columns(2)


with p1:

    mostrar_kpi(
        "Habilidades",
        cantidad_habilidades
    )


with p2:

    mostrar_kpi(
        "Idiomas",
        cantidad_idiomas
    )


# ============================================================
# HARD SKILLS / SOFT SKILLS
# ============================================================

d1, d2 = st.columns(2)


with d1:

    with st.expander(
        "Hard Skills",
        expanded=False
    ):

        hard_skills = formatear_lista(
            postulante.get(
                "hard_skills_detalle"
            )
        )

        if hard_skills:

            for skill in hard_skills:

                st.write(
                    f"• {skill}"
                )

        else:

            st.info(
                "No se registraron Hard Skills."
            )


with d2:

    with st.expander(
        "Soft Skills",
        expanded=False
    ):

        soft_skills = formatear_lista(
            postulante.get(
                "soft_skills_detalle"
            )
        )

        if soft_skills:

            for skill in soft_skills:

                st.write(
                    f"• {skill}"
                )

        else:

            st.info(
                "No se registraron Soft Skills."
            )


# ============================================================
# IDIOMAS
# ============================================================

with st.expander(
    "Idiomas",
    expanded=False
):

    idiomas_detalle = formatear_lista(
        postulante.get(
            "idiomas_detalle"
        )
    )

    if idiomas_detalle:

        for idioma in idiomas_detalle:

            st.write(
                f"• {idioma}"
            )

    else:

        st.info(
            "No se registraron idiomas."
        )


# ============================================================
# POSTULACIONES
# ============================================================

mostrar_seccion(
    "Postulaciones"
)


pendientes = obtener_entero(
    postulante.get(
        "postulaciones_pendientes"
    )
)


revision = obtener_entero(
    postulante.get(
        "postulaciones_revision"
    )
)


aceptadas = obtener_entero(
    postulante.get(
        "postulaciones_aceptadas"
    )
)


rechazadas = obtener_entero(
    postulante.get(
        "postulaciones_rechazadas"
    )
)


a1, a2, a3, a4, a5 = st.columns(5)


with a1:

    mostrar_kpi(
        "Total",
        total_postulaciones
    )


with a2:

    mostrar_kpi(
        "Pendientes",
        pendientes
    )


with a3:

    mostrar_kpi(
        "En revisión",
        revision
    )


with a4:

    mostrar_kpi(
        "Aceptadas",
        aceptadas
    )


with a5:

    mostrar_kpi(
        "Rechazadas",
        rechazadas
    )


# ============================================================
# GRÁFICO DE POSTULACIONES
# ============================================================

postulaciones_chart = pd.DataFrame({

    "Estado": [
        "Pendientes",
        "En revisión",
        "Aceptadas",
        "Rechazadas"
    ],

    "Cantidad": [
        pendientes,
        revision,
        aceptadas,
        rechazadas
    ]

})


chart_postulaciones = (

    alt.Chart(
        postulaciones_chart
    )

    .mark_bar(
        color=COLOR_AC,
        cornerRadiusTopLeft=5,
        cornerRadiusTopRight=5
    )

    .encode(

        x=alt.X(
            "Estado:N",
            title=None,
            axis=alt.Axis(
                labelAngle=0
            )
        ),

        y=alt.Y(
            "Cantidad:Q",
            title="Cantidad",
            scale=alt.Scale(
                domainMin=0
            ),
            axis=alt.Axis(
                tickMinStep=1,
                format="d"
            )
        ),

        tooltip=[

            alt.Tooltip(
                "Estado:N",
                title="Estado"
            ),

            alt.Tooltip(
                "Cantidad:Q",
                title="Cantidad"
            )

        ]

    )

    .properties(
        height=300
    )

    # ========================================================
    # ESTO HACE QUE EL GRÁFICO NO CREE SU PROPIO RECTÁNGULO
    # ========================================================

    .configure(
        background="transparent",
        padding=0
    )

    .configure_view(
        stroke=None
    )
)


mostrar_grafico_enmarcado(
    chart_postulaciones,
    "grafico_postulaciones"
)


# ============================================================
# EMPLEABILIDAD
# ============================================================

mostrar_seccion(
    "Empleabilidad"
)


score_empleabilidad = (
    obtener_score_empleabilidad(
        postulante
    )
)


nivel_empleabilidad = (
    obtener_nivel_empleabilidad(
        postulante
    )
)


e1, e2 = st.columns(2)


with e1:

    mostrar_kpi(
        "Nivel de empleabilidad",
        nivel_empleabilidad
    )


with e2:

    if score_empleabilidad is not None:

        mostrar_kpi(
            "Puntaje",
            f"{score_empleabilidad:.1f}"
        )

    else:

        mostrar_kpi(
            "Puntaje",
            "No disponible"
        )


# ============================================================
# GRÁFICO DE EMPLEABILIDAD
# ============================================================

if score_empleabilidad is not None:

    empleabilidad_chart = pd.DataFrame({

        "Indicador": [
            "Puntaje"
        ],

        "Valor": [
            score_empleabilidad
        ]

    })


    chart_empleabilidad = (

        alt.Chart(
            empleabilidad_chart
        )

        .mark_bar(
            color=COLOR_ROSA,
            cornerRadiusTopLeft=5,
            cornerRadiusTopRight=5
        )

        .encode(

            x=alt.X(
                "Indicador:N",
                title=None
            ),

            y=alt.Y(
                "Valor:Q",
                title="Puntaje",
                scale=alt.Scale(
                    domain=[
                        0,
                        100
                    ]
                ),
                axis=alt.Axis(
                    tickMinStep=10
                )
            ),

            tooltip=[

                alt.Tooltip(
                    "Indicador:N",
                    title="Indicador"
                ),

                alt.Tooltip(
                    "Valor:Q",
                    title="Puntaje"
                )

            ]

        )

        .properties(
            height=270
        )

        .configure(
            background="transparent",
            padding=0
        )

        .configure_view(
            stroke=None
        )
    )


    mostrar_grafico_enmarcado(
        chart_empleabilidad,
        "grafico_empleabilidad"
    )


else:

    st.info(
        "Este postulante no tiene un puntaje de empleabilidad registrado."
    )


# ============================================================
# ACTIVIDAD EN LA PLATAFORMA
# ============================================================

mostrar_seccion(
    "Actividad en la plataforma"
)


conversaciones_ia = obtener_entero(
    postulante.get(
        "cantidad_conversaciones"
    )
)


mensajes_ia = obtener_entero(
    postulante.get(
        "cantidad_mensajes_ia"
    )
)


cursos = obtener_entero(
    postulante.get(
        "cantidad_cursos"
    )
)


eventos = obtener_entero(
    postulante.get(
        "cantidad_eventos"
    )
)


compatibilidades = obtener_entero(
    postulante.get(
        "cantidad_analisis_compatibilidad"
    )
)


actividad_chart = pd.DataFrame({

    "Actividad": [

        "Conversaciones IA",
        "Mensajes IA",
        "Cursos inscritos",
        "Eventos",
        "Compatibilidades"

    ],

    "Cantidad": [

        conversaciones_ia,
        mensajes_ia,
        cursos,
        eventos,
        compatibilidades

    ]

})


# ============================================================
# GRÁFICO DE ACTIVIDAD
# ============================================================

chart_actividad = (

    alt.Chart(
        actividad_chart
    )

    .mark_bar(
        color=COLOR_GREEN,
        cornerRadiusEnd=5
    )

    .encode(

        y=alt.Y(
            "Actividad:N",
            title=None,
            sort="-x"
        ),

        x=alt.X(
            "Cantidad:Q",
            title="Cantidad",
            scale=alt.Scale(
                domainMin=0
            ),
            axis=alt.Axis(
                tickMinStep=1,
                format="d"
            )
        ),

        tooltip=[

            alt.Tooltip(
                "Actividad:N",
                title="Actividad"
            ),

            alt.Tooltip(
                "Cantidad:Q",
                title="Cantidad"
            )

        ]

    )

    .properties(
        height=300
    )

    .configure(
        background="transparent",
        padding=0
    )

    .configure_view(
        stroke=None
    )
)


mostrar_grafico_enmarcado(
    chart_actividad,
    "grafico_actividad"
)


# ============================================================
# USO DE CRÉDITOS
# ============================================================

mostrar_seccion(
    "Uso de créditos"
)


creditos_utilizados = obtener_decimal(
    postulante.get(
        "creditos_utilizados"
    ),
    0
)


cantidad_operaciones_creditos = obtener_entero(
    postulante.get(
        "cantidad_operaciones_creditos"
    )
)


c1, c2, c3 = st.columns(3)


with c1:

    mostrar_kpi(
        "Créditos disponibles",
        f"{creditos_disponibles:g}"
    )


with c2:

    mostrar_kpi(
        "Créditos utilizados",
        f"{creditos_utilizados:g}"
    )


with c3:

    mostrar_kpi(
        "Operaciones",
        cantidad_operaciones_creditos
    )


# ============================================================
# DETALLE DE CRÉDITOS
# ============================================================

detalle_creditos = obtener_texto(
    postulante.get(
        "uso_creditos_detalle"
    ),
    ""
)


datos_creditos = []


if detalle_creditos:

    try:

        contenido = json.loads(
            detalle_creditos
        )

        if isinstance(
            contenido,
            list
        ):

            datos_creditos = contenido

        elif isinstance(
            contenido,
            dict
        ):

            datos_creditos = [
                contenido
            ]

    except Exception:

        datos_creditos = []


if datos_creditos:

    creditos_df = pd.DataFrame(
        datos_creditos
    )


    columna_funcionalidad = None


    for columna in [

        "funcionalidad",
        "functionality",
        "nombre",
        "name",
        "evento",
        "eventName"

    ]:

        if columna in creditos_df.columns:

            columna_funcionalidad = columna

            break


    columna_creditos = None


    for columna in [

        "creditos",
        "credits",
        "totalCreditos",
        "total_credits",
        "cantidad_creditos"

    ]:

        if columna in creditos_df.columns:

            columna_creditos = columna

            break


    if (
        columna_funcionalidad
        and
        columna_creditos
    ):

        creditos_df = creditos_df.rename(
            columns={

                columna_funcionalidad:
                    "funcionalidad",

                columna_creditos:
                    "creditos"

            }
        )


        creditos_df[
            "creditos"
        ] = pd.to_numeric(
            creditos_df[
                "creditos"
            ],
            errors="coerce"
        ).fillna(0)


        creditos_df = (
            creditos_df
            .groupby(
                "funcionalidad",
                as_index=False
            )[
                "creditos"
            ]
            .sum()
            .sort_values(
                "creditos",
                ascending=False
            )
        )


        # ====================================================
        # GRÁFICO DE CRÉDITOS
        # ====================================================

        chart_creditos = (

            alt.Chart(
                creditos_df
            )

            .mark_bar(
                color=COLOR_ORANGE,
                cornerRadiusTopLeft=5,
                cornerRadiusTopRight=5
            )

            .encode(

                x=alt.X(
                    "funcionalidad:N",
                    title=None,
                    sort="-y",
                    axis=alt.Axis(
                        labelAngle=-30
                    )
                ),

                y=alt.Y(
                    "creditos:Q",
                    title="Créditos utilizados",
                    scale=alt.Scale(
                        domainMin=0
                    ),
                    axis=alt.Axis(
                        tickMinStep=1,
                        format="d"
                    )
                ),

                tooltip=[

                    alt.Tooltip(
                        "funcionalidad:N",
                        title="Funcionalidad"
                    ),

                    alt.Tooltip(
                        "creditos:Q",
                        title="Créditos"
                    )

                ]

            )

            .properties(
                height=320
            )

            .configure(
                background="transparent",
                padding=0
            )

            .configure_view(
                stroke=None
            )
        )


        mostrar_grafico_enmarcado(
            chart_creditos,
            "grafico_creditos"
        )


    else:

        st.info(
            "No hay suficiente detalle para generar el gráfico de créditos."
        )


else:

    st.info(
        "Este postulante no registra uso de créditos."
    )


# ============================================================
# RESUMEN PROFESIONAL
# ============================================================

resumen_profesional = obtener_texto(
    postulante.get(
        "resumen"
    ),
    ""
)


if resumen_profesional:

    mostrar_seccion(
        "Resumen profesional"
    )

    st.write(
        resumen_profesional
    )


# ============================================================
# LISTA DE POSTULANTES
# ============================================================

mostrar_seccion(
    "Lista de postulantes"
)


st.markdown(
    """
    <div class="table-help">
        Haz clic sobre una fila para seleccionar al postulante
        y actualizar todo el dashboard.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TABLA
# ============================================================

columnas_tabla = {

    "_id_postulante":
        "ID",

    "nombre_completo":
        "Postulante",

    "edad_dashboard":
        "Edad",

    "tipo_postulante_dashboard":
        "Tipo",

    "cantidad_postulaciones":
        "Postulaciones",

    "perfil_completado_pct":
        "Perfil %"

}


columnas_disponibles = [

    columna

    for columna
    in columnas_tabla

    if columna
    in df_filtrado.columns

]


tabla = (
    df_filtrado[
        columnas_disponibles
    ]
    .copy()
)


tabla = tabla.rename(
    columns={

        columna:
            columnas_tabla[
                columna
            ]

        for columna
        in columnas_disponibles

    }
)


# ============================================================
# FORMATO TABLA
# ============================================================

if "Edad" in tabla.columns:

    tabla[
        "Edad"
    ] = pd.to_numeric(
        tabla[
            "Edad"
        ],
        errors="coerce"
    )


if "Postulaciones" in tabla.columns:

    tabla[
        "Postulaciones"
    ] = (
        pd.to_numeric(
            tabla[
                "Postulaciones"
            ],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )


if "Perfil %" in tabla.columns:

    tabla[
        "Perfil %"
    ] = (
        pd.to_numeric(
            tabla[
                "Perfil %"
            ],
            errors="coerce"
        )
        .fillna(0)
        .round(0)
        .astype(int)
        .astype(str)
        + "%"
    )


# ============================================================
# TABLA INTERACTIVA
# ============================================================

resultado_tabla = st.dataframe(

    tabla,

    use_container_width=True,

    hide_index=True,

    height=380,

    on_select="rerun",

    selection_mode="single-row",

    key="tabla_postulantes"

)


# ============================================================
# DETECTAR FILA SELECCIONADA
# ============================================================

filas_seleccionadas = (
    resultado_tabla
    .selection
    .rows
)


if filas_seleccionadas:

    fila_seleccionada = (
        filas_seleccionadas[0]
    )


    nuevo_id = (
        df_filtrado
        .iloc[
            fila_seleccionada
        ][
            "_id_postulante"
        ]
    )


    id_actual = (
        st.session_state[
            "postulante_seleccionado"
        ]
    )


    if nuevo_id != id_actual:

        st.session_state[
            "postulante_seleccionado"
        ] = nuevo_id

        st.rerun()


# ============================================================
# PIE DE PÁGINA
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#6B7280;
        font-size:12px;
        margin-top:30px;
        padding-top:15px;
        border-top:1px solid #D9DEE3;
    ">
        Dashboard Individual · Laboral.AI
    </div>
    """,
    unsafe_allow_html=True
)