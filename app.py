import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import os

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Dashboard de Postulantes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Espacio superior
st.markdown(
    "<div style='height: 15px;'></div>",
    unsafe_allow_html=True
)


# ============================================================
# TÍTULO + ACTUALIZAR DATOS
# ============================================================

col_titulo, col_actualizar = st.columns(
    [6, 1]
)

with col_titulo:

    st.title(
        "Dashboard de Postulantes"
    )


with col_actualizar:

    # Bajar un poco el botón respecto al título
    st.markdown(
        "<div style='height: 20px;'></div>",
        unsafe_allow_html=True
    )

    if st.button(
        "🔄 Actualizar",
        width="stretch",
        key="btn_actualizar_datos"
    ):

        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()


# ============================================================
# COLORES CORPORATIVOS
# ============================================================

COLORS = {

    # ========================================================
    # AZULES
    # ========================================================

    "azul": "#A2B9EE",
    "celeste": "#A2DCEE",
    "azul_eventos": "#7FB3D5",
    "azul_modalidad": "#A7C7E7",
    "azul_claro": "#B8C9F2",
    "azul_EXclaro": "#C0CCE8",
    "azul_medio": "#89A8E8",
    "azul_profundo": "#7189C9",

    # NUEVOS AZULES
    "azul_grafico_carreras": "#66c7d1",
    "azul_grafico_invitaciones": "#3d8290",
    "azul_grafico_quizzes": "#004567",
    "azul_evolucion": "#323f83",
    "azul_chatbot": "#70afe2",
    "azul_secundario": "#a7bddc",

    # ========================================================
    # VERDES Y TURQUESA
    # ========================================================

    "menta": "#8EE8D8",
    "verde_ia": "#9AD0C2",
    "turquesa": "#7CCCC4",
    "verde_claro": "#B9E6D9",
    "verde_suave": "#B1DFD0",
    "verde_salvia": "#ABD1C0",

    # NUEVOS VERDES
    "verde_experiencia": "#a6c263",
    "verde_activos": "#bad29a",
    "verde_eventos": "#4ed5a8",
    "verde_cursos": "#cbeba3",

    # ========================================================
    # MORADOS Y LAVANDA
    # ========================================================

    "periwinkle": "#A1A3E4",
    "lavanda": "#CEA3E7",
    "lila": "#D8C4E8",
    "morado_suave": "#B8A9E8",
    "violeta_claro": "#C4B5E0",

    # NUEVO MORADO
    "morado_practicas": "#7030a0",

    # ========================================================
    # TONOS CÁLIDOS SUAVES
    # ========================================================

    "rosa_lavanda": "#DDB9D8",
    "rosa_pastel": "#E8C1D3",
    "rosa_hielo": "#EFCEDB",
    "rosa_malva": "#E6C1DA",
    "rosa_suave": "#E5BFD0",

    # NUEVO ROSA
    "rosa_eventos": "#e174b1",

    "amarillo": "#F3D58A",
    "amarillo_claro": "#F7E3A6",
    "amarillo_suave": "#F4D99B",
    "amarillo_pastel": "#F8E7B5",
    "vainilla": "#F6E4B5",
    "dorado_suave": "#F5F074",

    # NUEVO AMARILLO
    "amarillo_areas": "#ffde59",

    # ========================================================
    # TONOS NEUTROS
    # ========================================================

    "texto": "#333333",
    "fondo_card": "#CED6E2",
    "borde": "#D9E2F0",
    "gris": "#E9EEF5",
    "gris_medio": "#D5DCE8",
    "gris_claro": "#F3F5F8",
}


MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre",
    11: "Noviembre", 12: "Diciembre"
}


# ============================================================
# ESTILO
# ============================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: "Trebuchet MS", "Segoe UI", sans-serif;
}

.stApp {
    background-color: white;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
}

.dashboard-title {
    font-size: 30px;
    font-weight: 700;
    color: #333333;
}

.dashboard-subtitle {
    font-size: 14px;
    color: #666666;
    margin-bottom: 18px;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #333333;
    margin-top: 20px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# CARGAR DATA
# ============================================================

ROOT = Path(__file__).resolve().parent
RUTA_DATA = ROOT / "data" / "cache" / "postulantes_dashboard.csv"


@st.cache_data
def cargar_dashboard():

    if not RUTA_DATA.exists():
        st.error("No se encontró el archivo postulantes_dashboard.csv")
        st.stop()

    return pd.read_csv(
        RUTA_DATA,
        low_memory=True
    )


# ============================================================
# CARGAR DASHBOARD PRINCIPAL
# ============================================================

df_dashboard = cargar_dashboard()


# ============================================================
# VALIDAR DASHBOARD
# ============================================================

if df_dashboard.empty:
    st.warning("El archivo está vacío.")
    st.stop()


# ============================================================
# CARGAR EVENTOS
# ============================================================

RUTA_EVENTOS = (
    ROOT / "data" / "cache" / "eventos_dashboard.csv"
)


@st.cache_data
def cargar_eventos():

    if not RUTA_EVENTOS.exists():
        return pd.DataFrame()

    return pd.read_csv(
        RUTA_EVENTOS,
        low_memory=False
    )


df_eventos = cargar_eventos()


print("\n========== EVENTOS PARA DASHBOARD ==========")

print(
    "Registros:",
    len(df_eventos)
)

print(
    "Columnas:",
    df_eventos.columns.tolist()
)

print(
    df_eventos.head()
)

# ============================================================
# INTERÉS EN CURSOS
# ============================================================

RUTA_CURSOS_INTERES = (
    ROOT / "data" / "cache" / "cursos_interes_dashboard.csv"
)

df_cursos_interes = pd.read_csv(
    RUTA_CURSOS_INTERES,
    encoding="utf-8-sig"
)

# ============================================================
# CARGAR DETALLE DE QUIZZES
# ============================================================

RUTA_QUIZZES = (
    ROOT / "data" / "cache" / "quizzes_detalle_usuarios.csv"
)


@st.cache_data
def cargar_quizzes():

    if not RUTA_QUIZZES.exists():
        return pd.DataFrame()

    return pd.read_csv(
        RUTA_QUIZZES,
        low_memory=False
    )


df_quizzes = cargar_quizzes()

print("\n========== QUIZZES ==========")

print("Ruta:", RUTA_QUIZZES)

print("Existe:", RUTA_QUIZZES.exists())

print("Registros:", len(df_quizzes))

print("Columnas:", df_quizzes.columns.tolist())

print(df_quizzes.head())

# ============================================================
# PREPARACIÓN
# ============================================================

if "_id_postulante" in df_dashboard.columns:
    df_dashboard["_id_postulante"] = df_dashboard["_id_postulante"].astype(str)


if "createdAt_user" in df_dashboard.columns:

    df_dashboard["createdAt_user"] = pd.to_datetime(
        df_dashboard["createdAt_user"],
        errors="coerce"
    )

    df_dashboard["año"] = df_dashboard["createdAt_user"].dt.year
    df_dashboard["mes_num"] = df_dashboard["createdAt_user"].dt.month
    df_dashboard["mes"] = df_dashboard["mes_num"].map(MESES)

# ============================================================
# PREPARAR QUIZZES
# ============================================================

if not df_quizzes.empty:

    # Normalizar ID de usuario
   if "_id_user" in df_quizzes.columns:

    df_quizzes["_id_user"] = (
        df_quizzes["_id_user"]
        .astype("string")
        .str.strip()
    )

    # Normalizar campos de quiz
    for columna in [
        "quiz_id",
        "quiz_key",
        "quiz_nombre",
        "estado"
    ]:

        if columna in df_quizzes.columns:

            df_quizzes[columna] = (
                df_quizzes[columna]
                .astype("string")
                .str.strip()
            )


# ============================================================
# FUNCIONES
# ============================================================

import unicodedata
import re


# ============================================================
# LIMPIAR TEXTO
# ============================================================

def normalizar_texto(valor):

    if pd.isna(valor):
        return pd.NA

    valor = str(valor).strip()

    if valor == "":
        return pd.NA

    # Espacios repetidos
    valor = re.sub(r"\s+", " ", valor)

    # Quitar tildes para comparar
    valor = unicodedata.normalize("NFD", valor)

    valor = "".join(
        caracter
        for caracter in valor
        if unicodedata.category(caracter) != "Mn"
    )

    return valor.lower().strip()


# ============================================================
# LIMPIAR CATEGORÍAS
# ============================================================

def limpiar_categoria(serie):

    return (
        serie.astype("string")
        .str.strip()
        .replace({
            "": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
            "none": pd.NA,
            "null": pd.NA,
            "N/A": pd.NA,
            "n/a": pd.NA,
            "Sin registro": pd.NA,
            "sin registro": pd.NA
        })
    )


# ============================================================
# NORMALIZAR ÁREAS PROFESIONALES
# ============================================================

def normalizar_area(valor):

    valor = normalizar_texto(valor)

    if pd.isna(valor):
        return pd.NA

    equivalencias = {

        # ADMINISTRACIÓN Y NEGOCIOS
        "administracion y negocios":
            "Administración y Negocios",

        # ARQUITECTURA Y DISEÑO
        "arquitectura y diseno":
            "Arquitectura y Diseño",

        # CIENCIAS
        "ciencias":
            "Ciencias",

        # CIENCIAS SOCIALES Y HUMANIDADES
        "ciencias sociales y humanidades":
            "Ciencias Sociales y Humanidades",

        # ECONOMÍA Y FINANZAS
        "economia y finanzas":
            "Economía y Finanzas",

        # INGENIERÍA Y TECNOLOGÍA
        "ingenieria y tecnologia":
            "Ingeniería y Tecnología"
    }

    return equivalencias.get(
        valor,
        str(valor).strip().title()
    )


# ============================================================
# NORMALIZAR CARRERAS
# ============================================================

def normalizar_carrera(valor):

    valor = normalizar_texto(valor)

    if pd.isna(valor):
        return pd.NA

    equivalencias = {

        # ====================================================
        # ADMINISTRACIÓN Y NEGOCIOS
        # ====================================================

        "administracion":
            "Administración de Empresas",

        "administracion de empresas":
            "Administración de Empresas",

        "licenciatura en administracion de empresas":
            "Administración de Empresas",

        "gestion y alta direccion":
                    "Administración de Empresas",

        "Universitario En Educacion Comercial":
                            "Administración de Empresas",

        "administracion y marketing":
            "Administración y Marketing",

        "Administracion y Marketing":
                        "Administración y Marketing",

        "marketing y administración":
            "Administración y Marketing",

        "Marketing Y Administracion":
                    "Administración y Marketing",


        "administracion de negocios internacionales":
            "Administración de Negocios Internacionales",

        "administracion y negocios internacionales":
            "Administración de Negocios Internacionales",

        "istracion de negocios internacionales":
            "Administración de Negocios Internacionales",

        "nistracion y negocios internacionales":
            "Administración de Negocios Internacionales",

        "marketing":
            "Marketing",

        "marketing digital":
            "Marketing",

        "marketing estrategico":
            "Marketing",

        "graduada de marketing":
            "Marketing",

        "Growth Marketing":
                    "Marketing",


        "economia y negocios internacionales":
            "Economía y Negocios Internacionales",

        "negocios internacionales":
            "Negocios Internacionales",

        


        # ====================================================
        # ARQUITECTURA Y DISEÑO
        # ====================================================

        "diseno grafico":
            "Diseño Gráfico",

        "diseno grafico digital":
            "Diseño Gráfico",

        "diseno grafico profesional":
            "Diseño Gráfico",

        "diseno grafico tecnico":
            "Diseño Gráfico",

        "bachiller en diseno grafico":
            "Diseño Gráfico",

        "bachelor's degree in arts, major in graphic design":
            "Diseño Gráfico",

        "bachiller en arte con mencion en diseno grafico":
            "Diseño Gráfico",

        "arquitectura":
            "Arquitectura",

        "arquitectura y urbanismo":
            "Arquitectura",

        "Bachiller En Arquitectura Y Urbanismo":
                    "Arquitectura",

        "Arquitectura y Urbanismo":
                            "Arquitectura",

        "Arquitectura Sostenible":
                            "Arquitectura",

        "diseno y desarrollo web":
            "Diseño y Desarrollo Web",

        "diseño y desarrollo web":
            "Diseño y Desarrollo Web",

        "Programa De Diseno Grafico Publicitario":
                    "Diseño Gráfico",

        "Programa Especializado en Diseno Instruccional: Aprendizaje Activo y Pedagogia Digital":
                            "Diseño Gráfico",

    


        # ====================================================
        # CIENCIAS
        # ====================================================

        "fisica":
            "Física",

        "matematica":
            "Matemática",

        "microbiologia y parasitologia":
            "Microbiología y Parasitología",

        "biologia marina":
            "Biología Marina",

        "ciencias biologicas":
            "Ciencias Biológicas",

        "ciencias de la computacion":
            "Ciencias de la Computación",


        # ====================================================
        # CIENCIAS SOCIALES Y HUMANIDADES
        # ====================================================

        "psicologia":
            "Psicología",

        "licenciatura en psicologia":
            "Psicología",

        "licenciada en psicologia":
            "Psicología",

        "estudiante de psicologia":
            "Psicología",

        "Bachiller En Psicologia":
                    "Psicología",

        "derecho":
            "Derecho",

        "educacion secundaria":
            "Educación",

        "comunicacion audiovisual":
            "Comunicación Audiovisual",

        "ciencias de la comunicacion":
            "Ciencias de la Comunicación",

        "comunicacion y publicidad":
            "Comunicación y Publicidad",


        # ====================================================
        # ECONOMÍA Y FINANZAS
        # ====================================================

        "economia":
            "Economía",

        "economics":
            "Economía",

        "estudiante de economia":
            "Economía",

        "licenciada en economia":
            "Economía",

        "Economia y Finanzas":
                    "Economía",

        "contabilidad":
            "Contabilidad",

        "bachiller en contabilidad":
            "Contabilidad",

        "Contabilidad y Finanzas":
                    "Contabilidad",

        "titulada contabilidad tecnica":
            "Contabilidad",

        "contabilidad y finanzas":
            "Contabilidad",

        "contabilidad de costos y pye":
            "Contabilidad",

        "Bachiller En Auditoria y Contabilidad (Mejor Egresado)":
                    "Contabilidad",

        "contabilidad de costos y pymes":
            "Contabilidad",

        "corporate finance and economics":
            "Finanzas",

        "Business Administration, Corporate Finance, And Economics":
                    "Finanzas",

        "corporate finance, and economics":
            "Finanzas",

        "diplomado de finanzas empresariales":
            "Finanzas",

        "Finanzas Personales":
                    "Finanzas",

        "licenciatura en finanzas":
            "Finanzas",

        "curso accounting fundamentals":
            "Contabilidad",

        

        # ====================================================
        # INGENIERÍA Y TECNOLOGÍA
        # ====================================================

        "ingenieria industrial":
            "Ingeniería Industrial",

        "ingenieria ambiental":
            "Ingeniería Ambiental",

        "ingenieria de sistemas":
            "Ingeniería de Sistemas",

        "ingenieria de sistemas e informatica":
            "Ingeniería de Sistemas",

        "ingenieria informatica":
            "Ingeniería Informática",

        "ingenieria mecatronica":
            "Ingeniería Mecatrónica",

        "ingenieria civil":
            "Ingeniería Civil",

        "Bim Aplicado A Topografia y Diseno De Infraestructura Vial":
                    "Ingeniería Civil",

        "ingenieria de software":
            "Ingeniería de Software",

        "ingenieria empresarial":
            "Ingeniería Empresarial",

        "ingenieria empresarial y de sistemas":
            "Ingeniería Empresarial",

        "ingenieria industrial y comercial":
            "Ingeniería Industrial",

        "ingenieria economica y de negocios":
            "Ingeniería Económica y de Negocios",


        # ====================================================
        # SALUD
        # ====================================================

        "enfermeria":
            "Enfermería",

        "enfermeria tecnica":
            "Enfermería",

        "tecnico en enfermeria":
            "Enfermería",

        "tecnica en enfermeria":
            "Enfermería",

        "medicina humana":
            "Medicina Humana",

        "estomatologia":
            "Estomatología",

        "tec. farmacia":
            "Farmacia",

        "tecnico en farmacia":
            "Farmacia",

        "medicina veterinaria y zootecnia":
            "Medicina Veterinaria y Zootecnia"
    }


    # ========================================================
    # VALORES QUE NO DEBEN CONTARSE COMO CARRERAS
    # ========================================================

    no_es_carrera = {

        "design thinking",

        "distincion en competencias matematicas",

        "formacion en competencias matematicas",

        "ingles",
        "ingles a2 mcer",
        "ingles basico",
        "ingles intermedio",
        "ingles avanzado",
        "english",
        "english basic",
        "english intermediate",
        "english advanced",
        "Idioma Ingles",
        "Curso De Ingles",

        "excel",
        "excel avanzado",
        "excel intermedio",

        "certificate",
        "certificado",
        "diploma",
        "diplomado",

        "primaria",
        "bachiller en ciencias",
        "other",

        "curso accounting fundamentals",

        'Curso "Accounting Fundamentals"',

        "implementacion de iniciativas sociales",

        "diseno e implementacion de iniciativas sociales",

        "Implementación de Iniciativa Sociales"




    }


    if valor in no_es_carrera:
        return pd.NA


    return equivalencias.get(
    valor,
    pd.NA
)


# ============================================================
# PORCENTAJE
# ============================================================

def porcentaje(valor, total):

    return (
        0
        if total == 0
        else round(valor / total * 100, 1)
    )


# ============================================================
# CONTAR BOOLEANOS
# ============================================================

def contar_booleano(df, columna):

    if columna not in df.columns:
        return 0

    return int(
        pd.to_numeric(
            df[columna],
            errors="coerce"
        )
        .fillna(0)
        .gt(0)
        .sum()
    )


# ============================================================
# BARRA
# ============================================================

def crear_barra(data, categoria, valor, color):

    fig = px.bar(
        data,
        x=valor,
        y=categoria,
        orientation="h"
    )

    fig.update_traces(
        marker_color=color
    )


    return fig


# ============================================================
# DONUT
# ============================================================

def crear_donut(
    data,
    nombres,
    valores,
    colores
):

    fig = px.pie(
        data,
        names=nombres,
        values=valores,
        hole=.58
    )

    fig.update_traces(
        marker=dict(
            colors=colores,
            line=dict(
                color="white",
                width=2
            )
        ),
        textinfo="percent",
        textposition="outside"
    )

    fig.update_layout(
        height=350,
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),
        paper_bgcolor="white"
    )

    return fig


# ============================================================
# NORMALIZAR CATEGORÍAS DEL DASHBOARD
# ============================================================

if "area_profesional" in df_dashboard.columns:

    df_dashboard["area_profesional"] = (
        df_dashboard["area_profesional"]
        .apply(normalizar_area)
    )


if "carrera_principal" in df_dashboard.columns:

    df_dashboard["carrera_principal"] = (
        df_dashboard["carrera_principal"]
        .apply(normalizar_carrera)
    )

# ============================================================
# COLOR DE FONDO DEL SIDEBAR
# ============================================================

st.markdown("""
<style>

[data-testid="stSidebar"] {
    background-color: #082e47;
}

/* Textos del sidebar */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: white !important;
}

/* Botón Limpiar filtros */
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] button p,
[data-testid="stSidebar"] button span {
    color: black !important;
}

</style>
""", unsafe_allow_html=True)
# ============================================================
# SIDEBAR - FILTROS
# ============================================================

def limpiar_filtros():
    """Restablece todos los filtros a su valor inicial."""
    
    st.session_state["filtro_año"] = "Todos"
    st.session_state["filtro_area"] = "Todas"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("Filtros")
    st.caption("Refina la información del dashboard")

    st.divider()

    # ========================================================
    # OPCIONES DE AÑO
    # ========================================================

    if "año" in df_dashboard.columns:

        años = sorted(
            df_dashboard["año"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

    else:

        años = []

    # ========================================================
    # OPCIONES DE ÁREA PROFESIONAL
    # ========================================================

    if "area_profesional" in df_dashboard.columns:

        areas = sorted(
            limpiar_categoria(
                df_dashboard["area_profesional"]
            )
            .dropna()
            .unique()
            .tolist()
        )

    else:

        areas = []

    # ========================================================
    # INICIALIZAR FILTROS
    # ========================================================

    if "filtro_año" not in st.session_state:

        st.session_state["filtro_año"] = "Todos"

    if "filtro_area" not in st.session_state:

        st.session_state["filtro_area"] = "Todas"

    # ========================================================
    # FILTRO AÑO
    # ========================================================

    año = st.selectbox(
        "Año",
        options=["Todos"] + años,
        key="filtro_año"
    )

    # ========================================================
    # FILTRO ÁREA PROFESIONAL
    # ========================================================

    area = st.selectbox(
        "Área profesional",
        options=["Todas"] + areas,
        key="filtro_area"
    )

    st.divider()

    # ========================================================
    # BOTÓN LIMPIAR FILTROS
    # ========================================================

    st.button(
        "🧹 Limpiar filtros",
        use_container_width=True,
        on_click=limpiar_filtros
    )


# ============================================================
# FILTRAR DATASET
# ============================================================

df = df_dashboard.copy()


# ============================================================
# FILTRO AÑO
# ============================================================

if (
    año != "Todos"
    and "año" in df.columns
):

    df = df[
        df["año"].eq(
            int(año)
        )
    ]


# ============================================================
# FILTRO ÁREA PROFESIONAL
# ============================================================

if (
    area != "Todas"
    and "area_profesional" in df.columns
):

    df = df[
        limpiar_categoria(
            df["area_profesional"]
        ).eq(area)
    ]

# ============================================================
# FILTRAR QUIZZES SEGÚN LOS FILTROS GENERALES
# ============================================================

df_quizzes_filtrado = df_quizzes.copy()

if not df_quizzes_filtrado.empty:

    # --------------------------------------------------------
    # NORMALIZAR IDs
    # --------------------------------------------------------

    if "_id_user" in df_quizzes_filtrado.columns:

        df_quizzes_filtrado["_id_user"] = (
            df_quizzes_filtrado["_id_user"]
            .astype("string")
            .str.strip()
        )

    if "_id_postulante" in df.columns:

        ids_filtrados = (
            df["_id_postulante"]
            .astype("string")
            .str.strip()
            .unique()
        )

        df_quizzes_filtrado = df_quizzes_filtrado[
            df_quizzes_filtrado["_id_user"]
            .isin(ids_filtrados)
        ].copy()


# ============================================================
# ELIMINAR DUPLICADOS
# ============================================================

if "_id_postulante" in df.columns:

    df = df.drop_duplicates(
        subset="_id_postulante",
        keep="first"
    )


# ============================================================
# REINICIAR ÍNDICE
# ============================================================

df = df.reset_index(drop=True)



# ============================================================
# TÍTULO
# ============================================================



st.markdown(
    '<div class="dashboard-subtitle">Análisis de perfiles, formación, experiencia y participación en Laboral.AI</div>',
    unsafe_allow_html=True
)


# ============================================================
# KPIs
# ============================================================

st.markdown(
    '<div class="section-title">KPIs</div>',
    unsafe_allow_html=True
)


# ============================================================
# KPIs GENERALES
# ============================================================

total = len(df)

con_cv = contar_booleano(
    df,
    "tiene_cv"
)

uso_ia = contar_booleano(
    df,
    "uso_ia"
)

eventos = contar_booleano(
    df,
    "participo_evento"
)

cursos = contar_booleano(
    df,
    "cantidad_cursos"
)


# ============================================================
# QUIZZES
# Aplicar los mismos filtros del dashboard
# ============================================================

quizzes_kpi = df_quizzes.copy()


# ------------------------------------------------------------
# FILTRO AÑO
# ------------------------------------------------------------

if año != "Todos":

    ids_año = (
        df_dashboard[
            df_dashboard["año"].eq(int(año))
        ]["_id_postulante"]
        .astype("string")
        .str.strip()
        .dropna()
        .unique()
    )

    quizzes_kpi = quizzes_kpi[
        quizzes_kpi["_id_user"]
        .astype("string")
        .str.strip()
        .isin(ids_año)
    ]


# ------------------------------------------------------------
# FILTRO ÁREA PROFESIONAL
# ------------------------------------------------------------

if area != "Todas":

    ids_area = (
        df_dashboard[
            df_dashboard["area_profesional"].eq(area)
        ]["_id_postulante"]
        .astype("string")
        .str.strip()
        .dropna()
        .unique()
    )

    quizzes_kpi = quizzes_kpi[
        quizzes_kpi["_id_user"]
        .astype("string")
        .str.strip()
        .isin(ids_area)
    ]


# ------------------------------------------------------------
# CONTAR USUARIOS ÚNICOS CON QUIZ
# ------------------------------------------------------------

quizzes = (
    quizzes_kpi["_id_user"]
    .dropna()
    .astype("string")
    .str.strip()
    .nunique()
)


# ============================================================
# USUARIOS ACTIVOS
# ============================================================

usuarios_activos = 0

if "isActive" in df.columns:

    usuarios_activos = (
        df["isActive"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1"])
        .sum()
    )

    usuarios_activos = int(
        usuarios_activos
    )


# ============================================================
# MOSTRAR KPIs
# ============================================================

cols = st.columns(7)


datos_kpi = [
    ("👥", "Postulantes", total),
    ("🟢", "Usuarios activos", usuarios_activos),
    ("📄", "Con CV", con_cv),
    ("🤖", "Uso de Chatbot", uso_ia),
    ("🎫", "Eventos", eventos),
    ("📚", "Cursos", cursos),
    ("📝", "Quizzes", quizzes)
]


for col, (icono, titulo, valor) in zip(
    cols,
    datos_kpi
):

    with col:

        delta = (
            "100%"
            if titulo == "Postulantes"
            else f"{porcentaje(valor, total)}%"
        )

        st.metric(
            f"{icono} {titulo}",
            str(valor),
            delta
        )

# ============================================================
# PERFIL PROFESIONAL
# ============================================================

st.markdown('<div class="section-title">Perfil profesional</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:

    st.markdown(
    "<p style='font-size:16px; font-weight:600; margin-bottom:8px;'>Top 10 de carreras con mayor cantidad de postulantes</p>",
    unsafe_allow_html=True
    )


    if "carrera_principal" in df.columns:

        carreras = (
            limpiar_categoria(df["carrera_principal"])
            .dropna()
            .value_counts()
            .head(10)
            .reset_index()
        )

        carreras.columns = ["Carrera", "Postulantes"]

        st.plotly_chart(
            crear_barra(
                carreras,
                "Carrera",
                "Postulantes",
                COLORS["azul_grafico_carreras"]
            ),
            use_container_width=True
        )

with c2:

    st.markdown(
    "<p style='font-size:16px; font-weight:600; margin-bottom:8px;'>Top 8 de áreas profesionales</p>",
    unsafe_allow_html=True
    )


    if "area_profesional" in df.columns:

        areas_df = (
            limpiar_categoria(df["area_profesional"])
            .dropna()
            .value_counts()
            .head(10)
            .reset_index()
        )

        areas_df.columns = ["Área", "Postulantes"]

        st.plotly_chart(
            crear_barra(
                areas_df,
                "Área",
                "Postulantes",
                COLORS["amarillo_areas"]
            ),
            use_container_width=True
        )

# ============================================================
# EXPERIENCIA
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Experiencia
    </div>
    """,
    unsafe_allow_html=True
)


c3, c4 = st.columns(2)


# ============================================================
# EXPERIENCIA LABORAL
# ============================================================

with c3:

    st.markdown(
    "<p style='font-size:16px; font-weight:600; margin-bottom:8px;'>Experiencia laboral</p>",
    unsafe_allow_html=True
    )


    if "Rango_experiencia" in df.columns:

        orden = [
            "Sin experiencia registrada",
            "Menos de 1 año",
            "1 a 3 años",
            "3 a 5 años",
            "Más de 5 años"
        ]

        experiencia_df = (
            df["Rango_experiencia"]
            .value_counts()
            .reindex(
                orden,
                fill_value=0
            )
            .reset_index()
        )

        experiencia_df.columns = [
            "Rango",
            "Postulantes"
        ]

        fig = crear_barra(
            experiencia_df,
            "Rango",
            "Postulantes",
            COLORS["verde_experiencia"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# PRÁCTICAS
# ============================================================

with c4:

    st.markdown(
    "<p style='font-size:16px; font-weight:600; margin-bottom:8px;'>Experiencia en prácticas</p>",
    unsafe_allow_html=True
    )


    if "Rango_practica" in df.columns:

        orden_practicas = [
            "Sin prácticas registradas",
            "Menos de 1 año",
            "1 a 2 años",
            "Más de 2 años"
        ]

        practicas_df = (
            df["Rango_practica"]
            .value_counts()
            .reindex(
                orden_practicas,
                fill_value=0
            )
            .reset_index()
        )

        practicas_df.columns = [
            "Rango",
            "Postulantes"
        ]

        fig = crear_barra(
            practicas_df,
            "Rango",
            "Postulantes",
            COLORS["morado_practicas"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ============================================================
# CARGAR CÓDIGOS DE INVITACIONES
# ============================================================

ruta_codigos_invitacion = os.path.join(
    "data",
    "codigos_laboral_heros_aliados.csv"
)

if os.path.exists(ruta_codigos_invitacion):

    df_codigos_invitacion = pd.read_csv(
        ruta_codigos_invitacion
    )

    df_codigos_invitacion["codigo"] = (
        df_codigos_invitacion["codigo"]
        .astype("string")
        .str.strip()
    )

    df_codigos_invitacion["origen"] = (
        df_codigos_invitacion["origen"]
        .astype("string")
        .str.strip()
    )

else:

    df_codigos_invitacion = pd.DataFrame(
        columns=[
            "codigo",
            "origen",
            "counter"
        ]
    )

# ============================================================
# INVITACIONES - ALIADOS Y LABORAL HEROS
# ============================================================

st.markdown(
    '<div class="section-title">Invitaciones</div>',
    unsafe_allow_html=True
)


# ============================================================
# PREPARAR DATOS
# ============================================================

if (
    "origen_invitacion" in df.columns
    and "codigo_invitacion" in df.columns
):

    df_invitaciones = df[
        df["origen_invitacion"].notna()
        & df["codigo_invitacion"].notna()
        & df["origen_invitacion"].isin([
            "Aliados",
            "Laboral Heros"
        ])
    ].copy()


    # --------------------------------------------------------
    # LIMPIAR TEXTOS
    # --------------------------------------------------------

    df_invitaciones["origen_invitacion"] = (
        df_invitaciones["origen_invitacion"]
        .astype("string")
        .str.strip()
    )

    df_invitaciones["codigo_invitacion"] = (
        df_invitaciones["codigo_invitacion"]
        .astype("string")
        .str.strip()
    )


    # --------------------------------------------------------
    # FILTRO DE ORIGEN
    # --------------------------------------------------------

    if "filtro_origen_invitacion" not in st.session_state:

        st.session_state["filtro_origen_invitacion"] = "Todos"


    filtro_origen = st.selectbox(
        "Filtrar por origen",
        options=[
            "Todos",
            "Aliados",
            "Laboral Heros"
        ],
        key="filtro_origen_invitacion"
    )


    # ========================================================
    # APLICAR FILTRO
    # ========================================================

    if filtro_origen == "Todos":

        df_invitaciones_filtrado = (
            df_invitaciones.copy()
        )

    else:

        df_invitaciones_filtrado = df_invitaciones[
            df_invitaciones["origen_invitacion"]
            == filtro_origen
        ].copy()


    # ========================================================
    # GRÁFICOS
    # ========================================================

    g1, g2 = st.columns(2)


    # ========================================================
    # GRÁFICO 1
    # POSTULANTES INVITADOS
    # ========================================================

    with g1:

        st.markdown(
            """
            <p style='font-size:16px; font-weight:600; margin-bottom:8px;'>
                Postulantes invitados por origen
            </p>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # TODOS
        # ALIADOS VS LABORAL HEROS
        # ----------------------------------------------------

        if filtro_origen == "Todos":

            invitados_origen = (
                df_invitaciones_filtrado
                .groupby("origen_invitacion")
                .size()
                .reindex(
                    [
                        "Aliados",
                        "Laboral Heros"
                    ],
                    fill_value=0
                )
                .reset_index(
                    name="Postulantes"
                )
            )


            fig_invitaciones = crear_barra(
                invitados_origen,
                "origen_invitacion",
                "Postulantes",
                COLORS["azul_grafico_invitaciones"]
            )


            st.plotly_chart(
                fig_invitaciones,
                use_container_width=True,
                key="grafico_invitaciones_origen"
            )


        # ----------------------------------------------------
        # ALIADOS O LABORAL HEROS
        # MOSTRAR CÓDIGOS
        # ----------------------------------------------------

        else:

            invitados_codigo = (
                df_invitaciones_filtrado
                .groupby(
                    "codigo_invitacion"
                )
                .size()
                .reset_index(
                    name="Postulantes"
                )
                .sort_values(
                    "Postulantes",
                    ascending=True
                )
            )


            if not invitados_codigo.empty:

                fig_invitaciones = crear_barra(
                    invitados_codigo,
                    "codigo_invitacion",
                    "Postulantes",
                    COLORS["turquesa"]
                )


                st.plotly_chart(
                    fig_invitaciones,
                    use_container_width=True,
                    key="grafico_invitaciones_codigo"
                )

            else:

                st.info(
                    "No hay postulantes invitados "
                    "para el origen seleccionado."
                )


    # ========================================================
    # GRÁFICO 2
    # USUARIOS ACTIVOS POR ORIGEN
    # ========================================================

    with g2:

        st.markdown(
            """
            <p style='font-size:16px; font-weight:600; margin-bottom:8px;'>
                Usuarios activos por origen Top 5
            </p>
            """,
            unsafe_allow_html=True
        )


        # ----------------------------------------------------
        # SOLO USUARIOS ACTIVOS
        # ----------------------------------------------------

        df_activos = df_invitaciones_filtrado[
            df_invitaciones_filtrado["isActive"]
            .astype(str)
            .str.lower()
            .isin([
                "true",
                "1"
            ])
        ].copy()


        # ----------------------------------------------------
        # TODOS
        # ACTIVOS DE ALIADOS VS LABORAL HEROS
        # ----------------------------------------------------

        if filtro_origen == "Todos":

            activos_origen = (
                df_activos
                .groupby(
                    "origen_invitacion"
                )
                .size()
                .reindex(
                    [
                        "Aliados",
                        "Laboral Heros"
                    ],
                    fill_value=0
                )
                .reset_index(
                    name="Activos"
                )
            )


            fig_activos = crear_donut(
                activos_origen,
                "origen_invitacion",
                "Activos",
                [
                    COLORS["azul_grafico_quizzes"],
                    COLORS["verde_activos"]
                ]
            )


            st.plotly_chart(
                fig_activos,
                use_container_width=True,
                key="grafico_activos_invitaciones"
            )


        # ----------------------------------------------------
        # ALIADOS O LABORAL HEROS
        # TOP 5 CÓDIGOS ACTIVOS
        # ----------------------------------------------------

        else:

            activos_codigo = (
                df_activos
                .groupby(
                    "codigo_invitacion"
                )
                .size()
                .reset_index(
                    name="Activos"
                )
                .sort_values(
                    "Activos",
                    ascending=False
                )
                .head(5)
            )


            if not activos_codigo.empty:

                fig_activos = crear_donut(
                    activos_codigo,
                    "codigo_invitacion",
                    "Activos",
                    [
                        COLORS["menta"],
                        COLORS["turquesa"],
                        COLORS["azul_modalidad"],
                        COLORS["periwinkle"],
                        COLORS["celeste"]
                    ]
                )


                st.plotly_chart(
                    fig_activos,
                    use_container_width=True,
                    key="grafico_activos_invitaciones"
                )

            else:

                st.info(
                    "No hay usuarios activos "
                    "para el origen seleccionado."
                )


else:

    st.info(
        "No hay información disponible sobre invitaciones."
    )

    
# ============================================================
# USO DE LA PLATAFORMA
# ============================================================

st.markdown('<div class="section-title">Uso de la plataforma</div>', unsafe_allow_html=True)

u1, u2 = st.columns(2)

with u1:

    st.markdown(
    "<p style='font-size:16px; font-weight:600; margin-bottom:8px;'>Uso de Chatbot</p>",
    unsafe_allow_html=True
    )


    ia_df = pd.DataFrame({
        "Estado": ["Utilizó Chatbot", "No utilizó Chatbot"],
        "Postulantes": [uso_ia, max(total - uso_ia, 0)]
    })

    st.plotly_chart(
        crear_donut(
            ia_df,
            "Estado",
            "Postulantes",
            [COLORS["azul_chatbot"], COLORS["gris_medio"]]
        ),
        use_container_width=True
    )

with u2:

    st.markdown(
    "<p style='font-size:16px; font-weight:600; margin-bottom:8px;'>Participación en eventos</p>",
    unsafe_allow_html=True
    )


    ev_df = pd.DataFrame({
    "Estado": ["Participó", "No participó"],
    "Postulantes": [eventos, max(total - eventos, 0)]
     })

    st.plotly_chart(
    crear_donut(
        ev_df,
        "Estado",
        "Postulantes",
        [
            COLORS["verde_eventos"],
            COLORS["gris_medio"]
        ]
    ),
    use_container_width=True
)





# ============================================================
# NORMALIZAR ID
# ============================================================

df_cursos_interes["_id_postulante"] = (
    df_cursos_interes["_id_postulante"]
    .astype("string")
    .str.strip()
)


# ============================================================
# NORMALIZAR CATEGORÍA
# ============================================================

df_cursos_interes["categoria_curso"] = (
    df_cursos_interes["categoria_curso"]
    .astype("string")
    .str.strip()
)


# ============================================================
# TRAER AÑO Y ÁREA PROFESIONAL
# DESDE EL DATASET PRINCIPAL
# ============================================================

columnas_filtros = [
    "_id_postulante",
    "año",
    "area_profesional"
]

df_cursos_interes = df_cursos_interes.merge(
    df_dashboard[columnas_filtros].drop_duplicates(
        subset="_id_postulante"
    ),
    on="_id_postulante",
    how="left"
)


# ============================================================
# VALIDACIÓN
# ============================================================

print("\n========== CURSOS PARA DASHBOARD ==========")

print(
    "Registros:",
    len(df_cursos_interes)
)

print(
    "Postulantes únicos:",
    df_cursos_interes["_id_postulante"].nunique()
)

print(
    "Columnas:",
    df_cursos_interes.columns.tolist()
)

print(
    "\nAños:",
    df_cursos_interes["año"].value_counts(dropna=False)
)

print(
    "\nÁreas profesionales:"
)

print(
    df_cursos_interes["area_profesional"]
    .value_counts(dropna=False)
)

# ============================================================
# EVENTOS Y CURSOS
# ============================================================

col_eventos, col_cursos = st.columns(2)


# ============================================================
# PARTICIPACIÓN SEGÚN TIPO DE EVENTO
# ============================================================

with col_eventos:

    st.markdown(
        """
        <p style="
            font-size:16px;
            font-weight:600;
            margin-bottom:8px;
        ">
            Participación según tipo de evento
        </p>
        """,
        unsafe_allow_html=True
    )

    if not df_eventos.empty:

        # Mostrar temporalmente las columnas para comprobar
        # la estructura del archivo
        print(
            "\nCOLUMNAS EVENTOS:",
            df_eventos.columns.tolist()
        )

        # ----------------------------------------------------
        # BUSCAR COLUMNA DEL TIPO DE EVENTO
        # ----------------------------------------------------

        posibles_columnas_evento = [
            "tipo_evento",
            "tipoEvento",
            "event_type",
            "eventType",
            "nombre_evento",
            "nombreEvento",
            "evento",
            "event_name",
            "eventName"
        ]

        columna_tipo_evento = next(
            (
                columna
                for columna in posibles_columnas_evento
                if columna in df_eventos.columns
            ),
            None
        )

        if columna_tipo_evento is not None:

            eventos_grafico = df_eventos.copy()

            eventos_grafico[columna_tipo_evento] = (
                eventos_grafico[columna_tipo_evento]
                .astype("string")
                .str.strip()
            )

            eventos_grafico = eventos_grafico[
                eventos_grafico[columna_tipo_evento].notna()
                & (
                    eventos_grafico[columna_tipo_evento] != ""
                )
            ]

            eventos_grafico = (
                eventos_grafico
                .groupby(columna_tipo_evento)
                .size()
                .reset_index(name="Postulantes")
                .sort_values(
                    "Postulantes",
                    ascending=False
                )
            )

            eventos_grafico.columns = [
                "Tipo de evento",
                "Postulantes"
            ]

            if not eventos_grafico.empty:

                st.plotly_chart(
                    crear_barra(
                        eventos_grafico,
                        "Tipo de evento",
                        "Postulantes",
                        COLORS["rosa_eventos"]
                    ),
                    use_container_width=True,
                    key="grafico_tipo_evento"
                )

            else:

                st.info(
                    "No hay participación registrada por tipo de evento."
                )

        else:

            st.warning(
                "No se encontró la columna del tipo de evento."
            )

    else:

        st.info(
            "No hay información disponible sobre eventos."
        )


# ============================================================
# INTERÉS EN CURSOS
# ============================================================

with col_cursos:

    st.markdown(
        """
        <p style="
            font-size:16px;
            font-weight:600;
            margin-bottom:8px;
        ">
            Interés en cursos
        </p>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # COPIA PARA FILTROS
    # --------------------------------------------------------

    cursos_filtrados = df_cursos_interes.copy()

    # --------------------------------------------------------
    # FILTRO AÑO
    # --------------------------------------------------------

    if año != "Todos":

        cursos_filtrados = cursos_filtrados[
            cursos_filtrados["año"].eq(int(año))
        ]

    # --------------------------------------------------------
    # FILTRO ÁREA PROFESIONAL
    # --------------------------------------------------------

    if area != "Todas":

        cursos_filtrados = cursos_filtrados[
            cursos_filtrados["area_profesional"].eq(area)
        ]

    # --------------------------------------------------------
    # GRÁFICO POR CATEGORÍA
    # --------------------------------------------------------

    if not cursos_filtrados.empty:

        categorias_grafico = (
            cursos_filtrados[
                cursos_filtrados["categoria_curso"].notna()
            ]
            .groupby("categoria_curso")["_id_postulante"]
            .nunique()
            .reset_index(name="Postulantes")
            .sort_values(
                "Postulantes",
                ascending=True
            )
            .tail(10)
        )

        categorias_grafico.columns = [
            "Categoría",
            "Postulantes"
        ]

        if not categorias_grafico.empty:

            st.plotly_chart(
                crear_barra(
                    categorias_grafico,
                    "Categoría",
                    "Postulantes",
                    COLORS["verde_cursos"]
                ),
                use_container_width=True,
                key="grafico_categorias_cursos"
            )

        else:

            st.info(
                "No hay información disponible sobre categorías de cursos."
            )

    else:

        st.info(
            "No hay información disponible sobre cursos."
        )


# ============================================================
# QUIZZES
# ============================================================

st.markdown(
    '<div class="section-title">Quizzes</div>',
    unsafe_allow_html=True
)


# ============================================================
# VALIDAR DATA DE QUIZZES
# ============================================================

if df_quizzes.empty:

    st.info(
        "No hay información disponible sobre quizzes."
    )

else:

    # ========================================================
    # COLUMNAS NECESARIAS
    # ========================================================

    columnas_necesarias = [
        "_id_user",
        "quiz_id",
        "quiz_key",
        "quiz_nombre",
        "estado"
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_necesarias
        if columna not in df_quizzes.columns
    ]


    if columnas_faltantes:

        st.warning(
            "Faltan columnas en quizzes_detalle_usuarios.csv: "
            + ", ".join(columnas_faltantes)
        )

    else:

        # ====================================================
        # LIMPIAR DATOS
        # ====================================================

        for columna in columnas_necesarias:

            df_quizzes[columna] = (
                df_quizzes[columna]
                .astype("string")
                .str.strip()
            )


        # ====================================================
        # NORMALIZAR ESTADOS
        # ====================================================

        df_quizzes["estado"] = (
            df_quizzes["estado"]
            .str.lower()
            .str.strip()
            .replace({
                "iniciado": "Iniciado",
                "en proceso": "En proceso",
                "completado": "Completado"
            })
        )


        # ====================================================
        # ELIMINAR REGISTROS SIN USUARIO
        # ====================================================

        df_quizzes = df_quizzes[
            df_quizzes["_id_user"].notna()
            & (df_quizzes["_id_user"] != "")
        ].copy()


        # ====================================================
        # FILTROS PRINCIPALES
        # ====================================================

        quizzes_filtrados = df_quizzes.copy()


        # ====================================================
        # FILTRO POR AÑO
        # ====================================================

        if año != "Todos":

            ids_año = (
                df_dashboard[
                    df_dashboard["año"].eq(int(año))
                ]["_id_postulante"]
                .astype("string")
                .str.strip()
                .unique()
            )

            quizzes_filtrados = quizzes_filtrados[
                quizzes_filtrados["_id_user"].isin(ids_año)
            ]


        # ====================================================
        # FILTRO POR ÁREA PROFESIONAL
        # ====================================================

        if area != "Todas":

            ids_area = (
                df_dashboard[
                    df_dashboard["area_profesional"].eq(area)
                ]["_id_postulante"]
                .astype("string")
                .str.strip()
                .unique()
            )

            quizzes_filtrados = quizzes_filtrados[
                quizzes_filtrados["_id_user"].isin(ids_area)
            ]


        # ====================================================
        # CONTENEDORES
        # ====================================================

        izquierda, derecha = st.columns(
            [1.15, 1]
        )


        # ====================================================
        # IZQUIERDA
        # COMPLETACIÓN POR QUIZ
        # ====================================================

        with izquierda:

            st.markdown(
                """
                <p style="
                    font-size:16px;
                    font-weight:600;
                    margin-bottom:12px;
                ">
                    Completación por quiz
                </p>
                """,
                unsafe_allow_html=True
            )


            if quizzes_filtrados.empty:

                st.info(
                    "No hay quizzes para los filtros seleccionados."
                )

            else:

                # ============================================
                # RESUMEN POR QUIZ
                # ============================================

                resumen_quizzes = (
                    quizzes_filtrados
                    .groupby(
                        [
                            "quiz_id",
                            "quiz_key",
                            "quiz_nombre"
                        ],
                        dropna=False
                    )
                    .agg(
                        Iniciaron=(
                            "_id_user",
                            "nunique"
                        ),
                        Completaron=(
                            "_id_user",
                            lambda x: (
                                quizzes_filtrados
                                .loc[
                                    x.index,
                                    "estado"
                                ]
                                .eq("Completado")
                                .sum()
                            )
                        )
                    )
                    .reset_index()
                )


                # ============================================
                # PORCENTAJE
                # ============================================

                resumen_quizzes["Completación"] = (
                    resumen_quizzes["Completaron"]
                    .div(
                        resumen_quizzes["Iniciaron"]
                    )
                    .fillna(0)
                    .mul(100)
                    .round(1)
                )


                # ============================================
                # ORDENAR
                # ============================================

                resumen_quizzes = (
                    resumen_quizzes
                    .sort_values(
                        "Completación",
                        ascending=True
                    )
                )


                # ============================================
                # GRÁFICO
                # ============================================

                fig_quizzes = px.bar(
                    resumen_quizzes,
                    x="Completación",
                    y="quiz_nombre",
                    orientation="h",
                    text="Completación"
                )


                fig_quizzes.update_traces(
                    marker_color=COLORS["azul_grafico_quizzes"],
                    marker_line_width=0,
                    texttemplate="%{text:.1f}%",
                    textposition="outside",
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "Completación: %{x:.1f}%"
                        "<extra></extra>"
                    )
                )


                fig_quizzes.update_layout(
                    height=max(
                        300,
                        len(resumen_quizzes) * 60
                    ),
                    margin=dict(
                        l=10,
                        r=55,
                        t=10,
                        b=10
                    ),
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    showlegend=False,

                    xaxis=dict(
                        range=[
                            0,
                            max(
                                100,
                                resumen_quizzes[
                                    "Completación"
                                ].max() + 10
                            )
                        ],
                        ticksuffix="%",
                        showgrid=False,
                        zeroline=False,
                        showline=False,
                        title=None
                    ),

                    yaxis=dict(
                        title=None,
                        showgrid=False,
                        zeroline=False,
                        showline=False
                    )
                )


                st.plotly_chart(
                    fig_quizzes,
                    width="stretch",
                    key="grafico_completacion_quizzes"
                )


        # ====================================================
        # DERECHA
        # DETALLE DEL QUIZ
        # ====================================================

        with derecha:

            st.markdown(
                """
                <p style="
                    font-size:16px;
                    font-weight:600;
                    margin-bottom:12px;
                ">
                    Detalle del quiz
                </p>
                """,
                unsafe_allow_html=True
            )


            # =================================================
            # LISTA DE QUIZZES
            # =================================================

            opciones_quiz = (
                quizzes_filtrados[
                    [
                        "quiz_id",
                        "quiz_nombre"
                    ]
                ]
                .drop_duplicates()
                .dropna(subset=["quiz_nombre"])
                .sort_values("quiz_nombre")
            )


            if opciones_quiz.empty:

                st.info(
                    "No hay quizzes para los filtros seleccionados."
                )

            else:

                opciones_nombres = (
                    opciones_quiz[
                        "quiz_nombre"
                    ]
                    .astype(str)
                    .tolist()
                )


                # =============================================
                # TODOS
                # =============================================

                opciones_nombres = (
                    ["Todos"]
                    + opciones_nombres
                )


                quiz_seleccionado = st.selectbox(
                    "Seleccionar quiz",
                    options=opciones_nombres,
                    key="quiz_seleccionado"
                )


                # =================================================
                # FILTRAR QUIZ SELECCIONADO
                # =================================================

                if quiz_seleccionado == "Todos":

                    detalle_quiz = (
                        quizzes_filtrados
                        .copy()
                    )

                else:

                    detalle_quiz = (
                        quizzes_filtrados[
                            quizzes_filtrados[
                                "quiz_nombre"
                            ]
                            == quiz_seleccionado
                        ]
                        .copy()
                    )


                # =================================================
                # ELIMINAR DUPLICADOS
                # =================================================

                detalle_quiz = (
                    detalle_quiz
                    .drop_duplicates(
                        subset=[
                            "_id_user",
                            "quiz_id"
                        ],
                        keep="last"
                    )
                )


                # =================================================
                # CONTADORES
                # =================================================

                iniciaron = (
                    detalle_quiz[
                        "_id_user"
                    ]
                    .nunique()
                )


                en_proceso = (
                    detalle_quiz[
                        detalle_quiz["estado"]
                        == "En proceso"
                    ]["_id_user"]
                    .nunique()
                )


                completaron = (
                    detalle_quiz[
                        detalle_quiz["estado"]
                        == "Completado"
                    ]["_id_user"]
                    .nunique()
                )


                # =================================================
                # COMPLETACIÓN
                # =================================================

                completacion = porcentaje(
                    completaron,
                    iniciaron
                )


                # =================================================
                # MÉTRICAS PRINCIPALES
                # =================================================

                m1, m2, m3 = st.columns(3)


                with m1:

                    st.metric(
                        "🚀 Iniciaron",
                        f"{iniciaron:,}"
                    )


                with m2:

                    st.metric(
                        "⏳ En proceso",
                        f"{en_proceso:,}"
                    )


                with m3:

                    st.metric(
                        "✅ Completaron",
                        f"{completaron:,}"
                    )


                # =================================================
                # COMPLETACIÓN
                # =================================================

                st.metric(
                    "📊 Completación",
                    f"{completacion:.1f}%"
                )


                

# ============================================================
# EVOLUCIÓN
# ============================================================

st.markdown('<div class="section-title">Evolución de registros</div>', unsafe_allow_html=True)

if "createdAt_user" in df.columns and df["createdAt_user"].notna().any():

    registros = (
        df.dropna(subset=["createdAt_user"])
        .groupby([
            df["createdAt_user"].dt.year.rename("Año"),
            df["createdAt_user"].dt.month.rename("Mes_num")
        ])
        .size()
        .reset_index(name="Postulantes")
    )

    registros["Mes"] = registros["Mes_num"].map(MESES)

    fig = px.bar(
        registros,
        x="Mes",
        y="Postulantes",
        color_discrete_sequence=[COLORS["azul_evolucion"]]
    )

    fig.update_layout(
        height=390,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


st.markdown("---")
st.caption("Dashboard de Postulantes · Laboral.AI")