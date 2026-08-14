import tkinter as tk
from tkinter import ttk
from pathlib import Path

import pandas as pd

from scripts.conexion import db


# ============================================================
# RUTAS DE SALIDA
# ============================================================

RUTA_DETALLE = Path(
    "data/cache/cursos_interes_dashboard.csv"
)

RUTA_RESUMEN = Path(
    "data/cache/cursos_interes_postulantes.csv"
)


# ============================================================
# CARGAR COLECCIONES
# ============================================================

def cargar_colecciones():

    courses = list(
        db["courses"].find({})
    )

    courseenrollments = list(
        db["courseenrollments"].find({})
    )

    courses = pd.DataFrame(courses)

    courseenrollments = pd.DataFrame(
        courseenrollments
    )

    print(
        f"📚 Cursos encontrados: {len(courses)}"
    )

    print(
        f"👥 Inscripciones encontradas: "
        f"{len(courseenrollments)}"
    )

    return (
        courses,
        courseenrollments
    )


# ============================================================
# CLASIFICAR CURSOS
# ============================================================

def clasificar_curso(nombre):

    if pd.isna(nombre):
        return None

    nombre = str(
        nombre
    ).strip().lower()


    # --------------------------------------------------------
    # CURSOS DE PRUEBA
    # --------------------------------------------------------

    cursos_prueba = [
        "test de curso",
        "test pago",
        "test sincrono",
        "curso sin nombre"
    ]

    if nombre in cursos_prueba:
        return None


    # --------------------------------------------------------
    # EMPLEABILIDAD Y CV
    # --------------------------------------------------------

    if any(
        texto in nombre
        for texto in [
            "taller de cv",
            "optimiza tu cv"
        ]
    ):
        return "Empleabilidad y CV"


    # --------------------------------------------------------
    # MARCA PERSONAL Y LINKEDIN
    # --------------------------------------------------------

    if any(
        texto in nombre
        for texto in [
            "linkedin boost",
            "linkedin",
            "marcas"
        ]
    ):
        return "Marca personal y LinkedIn"


    # --------------------------------------------------------
    # LIDERAZGO Y HABILIDADES PROFESIONALES
    # --------------------------------------------------------

    if any(
        texto in nombre
        for texto in [
            "mentalidad de líder",
            "presentaciones de alto impacto",
            "rodrigo reyes"
        ]
    ):
        return "Liderazgo y habilidades profesionales"


    # --------------------------------------------------------
    # PRODUCTIVIDAD Y HERRAMIENTAS DIGITALES
    # --------------------------------------------------------

    if "google workspace" in nombre:

        return (
            "Productividad y herramientas digitales"
        )


    # --------------------------------------------------------
    # NEGOCIOS Y COMUNICACIÓN
    # --------------------------------------------------------

    if "negocia y convence" in nombre:

        return "Negocios y comunicación"


    # --------------------------------------------------------
    # ORIENTACIÓN PROFESIONAL
    # --------------------------------------------------------

    if "ikigai" in nombre:

        return "Orientación profesional"


    # --------------------------------------------------------
    # TECNOLOGÍA E INNOVACIÓN
    # --------------------------------------------------------

    if any(
        texto in nombre
        for texto in [
            "bootcamp de desarrollo web full stack",
            "flujos end to end"
        ]
    ):
        return "Tecnología e innovación"


    # --------------------------------------------------------
    # OTROS NO CLASIFICADOS
    # --------------------------------------------------------

    return None


# ============================================================
# BUSCAR COLUMNA
# ============================================================

def buscar_columna(df, posibles):

    for columna in posibles:

        if columna in df.columns:

            return columna

    return None


# ============================================================
# PROCESAR CURSOS
# ============================================================

def procesar_cursos(
    courses,
    courseenrollments
):

    if courses.empty:

        print(
            "❌ No hay cursos."
        )

        return (
            pd.DataFrame(),
            pd.DataFrame()
        )


    if courseenrollments.empty:

        print(
            "❌ No hay inscripciones."
        )

        return (
            pd.DataFrame(),
            pd.DataFrame()
        )


    # ========================================================
    # COLUMNAS DE COURSES
    # ========================================================

    columna_id_curso = buscar_columna(
        courses,
        [
            "_id",
            "courseId",
            "course_id",
            "id"
        ]
    )


    columna_nombre = buscar_columna(
        courses,
        [
            "name",
            "nombre",
            "title",
            "courseName"
        ]
    )


    if columna_id_curso is None:

        print(
            "❌ No se encontró el ID del curso."
        )

        print(
            courses.columns.tolist()
        )

        return (
            pd.DataFrame(),
            pd.DataFrame()
        )


    if columna_nombre is None:

        print(
            "❌ No se encontró el nombre del curso."
        )

        print(
            courses.columns.tolist()
        )

        return (
            pd.DataFrame(),
            pd.DataFrame()
        )


    # ========================================================
    # COLUMNAS DE COURSEENROLLMENTS
    # ========================================================

    columna_curso_inscripcion = buscar_columna(
        courseenrollments,
        [
            "courseId",
            "course_id",
            "course",
            "courseID"
        ]
    )


    columna_usuario = buscar_columna(
        courseenrollments,
        [
            "userId",
            "user_id",
            "user",
            "userID"
        ]
    )


    if columna_curso_inscripcion is None:

        print(
            "❌ No se encontró el ID del curso "
            "en courseenrollments."
        )

        print(
            courseenrollments.columns.tolist()
        )

        return (
            pd.DataFrame(),
            pd.DataFrame()
        )


    if columna_usuario is None:

        print(
            "❌ No se encontró el ID del usuario "
            "en courseenrollments."
        )

        print(
            courseenrollments.columns.tolist()
        )

        return (
            pd.DataFrame(),
            pd.DataFrame()
        )


    # ========================================================
    # CONVERTIR IDS A STRING
    # ========================================================

    courses[
        columna_id_curso
    ] = (
        courses[columna_id_curso]
        .astype("string")
        .str.strip()
    )


    courseenrollments[
        columna_curso_inscripcion
    ] = (
        courseenrollments[
            columna_curso_inscripcion
        ]
        .astype("string")
        .str.strip()
    )


    courseenrollments[
        columna_usuario
    ] = (
        courseenrollments[
            columna_usuario
        ]
        .astype("string")
        .str.strip()
    )


    # ========================================================
    # CLASIFICAR CURSOS
    # ========================================================

    courses[
        "categoria_curso"
    ] = (
        courses[columna_nombre]
        .apply(clasificar_curso)
    )


    # ========================================================
    # ELIMINAR CURSOS DE PRUEBA
    # ========================================================

    courses_validos = courses[
        courses[
            "categoria_curso"
        ].notna()
    ].copy()


    print(
        f"\n✅ Cursos válidos para análisis: "
        f"{len(courses_validos)}"
    )


        # ========================================================
    # CRUZAR INSCRIPCIONES + CURSOS
    # ========================================================

    resultado = courseenrollments.merge(
        courses_validos[
            [
                columna_id_curso,
                columna_nombre,
                "categoria_curso"
            ]
        ],
        left_on=columna_curso_inscripcion,
        right_on=columna_id_curso,
        how="inner",
        suffixes=("_inscripcion", "_curso")
    )

    # ========================================================
    # VALIDAR RESULTADO DEL MERGE
    # ========================================================

    print(
        "\n========== COLUMNAS DESPUÉS DEL MERGE =========="
    )

    print(
        resultado.columns.tolist()
    )

    print(
        "\nRegistros después del merge:",
        len(resultado)
    )

    print(
        "\nPrimeros registros:"
    )

    print(
        resultado.head(5).to_string(
            index=False
        )
    )

    # ========================================================
    # CREAR DATASET DETALLADO
    # ========================================================
    detalle = pd.DataFrame({

    "_id_postulante": resultado[
        columna_usuario
    ].astype("string"),

    "_id_course": resultado[
        "_id_curso"
    ].astype("string"),

    "curso": resultado[
        "title"
    ].astype("string"),

    "categoria_curso": resultado[
        "categoria_curso"
    ].astype("string")
    })
    

    # ========================================================
    # ELIMINAR DUPLICADOS
    # ========================================================

    detalle = detalle.drop_duplicates(
        subset=[
            "_id_postulante",
            "_id_course"
        ]
    )

    # ========================================================
    # ELIMINAR IDS VACÍOS
    # ========================================================

    detalle = detalle[
        detalle["_id_postulante"].notna()
        & detalle["_id_course"].notna()
    ].copy()


    detalle = detalle.rename(
        columns={
            columna_usuario:
                "_id_postulante",

            columna_id_curso:
                "_id_course",

            columna_nombre:
                "curso"
        }
    )


    # ========================================================
    # ELIMINAR DUPLICADOS
    # ========================================================
    #
    # Un postulante puede aparecer más de una vez
    # en la misma inscripción.
    #
    # ========================================================

    detalle = detalle.drop_duplicates(
        subset=[
            "_id_postulante",
            "_id_course"
        ]
    )


    # ========================================================
    # ELIMINAR IDs VACÍOS
    # ========================================================

    detalle = detalle[
        detalle["_id_postulante"].notna()
        & detalle["_id_course"].notna()
    ].copy()


    # ========================================================
    # RESUMEN POR CATEGORÍA
    # ========================================================

    resumen = (
        detalle
        .groupby(
            "categoria_curso"
        )[
            "_id_postulante"
        ]
        .nunique()
        .reset_index(
            name="cantidad_postulantes"
        )
    )


    # ========================================================
    # ORDENAR RESUMEN
    # ========================================================

    resumen = resumen.sort_values(
        "cantidad_postulantes",
        ascending=False
    ).reset_index(
        drop=True
    )


    # ========================================================
    # MOSTRAR DETALLE
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "📚 CURSOS DETALLADOS"
    )

    print(
        "=" * 70
    )

    print(
        detalle.head(20).to_string(
            index=False
        )
    )


    # ========================================================
    # MOSTRAR RESUMEN
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "📊 POSTULANTES POR CATEGORÍA"
    )

    print(
        "=" * 70
    )

    print(
        resumen.to_string(
            index=False
        )
    )


    # ========================================================
    # VALIDACIÓN DE IDS
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "🔑 VALIDACIÓN DE IDs"
    )

    print(
        "=" * 70
    )

    print(
        "Postulantes únicos:",
        detalle["_id_postulante"].nunique()
    )

    print(
        "Cursos únicos:",
        detalle["_id_course"].nunique()
    )

    print(
        "Registros detalle:",
        len(detalle)
    )


    return (
        detalle,
        resumen
    )


# ============================================================
# GUARDAR CSV
# ============================================================

def guardar_csv(
    df,
    ruta
):

    ruta.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    df.to_csv(
        ruta,
        index=False,
        encoding="utf-8-sig"
    )


    print(
        "\n✅ CSV guardado:"
    )

    print(
        ruta
    )


# ============================================================
# MOSTRAR DATAFRAME
# ============================================================

def mostrar_dataframe(df):

    ventana = tk.Tk()

    ventana.title(
        "Cursos de interés - DataFrame"
    )

    ventana.geometry(
        "1100x650"
    )


    titulo = ttk.Label(
        ventana,
        text="Cursos de interés de los postulantes",
        font=("Segoe UI", 14, "bold")
    )

    titulo.pack(
        pady=10
    )


    frame = ttk.Frame(
        ventana
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )


    columnas = list(
        df.columns
    )


    tabla = ttk.Treeview(
        frame,
        columns=columnas,
        show="headings"
    )


    for columna in columnas:

        tabla.heading(
            columna,
            text=columna
        )

        tabla.column(
            columna,
            width=280
        )


    for _, fila in df.iterrows():

        valores = [
            str(valor)
            for valor in fila
        ]

        tabla.insert(
            "",
            "end",
            values=valores
        )


    scroll_vertical = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tabla.yview
    )


    tabla.configure(
        yscrollcommand=scroll_vertical.set
    )


    scroll_horizontal = ttk.Scrollbar(
        frame,
        orient="horizontal",
        command=tabla.xview
    )


    tabla.configure(
        xscrollcommand=scroll_horizontal.set
    )


    tabla.grid(
        row=0,
        column=0,
        sticky="nsew"
    )


    scroll_vertical.grid(
        row=0,
        column=1,
        sticky="ns"
    )


    scroll_horizontal.grid(
        row=1,
        column=0,
        sticky="ew"
    )


    frame.grid_rowconfigure(
        0,
        weight=1
    )

    frame.grid_columnconfigure(
        0,
        weight=1
    )


    boton = ttk.Button(
        ventana,
        text="Cerrar",
        command=ventana.destroy
    )


    boton.pack(
        pady=10
    )


    ventana.mainloop()


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n" + "=" * 70
    )

    print(
        "🎓 PROCESAMIENTO DE CURSOS"
    )

    print(
        "=" * 70
    )


    # --------------------------------------------------------
    # CARGAR
    # --------------------------------------------------------

    courses, courseenrollments = (
        cargar_colecciones()
    )


    # --------------------------------------------------------
    # PROCESAR
    # --------------------------------------------------------

    detalle, resumen = procesar_cursos(
        courses,
        courseenrollments
    )


    if detalle.empty:

        print(
            "\n❌ No se generó información."
        )

        return


    # ========================================================
    # GUARDAR DATASET DETALLADO
    # ========================================================

    guardar_csv(
        detalle,
        RUTA_DETALLE
    )


    # ========================================================
    # GUARDAR RESUMEN
    # ========================================================

    guardar_csv(
        resumen,
        RUTA_RESUMEN
    )


    # ========================================================
    # MOSTRAR DETALLE
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "🪟 ABRIENDO DATAFRAME DETALLADO"
    )

    print(
        "=" * 70
    )


    mostrar_dataframe(
        detalle
    )


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    main()