import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


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
st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Título
st.title("Dashboard de Postulantes")


# ============================================================
# COLORES CORPORATIVOS
# ============================================================

COLORS = {
    "azul": "#A2B9EE",
    "celeste": "#A2DCEE",
    "menta": "#ADEEE2",
    "periwinkle": "#9A9CEA",
    "azul_eventos": "#7FB3D5",
    "verde_ia": "#9AD0C2",
    "turquesa": "#7CCCC4",
    "lavanda": "#CDB4DB",
    "azul_modalidad": "#A7C7E7",
    "texto": "#333333",
    "fondo_card": "#CED6E2",
    "borde": "#D9E2F0",
    "gris": "#E9EEF5"
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

[data-testid="stSidebar"] {
    background-color: #F7F9FC;
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

    return pd.read_csv(RUTA_DATA, low_memory=False)


df_dashboard = cargar_dashboard()

# ============================================================
# CARGAR EVENTOS
# ============================================================

RUTA_EVENTOS = ROOT / "data" / "cache" / "eventos_dashboard.csv"


@st.cache_data
def cargar_eventos():

    if not RUTA_EVENTOS.exists():
        return pd.DataFrame()

    return pd.read_csv(
        RUTA_EVENTOS,
        low_memory=False
    )

if df_dashboard.empty:
    st.warning("El archivo está vacío.")
    st.stop()


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

    fig.update_layout(
        height=350,
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        xaxis=dict(
            showticklabels=False,
            showgrid=False
        ),
        yaxis=dict(
            categoryorder="total ascending"
        )
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

st.markdown('<div class="section-title">Indicadores/KPIs</div>', unsafe_allow_html=True)

total = len(df)
con_cv = contar_booleano(df, "tiene_cv")
uso_ia = contar_booleano(df, "uso_ia")
eventos = contar_booleano(df, "participo_evento")
cursos = contar_booleano(df, "cantidad_cursos")

cols = st.columns(5)

datos_kpi = [
    ("👥", "Postulantes", total),
    ("📄", "Con CV", con_cv),
    ("🤖", "Uso IA", uso_ia),
    ("🎫", "Eventos", eventos),
    ("📚", "Cursos", cursos)
]

for col, (icono, titulo, valor) in zip(cols, datos_kpi):

    with col:

        delta = "100%" if titulo == "Postulantes" else f"{porcentaje(valor, total)}%"

        st.metric(
            f"{icono} {titulo}",
            f"{valor:,}",
            delta
        )


# ============================================================
# PERFIL PROFESIONAL
# ============================================================

st.markdown('<div class="section-title">Perfil profesional</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:

    st.markdown(
    "<p style='font-size:16px; font-weight:600; margin-bottom:8px;'>Carreras con mayor cantidad de postulantes</p>",
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
                COLORS["celeste"]
            ),
            use_container_width=True
        )

with c2:

    st.markdown(
    "<p style='font-size:16px; font-weight:600; margin-bottom:8px;'>Áreas profesionales</p>",
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
                COLORS["azul"]
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
            COLORS["periwinkle"]
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
            COLORS["menta"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# ============================================================
# USO DE LA PLATAFORMA
# ============================================================

st.markdown('<div class="section-title">Uso de la plataforma</div>', unsafe_allow_html=True)

u1, u2 = st.columns(2)

with u1:

    st.markdown(
    "<p style='font-size:16px; font-weight:600; margin-bottom:8px;'>Uso de IA</p>",
    unsafe_allow_html=True
    )


    ia_df = pd.DataFrame({
        "Estado": ["Utilizó IA", "No utilizó IA"],
        "Postulantes": [uso_ia, max(total - uso_ia, 0)]
    })

    st.plotly_chart(
        crear_donut(
            ia_df,
            "Estado",
            "Postulantes",
            [COLORS["verde_ia"], COLORS["gris"]]
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
            [COLORS["azul_eventos"], COLORS["gris"]]
        ),
        use_container_width=True,
        key="donut_participacion_eventos"
    )





# ============================================================
# PARTICIPACIÓN SEGÚN TIPO DE EVENTO
# ============================================================

st.markdown(
    '<div class="section-title">Participación según tipo de evento</div>',
    unsafe_allow_html=True
)

df_eventos = cargar_eventos()

if not df_eventos.empty and "tipo_evento" in df_eventos.columns:

    # --------------------------------------------------------
    # FILTRAR EVENTOS SEGÚN LOS POSTULANTES FILTRADOS
    # --------------------------------------------------------

    if "_id_postulante" in df.columns and "_id_postulante" in df_eventos.columns:

        ids_filtrados = (
            df["_id_postulante"]
            .dropna()
            .astype(str)
            .unique()
        )

        eventos_filtrados = df_eventos[
            df_eventos["_id_postulante"]
            .astype(str)
            .isin(ids_filtrados)
        ].copy()

    else:

        eventos_filtrados = df_eventos.copy()

    # --------------------------------------------------------
    # CONTAR TIPOS DE EVENTO
    # --------------------------------------------------------

    eventos_tipo = (
        limpiar_categoria(
            eventos_filtrados["tipo_evento"]
        )
        .dropna()
        .value_counts()
        .reset_index()
    )

    eventos_tipo.columns = [
        "Tipo de evento",
        "Participaciones"
    ]

    # --------------------------------------------------------
    # GRÁFICO
    # --------------------------------------------------------

    if not eventos_tipo.empty:

        fig_eventos = crear_barra(
            eventos_tipo,
            "Tipo de evento",
            "Participaciones",
            COLORS["azul_eventos"]
        )

        st.plotly_chart(
            fig_eventos,
            use_container_width=True,
            key="grafico_tipo_evento"
        )

    else:

        st.info(
            "No hay participación en eventos para los filtros seleccionados."
        )

else:

    st.info(
        "No hay información disponible sobre los tipos de eventos."
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
        color_discrete_sequence=[COLORS["periwinkle"]]
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