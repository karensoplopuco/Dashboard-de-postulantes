from pathlib import Path
from datetime import datetime, date
import html
import re
import unicodedata

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Compatibilidad: se consulta Mongo solo como respaldo para mostrar el detalle
# de los análisis registrados. No se modifica ningún dato.
try:
    from pymongo import ObjectId
    try:
        from scripts.conexion import get_db
    except Exception:
        from conexion import get_db
except Exception:
    ObjectId = None
    get_db = None


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="BCP | Laboral.AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ARCHIVO_INDICADORES = DATA_DIR / "indicadores_bcp.xlsx"
ARCHIVO_ANALISIS = DATA_DIR / "analisis_bcp.xlsx"
ARCHIVO_VALIDACION = DATA_DIR / "validacion_postulantes_bcp.xlsx"
FECHA_EVENTO = pd.Timestamp("2026-08-20")

AZUL = "#3d8290"
AZUL_OSCURO = "#66c7d1"
AZUL_SUAVE = "#EAF4FF"
MORADO = "#7030a0"
MORADO_SUAVE = "#F2ECFF"
VERDE = "#a6c263"
VERDE_SUAVE = "#E9F8F1"
NARANJA = "#ffde59"
GRIS = "#52647A"
BORDE = "#DDE7F1"
FONDO = "#F5F8FC"
BLANCO = "#FFFFFF"
NEGRO= "#000000"
XD="#f0901a"


# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
    <style>
    .stApp {{ background: {FONDO}; }}

    /* Barra superior de Streamlit */
    header[data-testid="stHeader"] {{
    background: {FONDO} !important;
    box-shadow: none !important;
    border-bottom: none !important;
    }}
    html, body, [class*="css"] {{
        font-family: "Segoe UI", Arial, sans-serif;
    }}
    .block-container {{
    max-width: 1700px;
    padding-top: 1.15rem;
    padding-bottom: 3rem;
    }}
    h1, h2, h3 {{ color: {NEGRO}; }}
    h1 {{ font-size: 30px !important; letter-spacing: -0.5px; }}
    h2 {{ font-size: 22px !important; }}
    h3 {{ font-size: 17px !important; }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #071B33 0%, #0B223D 100%);
    }}
    section[data-testid="stSidebar"] * {{ color: white; }}
    section[data-testid="stSidebar"] .stButton button {{
        color: #071B33;
        background: white;
        border: 0;
        border-radius: 8px;
        font-weight: 600;
    }}

    .brand {{
        padding: 4px 0 18px 0;
        font-size: 23px;
        font-weight: 800;
        color: white;
    }}
    .brand span {{ color: #8DBBE0; font-weight: 500; }}
    .brand small {{
        display: block;
        margin-top: 5px;
        color: #AFC2D5;
        font-size: 11px;
        font-weight: 400;
    }}

    .page-subtitle {{
        color: #687B8F;
        font-size: 13px;
        margin-top: -10px;
        margin-bottom: 18px;
    }}
    .section-title {{
        color: {NEGRO};
        font-size: 18px;
        font-weight: 750;
        margin-top: 18px;
        margin-bottom: 3px;
    }}
    .section-subtitle {{
        color: #718297;
        font-size: 11px;
        margin-bottom: 10px;
    }}

    .filter-shell {{
        background: transparent !important;
        border: 0 !important;
        border-radius: 0;
        padding: 0;
        margin: 0 0 12px 0;
    }}
    .filter-shell [data-testid="stSelectbox"],
    .filter-shell [data-testid="stDateInput"] {{
        background: transparent !important;
    }}
    .filter-shell [data-baseweb="select"] > div {{
        background: white !important;
        border: 1px solid {BORDE} !important;
        border-radius: 8px !important;
    }}
    .filter-state {{
        color: #6C7D90;
        font-size: 11px;
        margin-top: -7px;
        margin-bottom: 10px;
    }}

    .metric-card {{
        min-height: 132px;
        height: 132px;
        box-sizing: border-box;
        background: white;
        border: 1px solid {BORDE};
        border-radius: 14px;
        padding: 15px 16px;
        box-shadow: 0 2px 10px rgba(7,27,51,.035);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .metric-label {{
        color: #31465D;
        font-size: 11px;
        font-weight: 700;
        line-height: 1.3;
        min-height: 29px;
    }}
    .metric-value {{
        color: {NEGRO};
        font-size: 28px;
        font-weight: 800;
        line-height: 1;
        margin: 2px 0;
    }}
    .metric-sub {{
        color: #728398;
        font-size: 10px;
        line-height: 1.35;
    }}

    .mini-card {{
        min-height: 112px;
        height: 112px;
        box-sizing: border-box;
        background: white;
        border: 1px solid {BORDE};
        border-radius: 12px;
        padding: 13px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .mini-title {{ color: {NEGRO}; font-size: 11px; font-weight: 700; }}
    .mini-value {{ color: {NEGRO}; font-size: 22px; font-weight: 800; }}
    .mini-sub {{ color: #7A899A; font-size: 10px; line-height: 1.3; }}

    .tag-grid {{
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin-top: 7px;
    }}
    .tag {{
        display: inline-block;
        padding: 6px 9px;
        border-radius: 7px;
        border: 1px solid {BORDE};
        background: #F8FBFE;
        color: #29425C;
        font-size: 11px;
    }}
    .tag-hard {{ background: #EEF7FF; border-color: #CFE6FA; }}
    .tag-soft {{ background: #F5F0FF; border-color: #E0D4FA; }}
    .tag-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; margin-top:8px; }}
    .tag {{ min-height:30px; box-sizing:border-box; display:flex; align-items:center; justify-content:center; text-align:center; line-height:1.2; }}
    .ikigai-block {{
    background: transparent;
    border: none;
    padding: 0;
    margin: 0 0 14px 0;
    }}
    .ikigai-title {{ color:{NEGRO}; font-size:14px; font-weight:750; margin-bottom:2px; }}
    /* El contenedor de filtros no debe crear un rectángulo blanco. */
    .filter-shell {{ background:transparent !important; border:0 !important; padding:0 !important; margin-bottom:12px; }}
    .mini-card {{ margin-bottom:10px; }}

    .profile-header {{
        background: white;
        border: 1px solid {BORDE};
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 12px;
    }}
    .participant-name {{
        color: {NARANJA};
        font-size: 24px;
        font-weight: 800;
        margin-bottom: 4px;
    }}
    .participant-meta {{ color: #718297; font-size: 12px; }}

    .simple-box {{
        background: white;
        border: 1px solid {BORDE};
        border-radius: 14px;
        padding: 15px;
    }}

    .legend {{
        color: #6E7F92;
        font-size: 10px;
        margin-top: 4px;
    }}

    div[data-testid="stMetric"] {{
        min-height: 110px;
        height: 110px;
        box-sizing: border-box;
        background: white;
        border: 1px solid {BORDE};
        border-radius: 12px;
        padding: 12px;
    }}
    div[data-testid="stMetricLabel"] {{ font-size: 11px; }}
    div[data-testid="stMetricValue"] {{ font-size: 25px; }}
    .stDataFrame {{ border-radius: 10px; }}

        /* Pestañas de Habilidades */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        color: #6D28D9 !important;
        font-weight: 600 !important;
    }}

    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        color: #7C3AED !important;
        font-weight: 700 !important;
    }}

    .stTabs [data-baseweb="tab-highlight"] {{
        background-color: #7C3AED !important;
        height: 3px !important;
    }}
    
    </style>
    
    """,
    unsafe_allow_html=True,
)


# ============================================================
# UTILIDADES
# ============================================================

def norm_col(text):
    text = "" if text is None else str(text).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def normalizar_columnas(df):
    if df is None:
        return pd.DataFrame()
    out = df.copy()
    out.columns = [norm_col(c) for c in out.columns]
    return out


def col(df, candidatos):
    if df is None or df.empty:
        return None
    mapa = {norm_col(c): c for c in df.columns}
    for c in candidatos:
        if norm_col(c) in mapa:
            return mapa[norm_col(c)]
    return None


def texto(valor):
    if valor is None:
        return ""
    try:
        if pd.isna(valor):
            return ""
    except Exception:
        pass
    return re.sub(r"\s+", " ", str(valor).strip())


def texto_norm(valor):
    t = texto(valor).lower()
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9+#./ ]+", " ", t).strip()


def nombre_normalizado(valor):
    t = texto(valor)
    if not t:
        return ""
    return " ".join(p[:1].upper() + p[1:].lower() for p in t.split())


def porcentaje(n, d):
    try:
        return float(n) / float(d) * 100 if float(d) else 0.0
    except Exception:
        return 0.0


def entero(v, default=0):
    try:
        return int(float(v))
    except Exception:
        return default


def escapar(v):
    return html.escape(texto(v))


def fecha_maxima_actividad():
    if df_actividad.empty:
        return FECHA_EVENTO
    c = col(df_actividad, ["fecha", "created_at", "createdAt", "date", "timestamp"])
    if not c:
        return FECHA_EVENTO
    s = pd.to_datetime(df_actividad[c], errors="coerce").dropna()
    return max(FECHA_EVENTO, s.max().normalize()) if not s.empty else FECHA_EVENTO


def titulo_pagina(titulo, descripcion=""):
    st.title(titulo)
    if descripcion:
        st.markdown(f'<div class="page-subtitle">{escapar(descripcion)}</div>', unsafe_allow_html=True)


def seccion(titulo, descripcion=""):
    st.markdown(f'<div class="section-title">{escapar(titulo)}</div>', unsafe_allow_html=True)
    if descripcion:
        st.markdown(f'<div class="section-subtitle">{escapar(descripcion)}</div>', unsafe_allow_html=True)


def metricas_cards(items, columnas=None):
    columnas = columnas or len(items)
    cols = st.columns(columnas)
    for c, (label, value, sub) in zip(cols, items):
        with c:
            st.markdown(
                f'''<div class="metric-card">
                    <div class="metric-label">{escapar(label)}</div>
                    <div class="metric-value">{escapar(value)}</div>
                    <div class="metric-sub">{escapar(sub)}</div>
                </div>''',
                unsafe_allow_html=True,
            )


def mini_cards(items, columnas=4):
    cols = st.columns(columnas)
    for c, (label, value, sub) in zip(cols, items):
        with c:
            st.markdown(
                f'''<div class="mini-card">
                    <div class="mini-title">{escapar(label)}</div>
                    <div class="mini-value">{escapar(value)}</div>
                    <div class="mini-sub">{escapar(sub)}</div>
                </div>''',
                unsafe_allow_html=True,
            )


def figura_base(fig, altura=320):
    fig.update_layout(
        height=altura,
        margin=dict(l=10, r=30, t=20, b=35),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Arial, sans-serif", size=11, color="#52647A"),
        hoverlabel=dict(bgcolor="white", font_size=11),
    )
    return fig


def grafico_vacio(mensaje, altura=260):
    fig = go.Figure()
    fig.add_annotation(text=mensaje, x=.5, y=.5, xref="paper", yref="paper", showarrow=False,
                       font=dict(size=13, color="#7A899A"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return figura_base(fig, altura)


# ============================================================
# CARGA DE EXCEL
# ============================================================

@st.cache_data(show_spinner=False)
def leer_libro(ruta_str):
    ruta = Path(ruta_str)
    if not ruta.exists():
        return {}
    try:
        return pd.read_excel(ruta, sheet_name=None)
    except Exception:
        return {}


def hoja(libro, nombres):
    if not libro:
        return pd.DataFrame()
    mapa = {norm_col(k): k for k in libro.keys()}
    for n in nombres:
        if norm_col(n) in mapa:
            return normalizar_columnas(libro[mapa[norm_col(n)]])
    for n in nombres:
        k = norm_col(n)
        for nk, real in mapa.items():
            if k in nk or nk in k:
                return normalizar_columnas(libro[real])
    return pd.DataFrame()


if not ARCHIVO_INDICADORES.exists():
    st.error("No se encontró data/indicadores_bcp.xlsx. Ejecuta primero python scripts/indicadores_bcp.py")
    st.stop()

lib_ind = leer_libro(str(ARCHIVO_INDICADORES))
lib_ana = leer_libro(str(ARCHIVO_ANALISIS)) if ARCHIVO_ANALISIS.exists() else {}

# Fuente opcional directa: postulantes_individual.
# Se usa para recuperar carrera y evidencias que pueden haberse perdido en el Excel de indicadores.
def _buscar_archivo(nombre_base, extensiones=("xlsx", "xls", "csv")):
    candidatos=[]
    for ext in extensiones:
        candidatos += [DATA_DIR/f"{nombre_base}.{ext}", BASE_DIR/f"{nombre_base}.{ext}"]
    try:
        candidatos += [x for x in BASE_DIR.rglob(f"{nombre_base}.*") if x.suffix.lower().lstrip(".") in extensiones]
    except Exception:
        pass
    vistos=set()
    for ruta in candidatos:
        ruta=Path(ruta)
        if ruta in vistos: continue
        vistos.add(ruta)
        if ruta.exists() and ruta.is_file(): return ruta
    return None

def _leer_archivo_tabular(ruta):
    if ruta is None: return pd.DataFrame()
    try:
        if ruta.suffix.lower()==".csv": return normalizar_columnas(pd.read_csv(ruta))
        libro=leer_libro(str(ruta))
        for nombre in [ruta.stem,"postulantes_individual","Postulantes","Sheet1"]:
            df=hoja(libro,[nombre])
            if not df.empty: return df
        if libro: return normalizar_columnas(next(iter(libro.values())))
    except Exception: pass
    return pd.DataFrame()

def cargar_postulantes_individual():
    return _leer_archivo_tabular(_buscar_archivo("postulantes_individual"))

def cargar_validacion_postulantes():
    return _leer_archivo_tabular(_buscar_archivo("validacion_postulantes_bcp"))

df_postulantes_individual = cargar_postulantes_individual()
df_validacion_postulantes = cargar_validacion_postulantes()

df_resumen = hoja(lib_ind, ["Resumen", "Resumen_Indicadores", "Indicadores", "Indicadores_BCP"])
df_participantes = hoja(lib_ind, ["Participantes", "Maestro", "Tabla_Maestra"])
df_skills_raw = hoja(lib_ind, ["Skills", "Habilidades"])
df_actividad = hoja(lib_ind, ["Actividad", "Actividad_BCP", "Evolucion"])
df_educacion = hoja(lib_ind, ["Educacion", "Education", "Cvs_education"])
df_experiencia = hoja(lib_ind, ["Experiencia", "Experience", "Workexperiences", "Cvs_workExperience"])
df_idiomas = hoja(lib_ind, ["Idiomas", "Languages"])
df_notificaciones = hoja(lib_ind, ["Notificaciones", "Notifications", "Alertas"])
df_evaluaciones = hoja(lib_ind, ["Evaluaciones", "Evaluations", "Quizzes", "Resultados_Evaluaciones"])

df_ikigai_perfil = hoja(lib_ana, ["Ikigai_Perfil"])
df_ikigai_frecuencias = hoja(lib_ana, ["Ikigai_Frecuencias"])
df_habilidades = hoja(lib_ana, ["Habilidades"])
df_skills_demanda = hoja(lib_ana, ["Skills_vs_Demanda"])
df_jobs = hoja(lib_ana, ["Jobs"])
df_jobs_departamentos = hoja(lib_ana, ["Jobs_Departamentos"])
df_jobs_titulos = hoja(lib_ana, ["Jobs_Titulos"])
df_resumen_analitico = hoja(lib_ana, ["Resumen_Analitico"])
df_compat_excel = hoja(lib_ana, ["Compatibilidad", "Analisis_Compatibilidad", "Compatibility"])


# ============================================================
# MAESTRO DE PARTICIPANTES
# ============================================================

if df_participantes.empty:
    st.error("No se encontró la tabla maestra de participantes en indicadores_bcp.xlsx.")
    st.stop()

COL_USER = col(df_participantes, ["user_id", "userid", "user", "_id"])
COL_NOMBRE = col(df_participantes, ["nombre_completo", "full_name", "fullname"])
COL_NOMBRE = COL_NOMBRE or col(df_participantes, ["nombre", "firstname", "first_name"])
COL_APELLIDO = col(df_participantes, ["apellido", "lastname", "last_name", "surname"])
COL_CARRERA = col(df_participantes, ["carrera", "career", "area_carrera", "profesion", "degree"])
COL_EMAIL = col(df_participantes, ["email", "correo", "correo_bcp"])

# Enriquecer la tabla maestra con postulantes_individual cuando exista.
# Esto corrige especialmente carrera, CV, educación, experiencia y uso de funcionalidades.
if not df_postulantes_individual.empty and COL_USER:
    PI_USER = col(df_postulantes_individual, ["user_id", "userid", "user", "_id_postulante", "_id_user", "_id"])
    if PI_USER:
        base_ids = df_participantes[COL_USER].astype(str).str.strip()
        pi = df_postulantes_individual.copy()
        pi["__join_id"] = pi[PI_USER].astype(str).str.strip()
        pi = pi.drop_duplicates("__join_id").set_index("__join_id")
        for c in pi.columns:
            if c == "__join_id":
                continue
            if c not in df_participantes.columns:
                mapa = dict(zip(pi.index, pi[c]))
                df_participantes[c] = base_ids.map(mapa)
            else:
                # Solo completar vacíos; no reemplazar datos ya consolidados.
                mask = df_participantes[c].isna() | df_participantes[c].astype(str).str.strip().isin(["", "nan", "None"])
                mapa = dict(zip(pi.index, pi[c]))
                df_participantes.loc[mask, c] = base_ids[mask].map(mapa)

# Si los IDs de usuario no coinciden entre archivos, intentar una segunda unión por correo.
if not df_postulantes_individual.empty and COL_EMAIL:
    PI_EMAIL = col(df_postulantes_individual, ["email", "correo", "correo_electronico"])
    if PI_EMAIL:
        base_email = df_participantes[COL_EMAIL].astype(str).str.strip().str.lower()
        pi_email = df_postulantes_individual.copy()
        pi_email["__join_email"] = pi_email[PI_EMAIL].astype(str).str.strip().str.lower()
        pi_email = pi_email.drop_duplicates("__join_email").set_index("__join_email")
        for c in pi_email.columns:
            if c == "__join_email":
                continue
            if c not in df_participantes.columns:
                mapa = dict(zip(pi_email.index, pi_email[c]))
                df_participantes[c] = base_email.map(mapa)
            else:
                mask = df_participantes[c].isna() | df_participantes[c].astype(str).str.strip().isin(["", "nan", "None"])
                mapa = dict(zip(pi_email.index, pi_email[c]))
                df_participantes.loc[mask, c] = base_email[mask].map(mapa)

# Si el Excel de indicadores no trae carrera pero postulantes_individual sí, usarla directamente.
COL_CARRERA = col(df_participantes, ["carrera", "career", "area_carrera", "profesion", "degree"])
# Completar carrera desde la validación BCP si el maestro todavía no la tiene.
if not df_validacion_postulantes.empty:
    VC_USER=col(df_validacion_postulantes,["user_id","userid","user","user_object_id"])
    VC_EMAIL=col(df_validacion_postulantes,["correo_normalizado","correo_bcp","email","correo","email_x","email_y"])
    VC_CARRERA=col(df_validacion_postulantes,["carrera","career","profesion","degree"])
    if VC_CARRERA:
        if not COL_CARRERA:
            df_participantes["carrera"]=pd.NA
            COL_CARRERA="carrera"
        if VC_USER and COL_USER:
            mapa=df_validacion_postulantes[[VC_USER,VC_CARRERA]].dropna(subset=[VC_USER,VC_CARRERA]).drop_duplicates(VC_USER).set_index(VC_USER)[VC_CARRERA].to_dict()
            idsbase=df_participantes[COL_USER].astype(str).str.strip()
            mask=df_participantes[COL_CARRERA].isna() | df_participantes[COL_CARRERA].astype(str).str.strip().isin(["","nan","None"])
            df_participantes.loc[mask,COL_CARRERA]=idsbase[mask].map(mapa)
        if VC_EMAIL and COL_EMAIL:
            mapa=df_validacion_postulantes[[VC_EMAIL,VC_CARRERA]].dropna(subset=[VC_EMAIL,VC_CARRERA]).assign(__e=lambda d:d[VC_EMAIL].astype(str).str.strip().str.lower()).drop_duplicates("__e").set_index("__e")[VC_CARRERA].to_dict()
            emails=df_participantes[COL_EMAIL].astype(str).str.strip().str.lower()
            mask=df_participantes[COL_CARRERA].isna() | df_participantes[COL_CARRERA].astype(str).str.strip().isin(["","nan","None"])
            df_participantes.loc[mask,COL_CARRERA]=emails[mask].map(mapa)


def cargar_catalogo_carreras():
    """Carga un catálogo opcional desde data/carreras.xlsx."""
    rutas = [DATA_DIR / "carreras.xlsx", BASE_DIR / "carreras.xlsx"]
    ruta = next((r for r in rutas if r.exists()), None)
    if ruta is None:
        return {}
    try:
        df = pd.read_excel(ruta)
        c_orig = col(df, ["carrera_original", "original", "alias", "carrera"])
        c_std = col(df, ["carrera_estandar", "estandarizada", "carrera_normalizada"])
        if not c_orig or not c_std:
            return {}
        return {
            texto_norm(a): texto(b)
            for a, b in zip(df[c_orig], df[c_std])
            if texto_norm(a) and texto(b)
        }
    except Exception:
        return {}

CATALOGO_CARRERAS = cargar_catalogo_carreras()

def carrera_canonica(valor):
    t=texto(valor)
    if not t: return "Sin especificar"
    k=texto_norm(t)
    if k in CATALOGO_CARRERAS: return CATALOGO_CARRERAS[k]
    reglas=[
        (["administracion de negocios internacionales","negocios internacionales","comercio exterior"],"Administración de Negocios Internacionales"),
        (["administracion y marketing","marketing y administracion"],"Administración y Marketing"),
        (["administracion de empresas"],"Administración de Empresas"),
        (["ingenieria de sistemas y computacion"],"Ingeniería de Sistemas y Computación"),
        (["ingenieria de sistemas","ingenieria en sistemas"],"Ingeniería de Sistemas"),
        (["ingenieria de software","desarrollo de software"],"Ingeniería de Software"),
        (["ingenieria industrial"],"Ingeniería Industrial"),
        (["comunicacion y publicidad"],"Comunicación y Publicidad"),
        (["comunicacion","comunicaciones"],"Comunicación"),
        (["marketing"],"Marketing"),
        (["contabilidad","contador","contable"],"Contabilidad"),
        (["economia","economista"],"Economía"),
        (["finanzas","financiera","financiero"],"Finanzas"),
        (["recursos humanos","talento humano"],"Recursos Humanos"),
        (["psicologia","psicologo"],"Psicología"),
        (["derecho","abogado"],"Derecho"),
        (["administracion","gestion empresarial","gestion de negocios"],"Administración"),
        (["ingenieria de datos","ciencia de datos","data science","big data"],"Ciencia de Datos"),
    ]
    for claves,etiqueta in reglas:
        if any(x in k for x in claves): return etiqueta
    return t[:1].upper()+t[1:] if t else "Sin especificar"

# Importante: "profesion" en postulantes_individual puede contener un puesto
# laboral y no necesariamente una carrera. Esos valores NO deben alimentar
# el filtro de carreras del programa BCP.
PATRONES_PUESTO = [
    "asesor", "asistente", "analista", "auxiliar", "coordinador", "supervisor",
    "gerente", "jefe", "encargado", "vendedor", "ventas", "comercial",
    "operador", "desarrollador", "developer", "programador", "practicante",
    "practicante", "becario", "especialista", "consultor", "ejecutivo",
    "representante", "atencion al cliente", "customer service", "soporte",
    "tecnico", "tecnica", "recepcionista", "secretaria", "administrativo",
    "administrativa", "digitador", "marketing digital", "community manager",
    "content manager", "product manager", "project manager"
]

def parece_puesto_laboral(valor):
    k=texto_norm(valor)
    if not k:
        return False
    return any(p in k for p in PATRONES_PUESTO)

def carrera_desde_fila(row):
    """Obtiene carrera académica/profesional, evitando usar puestos laborales."""
    candidatos = [
        "carrera", "career", "carrera_profesional", "profesion_academica",
        "formacion_academica", "especialidad", "degree"
    ]
    for nombre in candidatos:
        c = col(row.to_frame().T, [nombre])
        if c:
            v = texto(row.get(c, ""))
            if v and not parece_puesto_laboral(v):
                return carrera_canonica(v)

    # Solo usamos "profesion" si no parece ser un cargo laboral.
    c_prof = col(row.to_frame().T, ["profesion"])
    if c_prof:
        v = texto(row.get(c_prof, ""))
        if v and not parece_puesto_laboral(v):
            return carrera_canonica(v)

    # Último respaldo: buscar una carrera conocida dentro del detalle de formación.
    c_form = col(row.to_frame().T, ["formaciones_detalle"])
    if c_form:
        txt = texto(row.get(c_form, ""))
        kn = texto_norm(txt)
        for alias, estandar in CATALOGO_CARRERAS.items():
            if alias and alias in kn:
                return estandar
        for candidato in [
            "ingenieria de sistemas", "ingenieria de software", "ingenieria industrial",
            "administracion de empresas", "administracion", "marketing", "contabilidad",
            "economia", "finanzas", "psicologia", "derecho", "comunicacion",
            "ciencia de datos", "big data"
        ]:
            if candidato in kn:
                return carrera_canonica(candidato)
    return "Sin especificar"


# Crear la columna carrera en la validación en memoria usando postulantes_individual.
# Prioridad: user_id y luego correo normalizado.
if not df_validacion_postulantes.empty:
    VC=df_validacion_postulantes.copy()
    if "carrera" not in VC.columns:
        VC["carrera"]=pd.NA
    pc=col(df_postulantes_individual,["carrera","career","degree","profesion","formaciones_detalle"]) if not df_postulantes_individual.empty else None
    pu=col(df_postulantes_individual,["user_id","userid","user","_id_user","_id"]) if not df_postulantes_individual.empty else None
    pe=col(df_postulantes_individual,["email","correo","correo_electronico"]) if not df_postulantes_individual.empty else None
    vu=col(VC,["user_id","userid","user","user_object_id"])
    ve=col(VC,["correo_normalizado","correo_bcp","email","correo","email_x","email_y"])
    if pc and pu and vu:
        mapa=(df_postulantes_individual[[pu,pc]].dropna(subset=[pu,pc]).drop_duplicates(pu).set_index(pu)[pc].map(carrera_canonica).to_dict())
        idsval=VC[vu].astype(str).str.strip()
        mask=VC["carrera"].isna()|VC["carrera"].astype(str).str.strip().isin(["","nan","None"])
        VC.loc[mask,"carrera"]=idsval[mask].map(mapa)
    if pc and pe and ve:
        mapa=(df_postulantes_individual[[pe,pc]].dropna(subset=[pe,pc]).assign(__e=lambda d:d[pe].astype(str).str.strip().str.lower()).drop_duplicates("__e").set_index("__e")[pc].map(carrera_canonica).to_dict())
        emails=VC[ve].astype(str).str.strip().str.lower()
        mask=VC["carrera"].isna()|VC["carrera"].astype(str).str.strip().isin(["","nan","None"])
        VC.loc[mask,"carrera"]=emails[mask].map(mapa)
    df_validacion_postulantes=VC


def nombre_participante(row):
    if COL_NOMBRE:
        n = nombre_normalizado(row.get(COL_NOMBRE, ""))
    else:
        n = ""
    if COL_APELLIDO:
        a = nombre_normalizado(row.get(COL_APELLIDO, ""))
        if a and a.lower() not in n.lower():
            n = f"{n} {a}".strip()
    return n or "Participante BCP"


def ids_maestro(df=None):
    base = df if df is not None else df_participantes
    if base.empty or not COL_USER:
        return set()
    return set(base[COL_USER].dropna().astype(str).str.strip())


df_participantes = df_participantes.copy()

# Marcar únicamente los participantes que pertenecen al grupo BCP validado.
df_participantes["__bcp_validado"] = True
if not df_validacion_postulantes.empty:
    vu = col(df_validacion_postulantes, ["user_id", "userid", "user", "user_object_id"])
    ve = col(df_validacion_postulantes, ["correo_normalizado", "correo_bcp", "email", "correo", "email_x", "email_y"])
    ids_val = set()
    emails_val = set()
    if vu:
        ids_val = set(df_validacion_postulantes[vu].dropna().astype(str).str.strip())
    if ve:
        emails_val = set(df_validacion_postulantes[ve].dropna().astype(str).str.strip().str.lower())
    if COL_USER or COL_EMAIL:
        ok_id = df_participantes[COL_USER].astype(str).str.strip().isin(ids_val) if (COL_USER and ids_val) else pd.Series(False, index=df_participantes.index)
        ok_email = df_participantes[COL_EMAIL].astype(str).str.strip().str.lower().isin(emails_val) if (COL_EMAIL and emails_val) else pd.Series(False, index=df_participantes.index)
        if ids_val or emails_val:
            df_participantes["__bcp_validado"] = ok_id | ok_email

df_participantes["__nombre"] = df_participantes.apply(nombre_participante, axis=1)
df_participantes["__carrera"] = df_participantes.apply(carrera_desde_fila, axis=1)
TOTAL_PARTICIPANTES = len(df_participantes)


# ============================================================
# FILTROS
# ============================================================

def opciones_carreras():
    """Devuelve SOLO las carreras de los participantes BCP validados.

    No se recorren todos los registros de postulantes_individual porque allí
    pueden existir personas ajenas al programa y valores que son cargos laborales.
    """
    valores=set()
    if df_participantes.empty:
        return []

    # El maestro de indicadores_bcp es el universo BCP. La validación sirve
    # como comprobación adicional por user_id/correo.
    base = df_participantes.copy()
    if "__bcp_validado" in base.columns:
        base = base[base["__bcp_validado"]].copy()

    if "__carrera" in base.columns:
        for x in base["__carrera"].dropna().astype(str):
            if x.strip() and x != "Sin especificar" and not parece_puesto_laboral(x):
                valores.add(x.strip())
    return sorted(valores)


def ids_actividad_rango(rango):
    if df_actividad.empty:
        return set()
    c_fecha = col(df_actividad, ["fecha", "created_at", "createdAt", "date", "timestamp"])
    c_user = col(df_actividad, ["user_id", "userid", "user"])
    if not c_fecha or not c_user:
        return set()
    tmp = df_actividad.copy()
    tmp["__fecha"] = pd.to_datetime(tmp[c_fecha], errors="coerce")
    ini = pd.Timestamp(rango[0])
    fin = pd.Timestamp(rango[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    tmp = tmp[tmp["__fecha"].between(ini, fin, inclusive="both")]
    return set(tmp[c_user].dropna().astype(str).str.strip())


def _restablecer_filtros():
    st.session_state["f_periodo"] = "Desde el evento"
    st.session_state["f_carrera"] = "Todas"
    st.session_state["f_rango_personalizado"] = (
        FECHA_EVENTO.date(),
        fecha_maxima_actividad().date(),
    )

def render_filtros():
    hoy = max(fecha_maxima_actividad().date(), FECHA_EVENTO.date())

    # Deben existir antes de instanciar los widgets.
    st.session_state.setdefault("f_periodo", "Desde el evento")
    st.session_state.setdefault("f_carrera", "Todas")
    st.session_state.setdefault(
        "f_rango_personalizado",
        (FECHA_EVENTO.date(), hoy),
    )

    with st.container():
        st.markdown('<div class="filter-shell">', unsafe_allow_html=True)
        a, b, c = st.columns([1.05, 1.05, .55])

        with a:
            periodo = st.selectbox(
                "Rango de fechas",
                ["Desde el evento", "Últimos 7 días", "Últimos 30 días", "Personalizado"],
                key="f_periodo",
            )
            if periodo == "Últimos 7 días":
                inicio = max(FECHA_EVENTO.date(), hoy - pd.Timedelta(days=6))
                rango = (inicio, hoy)
            elif periodo == "Últimos 30 días":
                inicio = max(FECHA_EVENTO.date(), hoy - pd.Timedelta(days=29))
                rango = (inicio, hoy)
            elif periodo == "Personalizado":
                seleccionado = st.date_input(
                    "Selecciona el rango",
                    value=st.session_state["f_rango_personalizado"],
                    min_value=FECHA_EVENTO.date(),
                    max_value=hoy,
                    key="f_rango_personalizado",
                )
                rango = (
                    (seleccionado[0], seleccionado[1])
                    if isinstance(seleccionado, (tuple, list)) and len(seleccionado) == 2
                    else (FECHA_EVENTO.date(), hoy)
                )
            else:
                rango = (FECHA_EVENTO.date(), hoy)

        with b:
            carrera = st.selectbox(
                "Carrera",
                ["Todas"] + opciones_carreras(),
                key="f_carrera",
            )

        with c:
            st.write("")
            st.write("")
            st.button(
                "Limpiar filtros",
                use_container_width=True,
                on_click=_restablecer_filtros,
            )

        st.markdown("</div>", unsafe_allow_html=True)
    return rango, carrera


def contexto(rango, carrera):
    df = df_participantes.copy()
    if carrera != "Todas":
        df = df[df["__carrera"].eq(carrera)].copy()
    ids = ids_maestro(df)
    activos = ids.intersection(ids_actividad_rango(rango))
    rango_completo = rango[0] <= FECHA_EVENTO.date() and rango[1] >= fecha_maxima_actividad().date()
    # El rango actúa sobre el contexto de participantes. En el periodo completo
    # se conserva el grupo completo; en rangos acotados se consideran los activos.
    ids_contexto = ids if rango_completo else activos
    return df[df[COL_USER].astype(str).isin(ids_contexto)].copy() if COL_USER else df, ids_contexto


# ============================================================
# HABILIDADES
# ============================================================

def skill_canonica(valor):
    t = texto(valor)
    k = texto_norm(t)
    aliases = {
        "comunicacion": "Comunicación",
        "comunicacion efectiva": "Comunicación",
        "habilidades comunicativas": "Comunicación",
        "resolucion de problemas": "Resolución de problemas",
        "resolucion problemas": "Resolución de problemas",
        "solucion de problemas": "Resolución de problemas",
        "proactividad": "Proactividad",
        "proactivo": "Proactividad",
        "iniciativa": "Proactividad",
        "organizacion": "Organización",
        "organizacion y priorizacion": "Organización",
        "planificacion": "Organización",
        "planificacion y organizacion": "Organización",
        "trabajo en equipo": "Trabajo en equipo",
        "trabajo colaborativo": "Trabajo en equipo",
        "colaboracion": "Trabajo en equipo",
        "colaboracion efectiva": "Trabajo en equipo",
        "liderazgo": "Liderazgo",
        "leadership": "Liderazgo",
        "adaptabilidad": "Adaptabilidad",
        "adaptabilidad al cambio": "Adaptabilidad",
        "flexibilidad": "Adaptabilidad",
        "creatividad": "Creatividad",
        "creatividad y diseno": "Creatividad",
        "diseno": "Creatividad",
        "design thinking": "Design Thinking",
        "desing thinking": "Design Thinking",
        "atencion al detalle": "Atención al detalle",
        "pensamiento critico": "Pensamiento crítico",
        "powerbi": "Power BI",
        "power bi": "Power BI",
        "microsoft power bi": "Power BI",
        "excel": "Excel",
        "microsoft excel": "Excel",
        "ms excel": "Excel",
        "sql": "SQL",
        "python": "Python",
        "desarrollo en python": "Python",
        "javascript": "JavaScript",
        "desarrollo en javascript": "JavaScript",
        "typescript": "TypeScript",
        "java": "Java",
        "power automate": "Power Automate",
        "power apps": "Power Apps",
        "powerapps": "Power Apps",
        "git": "Git",
        "github": "GitHub",
        "html": "HTML",
        "css": "CSS",
        "r": "R",
        "communication": "Comunicación", "communication skills": "Comunicación",
        "effective communication": "Comunicación",
        "problem solving": "Resolución de problemas", "problem solving skills": "Resolución de problemas",
        "teamwork": "Trabajo en equipo", "team work": "Trabajo en equipo", "collaboration": "Trabajo en equipo",
        "leadership skills": "Liderazgo", "adaptability skills": "Adaptabilidad", "adaptability to change": "Adaptabilidad",
        "proactivity": "Proactividad", "initiative": "Proactividad",
        "organization skills": "Organización", "organizational skills": "Organización", "planning": "Organización",
        "time management": "Gestión del tiempo", "creative thinking": "Creatividad",
        "continuous learning": "Aprendizaje continuo", "lifelong learning": "Aprendizaje continuo",
        "attention to detail": "Atención al detalle", "detail oriented": "Atención al detalle",
        "critical thinking": "Pensamiento crítico", "analytical thinking": "Análisis", "analytical skills": "Análisis", "analysis": "Análisis",
        "customer service": "Atención al cliente", "customer orientation": "Atención al cliente",
        "quality of work": "Calidad del trabajo", "project management": "Gestión de proyectos",
    }
    if k in aliases:
        return aliases[k]

    # Agrupa variantes que expresan la misma habilidad aunque vengan
    # con palabras adicionales, puntuacion o pequenas diferencias de redaccion.
    if "comunicacion" in k or "habilidades comunicativas" in k:
        return "Comunicación"
    if "resolucion de problemas" in k or "solucion de problemas" in k:
        return "Resolución de problemas"
    if "trabajo en equipo" in k or "trabajo colaborativo" in k or "colaboracion" in k:
        return "Trabajo en equipo"
    if "liderazgo" in k or "leadership" in k:
        return "Liderazgo"
    if "adaptabilidad" in k or "flexibilidad al cambio" in k:
        return "Adaptabilidad"
    if "proactividad" in k or "proactivo" in k or "iniciativa" in k:
        return "Proactividad"
    if "organizacion" in k or "planificacion" in k or "organization" in k or "planning" in k: return "Organización"
    if "aprendizaje continuo" in k or "continuous learning" in k or "lifelong learning" in k: return "Aprendizaje continuo"
    if "atencion al detalle" in k or "attention to detail" in k or "detail oriented" in k: return "Atención al detalle"
    if "pensamiento critico" in k or "critical thinking" in k: return "Pensamiento crítico"
    if "pensamiento analitico" in k or "analytical thinking" in k or "analisis" in k: return "Análisis"
    if "gestion del tiempo" in k or "time management" in k: return "Gestión del tiempo"
    if "atencion al cliente" in k or "customer service" in k: return "Atención al cliente"
    if "calidad del trabajo" in k or "quality of work" in k: return "Calidad del trabajo"
    if "gestion de proyectos" in k or "project management" in k: return "Gestión de proyectos"

    return t[:1].upper() + t[1:] if t else ""


def tipo_skill(valor):
    k = texto_norm(valor)
    if k in {"hard", "hard skill", "hard skills", "technical", "tecnica", "tecnico", "tecnicas"}:
        return "Hard skills"
    if k in {"soft", "soft skill", "soft skills", "blanda", "blandas"}:
        return "Soft skills"
    return "Sin clasificar"


def skills_preparadas(ids=None):
    if df_skills_raw.empty:
        return pd.DataFrame(columns=["habilidad", "tipo", "__user"])
    out = df_skills_raw.copy()
    c_name = col(out, ["name", "habilidad", "skill"])
    c_type = col(out, ["type", "tipo", "skill_type"])
    c_user = col(out, ["user_id", "userid", "user"])
    if not c_name:
        return pd.DataFrame(columns=["habilidad", "tipo", "__user"])
    if ids is not None and c_user:
        out = out[out[c_user].astype(str).str.strip().isin(ids)].copy()
    out["habilidad"] = out[c_name].map(skill_canonica)
    out["tipo"] = out[c_type].map(tipo_skill) if c_type else "Sin clasificar"
    out["__user"] = out[c_user].astype(str).str.strip() if c_user else ""
    return out[out["habilidad"].ne("")].copy()


def tabla_skills(ids=None, tipo=None):
    out = skills_preparadas(ids)
    if tipo:
        out = out[out["tipo"].eq(tipo)]
    if out.empty:
        return pd.DataFrame(columns=["Habilidad", "Participantes"])
    res = out.groupby("habilidad")["__user"].nunique().reset_index(name="Participantes")
    return res.rename(columns={"habilidad": "Habilidad"}).sort_values(
        ["Participantes", "Habilidad"], ascending=[False, True]
    ).reset_index(drop=True)


def grafico_skills(ids=None, tipo="Hard skills", limite=10, altura=360):
    df = tabla_skills(ids, tipo).head(limite).sort_values("Participantes")
    if df.empty:
        return grafico_vacio("No hay habilidades disponibles.", altura)
    fig = px.bar(df, x="Participantes", y="Habilidad", orientation="h", text="Participantes")
    fig.update_traces(marker_color=VERDE if tipo == "Hard skills" else MORADO,
                      textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis_title="Participantes", yaxis_title="", showlegend=False)
    fig.update_xaxes(dtick=1, showgrid=True, gridcolor="#EEF3F8", rangemode="tozero")
    return figura_base(fig, altura)


# ============================================================
# IKIGAI
# ============================================================

DIMENSIONES = [
    "Fortalezas",
    "Aspectos por desarrollar",
    "Motivaciones",
    "Dirección profesional",
    "Problemas de interés",
    "Áreas de trabajo sugeridas",
]


def concepto_ikigai(valor, dimension):
    t = texto(valor)
    k = texto_norm(t)
    if not k:
        return ""

    reglas = [
        (["resolucion de problemas", "resolver problemas", "solucion de problemas"], "Resolución de problemas"),
        (["analisis de datos", "analizar datos", "analitico", "analisis"], "Análisis"),
        (["atencion al detalle", "detalle"], "Atención al detalle"),
        (["comunicacion", "comunicar"], "Comunicación"),
        (["organizacion", "priorizacion", "planificacion"], "Organización"),
        (["aprendizaje", "aprender", "seguir aprendiendo"], "Aprendizaje continuo"),
        (["liderazgo", "liderar"], "Liderazgo"),
        (["adaptabilidad", "flexibilidad", "cambio"], "Adaptabilidad"),
        (["creatividad", "diseno"], "Creatividad"),
        (["pensamiento critico"], "Pensamiento crítico"),
        (["confianza", "seguridad en mi"], "Confianza profesional"),
        (["gestion de proyectos", "proyectos tecnologicos"], "Gestión de proyectos"),
        (["tecnologia", "tecnologico", "tecnologia"], "Tecnología"),
        (["automatizacion", "automatizar"], "Automatización"),
        (["emprendimiento", "emprender"], "Emprendimiento"),
        (["impacto social", "ayudar a las personas", "impactar"], "Impacto social"),
        (["marketing", "mercadotecnia"], "Marketing"),
        (["finanzas", "financiero"], "Finanzas"),
        (["contabilidad", "contable"], "Contabilidad"),
        (["recursos humanos", "talento humano"], "Recursos Humanos"),
        (["educacion", "educativo"], "Educación"),
        (["salud", "sanitario"], "Salud"),
        (["medio ambiente", "ambiental", "climatico"], "Medio ambiente"),
    ]
    for claves, etiqueta in reglas:
        if any(c in k for c in claves):
            return etiqueta
    # Para textos que no encajan en una categoría se mantiene una versión corta.
    limpio = re.sub(r"[.;:!?]+.*$", "", t).strip()
    palabras = limpio.split()
    if len(palabras) > 7:
        limpio = " ".join(palabras[:7]) + "…"
    return limpio[:1].upper() + limpio[1:] if limpio else ""


def ikigai_dimension(dimension, ids=None, limite=10):
    if df_ikigai_frecuencias.empty:
        return pd.DataFrame(columns=["Concepto", "Participantes"])
    c_dim = col(df_ikigai_frecuencias, ["dimension"])
    c_val = col(df_ikigai_frecuencias, ["valor", "respuesta", "concepto"])
    c_count = col(df_ikigai_frecuencias, ["participantes", "frecuencia", "count"])
    c_user = col(df_ikigai_frecuencias, ["user_id", "userid", "user"])
    if not c_dim or not c_val:
        return pd.DataFrame(columns=["Concepto", "Participantes"])
    out = df_ikigai_frecuencias.copy()
    out = out[out[c_dim].map(texto_norm).eq(texto_norm(dimension))].copy()
    if ids and c_user:
        out = out[out[c_user].astype(str).str.strip().isin(ids)].copy()
    out["Concepto"] = out[c_val].map(lambda x: concepto_ikigai(x, dimension))
    out = out[out["Concepto"].ne("")]
    if c_user:
        out["__user"] = out[c_user].astype(str).str.strip()
        res = out.groupby("Concepto")["__user"].nunique().reset_index(name="Participantes")
    elif c_count:
        out["__count"] = pd.to_numeric(out[c_count], errors="coerce").fillna(0)
        res = out.groupby("Concepto")["__count"].sum().reset_index(name="Participantes")
    else:
        res = out.groupby("Concepto").size().reset_index(name="Participantes")
    return res.sort_values(["Participantes", "Concepto"], ascending=[False, True]).head(limite)


def grafico_ikigai(dimension, ids=None, limite=10, altura=390):
    df = ikigai_dimension(dimension, ids, limite).sort_values("Participantes")
    if df.empty:
        return grafico_vacio("No hay información disponible para esta dimensión.", altura)
    fig = px.bar(df, x="Participantes", y="Concepto", orientation="h", text="Participantes")
    fig.update_traces(marker_color=MORADO, textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis_title="Participantes", yaxis_title="", showlegend=False)
    fig.update_xaxes(dtick=1, showgrid=True, gridcolor="#EEF3F8", rangemode="tozero")
    return figura_base(fig, altura)


# ============================================================
# ACTIVIDAD Y PERFIL
# ============================================================

def ids_carrera(carrera):
    if carrera == "Todas":
        return ids_maestro()
    return set(df_participantes.loc[df_participantes["__carrera"].eq(carrera), COL_USER].astype(str))


def _evidencia_positiva(serie):
    def ok(v):
        if isinstance(v, (bool, np.bool_)):
            return bool(v)
        if v is None:
            return False
        try:
            if pd.isna(v):
                return False
        except Exception:
            pass
        if isinstance(v, (int, float, np.integer, np.floating)):
            return float(v) > 0
        k = texto_norm(v)
        if k in {"true", "1", "si", "yes", "completo", "completado", "activo", "presente"}:
            return True
        if k in {"false", "0", "no", "none", "null", "nan", "pendiente", ""}:
            return False
        return True
    return serie.map(ok)

def _usuarios_con_campo(df, ids, candidatos):
    if df is None or df.empty or not ids:
        return set()
    cu = col(df, ["user_id", "userid", "user", "_id_user", "_id"])
    if not cu:
        return set()
    d = df[df[cu].astype(str).str.strip().isin(ids)].copy()
    if d.empty:
        return set()
    presentes = set()
    for candidato in candidatos:
        cc = col(d, [candidato])
        if cc:
            presentes |= set(d.loc[_evidencia_positiva(d[cc]), cu].astype(str).str.strip())
    return presentes

def _usuarios_en_detalle(df, ids):
    if df is None or df.empty or not ids:
        return set()
    cu = col(df, ["user_id", "userid", "user", "_id_user", "_id_postulante", "postulante_id", "_id", "cv"])
    if not cu:
        return set()
    return set(df[cu].dropna().astype(str).str.strip()).intersection(ids)

def _ids_desde_maestro(ids, candidatos):
    """Obtiene participantes con evidencia directamente desde postulantes_individual/maestro."""
    if df_participantes.empty or not COL_USER or not ids:
        return set()
    d = df_participantes[df_participantes[COL_USER].astype(str).str.strip().isin(ids)].copy()
    encontrados = set()
    for c in candidatos:
        cc = col(d, [c])
        if cc:
            encontrados |= set(d.loc[_evidencia_positiva(d[cc]), COL_USER].astype(str).str.strip())
    return encontrados

def _valor_resumen_indicador(nombre):
    """Lee un indicador agregado de indicadores_bcp.xlsx.
    Se usa como fuente de respaldo cuando se analiza todo el BCP sin filtros,
    porque ese archivo ya contiene los conteos validados por el cruce de participantes.
    """
    if df_resumen.empty:
        return None
    c = col(df_resumen, [nombre])
    if not c:
        # Variantes frecuentes del mismo indicador.
        variantes = {
            "participantes_en_cursos": ["participantes_cursos", "cursos"],
            "participantes_evaluaciones": ["evaluaciones", "participantes_con_evaluaciones"],
            "participantes_chatbot": ["chatbot", "participantes_con_chatbot"],
            "participantes_alertas": ["alertas", "participantes_con_alertas"],
            "participantes_compatibilidad": ["compatibilidad", "participantes_con_compatibilidad"],
            "participantes_eventos": ["eventos", "participantes_con_eventos"],
            "ikigai_iniciado": ["participantes_ikigai", "ikigai_iniciados"],
            "ikigai_completado": ["ikigai_completados"],
            "ikigai_con_resultado": ["ikigai_resultado", "ikigai_con_resultados"],
            "participantes_con_cv": ["con_cv", "cv"],
            "participantes_con_educacion": ["con_educacion", "educacion"],
            "participantes_con_experiencia": ["con_experiencia", "experiencia"],
            "participantes_con_habilidades": ["con_habilidades", "habilidades"],
        }
        c = col(df_resumen, variantes.get(nombre, []))
    if not c:
        return None
    vals = pd.to_numeric(df_resumen[c], errors="coerce").dropna()
    return int(vals.iloc[0]) if not vals.empty else None


def metricas_contexto(df_contexto, ids_contexto, rango):
    total = len(df_contexto)
    activos = len(ids_contexto.intersection(ids_actividad_rango(rango)))

    # Conteos individuales: primero se intenta obtener evidencia por participante.
    cv_ids = _usuarios_con_campo(
        df_contexto, ids_contexto,
        ["tiene_cv", "_id_cv", "cv_nombre", "cv_name", "cv"]
    )
    cv_ids |= _ids_desde_maestro(ids_contexto, ["tiene_cv", "_id_cv", "cv_nombre", "cv_name", "cv_tipo", "cv_paginas"])

    edu_ids = _usuarios_en_detalle(df_educacion, ids_contexto)
    edu_ids |= _usuarios_con_campo(df_contexto, ids_contexto,
        ["tiene_educacion", "nivel_educativo", "instituciones", "formaciones_detalle", "cantidad_formaciones"])
    edu_ids |= _ids_desde_maestro(ids_contexto,
        ["nivel_educativo", "instituciones", "formaciones_detalle", "cantidad_formaciones"])

    exp_ids = _usuarios_en_detalle(df_experiencia, ids_contexto)
    exp_ids |= _usuarios_con_campo(df_contexto, ids_contexto,
        ["tiene_experiencia", "experiencia_detalle", "cantidad_experiencias", "meses_experiencia", "años_experiencia"])
    exp_ids |= _ids_desde_maestro(ids_contexto,
        ["tiene_experiencia", "experiencia_detalle", "cantidad_experiencias", "meses_experiencia", "años_experiencia", "experiencia_formato"])

    skills = skills_preparadas(ids_contexto)
    skill_users = int(skills["__user"].nunique()) if not skills.empty else 0

    ikigai_iniciado_ids = (
        _usuarios_en_detalle(df_ikigai_perfil, ids_contexto)
        | _usuarios_en_detalle(df_ikigai_frecuencias, ids_contexto)
        | _usuarios_con_campo(df_contexto, ids_contexto,
            ["ikigai_iniciado", "tiene_ikigai", "autoconocimiento_iniciado"])
    )
    ikigai_completado_ids = _usuarios_con_campo(df_contexto, ids_contexto,
        ["ikigai_completado", "autoconocimiento_completado"])
    ikigai_resultado_ids = _usuarios_con_campo(df_contexto, ids_contexto,
        ["ikigai_con_resultado", "ikigai_resultado", "resultado_ikigai"])

    # Funcionalidades: usar primero evidencia individual; si estamos viendo TODO el
    # conjunto BCP, usar los indicadores validados de indicadores_bcp.xlsx.
    eval_ids = _usuarios_con_campo(df_contexto, ids_contexto,
        ["participantes_evaluaciones", "tiene_evaluaciones", "evaluaciones", "cantidad_evaluaciones",
         "cantidad_quizzes", "cantidad_respuestas_quiz", "cantidad_resultados_quiz", "completo_quiz"])
    eval_ids |= _ids_desde_maestro(ids_contexto,
        ["participantes_evaluaciones", "tiene_evaluaciones", "evaluaciones", "cantidad_evaluaciones",
         "cantidad_quizzes", "cantidad_respuestas_quiz", "cantidad_resultados_quiz", "completo_quiz"])
    eval_ids |= _usuarios_en_detalle(df_evaluaciones, ids_contexto)

    curso_ids = _usuarios_con_campo(df_contexto, ids_contexto,
        ["participantes_cursos", "tiene_cursos", "cursos", "cantidad_cursos", "total_registros_curso"])
    curso_ids |= _ids_desde_maestro(ids_contexto,
        ["participantes_cursos", "tiene_cursos", "cursos", "cantidad_cursos", "total_registros_curso"])

    chatbot_ids = _usuarios_con_campo(df_contexto, ids_contexto,
        ["participantes_chatbot", "tiene_chatbot", "chatbot", "cantidad_conversaciones", "cantidad_mensajes_ia", "uso_ia"])
    chatbot_ids |= _ids_desde_maestro(ids_contexto,
        ["participantes_chatbot", "tiene_chatbot", "chatbot", "cantidad_conversaciones", "cantidad_mensajes_ia", "uso_ia"])

    alertas_ids = _usuarios_con_campo(df_contexto, ids_contexto,
        ["participantes_alertas", "tiene_alertas", "alertas", "cantidad_alertas"])
    alertas_ids |= _ids_desde_maestro(ids_contexto,
        ["participantes_alertas", "tiene_alertas", "alertas", "cantidad_alertas"])
    alertas_ids |= _usuarios_en_detalle(df_notificaciones, ids_contexto) if "df_notificaciones" in globals() else set()

    compat_ids = _usuarios_con_campo(df_contexto, ids_contexto,
        ["participantes_compatibilidad", "tiene_compatibilidad", "compatibilidad",
         "cantidad_analisis_compatibilidad", "score_compatibilidad_promedio", "ultimo_score_compatibilidad"])
    compat_ids |= _ids_desde_maestro(ids_contexto,
        ["participantes_compatibilidad", "tiene_compatibilidad", "compatibilidad",
         "cantidad_analisis_compatibilidad", "score_compatibilidad_promedio", "ultimo_score_compatibilidad"])

    eventos_ids = _usuarios_con_campo(df_contexto, ids_contexto,
        ["participantes_eventos", "tiene_eventos", "eventos", "cantidad_eventos", "participo_evento"])
    eventos_ids |= _ids_desde_maestro(ids_contexto,
        ["participantes_eventos", "tiene_eventos", "eventos", "cantidad_eventos", "participo_evento"])

    # Los indicadores mostrados por el usuario son los valores validados para el
    # conjunto completo: 2 cursos, 14 evaluaciones, 1 chatbot, 1 alerta,
    # 1 compatibilidad y 17 eventos. No se inventan valores: solo se usan como
    # respaldo cuando no hay filtros que cambien el universo.
    sin_filtros = (total == _valor_resumen_indicador("participantes_bcp")) if _valor_resumen_indicador("participantes_bcp") is not None else False
    if sin_filtros:
        v = _valor_resumen_indicador("participantes_en_cursos")
        if v is not None: cursos_n = v
        else: cursos_n = len(curso_ids)
        v = _valor_resumen_indicador("participantes_evaluaciones")
        if v is not None: evaluaciones_n = v
        else: evaluaciones_n = len(eval_ids)
        v = _valor_resumen_indicador("participantes_chatbot")
        if v is not None: chatbot_n = v
        else: chatbot_n = len(chatbot_ids)
        v = _valor_resumen_indicador("participantes_alertas")
        if v is not None: alertas_n = v
        else: alertas_n = len(alertas_ids)
        v = _valor_resumen_indicador("participantes_compatibilidad")
        if v is not None: compat_n = v
        else: compat_n = len(compat_ids)
        v = _valor_resumen_indicador("participantes_eventos")
        if v is not None: eventos_n = v
        else: eventos_n = len(eventos_ids)
        v = _valor_resumen_indicador("ikigai_iniciado")
        if v is not None: ikigai_iniciado_n = v
        else: ikigai_iniciado_n = len(ikigai_iniciado_ids)
        v = _valor_resumen_indicador("ikigai_completado")
        ikigai_completado_n = v if v is not None else len(ikigai_completado_ids)
        v = _valor_resumen_indicador("ikigai_con_resultado")
        ikigai_resultado_n = v if v is not None else len(ikigai_resultado_ids)
    else:
        cursos_n, evaluaciones_n, chatbot_n = len(curso_ids), len(eval_ids), len(chatbot_ids)
        alertas_n, compat_n, eventos_n = len(alertas_ids), len(compat_ids), len(eventos_ids)
        ikigai_iniciado_n, ikigai_completado_n, ikigai_resultado_n = len(ikigai_iniciado_ids), len(ikigai_completado_ids), len(ikigai_resultado_ids)

    return {
        "total": total, "activos": activos,
        "cv": len(cv_ids), "educacion": len(edu_ids), "experiencia": len(exp_ids), "habilidades": skill_users,
        "ikigai_iniciado": ikigai_iniciado_n, "ikigai_completado": ikigai_completado_n, "ikigai_resultado": ikigai_resultado_n,
        "evaluaciones": evaluaciones_n, "cursos": cursos_n, "chatbot": chatbot_n, "alertas": alertas_n,
        "compatibilidad": compat_n, "eventos": eventos_n,
    }


def evolucion_df(rango, ids):
    if df_actividad.empty:
        return pd.DataFrame()
    cf = col(df_actividad, ["fecha", "created_at", "createdAt", "date", "timestamp"])
    cu = col(df_actividad, ["user_id", "userid", "user"])
    if not cf:
        return pd.DataFrame()
    d = df_actividad.copy()
    d["__fecha"] = pd.to_datetime(d[cf], errors="coerce")
    ini = pd.Timestamp(rango[0]); fin = pd.Timestamp(rango[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    d = d[d["__fecha"].between(ini, fin, inclusive="both")]
    if cu and ids:
        d = d[d[cu].astype(str).str.strip().isin(ids)]
    if d.empty:
        return pd.DataFrame()
    d["Semana"] = d["__fecha"].dt.to_period("W-MON").apply(lambda x: x.start_time)
    if cu:
        return d.groupby("Semana")[cu].nunique().reset_index(name="Participantes").sort_values("Semana")
    return d.groupby("Semana").size().reset_index(name="Participantes").sort_values("Semana")


def grafico_evolucion(rango, ids):
    d = evolucion_df(rango, ids)
    if d.empty:
        return grafico_vacio("No hay registros de actividad en el rango seleccionado.", 320)
    fig = px.line(d, x="Semana", y="Participantes", markers=True, text="Participantes")
    fig.update_traces(line=dict(color=XD, width=3), marker=dict(size=8), textposition="top center")
    fig.update_layout(xaxis_title="", yaxis_title="Participantes únicos", showlegend=False)
    fig.update_yaxes(dtick=1, rangemode="tozero", showgrid=True, gridcolor="#EEF3F8")
    fig.update_xaxes(showgrid=False)
    return figura_base(fig, 320)


# ============================================================
# COMPATIBILIDAD
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def compatibilidad_mongo(ids_tuple):
    if get_db is None:
        return pd.DataFrame()
    ids = list(ids_tuple)
    if not ids:
        return pd.DataFrame()
    try:
        db = get_db()
        consulta = []
        consulta.extend(ids)
        if ObjectId:
            for x in ids:
                try:
                    consulta.append(ObjectId(x))
                except Exception:
                    pass
        docs = list(db.jobcompatibilityanalyses.find({"userId": {"$in": consulta}}))
        if not docs:
            return pd.DataFrame()
        rows = []
        for d in docs:
            rows.append({
                "user_id": str(d.get("userId", "")),
                "job_id": str(d.get("jobId", "")),
                "porcentaje": pd.to_numeric(d.get("compatibilityPercentage"), errors="coerce"),
                "nivel": texto(d.get("compatibilityLevel")),
                "estado": texto(d.get("status")),
                "fecha": d.get("createdAt"),
            })
        out = pd.DataFrame(rows)
        out["fecha"] = pd.to_datetime(out["fecha"], errors="coerce")
        return out
    except Exception:
        return pd.DataFrame()


def compatibilidad_df(ids, rango=None):
    out = compatibilidad_mongo(tuple(sorted(ids)))
    if out.empty and not df_compat_excel.empty:
        out = df_compat_excel.copy()
        cu = col(out, ["user_id", "userid", "user"])
        cp = col(out, ["compatibility_percentage", "compatibilitypercentage", "porcentaje", "compatibilidad_porcentaje"])
        cf = col(out, ["fecha", "created_at", "createdAt"])
        if cu:
            out = out[out[cu].astype(str).str.strip().isin(ids)].copy()
        if cp:
            out["porcentaje"] = pd.to_numeric(out[cp], errors="coerce")
        if cf:
            out["fecha"] = pd.to_datetime(out[cf], errors="coerce")
        else:
            out["fecha"] = pd.NaT
    if out.empty:
        return out
    if rango is not None and "fecha" in out.columns and out["fecha"].notna().any():
        ini = pd.Timestamp(rango[0]); fin = pd.Timestamp(rango[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        out = out[(out["fecha"].isna()) | out["fecha"].between(ini, fin, inclusive="both")]
    return out


def metricas_compatibilidad(ids, rango=None):
    d = compatibilidad_df(ids, rango)
    if d.empty:
        return 0, 0, np.nan
    d = d.drop_duplicates(subset=[c for c in ["user_id", "job_id", "fecha", "porcentaje"] if c in d.columns])
    valid = pd.to_numeric(d.get("porcentaje", pd.Series(dtype=float)), errors="coerce")
    valid = valid[(valid >= 0) & (valid <= 100)]
    participantes = d["user_id"].nunique() if "user_id" in d.columns else 0
    return int(participantes), len(d), float(valid.mean()) if not valid.empty else np.nan


def grafico_compatibilidad(ids, rango):
    d = compatibilidad_df(ids, rango)
    if d.empty or "porcentaje" not in d.columns:
        return grafico_vacio("No hay porcentajes de compatibilidad disponibles.", 300)
    d = d.copy()
    d["porcentaje"] = pd.to_numeric(d["porcentaje"], errors="coerce")
    d = d[d["porcentaje"].between(0, 100)]
    if d.empty:
        return grafico_vacio("No hay porcentajes de compatibilidad válidos.", 300)
    bins = [0, 20, 40, 60, 80, 100.0001]
    labels = ["0–20%", "21–40%", "41–60%", "61–80%", "81–100%"]
    d["Rango"] = pd.cut(d["porcentaje"], bins=bins, labels=labels, include_lowest=True, right=True)
    dist = d["Rango"].value_counts(sort=False).reset_index()
    dist.columns = ["Rango", "Análisis"]
    fig = px.bar(dist, x="Rango", y="Análisis", text="Análisis")
    fig.update_traces(marker_color=MORADO, textposition="outside")
    fig.update_layout(xaxis_title="Porcentaje de compatibilidad", yaxis_title="Análisis", showlegend=False)
    fig.update_yaxes(dtick=1, rangemode="tozero", showgrid=True, gridcolor="#EEF3F8")
    return figura_base(fig, 300)


# ============================================================
# DEMANDA Y MERCADO
# ============================================================

def titulo_puesto(valor):
    t = texto(valor)
    if not t:
        return "Sin especificar"

    k = texto_norm(t)
    reglas = [
        (["frontend developer", "frontend engineer", "desarrollador frontend", "frontend"],
         "Desarrollador Frontend"),
        (["backend developer", "desarrollador backend", "backend"],
         "Desarrollador Backend"),
        (["full stack", "fullstack", "full stack developer", "fullstack developer"],
         "Desarrollador Full Stack"),
        (["software developer", "software engineer", "desarrollador de software"],
         "Desarrollador de Software"),
        (["data analyst", "analista de datos", "business intelligence"],
         "Analista de Datos"),
        (["data scientist", "cientifico de datos", "científico de datos"],
         "Científico de Datos"),
        (["ux ui", "ui ux", "product designer", "disenador ui", "diseñador ui"],
         "Diseñador UX/UI"),
        (["graphic designer", "disenador grafico", "diseñador grafico"],
         "Diseñador Gráfico"),
        (["marketing specialist", "especialista en marketing"],
         "Especialista de Marketing"),
        (["asesor comercial", "ejecutivo comercial", "ventas", "vendedor"],
         "Asesor Comercial"),
        (["atencion al cliente", "servicio al cliente", "customer service"],
         "Atención al Cliente"),
        (["recursos humanos", "talento humano"],
         "Recursos Humanos"),
        (["contador", "contable", "contabilidad"],
         "Contador"),
    ]
    for claves, etiqueta in reglas:
        if any(x in k for x in claves):
            return etiqueta

    t = re.sub(r"\b(practicante|prácticas|practicas|intern|internship)\b", "", t, flags=re.I)
    t = re.sub(r"\s*[-–—|/]\s*", " ", t)
    t = re.sub(r"\s+", " ", t).strip(" -–—|/")
    return t[:1].upper() + t[1:] if t else "Sin especificar"


def carrera_desde_puesto(puesto, departamento=""):
    k = texto_norm(f"{puesto} {departamento}")
    reglas = [
        (["marketing", "trade marketing"], "Marketing"),
        (["contabilidad", "contador", "contable"], "Contabilidad"),
        (["finanzas", "financiero"], "Finanzas"),
        (["economia", "economista"], "Economía"),
        (["recursos humanos", "talento humano"], "Recursos Humanos"),
        (["sistemas", "software", "data", "datos", "tecnologia", "automatizacion", "ciberseguridad", "devops"], "Ingeniería de Sistemas"),
        (["industrial", "operaciones", "logistica", "procesos"], "Ingeniería Industrial"),
        (["administrativ", "administracion"], "Administración"),
        (["derecho", "legal", "abogado"], "Derecho"),
        (["psicologia", "psicologo"], "Psicología"),
        (["comunicacion", "comunicaciones"], "Comunicaciones"),
    ]
    for claves, carrera in reglas:
        if any(x in k for x in claves):
            return carrera
    return "Sin especificar"


def jobs_abiertos(carrera="Todas", rango=None):
    if df_jobs.empty: return pd.DataFrame()
    out=df_jobs.copy()
    cs=col(out,["status"])
    if cs: out=out[out[cs].astype(str).str.upper().eq("OPEN")].copy()
    cc=col(out,["carrera","career","degree","area_carrera","profesion"])
    ct=col(out,["title"]); cd=col(out,["department"])
    if cc: out["__carrera_job"]=out[cc].map(carrera_canonica)
    else: out["__carrera_job"]=[carrera_desde_puesto(t,d) for t,d in zip(out[ct] if ct else [""]*len(out),out[cd] if cd else [""]*len(out))]
    if carrera!="Todas": out=out[out["__carrera_job"].eq(carrera)].copy()
    if rango is not None:
        cf=col(out,["fecha_publicacion","published_at","publishedAt","created_at","createdAt","fecha"])
        if cf:
            f=pd.to_datetime(out[cf],errors="coerce")
            ini=pd.Timestamp(rango[0]); fin=pd.Timestamp(rango[1])+pd.Timedelta(days=1)-pd.Timedelta(seconds=1)
            out=out[f.isna()|f.between(ini,fin,inclusive="both")].copy()
    return out


def demanda_tabla():
    if df_skills_demanda.empty:
        return pd.DataFrame(columns=["Habilidad", "Tipo", "Participantes", "Apariciones"])
    out = df_skills_demanda.copy()
    ch = col(out, ["habilidad", "skill", "name"])
    ct = col(out, ["tipo", "type", "skill_type"])
    cp = col(out, ["participantes", "frecuencia", "count"])
    cd = col(out, ["apariciones_en_requisitos", "apariciones", "demand_count", "frecuencia_demanda", "ofertas"])
    if not ch:
        return pd.DataFrame(columns=["Habilidad", "Tipo", "Participantes", "Apariciones"])
    out["Habilidad"] = out[ch].map(skill_canonica)
    out["Tipo"] = out[ct].map(tipo_skill) if ct else "Sin clasificar"
    out["Participantes"] = pd.to_numeric(out[cp], errors="coerce").fillna(0).astype(int) if cp else 0
    out["Apariciones"] = pd.to_numeric(out[cd], errors="coerce").fillna(0).astype(int) if cd else 0
    out = out[out["Habilidad"].ne("")]
    out = out.groupby(["Habilidad", "Tipo"], as_index=False)[["Participantes", "Apariciones"]].sum()
    return out.sort_values(["Apariciones", "Participantes", "Habilidad"], ascending=[False, False, True]).reset_index(drop=True)


def grafico_demanda(tipo, limite=10):
    d = demanda_tabla()
    d = d[d["Tipo"].eq(tipo)].head(limite).sort_values("Apariciones")
    if d.empty:
        return grafico_vacio("No hay información de demanda disponible.", 300)
    fig = px.bar(d, x="Apariciones", y="Habilidad", orientation="h", text="Apariciones")
    fig.update_traces(marker_color=AZUL, textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis_title="Apariciones en requisitos", yaxis_title="", showlegend=False)
    fig.update_xaxes(dtick=1, rangemode="tozero", showgrid=True, gridcolor="#EEF3F8")
    return figura_base(fig, 300)


def tabla_puestos_por_carrera(df_open):
    if df_open.empty:
        return pd.DataFrame(columns=["Carrera", "Puesto", "Ofertas"])
    ct = col(df_open, ["title"])
    cc = col(df_open, ["carrera", "career", "degree", "area_carrera", "profesion"])
    cd = col(df_open, ["department"])
    if not ct:
        return pd.DataFrame(columns=["Carrera", "Puesto", "Ofertas"])
    rows = []
    for _, r in df_open.iterrows():
        carrera = carrera_canonica(r.get(cc)) if cc else "Sin especificar"
        if carrera == "Sin especificar":
            carrera = carrera_desde_puesto(r.get(ct, ""), r.get(cd, ""))
        if carrera == "Sin especificar":
            continue
        rows.append((carrera, titulo_puesto(r.get(ct, ""))))
    if not rows:
        return pd.DataFrame(columns=["Carrera", "Puesto", "Ofertas"])
    return pd.DataFrame(rows, columns=["Carrera", "Puesto"]).groupby(["Carrera", "Puesto"], as_index=False).size().rename(columns={"size":"Ofertas"}).sort_values(["Carrera", "Ofertas", "Puesto"], ascending=[True, False, True])


# ============================================================
# FUNCIONALIDADES
# ============================================================


def grafico_funcionalidades(ids, rango, total):
    m = metricas_contexto(df_participantes[df_participantes[COL_USER].astype(str).isin(ids)] if COL_USER else df_participantes, ids, rango)
    cp, _, _ = metricas_compatibilidad(ids, rango)
    cp = m.get("compatibilidad", cp)
    d = pd.DataFrame([
        ("Autoconocimiento", m["ikigai_iniciado"]),
        ("Evaluaciones", m["evaluaciones"]),
        ("Cursos", m["cursos"]),
        ("Compatibilidad", cp),
        ("Chatbot", m["chatbot"]),
        ("Alertas", m["alertas"]),
        ("Eventos", m["eventos"]),
    ], columns=["Funcionalidad", "Participantes"])
    d["Porcentaje"] = d["Participantes"].map(lambda x: porcentaje(x, total))
    d = d.sort_values("Participantes")
    fig = px.bar(d, x="Participantes", y="Funcionalidad", orientation="h", text="Participantes", custom_data=["Porcentaje"])
    fig.update_traces(marker_color=AZUL, textposition="outside", cliponaxis=False,
                      hovertemplate="<b>%{y}</b><br>Participantes: %{x}<br>Porcentaje: %{customdata[0]:.1f}%<extra></extra>")
    fig.update_layout(xaxis_title="Participantes", yaxis_title="", showlegend=False)
    fig.update_xaxes(dtick=1, rangemode="tozero", showgrid=True, gridcolor="#EEF3F8")
    return figura_base(fig, 350)


# ============================================================
# DATOS DE RESUMEN ESTÁTICO PARA RESPALDO
# ============================================================

def resumen_val(candidatos, default=0):
    if df_resumen.empty:
        return default
    r = df_resumen.iloc[0]
    for c in candidatos:
        cc = norm_col(c)
        if cc in df_resumen.columns:
            return r[cc]
    return default


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        '<div class="brand">Laboral.AI <span>| BCP</span><small>Talento y oportunidades</small></div>',
        unsafe_allow_html=True,
    )
    pagina = st.radio(
        "Navegación",
        [
            "Resumen",
            "Perfil del grupo",
            "Evolución",
            "Autoconocimiento",
            "Habilidades",
            "Mercado laboral",
            "Uso de funcionalidades",
            "Detalle del participante",
        ],
        label_visibility="collapsed",
    )


# ============================================================
# RESUMEN
# ============================================================

if pagina == "Resumen":
    titulo_pagina(
        "Impacto del programa BCP en Laboral.AI",
        "Resumen de participación, desarrollo profesional, habilidades y oportunidades.",
    )
    rango, carrera = render_filtros()
    df_ctx, ids = contexto(rango, carrera)
    m = metricas_contexto(df_ctx, ids, rango)
    cp, n_analisis, promedio_comp = metricas_compatibilidad(ids, rango)
    habilidades = skills_preparadas(ids)
    total_skills = len(habilidades)
    hard = int(habilidades["tipo"].eq("Hard skills").sum()) if not habilidades.empty else 0
    soft = int(habilidades["tipo"].eq("Soft skills").sum()) if not habilidades.empty else 0
    unicas = int(habilidades["habilidad"].nunique()) if not habilidades.empty else 0
    pct_comp = porcentaje(cp, m["total"])
    pct_open = 0
    df_open = jobs_abiertos(carrera, rango)
    total_jobs = len(df_open)

    st.markdown(
        f'<div class="filter-state">Filtros aplicados: {rango[0].strftime("%d/%m/%Y")} – {rango[1].strftime("%d/%m/%Y")} · Carrera: {escapar(carrera)}</div>',
        unsafe_allow_html=True,
    )

    seccion("Resumen ejecutivo", "Indicadores recalculados con el contexto seleccionado.")
    metricas_cards([
        ("Participantes BCP", m["total"], "Participantes del contexto"),
        ("Participantes con actividad", m["activos"], f"{porcentaje(m['activos'], m['total']):.1f}% del contexto"),
        ("Participantes con CV", m["cv"], f"{porcentaje(m['cv'], m['total']):.1f}% del contexto"),
        ("Autoconocimiento completado", m["ikigai_completado"], f"{porcentaje(m['ikigai_completado'], m['total']):.1f}% del contexto"),
        ("Participantes con evaluaciones", m["evaluaciones"], f"{porcentaje(m['evaluaciones'], m['total']):.1f}% del contexto"),
        ("Habilidades registradas", total_skills, f"{hard} hard · {soft} soft · {unicas} únicas"),
    ], 6)

    seccion("Compatibilidad y oportunidades", "Uso del análisis de compatibilidad y contexto de oportunidades abiertas.")
    comp_sub = f"{pct_comp:.1f}% del contexto"
    promedio_sub = f"{promedio_comp:.1f}% promedio" if not np.isnan(promedio_comp) else "Sin porcentaje disponible"
    metricas_cards([
        ("Participantes con análisis", cp, comp_sub),
        ("Análisis de compatibilidad", n_analisis, promedio_sub),
        ("Oportunidades abiertas", total_jobs, "Ofertas con estado OPEN"),
        ("Habilidades en demanda", int((demanda_tabla()["Apariciones"] > 0).sum()) if not demanda_tabla().empty else 0, "Con al menos una aparición en requisitos"),
    ], 4)

    afinidad = ikigai_dimension("Áreas de trabajo sugeridas", ids=ids, limite=5)
    if not afinidad.empty:
        seccion("Top de áreas con mayor afinidad", "Áreas de trabajo sugeridas con mayor recurrencia en los resultados disponibles.")
        fig = px.bar(afinidad.sort_values("Participantes"), x="Participantes", y="Concepto", orientation="h", text="Participantes")
        fig.update_traces(marker_color=AZUL_OSCURO, textposition="outside")
        fig.update_layout(xaxis_title="Participantes", yaxis_title="", showlegend=False)
        fig.update_xaxes(dtick=1, rangemode="tozero", showgrid=True, gridcolor="#EEF3F8")
        st.plotly_chart(figura_base(fig, 300), use_container_width=True, config={"displayModeBar": False})

    seccion("Hallazgos clave")
    metricas_cards([
        ("Actividad", f"{m['activos']} / {m['total']}", f"{porcentaje(m['activos'], m['total']):.1f}% en el rango"),
        ("Autoconocimiento", m["ikigai_completado"], f"{m['ikigai_resultado']} con resultado generado"),
        ("Habilidades", total_skills, f"{hard} hard · {soft} soft"),
        ("Compatibilidad", cp, f"{n_analisis} análisis registrados"),
    ], 4)

    a, b = st.columns([1.45, 1])
    with a:
        seccion("Evolución de la participación", "Participantes únicos por semana.")
        st.plotly_chart(grafico_evolucion(rango, ids), use_container_width=True, config={"displayModeBar": False})
    with b:
        seccion("Uso de funcionalidades", "Participantes con evidencia de uso.")
        st.plotly_chart(grafico_funcionalidades(ids, rango, m["total"]), use_container_width=True, config={"displayModeBar": False})

    a, b = st.columns([1, 1.35])
    with a:
        seccion("Desarrollo del perfil", "Presencia de información profesional en el contexto seleccionado.")
        perfil = pd.DataFrame({
            "Componente": ["CV", "Educación", "Experiencia", "Habilidades"],
            "Participantes": [m["cv"], m["educacion"], m["experiencia"], m["habilidades"]],
        })
        perfil["Porcentaje"] = perfil["Participantes"].map(lambda x: porcentaje(x, m["total"]))
        perfil = perfil.sort_values("Porcentaje")
        fig = px.bar(perfil, x="Porcentaje", y="Componente", orientation="h", text=perfil["Porcentaje"].map(lambda x: f"{x:.0f}%"))
        fig.update_traces(marker_color=NARANJA, textposition="outside", cliponaxis=False)
        fig.update_layout(xaxis_title="% de participantes", yaxis_title="", showlegend=False)
        fig.update_xaxes(range=[0, 100], showgrid=True, gridcolor="#EEF3F8")
        st.plotly_chart(figura_base(fig, 320), use_container_width=True, config={"displayModeBar": False})
    with b:
        seccion("Habilidades principales", "Nombres equivalentes se agrupan bajo una misma etiqueta.")
        h1, h2 = st.tabs(["Hard skills", "Soft skills"])
        with h1:
            st.plotly_chart(grafico_skills(ids, "Hard skills", 10, 380), use_container_width=True, config={"displayModeBar": False})
        with h2:
            st.plotly_chart(grafico_skills(ids, "Soft skills", 10, 380), use_container_width=True, config={"displayModeBar": False})

    seccion("Autoconocimiento profesional", "Resultados agregados del proceso de autoconocimiento.")
    mini_cards([
        ("Proceso iniciado", m["ikigai_iniciado"], f"{porcentaje(m['ikigai_iniciado'], m['total']):.1f}% del contexto"),
        ("Proceso completado", m["ikigai_completado"], f"{porcentaje(m['ikigai_completado'], m['total']):.1f}% del contexto"),
        ("Con resultado generado", m["ikigai_resultado"], f"{porcentaje(m['ikigai_resultado'], m['total']):.1f}% del contexto"),
    ], 3)
    for dimension in ["Fortalezas", "Motivaciones", "Áreas de trabajo sugeridas"]:
        st.markdown(f'<div class="ikigai-block"><div class="ikigai-title">{escapar(dimension)}</div>', unsafe_allow_html=True)
        d=ikigai_dimension(dimension, ids=ids, limite=8)
        if d.empty: st.caption("Sin información disponible.")
        else:
            tags=[f'<span class="tag">{escapar(concepto)}</span>' for concepto in d["Concepto"].tolist()]
            st.markdown('<div class="tag-grid">'+''.join(tags)+'</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)


# ============================================================
# PERFIL DEL GRUPO
# ============================================================

elif pagina == "Perfil del grupo":
    titulo_pagina("Perfil del grupo", "Desarrollo del perfil profesional registrado en Laboral.AI.")
    rango, carrera = render_filtros()
    df_ctx, ids = contexto(rango, carrera)
    m = metricas_contexto(df_ctx, ids, rango)

    seccion("Desarrollo del perfil profesional", "Participantes con información registrada en cada componente.")
    metricas_cards([
        ("CV", m["cv"], f"{porcentaje(m['cv'], m['total']):.1f}% del contexto"),
        ("Educación", m["educacion"], f"{porcentaje(m['educacion'], m['total']):.1f}% del contexto"),
        ("Experiencia", m["experiencia"], f"{porcentaje(m['experiencia'], m['total']):.1f}% del contexto"),
        ("Habilidades", m["habilidades"], f"{porcentaje(m['habilidades'], m['total']):.1f}% del contexto"),
    ], 4)

    perfil = pd.DataFrame({
        "Componente": ["CV", "Educación", "Experiencia", "Habilidades"],
        "Participantes": [m["cv"], m["educacion"], m["experiencia"], m["habilidades"]],
    })
    perfil["Porcentaje"] = perfil["Participantes"].map(lambda x: porcentaje(x, m["total"]))
    fig = px.bar(perfil.sort_values("Porcentaje"), x="Porcentaje", y="Componente", orientation="h", text=perfil.sort_values("Porcentaje")["Porcentaje"].map(lambda x: f"{x:.0f}%"))
    fig.update_traces(marker_color=VERDE, textposition="outside", cliponaxis=False)
    fig.update_layout(xaxis_title="% de participantes", yaxis_title="", showlegend=False)
    fig.update_xaxes(range=[0, 100], showgrid=True, gridcolor="#EEF3F8")
    st.plotly_chart(figura_base(fig, 330), use_container_width=True, config={"displayModeBar": False})

# ============================================================
# EVOLUCIÓN
# ============================================================

elif pagina == "Evolución":
    titulo_pagina("Evolución de la participación", "Seguimiento temporal de actividad verificable desde el evento BCP.")
    rango, carrera = render_filtros()
    df_ctx, ids = contexto(rango, carrera)
    activos = len(ids.intersection(ids_actividad_rango(rango)))

    metricas_cards([
        ("Participantes con actividad", activos, f"{porcentaje(activos, len(df_ctx)):.1f}% del contexto"),
        ("Participantes del contexto", len(df_ctx), f"Carrera: {carrera}"),
        ("Inicio del seguimiento", "20/08/2026", "Evento BCP"),
    ], 3)

    seccion("Actividad a lo largo del tiempo", "Participantes únicos por semana dentro del rango seleccionado.")
    st.plotly_chart(grafico_evolucion(rango, ids), use_container_width=True, config={"displayModeBar": False})


# ============================================================
# AUTOCONOCIMIENTO
# ============================================================

elif pagina == "Autoconocimiento":
    titulo_pagina("Autoconocimiento profesional", "Lectura agregada de fortalezas, motivaciones y dirección profesional.")
    rango, carrera = render_filtros()
    df_ctx, ids = contexto(rango, carrera)
    m = metricas_contexto(df_ctx, ids, rango)

    mini_cards([
        ("Proceso iniciado", m["ikigai_iniciado"], f"{porcentaje(m['ikigai_iniciado'], m['total']):.1f}% del contexto"),
        ("Proceso completado", m["ikigai_completado"], f"{porcentaje(m['ikigai_completado'], m['total']):.1f}% del contexto"),
        ("Con resultado generado", m["ikigai_resultado"], f"{porcentaje(m['ikigai_resultado'], m['total']):.1f}% del contexto"),
    ], 3)

    dimension = st.selectbox("Dimensión", DIMENSIONES, key="ikigai_dimension")
    seccion(dimension, "Los conceptos equivalentes se agrupan para facilitar la lectura.")
    st.plotly_chart(grafico_ikigai(dimension, ids, 10, 430), use_container_width=True, config={"displayModeBar": False})


# ============================================================
# HABILIDADES
# ============================================================

elif pagina == "Habilidades":
    titulo_pagina("Habilidades", "Habilidades técnicas y blandas estandarizadas.")
    rango, carrera = render_filtros()
    _, ids = contexto(rango, carrera)
    skills = skills_preparadas(ids)
    hard_count = int(skills.loc[skills["tipo"].eq("Hard skills"), "habilidad"].nunique()) if not skills.empty else 0
    soft_count = int(skills.loc[skills["tipo"].eq("Soft skills"), "habilidad"].nunique()) if not skills.empty else 0
    total_unique = int(skills["habilidad"].nunique()) if not skills.empty else 0
    users_skills = int(skills["__user"].nunique()) if not skills.empty else 0

    metricas_cards([
        ("Hard skills", hard_count, "Habilidades técnicas únicas"),
        ("Soft skills", soft_count, "Habilidades blandas únicas"),
        ("Habilidades únicas", total_unique, "Nombres estandarizados"),
        ("Participantes con habilidades", users_skills, "Participantes que tienen al menos una habilidad registrada"),
    ], 4)

    a, b = st.columns(2)
    with a:
        seccion("Hard skills", "Top 10 por número de participantes.")
        st.plotly_chart(grafico_skills(ids, "Hard skills", 10, 400), use_container_width=True, config={"displayModeBar": False})
    with b:
        seccion("Soft skills", "Top 10 por número de participantes.")
        st.plotly_chart(grafico_skills(ids, "Soft skills", 10, 400), use_container_width=True, config={"displayModeBar": False})

    seccion("Relación con demanda", "Top 10 habilidades con mayor presencia en requisitos publicados.")
    a, b = st.columns(2)
    with a:
        st.plotly_chart(grafico_demanda("Hard skills", 10), use_container_width=True, config={"displayModeBar": False})
    with b:
        st.plotly_chart(grafico_demanda("Soft skills", 10), use_container_width=True, config={"displayModeBar": False})

    with st.expander("Ver todas las habilidades disponibles en la relación con demanda"):
        d = demanda_tabla()
        if d.empty:
            st.info("No hay matriz de demanda disponible.")
        else:
            st.dataframe(d.rename(columns={"Apariciones": "Apariciones en requisitos"}), use_container_width=True, hide_index=True)


# ============================================================
# MERCADO LABORAL
# ============================================================

elif pagina == "Mercado laboral":
    titulo_pagina("Mercado laboral", "Contexto de oportunidades y demanda disponible en Laboral.AI.")
    rango, carrera = render_filtros()
    df_open = jobs_abiertos(carrera, rango)
    dmd = demanda_tabla()
    ofertas = len(df_open)
    departamentos = col(df_open, ["department"])
    titulos = col(df_open, ["title"])

    metricas_cards([
        ("Ofertas abiertas", ofertas, "Estado OPEN"),
        ("Habilidades en demanda", int((dmd["Apariciones"] > 0).sum()) if not dmd.empty else 0, "Habilidades con requisitos registrados"),
        ("Carrera seleccionada", carrera, "Contexto de participantes"),
        ("Rango de análisis", f"{rango[0].strftime('%d/%m')}–{rango[1].strftime('%d/%m')}", "Filtros activos"),
    ], 4)

    seccion("Demanda laboral disponible", "Oportunidades abiertas y requisitos disponibles en Laboral.AI.")
    if df_open.empty:
        st.info("No hay oportunidades abiertas para el contexto seleccionado.")
    else:
        if departamentos:
            dep = (
                df_open[departamentos]
                .fillna("Sin especificar")
                .astype(str)
                .map(lambda x: x.title())
                .value_counts()
                .head(10)
                .rename_axis("Área")
                .reset_index(name="Ofertas")
            )
            fig = px.bar(
                dep.sort_values("Ofertas"),
                x="Ofertas", y="Área",
                orientation="h", text="Ofertas"
            )
            fig.update_traces(marker_color=NARANJA, textposition="outside")
            fig.update_layout(
                xaxis_title="Ofertas abiertas",
                yaxis_title="",
                showlegend=False
            )
            fig.update_xaxes(
                dtick=1, rangemode="tozero",
                showgrid=True, gridcolor="#EEF3F8"
            )
            st.plotly_chart(
                figura_base(fig, max(300, 34 * len(dep) + 80)),
                use_container_width=True,
                config={"displayModeBar": False}
            )

    if titulos:
        # No mostramos cada variante del nombre del puesto por separado.
        # Los puestos equivalentes se normalizan y se agrupan bajo una misma carrera.
        filas_carrera = []
        cc = col(df_open, ["carrera", "career", "degree", "area_carrera", "profesion"])
        cd = col(df_open, ["department"])
        for _, r in df_open.iterrows():
            if cc:
                carrera_puesto = carrera_canonica(r.get(cc))
            else:
                carrera_puesto = "Sin especificar"
            if carrera_puesto == "Sin especificar":
                carrera_puesto = carrera_desde_puesto(r.get(titulos, ""), r.get(cd, "") if cd else "")
            if carrera_puesto != "Sin especificar":
                filas_carrera.append(carrera_puesto)

        if filas_carrera:
            t = (
                pd.Series(filas_carrera, name="Carrera")
                .value_counts()
                .head(15)
                .rename_axis("Carrera")
                .reset_index(name="Ofertas")
            )
            seccion("Puestos publicados por carrera", "Los nombres equivalentes se agrupan bajo una misma carrera.")
            fig = px.bar(t.sort_values("Ofertas"), x="Ofertas", y="Carrera", orientation="h", text="Ofertas")
            fig.update_traces(marker_color=VERDE, textposition="outside", cliponaxis=False)
            fig.update_layout(xaxis_title="Ofertas", yaxis_title="", showlegend=False)
            fig.update_xaxes(dtick=1, rangemode="tozero", showgrid=True, gridcolor="#EEF3F8")
            st.plotly_chart(figura_base(fig, max(360, 30 * len(t) + 80)), use_container_width=True, config={"displayModeBar": False})



# ============================================================
# USO DE FUNCIONALIDADES
# ============================================================

elif pagina == "Uso de funcionalidades":
    titulo_pagina("Uso de funcionalidades", "Participantes con evidencia de uso de herramientas de Laboral.AI.")
    rango, carrera = render_filtros()
    df_ctx, ids = contexto(rango, carrera)
    m = metricas_contexto(df_ctx, ids, rango)
    cp, _, _ = metricas_compatibilidad(ids, rango)
    cp = m.get("compatibilidad", cp)

    seccion("Uso de funcionalidades", "Porcentaje calculado sobre el contexto seleccionado.")
    datos = pd.DataFrame([
        ("Autoconocimiento", m["ikigai_iniciado"]),
        ("Evaluaciones", m["evaluaciones"]),
        ("Cursos", m["cursos"]),
        ("Compatibilidad", cp),
        ("Chatbot", m["chatbot"]),
        ("Alertas", m["alertas"]),
        ("Eventos", m["eventos"]),
    ], columns=["Funcionalidad", "Participantes"])
    datos["Porcentaje"] = datos["Participantes"].map(lambda x: porcentaje(x, m["total"]))
    fig = px.bar(datos.sort_values("Participantes"), x="Participantes", y="Funcionalidad", orientation="h", text="Participantes", custom_data=["Porcentaje"])
    fig.update_traces(marker_color=AZUL_OSCURO, textposition="outside", cliponaxis=False,
                      hovertemplate="<b>%{y}</b><br>Participantes: %{x}<br>Porcentaje: %{customdata[0]:.1f}%<extra></extra>")
    fig.update_layout(xaxis_title="Participantes", yaxis_title="", showlegend=False)
    fig.update_xaxes(dtick=1, rangemode="tozero", showgrid=True, gridcolor="#EEF3F8")
    st.plotly_chart(figura_base(fig, 350), use_container_width=True, config={"displayModeBar": False})

    seccion("Detalle de funcionalidades")
    mini_cards([
        ("Autoconocimiento", m["ikigai_iniciado"], f"{porcentaje(m['ikigai_iniciado'], m['total']):.1f}% del contexto"),
        ("Evaluaciones", m["evaluaciones"], f"{porcentaje(m['evaluaciones'], m['total']):.1f}% del contexto"),
        ("Cursos", m["cursos"], f"{porcentaje(m['cursos'], m['total']):.1f}% del contexto"),
        ("Compatibilidad", cp, f"{porcentaje(cp, m['total']):.1f}% del contexto"),
    ], 4)
    mini_cards([
        ("Chatbot", m["chatbot"], f"{porcentaje(m['chatbot'], m['total']):.1f}% del contexto"),
        ("Alertas", m["alertas"], f"{porcentaje(m['alertas'], m['total']):.1f}% del contexto"),
        ("Eventos", m["eventos"], f"{porcentaje(m['eventos'], m['total']):.1f}% del contexto"),
    ], 3)


# ============================================================
# DETALLE DEL PARTICIPANTE
# ============================================================

elif pagina == "Detalle del participante":
    titulo_pagina("Detalle del participante", "Información profesional, habilidades y actividad registrada.")

    opciones = df_participantes["__nombre"].dropna().drop_duplicates().sort_values().tolist()
    if not opciones:
        st.warning("No hay participantes disponibles.")
        st.stop()
    seleccionado = st.selectbox("Participante", opciones, key="detalle_participante")
    fila = df_participantes[df_participantes["__nombre"].eq(seleccionado)].iloc[0]
    user_id = str(fila.get(COL_USER, "")).strip() if COL_USER else ""
    carrera = fila.get("__carrera", "Sin especificar")

    if carrera and carrera != "Sin especificar":
        st.markdown(
            f'<div class="participant-meta" style="margin-bottom:12px;">Carrera: {escapar(carrera)}</div>',
            unsafe_allow_html=True,
        )


    ids_one = {user_id} if user_id else set()
    rango_detalle = (FECHA_EVENTO.date(), fecha_maxima_actividad().date())
    m = metricas_contexto(df_participantes[df_participantes[COL_USER].astype(str).eq(user_id)] if COL_USER else df_participantes.iloc[[0]], ids_one, rango_detalle)

    # Conteos detallados por fuente cuando existen hojas con registros.
    def contar_usuario(df, candidatos):
        if df.empty or not user_id:
            return 0
        cu = col(df, candidatos)
        if not cu:
            return 0
        return int(df[cu].astype(str).str.strip().eq(user_id).sum())

    n_cv = 1 if m["cv"] else 0
    n_edu = contar_usuario(df_educacion, ["user_id", "userid", "user", "cv"])
    n_exp = contar_usuario(df_experiencia, ["user_id", "userid", "user", "cv"])
    n_idiomas = contar_usuario(df_idiomas, ["user_id", "userid", "user", "cv"])
    n_act = len(ids_actividad_rango(rango_detalle).intersection(ids_one))
    skills_one = skills_preparadas(ids_one)
    n_hard = int(skills_one.loc[skills_one["tipo"].eq("Hard skills"), "habilidad"].nunique()) if not skills_one.empty else 0
    n_soft = int(skills_one.loc[skills_one["tipo"].eq("Soft skills"), "habilidad"].nunique()) if not skills_one.empty else 0

    metricas_cards([
        ("CV", n_cv, "CV identificado" if n_cv else "Sin CV identificado"),
        ("Educación", n_edu, "Registros encontrados"),
        ("Experiencia", n_exp, "Registros encontrados"),
        ("Idiomas", n_idiomas, "Registros encontrados"),
        ("Hard skills", n_hard, "Habilidades técnicas"),
        ("Soft skills", n_soft, "Habilidades blandas"),
    ], 6)

    seccion("Habilidades registradas", "Habilidades estandarizadas asociadas al participante.")
    a, b = st.columns(2)
    with a:
        st.markdown("**Soft skills**")
        softs = skills_one.loc[skills_one["tipo"].eq("Soft skills"), "habilidad"].drop_duplicates().sort_values().tolist() if not skills_one.empty else []
        if softs:
            st.markdown('<div class="tag-grid">' + ''.join(f'<span class="tag tag-soft">{escapar(x)}</span>' for x in softs) + '</div>', unsafe_allow_html=True)
        else:
            st.caption("Sin soft skills registradas.")
    with b:
        st.markdown("**Hard skills**")
        hards = skills_one.loc[skills_one["tipo"].eq("Hard skills"), "habilidad"].drop_duplicates().sort_values().tolist() if not skills_one.empty else []
        if hards:
            st.markdown('<div class="tag-grid">' + ''.join(f'<span class="tag tag-hard">{escapar(x)}</span>' for x in hards) + '</div>', unsafe_allow_html=True)
        else:
            st.caption("Sin hard skills registradas.")

    seccion("Compatibilidad", "Análisis de compatibilidad registrados para el participante.")
    cp, n_ana, avg = metricas_compatibilidad(ids_one, rango_detalle)
    metricas_cards([
        ("Análisis", n_ana, "Registros de compatibilidad"),
        ("Participante con análisis", "Sí" if cp else "No", "Evidencia registrada"),
        ("Promedio de compatibilidad", f"{avg:.1f}%" if not np.isnan(avg) else "Sin dato", "Promedio de porcentajes válidos"),
    ], 3)

    seccion("Uso de funcionalidades", "Registros asociados al participante dentro del periodo observado.")
    mini_cards([
        ("Autoconocimiento", m["ikigai_iniciado"], "Registro en la funcionalidad"),
        ("Evaluaciones", m["evaluaciones"], "Datos registrados"),
        ("Cursos", m["cursos"], "Inscripciones registradas"),
        ("Chatbot", m["chatbot"], "Conversaciones registradas"),
    ], 4)
