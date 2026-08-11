import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Dashboard de Postulantes 📊",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


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

def limpiar_categoria(serie):

    return (
        serie.astype(str)
        .str.strip()
        .replace({
            "nan": pd.NA,
            "None": pd.NA,
            "": pd.NA,
            "Sin registro": pd.NA,
            "N/A": pd.NA
        })
    )


def porcentaje(valor, total):
    return 0 if total == 0 else round(valor / total * 100, 1)


def contar_booleano(df, columna):

    if columna not in df.columns:
        return 0

    return int(
        pd.to_numeric(df[columna], errors="coerce")
        .fillna(0)
        .gt(0)
        .sum()
    )


def crear_barra(data, categoria, valor, color):

    fig = px.bar(
        data,
        x=valor,
        y=categoria,
        orientation="h"
    )

    fig.update_traces(marker_color=color)

    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(categoryorder="total ascending")
    )

    return fig


def crear_donut(data, nombres, valores, colores):

    fig = px.pie(
        data,
        names=nombres,
        values=valores,
        hole=.58
    )

    fig.update_traces(
        marker=dict(colors=colores, line=dict(color="white", width=2)),
        textinfo="percent",
        textposition="outside"
    )

    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white"
    )

    return fig


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("Filtros")

    st.caption("Refina la información del dashboard")

    st.divider()

    # Año
    años = sorted(
        df_dashboard["año"].dropna().astype(int).unique()
    ) if "año" in df_dashboard.columns else []

    año = st.selectbox(
        "Año",
        ["Todos"] + años
    )

    # Área
    areas = sorted(
        limpiar_categoria(
            df_dashboard["area_profesional"]
        ).dropna().unique()
    ) if "area_profesional" in df_dashboard.columns else []

    area = st.selectbox(
        "Área profesional",
        ["Todas"] + areas
    )

    st.divider()

    if st.button(
        "Limpiar filtros",
        use_container_width=True
    ):
        st.rerun()


# ============================================================
# FILTRAR
# ============================================================

df = df_dashboard.copy()

if año != "Todos":
    df = df[df["año"] == int(año)]

if area != "Todas":
    df = df[
        df["area_profesional"]
        .astype(str)
        .eq(area)
    ]

if "_id_postulante" in df.columns:
    df = df.drop_duplicates("_id_postulante")


# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    '<div class="dashboard-title">Dashboard de Postulantes</div>',
    unsafe_allow_html=True
)

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

    st.subheader("Carreras con mayor cantidad de postulantes")

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

    st.subheader("Áreas profesionales")

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
# USO DE LA PLATAFORMA
# ============================================================

st.markdown('<div class="section-title">Uso de la plataforma</div>', unsafe_allow_html=True)

u1, u2 = st.columns(2)

with u1:

    st.subheader("Uso de IA")

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

    st.subheader("Participación en eventos")

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
        use_container_width=True
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