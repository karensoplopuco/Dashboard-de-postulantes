
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
    initial_sidebar_state="collapsed"
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
    "fondo_card": "#ced6e2",
    "borde": "#D9E2F0",
    "gris": "#E9EEF5"
}


MESES = {
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
    12: "Diciembre"
}


# ============================================================
# ESTILO GENERAL
# ============================================================

st.markdown(
    """
    <style>

    /* Fuente general */
    html, body, [class*="css"] {
        font-family: "Trebuchet MS", "Segoe UI", sans-serif;
    }

    /* Fondo */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Ancho */
    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Título */
    .dashboard-title {
        font-size: 32px;
        font-weight: 700;
        color: #333333;
        margin-bottom: 4px;
    }

    .dashboard-subtitle {
        font-size: 15px;
        color: #666666;
        margin-bottom: 20px;
    }

    /* Títulos */
    .section-title {
        font-size: 21px;
        font-weight: 700;
        color: #333333;
        margin-top: 18px;
        margin-bottom: 14px;
    }

    /* Texto de filtros */
    div[data-testid="stSelectbox"] label {
        font-weight: 600;
        color: #333333;
    }

    /* Títulos de gráficos */
    div[data-testid="stSubheader"] {
        color: #333333;
    }

    /* Ocultar índice */
    .stDataFrame {
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# RUTA DEL DATASET
# ============================================================

ROOT = Path(__file__).resolve().parent

RUTA_DATA = (
    ROOT
    / "data"
    / "cache"
    / "postulantes_dashboard.csv"
)


# ============================================================
# CARGAR DATASET
# ============================================================

@st.cache_data(show_spinner="Cargando dashboard...")
def cargar_dashboard():

    if not RUTA_DATA.exists():

        st.error(
            "No se encontró el archivo "
            "'data/cache/postulantes_dashboard.csv'."
        )

        st.stop()

    df = pd.read_csv(
        RUTA_DATA,
        low_memory=False
    )

    return df


df_dashboard = cargar_dashboard()


# ============================================================
# VALIDACIÓN
# ============================================================

if df_dashboard.empty:

    st.warning(
        "El archivo de postulantes está vacío."
    )

    st.stop()


# ============================================================
# NORMALIZAR ID
# ============================================================

if "_id_postulante" in df_dashboard.columns:

    df_dashboard["_id_postulante"] = (
        df_dashboard["_id_postulante"]
        .astype(str)
    )


# ============================================================
# FECHAS
# ============================================================

if "createdAt_user" in df_dashboard.columns:

    df_dashboard["createdAt_user"] = pd.to_datetime(
        df_dashboard["createdAt_user"],
        errors="coerce"
    )

    df_dashboard["año"] = (
        df_dashboard["createdAt_user"]
        .dt.year
    )

    df_dashboard["mes_num"] = (
        df_dashboard["createdAt_user"]
        .dt.month
    )

    df_dashboard["mes"] = (
        df_dashboard["mes_num"]
        .map(MESES)
    )


# ============================================================
# FUNCIONES
# ============================================================

def limpiar_categoria(serie):

    serie = serie.copy()

    serie = (
        serie
        .astype(str)
        .str.strip()
    )

    serie = serie.replace(
        {
            "nan": pd.NA,
            "None": pd.NA,
            "": pd.NA,
            "Sin registro": pd.NA,
            "Sin Registro": pd.NA,
            "sin registro": pd.NA,
            "N/A": pd.NA,
            "NA": pd.NA,
            "null": pd.NA
        }
    )

    return serie


def porcentaje(valor, total):

    if total == 0:
        return 0

    return round(
        (valor / total) * 100,
        1
    )


def contar_booleano(df, columna):

    if columna not in df.columns:
        return 0

    valores = pd.to_numeric(
        df[columna],
        errors="coerce"
    ).fillna(0)

    return int(
        valores.gt(0).sum()
    )


# ============================================================
# GRÁFICO DE BARRAS
# ============================================================

def crear_barra(
    data,
    categoria,
    valor,
    color,
    altura=360
):

    fig = px.bar(
        data,
        x=valor,
        y=categoria,
        orientation="h"
    )

    fig.update_traces(
        marker_color=color,
        text=None,
        hovertemplate=(
            "%{y}: %{x}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=altura,

        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),

        plot_bgcolor="white",
        paper_bgcolor="white",

        font=dict(
            family="Trebuchet MS",
            color=COLORS["texto"]
        ),

        showlegend=False,

        xaxis=dict(
            title=None,
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            showline=False
        ),

        yaxis=dict(
            title=None,
            categoryorder="total ascending",
            showgrid=False,
            zeroline=False
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
    colores,
    altura=360
):

    fig = px.pie(
        data,
        names=nombres,
        values=valores,
        hole=0.58
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

        textposition="outside",

        hovertemplate=(
            "%{label}: %{value}"
            " (%{percent})"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=altura,

        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10
        ),

        paper_bgcolor="white",
        plot_bgcolor="white",

        font=dict(
            family="Trebuchet MS",
            color=COLORS["texto"]
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        )
    )

    return fig


# ============================================================
# TÍTULO PRINCIPAL
# ============================================================

st.markdown(
    """
    <div class="dashboard-title">
        Dashboard de Postulantes
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="dashboard-subtitle">
        Análisis de perfiles, formación, experiencia y participación
        de los postulantes en Laboral.AI
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FILTROS
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Filtros
    </div>
    """,
    unsafe_allow_html=True
)


f1, f2 = st.columns(2)


# ============================================================
# FILTRO AÑO
# ============================================================

with f1:

    if "año" in df_dashboard.columns:

        años = (
            df_dashboard["año"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        años = sorted(años)

        año_seleccionado = st.selectbox(
            "Año",
            ["Todos"] + años
        )

    else:

        año_seleccionado = "Todos"


# ============================================================
# FILTRO ÁREA PROFESIONAL
# ============================================================

with f2:

    if "area_profesional" in df_dashboard.columns:

        areas = (
            limpiar_categoria(
                df_dashboard["area_profesional"]
            )
            .dropna()
            .unique()
            .tolist()
        )

        areas = sorted(areas)

        area_seleccionada = st.selectbox(
            "Área profesional",
            ["Todas"] + areas
        )

    else:

        area_seleccionada = "Todas"


# ============================================================
# APLICAR FILTROS
# ============================================================

df = df_dashboard.copy()


if (
    año_seleccionado != "Todos"
    and "año" in df.columns
):

    df = df[
        df["año"] == int(
            año_seleccionado
        )
    ]


if (
    area_seleccionada != "Todas"
    and "area_profesional" in df.columns
):

    df = df[
        df["area_profesional"]
        .astype(str)
        .eq(area_seleccionada)
    ]


# ============================================================
# ELIMINAR DUPLICADOS
# ============================================================

if "_id_postulante" in df.columns:

    df = df.drop_duplicates(
        subset="_id_postulante"
    )


# ============================================================
# KPIs
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Indicadores/KPIs
    </div>
    """,
    unsafe_allow_html=True
)


total_postulantes = len(df)


con_cv = contar_booleano(
    df,
    "tiene_cv"
)


uso_ia = contar_booleano(
    df,
    "uso_ia"
)


participaron_eventos = contar_booleano(
    df,
    "participo_evento"
)


postulantes_cursos = contar_booleano(
    df,
    "cantidad_cursos"
)


# ============================================================
# CARDS STREAMLIT
# ============================================================

k1, k2, k3, k4, k5 = st.columns(5)


def mostrar_kpi(
    columna,
    icono,
    titulo,
    valor,
    porcentaje_valor
):

    with columna:

        st.metric(
            label=f"{icono} {titulo}",
            value=f"{valor:,}",
            delta=f"{porcentaje_valor}%"
        )


mostrar_kpi(
    k1,
    "👥",
    "Postulantes",
    total_postulantes,
    "100"
)


mostrar_kpi(
    k2,
    "📄",
    "Con CV",
    con_cv,
    porcentaje(
        con_cv,
        total_postulantes
    )
)


mostrar_kpi(
    k3,
    "🤖",
    "Uso de IA",
    uso_ia,
    porcentaje(
        uso_ia,
        total_postulantes
    )
)


mostrar_kpi(
    k4,
    "🎫",
    "Eventos",
    participaron_eventos,
    porcentaje(
        participaron_eventos,
        total_postulantes
    )
)


mostrar_kpi(
    k5,
    "📚",
    "Cursos",
    postulantes_cursos,
    porcentaje(
        postulantes_cursos,
        total_postulantes
    )
)


# ============================================================
# PERFIL PROFESIONAL
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Perfil profesional
    </div>
    """,
    unsafe_allow_html=True
)


c1, c2 = st.columns(2)


# ============================================================
# CARRERAS
# ============================================================

with c1:

    st.subheader(
        "Carreras con mayor cantidad de postulantes"
    )

    if "carrera_principal" in df.columns:

        carreras = (
            limpiar_categoria(
                df["carrera_principal"]
            )
            .dropna()
            .value_counts()
            .head(10)
            .reset_index()
        )

        carreras.columns = [
            "Carrera",
            "Postulantes"
        ]

        carreras = carreras.sort_values(
            "Postulantes"
        )

        if not carreras.empty:

            fig = crear_barra(
                carreras,
                "Carrera",
                "Postulantes",
                COLORS["celeste"]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "No hay información disponible."
            )


# ============================================================
# ÁREAS
# ============================================================

with c2:

    st.subheader(
        "Áreas profesionales"
    )

    if "area_profesional" in df.columns:

        areas_df = (
            limpiar_categoria(
                df["area_profesional"]
            )
            .dropna()
            .value_counts()
            .head(10)
            .reset_index()
        )

        areas_df.columns = [
            "Área",
            "Postulantes"
        ]

        areas_df = areas_df.sort_values(
            "Postulantes"
        )

        if not areas_df.empty:

            fig = crear_barra(
                areas_df,
                "Área",
                "Postulantes",
                COLORS["azul"]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "No hay información disponible."
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

    st.subheader(
        "Experiencia laboral"
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

    st.subheader(
        "Experiencia en prácticas"
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

st.markdown(
    """
    <div class="section-title">
        Uso de la plataforma
    </div>
    """,
    unsafe_allow_html=True
)


c5, c6 = st.columns(2)


# ============================================================
# IA
# ============================================================

with c5:

    st.subheader(
        "Uso de IA"
    )

    ia_df = pd.DataFrame(
        {
            "Estado": [
                "Utilizó IA",
                "No utilizó IA"
            ],
            "Postulantes": [
                uso_ia,
                max(
                    total_postulantes - uso_ia,
                    0
                )
            ]
        }
    )

    fig = crear_donut(
        ia_df,
        "Estado",
        "Postulantes",
        [
            COLORS["verde_ia"],
            COLORS["gris"]
        ]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# MODALIDAD LABORAL
# ============================================================

with c6:

    st.subheader("Preferencia de modalidad laboral")

    # ========================================================
    # IMPORTANTE
    # ========================================================
    # Este gráfico es INDEPENDIENTE de los filtros:
    # - Año
    # - Área profesional
    #
    # Por eso usamos df_dashboard y NO df.
    # ========================================================

    modalidad_registros = pd.DataFrame()

    # ========================================================
    # FUNCIÓN PARA NORMALIZAR MODALIDAD
    # ========================================================

    def normalizar_modalidad(valor):

        if pd.isna(valor):
            return pd.NA

        valor = (
            str(valor)
            .strip()
            .lower()
        )

        equivalencias = {

            # ------------------------------------------------
            # REMOTO
            # ------------------------------------------------

            "remote": "Remoto",
            "remoto": "Remoto",
            "remota": "Remoto",
            "remote work": "Remoto",
            "trabajo remoto": "Remoto",
            "100% remoto": "Remoto",

            # ------------------------------------------------
            # HÍBRIDO
            # ------------------------------------------------

            "hybrid": "Híbrido",
            "hibrido": "Híbrido",
            "híbrido": "Híbrido",
            "hibrida": "Híbrido",
            "híbrida": "Híbrido",
            "trabajo híbrido": "Híbrido",
            "trabajo hibrido": "Híbrido",

            # ------------------------------------------------
            # PRESENCIAL
            # ------------------------------------------------

            "onsite": "Presencial",
            "on-site": "Presencial",
            "on site": "Presencial",
            "in-person": "Presencial",
            "in person": "Presencial",
            "presencial": "Presencial",
            "trabajo presencial": "Presencial",

            # ------------------------------------------------
            # VACÍOS
            # ------------------------------------------------

            "nan": pd.NA,
            "none": pd.NA,
            "null": pd.NA,
            "n/a": pd.NA,
            "na": pd.NA,
            "": pd.NA,
            "sin registro": pd.NA,
            "sin registrar": pd.NA,
            "no registrado": pd.NA,
            "no registra": pd.NA
        }

        return equivalencias.get(
            valor,
            pd.NA
        )

    # ========================================================
    # 1. USAR MODALIDAD_LABORAL DEL DATASET COMPLETO
    # ========================================================

    if "modalidad_laboral" in df_dashboard.columns:

        modalidad_registros = pd.DataFrame({

            "_id_postulante":
                df_dashboard["_id_postulante"]
                .astype(str)
                .str.strip(),

            "modalidad":
                df_dashboard["modalidad_laboral"]
                .apply(normalizar_modalidad)
        })

    # ========================================================
    # 2. SI NO EXISTE, USAR COLUMNA MODALIDAD
    # ========================================================

    if (
        modalidad_registros.empty
        or modalidad_registros["modalidad"]
        .notna()
        .sum() == 0
    ):

        if "modalidad" in df_dashboard.columns:

            modalidad_registros = pd.DataFrame({

                "_id_postulante":
                    df_dashboard["_id_postulante"]
                    .astype(str)
                    .str.strip(),

                "modalidad":
                    df_dashboard["modalidad"]
                    .apply(normalizar_modalidad)
            })

    # ========================================================
    # 3. ELIMINAR VALORES NO VÁLIDOS
    # ========================================================

    if not modalidad_registros.empty:

        modalidad_registros = modalidad_registros[
            modalidad_registros["modalidad"].isin(
                [
                    "Remoto",
                    "Híbrido",
                    "Presencial"
                ]
            )
        ]

    # ========================================================
    # 4. ELIMINAR DUPLICADOS POR POSTULANTE
    # ========================================================

    if not modalidad_registros.empty:

        modalidad_registros = (
            modalidad_registros
            .drop_duplicates(
                subset="_id_postulante"
            )
        )

    # ========================================================
    # 5. CONTAR MODALIDADES
    # ========================================================

    if not modalidad_registros.empty:

        modalidad_grafico = (
            modalidad_registros[
                "modalidad"
            ]
            .value_counts()
            .rename_axis("Modalidad")
            .reset_index(
                name="Cantidad"
            )
        )

    else:

        modalidad_grafico = pd.DataFrame(
            columns=[
                "Modalidad",
                "Cantidad"
            ]
        )

    # ========================================================
    # 6. ORDEN DE MODALIDADES
    # ========================================================

    if not modalidad_grafico.empty:

        orden_modalidad = [
            "Presencial",
            "Híbrido",
            "Remoto"
        ]

        modalidad_grafico["Modalidad"] = pd.Categorical(
            modalidad_grafico["Modalidad"],
            categories=orden_modalidad,
            ordered=True
        )

        modalidad_grafico = (
            modalidad_grafico
            .sort_values("Modalidad")
            .reset_index(drop=True)
        )

    # ========================================================
    # 7. COLORES
    # ========================================================

    if not modalidad_grafico.empty:

        colores_modalidad = {

            "Presencial":
                COLORS["azul_modalidad"],

            "Híbrido":
                COLORS["lavanda"],

            "Remoto":
                COLORS["turquesa"]
        }

        colores = [
            colores_modalidad.get(
                str(modalidad),
                COLORS["azul"]
            )
            for modalidad
            in modalidad_grafico["Modalidad"]
        ]

        # ====================================================
        # 8. GRÁFICO DONUT
        # ====================================================

        fig = px.pie(
            modalidad_grafico,
            names="Modalidad",
            values="Cantidad",
            hole=0.58
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

            textposition="outside",

            hovertemplate=(
                "<b>%{label}</b><br>"
                "Postulantes: %{value}<br>"
                "Porcentaje: %{percent}"
                "<extra></extra>"
            )
        )

        fig.update_layout(

            height=390,

            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10
            ),

            paper_bgcolor="white",

            plot_bgcolor="white",

            font=dict(
                family="Trebuchet MS",
                color=COLORS["texto"]
            ),

            legend=dict(
                orientation="h",

                yanchor="bottom",

                y=-0.15,

                xanchor="center",

                x=0.5
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No se encontraron registros de modalidad laboral."
        )

# 

# ============================================================
# FORMACIÓN Y PARTICIPACIÓN
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Formación y participación
    </div>
    """,
    unsafe_allow_html=True
)


c7, c8 = st.columns(2)


# ============================================================
# EVENTOS
# ============================================================

with c7:

    st.subheader(
        "Participación en eventos"
    )

    eventos_df = pd.DataFrame(
        {
            "Estado": [
                "Participó",
                "No participó"
            ],
            "Postulantes": [
                participaron_eventos,
                max(
                    total_postulantes
                    - participaron_eventos,
                    0
                )
            ]
        }
    )

    fig = crear_donut(
        eventos_df,
        "Estado",
        "Postulantes",
        [
            COLORS["azul_eventos"],
            COLORS["gris"]
        ]
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# NIVEL EDUCATIVO
# ============================================================

with c8:

    st.subheader(
        "Nivel educativo"
    )

    if "nivel_educativo" in df.columns:

        nivel_df = (
            limpiar_categoria(
                df["nivel_educativo"]
            )
            .dropna()
            .replace(
                {
                    "Bachelor": "Bachiller",
                    "Student": "Estudiante",
                    "Other": "Otros",
                    "Diploma": "Diplomado",
                    "Master": "Maestría",
                    "Certificate": "Certificado"
                }
            )
            .value_counts()
            .head(8)
            .reset_index()
        )

        nivel_df.columns = [
            "Nivel",
            "Postulantes"
        ]

        nivel_df = nivel_df.sort_values(
            "Postulantes"
        )

        if not nivel_df.empty:

            fig = crear_barra(
                nivel_df,
                "Nivel",
                "Postulantes",
                COLORS["azul"]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "No hay información educativa."
            )


# ============================================================
# EVOLUCIÓN DE REGISTROS
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Evolución de registros
    </div>
    """,
    unsafe_allow_html=True
)


if (
    "createdAt_user" in df.columns
    and df["createdAt_user"].notna().any()
):

    registros = (
        df.dropna(
            subset=["createdAt_user"]
        )
        .groupby(
            [
                df["createdAt_user"].dt.year.rename("año"),
                df["createdAt_user"].dt.month.rename("mes_num")
            ]
        )
        .size()
        .reset_index(
            name="Postulantes"
        )
    )

    registros["Mes"] = (
        registros["mes_num"]
        .map(MESES)
    )

    registros = registros.sort_values(
        [
            "año",
            "mes_num"
        ]
    )


    # --------------------------------------------------------
    # Si existe filtro central de año
    # --------------------------------------------------------

    if año_seleccionado != "Todos":

        registros = registros[
            registros["año"]
            == int(año_seleccionado)
        ]


    if not registros.empty:

        fig = px.bar(
            registros,
            x="Mes",
            y="Postulantes",
            color_discrete_sequence=[
                COLORS["periwinkle"]
            ]
        )

        fig.update_traces(
            hovertemplate=(
                "%{x}: %{y} postulantes"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            height=390,

            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10
            ),

            plot_bgcolor="white",
            paper_bgcolor="white",

            font=dict(
                family="Trebuchet MS",
                color=COLORS["texto"]
            ),

            xaxis=dict(
                title=None,
                showgrid=False
            ),

            yaxis=dict(
                title=None,
                showgrid=False,
                showticklabels=False,
                zeroline=False
            ),

            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "No hay registros para el año seleccionado."
        )

else:

    st.info(
        "No hay información suficiente para mostrar "
        "la evolución de registros."
    )


# ============================================================
# SIN RESULTADOS
# ============================================================

if total_postulantes == 0:

    st.warning(
        "No existen postulantes que coincidan "
        "con los filtros seleccionados."
    )


# ============================================================
# PIE
# ============================================================

st.markdown("---")

st.caption(
    "Dashboard de Postulantes · Laboral.AI"
)
