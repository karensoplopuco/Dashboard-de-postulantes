# Dashboard de Postulantes – Laboral.AI

## Descripción del proyecto

Este proyecto consiste en el desarrollo de un **dashboard interactivo de postulantes de Laboral.AI**, desarrollado con **Python, Pandas, Plotly y Streamlit**.

El objetivo principal es transformar información proveniente de diferentes colecciones de MongoDB en un dataset consolidado que permita analizar el perfil, formación, experiencia y participación de los postulantes dentro de la plataforma.

## Objetivos

* Consolidar información de diferentes colecciones de MongoDB.
* Limpiar y transformar los datos para su análisis.
* Realizar cruces entre usuarios, CV, educación, experiencias y participación en la plataforma.
* Construir indicadores clave (KPIs) sobre los postulantes.
* Analizar las principales características de los perfiles registrados.
* Facilitar el análisis mediante filtros interactivos.
* Presentar los resultados mediante un dashboard visual y profesional.

## Tecnologías utilizadas

* **Python**
* **Pandas** – limpieza, transformación y análisis de datos.
* **NumPy** – procesamiento de datos.
* **Plotly** – visualización interactiva.
* **Streamlit** – desarrollo del dashboard.
* **MongoDB** – fuente de datos.
* **PyMongo** – conexión con MongoDB.
* **python-dotenv** – manejo de variables de entorno.
* **Git y GitHub** – control de versiones.

## Fuente de datos

La información utilizada proviene de la base de datos **MongoDB de Laboral.AI**.

Entre las principales colecciones utilizadas se encuentran:

* `users`
* `cvs`
* `educations`
* `workexperiences`
* `companies`
* `jobs`
* `applications`
* `courseenrollments`
* `courses`
* `aiconversations`
* `aimessages`
* `events`
* `eventguests`

La información de estas colecciones fue procesada y relacionada para construir un dataset final orientado al análisis de postulantes.

## Procesamiento y construcción del dataset

Se desarrolló un proceso de transformación de datos que incluye:

1. Conexión y autenticación con MongoDB.
2. Lectura de las diferentes colecciones.
3. Conversión de datos a DataFrames mediante Pandas.
4. Normalización de identificadores para realizar los cruces.
5. Limpieza de valores nulos y categorías.
6. Cruce de información entre usuarios y CV.
7. Integración de información educativa.
8. Integración de experiencias laborales y prácticas.
9. Integración de postulaciones.
10. Integración de participación en eventos.
11. Integración del uso de inteligencia artificial.
12. Integración de participación en cursos.
13. Creación de variables derivadas para el análisis.
14. Eliminación de duplicados.
15. Generación de un dataset consolidado para el dashboard.

## Principales indicadores (KPIs)

El dashboard presenta cinco indicadores principales:

* 👥 **Postulantes:** cantidad total de postulantes considerados.
* 📄 **Con CV:** postulantes que cuentan con un CV registrado.
* 🤖 **Uso de IA:** postulantes que utilizaron las funcionalidades de inteligencia artificial.
* 🎫 **Eventos:** postulantes que participaron en eventos.
* 📚 **Cursos:** postulantes que cuentan con participación en cursos.

Los indicadores se actualizan de acuerdo con los filtros seleccionados.

## Filtros

El dashboard cuenta con filtros principales para facilitar el análisis:

* **Año**
* **Área profesional**

Estos filtros permiten analizar cómo varían los indicadores y gráficos según el periodo y el área profesional seleccionada.

## Análisis realizado

El dashboard permite analizar diferentes dimensiones de los postulantes:

### Perfil profesional

* Carreras con mayor cantidad de postulantes.
* Distribución de postulantes por área profesional.

### Experiencia

* Distribución de experiencia laboral.
* Distribución de experiencia en prácticas.

### Uso de la plataforma

* Uso de inteligencia artificial.
* Preferencia de modalidad laboral.

### Formación y participación

* Participación en eventos.
* Nivel educativo de los postulantes.

### Evolución de registros

Se presenta la evolución mensual de los registros de postulantes para identificar el comportamiento de los registros a través del tiempo.

## Visualizaciones

Se utilizaron diferentes tipos de gráficos para facilitar la interpretación de la información:

* **Gráficos de barras** para comparar cantidades.
* **Gráficos donut** para representar distribuciones y porcentajes.
* **Gráficos de evolución** para analizar registros por periodo.
* **KPI cards** para mostrar los principales indicadores.

Se aplicó una paleta de colores corporativa basada en tonos azules, celestes, lavanda y verde menta, buscando mantener una presentación limpia y profesional.

## Estructura del proyecto

```text
Dashboard-de-postulantes/
│
├── app.py
├── README.md
├── requirements.txt
├── .env
│
├── data/
│   ├── cache/
│   │   └── postulantes_dashboard.csv
│   │
│   └── output/
│
├── scripts/
│   ├── conexion.py
│   └── constructor.py
│
└── venv/
```

## Funcionamiento

El proyecto se encuentra organizado en dos partes principales:

### 1. Construcción de datos

El módulo `constructor.py` se encarga de procesar la información proveniente de MongoDB, realizar las transformaciones necesarias y generar el dataset utilizado por el dashboard.

El resultado se almacena en:

```text
data/cache/postulantes_dashboard.csv
```

### 2. Dashboard

El archivo `app.py` utiliza el dataset construido para generar la interfaz interactiva mediante Streamlit.

Para ejecutar el dashboard:


## Resultado

El proyecto permite convertir información dispersa de diferentes fuentes de Laboral.AI en una herramienta centralizada para el análisis de postulantes.

El dashboard facilita la identificación de:

* Cantidad de postulantes.
* Postulantes con CV.
* Uso de IA.
* Participación en eventos.
* Participación en cursos.
* Principales carreras.
* Áreas profesionales con mayor cantidad de postulantes.
* Distribución de experiencia laboral y prácticas.
* Nivel educativo.
* Preferencias de modalidad laboral.
* Evolución de registros.

De esta manera, la solución permite realizar un análisis más rápido y visual de los perfiles registrados en la plataforma y puede servir como apoyo para la **toma de decisiones y seguimiento de los postulantes de Laboral.AI**.
