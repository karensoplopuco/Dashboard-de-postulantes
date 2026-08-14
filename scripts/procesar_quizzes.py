# ============================================================
# scripts/procesar_quizzes.py
# PROCESAMIENTO DE QUIZZES
# ============================================================

import os
import tkinter as tk

from tkinter import ttk

import pandas as pd

from scripts.conexion import db


# ============================================================
# CONFIGURACIÓN
# ============================================================

RUTA_SALIDA_RESUMEN = (
    "data/cache/quizzes_dashboard.csv"
)

RUTA_SALIDA_DETALLE = (
    "data/cache/quizzes_detalle_usuarios.csv"
)


# ============================================================
# CARGAR COLECCIONES
# ============================================================

def cargar_colecciones():

    quizzes = pd.DataFrame(
        list(
            db["quizzes"].find({})
        )
    )

    quizresults = pd.DataFrame(
        list(
            db["quizresults"].find({})
        )
    )

    userquizdatas = pd.DataFrame(
        list(
            db["userquizdatas"].find({})
        )
    )

    questions = pd.DataFrame(
        list(
            db["questions"].find({})
        )
    )

    users = pd.DataFrame(
        list(
            db["users"].find({})
        )
    )

    return (
        quizzes,
        quizresults,
        userquizdatas,
        questions,
        users
    )


# ============================================================
# PROCESAR QUIZZES
# ============================================================

def procesar_quizzes(
    quizzes,
    quizresults,
    userquizdatas,
    questions
):

    if quizzes.empty:

        print(
            "❌ No existen quizzes."
        )

        return pd.DataFrame()


    # --------------------------------------------------------
    # CONVERTIR IDS A STRING
    # --------------------------------------------------------

    quizzes["_id"] = (
        quizzes["_id"]
        .astype(str)
    )

    if not quizresults.empty:

        quizresults["quiz"] = (
            quizresults["quiz"]
            .astype(str)
        )

        quizresults["user"] = (
            quizresults["user"]
            .astype(str)
        )

    if not userquizdatas.empty:

        userquizdatas["quiz"] = (
            userquizdatas["quiz"]
            .astype(str)
        )

        userquizdatas["user"] = (
            userquizdatas["user"]
            .astype(str)
        )


    # --------------------------------------------------------
    # INFORMACIÓN DE CADA QUIZ
    # --------------------------------------------------------

    resultado = quizzes[
        [
            "_id",
            "key",
            "title",
            "description",
            "questions"
        ]
    ].copy()

    resultado = resultado.rename(
        columns={
            "_id": "quiz_id",
            "key": "quiz_key",
            "title": "quiz_nombre"
        }
    )


    # --------------------------------------------------------
    # CANTIDAD DE PREGUNTAS
    # --------------------------------------------------------

    resultado["cantidad_preguntas"] = (
        resultado["questions"]
        .apply(
            lambda x:
            len(x)
            if isinstance(x, list)
            else 0
        )
    )


    # --------------------------------------------------------
    # RESULTADOS DEL QUIZ
    # --------------------------------------------------------

    if not quizresults.empty:

        resultados_por_quiz = (
            quizresults
            .groupby("quiz")
            .agg(
                usuarios_completaron=(
                    "user",
                    "nunique"
                )
            )
            .reset_index()
        )

        resultados_por_quiz = (
            resultados_por_quiz
            .rename(
                columns={
                    "quiz": "quiz_id"
                }
            )
        )

        resultado = resultado.merge(
            resultados_por_quiz,
            on="quiz_id",
            how="left"
        )

    else:

        resultado[
            "usuarios_completaron"
        ] = 0


    # --------------------------------------------------------
    # USUARIOS CON RESPUESTAS / EN PROCESO
    # --------------------------------------------------------

    if not userquizdatas.empty:

        usuarios_proceso = (
            userquizdatas
            .groupby("quiz")
            .agg(
                usuarios_con_respuestas=(
                    "user",
                    "nunique"
                )
            )
            .reset_index()
        )

        usuarios_proceso = (
            usuarios_proceso
            .rename(
                columns={
                    "quiz": "quiz_id"
                }
            )
        )

        resultado = resultado.merge(
            usuarios_proceso,
            on="quiz_id",
            how="left"
        )

    else:

        resultado[
            "usuarios_con_respuestas"
        ] = 0


    # --------------------------------------------------------
    # LIMPIAR NULOS
    # --------------------------------------------------------

    resultado[
        "usuarios_completaron"
    ] = (
        resultado[
            "usuarios_completaron"
        ]
        .fillna(0)
        .astype(int)
    )

    resultado[
        "usuarios_con_respuestas"
    ] = (
        resultado[
            "usuarios_con_respuestas"
        ]
        .fillna(0)
        .astype(int)
    )


    # --------------------------------------------------------
    # CALCULAR USUARIOS EN PROCESO
    #
    # Usuarios con respuestas
    # menos usuarios que completaron
    # --------------------------------------------------------

    resultado[
        "usuarios_en_proceso"
    ] = (
        resultado[
            "usuarios_con_respuestas"
        ]
        -
        resultado[
            "usuarios_completaron"
        ]
    )


    resultado[
        "usuarios_en_proceso"
    ] = (
        resultado[
            "usuarios_en_proceso"
        ]
        .clip(lower=0)
    )


    # --------------------------------------------------------
    # TOTAL DE USUARIOS QUE INICIARON
    # --------------------------------------------------------

    resultado[
        "usuarios_iniciaron"
    ] = (
        resultado[
            "usuarios_completaron"
        ]
        +
        resultado[
            "usuarios_en_proceso"
        ]
    )


    # --------------------------------------------------------
    # ESTADO PRINCIPAL
    # --------------------------------------------------------

    def determinar_estado(fila):

        if fila[
            "usuarios_completaron"
        ] > 0:

            return "Completado"

        elif fila[
            "usuarios_en_proceso"
        ] > 0:

            return "En proceso"

        else:

            return "No iniciado"


    resultado[
        "estado"
    ] = resultado.apply(
        determinar_estado,
        axis=1
    )


    # --------------------------------------------------------
    # SELECCIONAR COLUMNAS FINALES
    # --------------------------------------------------------

    resultado = resultado[
        [
            "quiz_id",
            "quiz_key",
            "quiz_nombre",
            "cantidad_preguntas",
            "usuarios_iniciaron",
            "usuarios_completaron",
            "usuarios_en_proceso",
            "estado"
        ]
    ]


    return resultado


# ============================================================
# OBTENER DETALLE POR USUARIO Y QUIZ
# ============================================================

def obtener_detalle_usuarios(
    quizzes,
    quizresults,
    userquizdatas,
    users
):

    # --------------------------------------------------------
    # VALIDACIONES
    # --------------------------------------------------------

    if quizzes.empty:

        return pd.DataFrame()


    # --------------------------------------------------------
    # COPIAS
    # --------------------------------------------------------

    quizzes = quizzes.copy()
    users = users.copy()

    quizresults = quizresults.copy()
    userquizdatas = userquizdatas.copy()


    # --------------------------------------------------------
    # CONVERTIR IDS A STRING
    # --------------------------------------------------------

    quizzes["_id"] = (
        quizzes["_id"]
        .astype(str)
    )

    users["_id"] = (
        users["_id"]
        .astype(str)
    )


    if not quizresults.empty:

        quizresults["quiz"] = (
            quizresults["quiz"]
            .astype(str)
        )

        quizresults["user"] = (
            quizresults["user"]
            .astype(str)
        )


    if not userquizdatas.empty:

        userquizdatas["quiz"] = (
            userquizdatas["quiz"]
            .astype(str)
        )

        userquizdatas["user"] = (
            userquizdatas["user"]
            .astype(str)
        )


    # --------------------------------------------------------
    # USUARIOS QUE INICIARON
    #
    # Se obtienen desde userquizdatas
    # --------------------------------------------------------

    if userquizdatas.empty:

        detalle_proceso = pd.DataFrame(
            columns=[
                "quiz_id",
                "_id_user"
            ]
        )

    else:

        detalle_proceso = (
            userquizdatas[
                [
                    "quiz",
                    "user"
                ]
            ]
            .drop_duplicates()
            .rename(
                columns={
                    "quiz": "quiz_id",
                    "user": "_id_user"
                }
            )
        )


    # --------------------------------------------------------
    # USUARIOS QUE COMPLETARON
    # --------------------------------------------------------

    if quizresults.empty:

        detalle_completados = pd.DataFrame(
            columns=[
                "quiz_id",
                "_id_user"
            ]
        )

    else:

        detalle_completados = (
            quizresults[
                [
                    "quiz",
                    "user"
                ]
            ]
            .drop_duplicates()
            .rename(
                columns={
                    "quiz": "quiz_id",
                    "user": "_id_user"
                }
            )
        )


    # --------------------------------------------------------
    # UNIR TODOS LOS USUARIOS
    #
    # Un usuario puede aparecer:
    # - solo en respuestas
    # - solo en resultados
    # - en ambos
    # --------------------------------------------------------

    detalle = pd.concat(
        [
            detalle_proceso,
            detalle_completados
        ],
        ignore_index=True
    ).drop_duplicates()


    # --------------------------------------------------------
    # SI NO HAY USUARIOS
    # --------------------------------------------------------

    if detalle.empty:

        return pd.DataFrame(
            columns=[
                "_id_user",
                "firstName",
                "lastName",
                "quiz_id",
                "quiz_key",
                "quiz_nombre",
                "estado"
            ]
        )


    # --------------------------------------------------------
    # IDENTIFICAR QUIÉNES COMPLETARON
    # --------------------------------------------------------

    completados_set = set(
        zip(
            detalle_completados["quiz_id"],
            detalle_completados["_id_user"]
        )
    )


    # --------------------------------------------------------
    # DETERMINAR ESTADO
    # --------------------------------------------------------

    detalle["estado"] = detalle.apply(
        lambda fila:
        "Completado"
        if (
            fila["quiz_id"],
            fila["_id_user"]
        )
        in completados_set
        else "En proceso",
        axis=1
    )


    # --------------------------------------------------------
    # INFORMACIÓN DEL QUIZ
    # --------------------------------------------------------

    informacion_quizzes = quizzes[
        [
            "_id",
            "key",
            "title"
        ]
    ].copy()

    informacion_quizzes = (
        informacion_quizzes
        .rename(
            columns={
                "_id": "quiz_id",
                "key": "quiz_key",
                "title": "quiz_nombre"
            }
        )
    )


    detalle = detalle.merge(
        informacion_quizzes,
        on="quiz_id",
        how="left"
    )


    # --------------------------------------------------------
    # INFORMACIÓN DEL USUARIO
    # --------------------------------------------------------

    columnas_usuario = [
        "_id"
    ]

    if "firstName" in users.columns:
        columnas_usuario.append(
            "firstName"
        )

    if "lastName" in users.columns:
        columnas_usuario.append(
            "lastName"
        )


    informacion_usuarios = users[
        columnas_usuario
    ].copy()


    informacion_usuarios = (
        informacion_usuarios
        .rename(
            columns={
                "_id": "_id_user"
            }
        )
    )


    # --------------------------------------------------------
    # ASEGURAR COLUMNAS DE NOMBRE
    # --------------------------------------------------------

    if "firstName" not in informacion_usuarios.columns:

        informacion_usuarios[
            "firstName"
        ] = ""


    if "lastName" not in informacion_usuarios.columns:

        informacion_usuarios[
            "lastName"
        ] = ""


    detalle = detalle.merge(
        informacion_usuarios[
            [
                "_id_user",
                "firstName",
                "lastName"
            ]
        ],
        on="_id_user",
        how="left"
    )


    # --------------------------------------------------------
    # LIMPIAR NOMBRES
    # --------------------------------------------------------

    detalle[
        "firstName"
    ] = (
        detalle[
            "firstName"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    detalle[
        "lastName"
    ] = (
        detalle[
            "lastName"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # ORDENAR COLUMNAS
    # --------------------------------------------------------

    detalle = detalle[
        [
            "_id_user",
            "firstName",
            "lastName",
            "quiz_id",
            "quiz_key",
            "quiz_nombre",
            "estado"
        ]
    ]


    # --------------------------------------------------------
    # ORDENAR DATOS
    # --------------------------------------------------------

    detalle = detalle.sort_values(
        by=[
            "quiz_nombre",
            "estado",
            "lastName",
            "firstName"
        ],
        ascending=[
            True,
            True,
            True,
            True
        ]
    )


    detalle = detalle.reset_index(
        drop=True
    )


    return detalle


# ============================================================
# MOSTRAR DATAFRAME
# ============================================================

def mostrar_dataframe(
    df,
    titulo_ventana="Quizzes - DataFrame",
    titulo_tabla="Completación de quizzes"
):

    ventana = tk.Tk()

    ventana.title(
        titulo_ventana
    )

    ventana.geometry(
        "1200x650"
    )


    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    titulo = ttk.Label(
        ventana,
        text=titulo_tabla,
        font=("Segoe UI", 14, "bold")
    )

    titulo.pack(
        pady=10
    )


    # --------------------------------------------------------
    # CONTENEDOR
    # --------------------------------------------------------

    frame = ttk.Frame(
        ventana
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )


    # --------------------------------------------------------
    # TABLA
    # --------------------------------------------------------

    columnas = list(
        df.columns
    )

    tabla = ttk.Treeview(
        frame,
        columns=columnas,
        show="headings"
    )


    # --------------------------------------------------------
    # ENCABEZADOS
    # --------------------------------------------------------

    for columna in columnas:

        tabla.heading(
            columna,
            text=columna
        )

        tabla.column(
            columna,
            width=170
        )


    # --------------------------------------------------------
    # DATOS
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # SCROLL VERTICAL
    # --------------------------------------------------------

    scroll_vertical = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tabla.yview
    )

    tabla.configure(
        yscrollcommand=scroll_vertical.set
    )


    # --------------------------------------------------------
    # SCROLL HORIZONTAL
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # BOTÓN CERRAR
    # --------------------------------------------------------

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
# GUARDAR CSV
# ============================================================

def guardar_csv(
    df,
    ruta
):

    os.makedirs(
        os.path.dirname(ruta),
        exist_ok=True
    )

    df.to_csv(
        ruta,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        "\n✅ CSV guardado en:"
    )

    print(
        ruta
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n" + "=" * 70
    )

    print(
        "🎓 PROCESAMIENTO DE QUIZZES"
    )

    print(
        "=" * 70
    )


    # --------------------------------------------------------
    # CARGAR COLECCIONES
    # --------------------------------------------------------

    (
        quizzes,
        quizresults,
        userquizdatas,
        questions,
        users
    ) = cargar_colecciones()


    print(
        f"\n📚 Quizzes: {len(quizzes)}"
    )

    print(
        f"📊 Resultados: {len(quizresults)}"
    )

    print(
        f"📝 Respuestas: {len(userquizdatas)}"
    )

    print(
        f"❓ Preguntas: {len(questions)}"
    )

    print(
        f"👥 Usuarios: {len(users)}"
    )


    # --------------------------------------------------------
    # PROCESAR RESUMEN
    # --------------------------------------------------------

    resultado = procesar_quizzes(
        quizzes,
        quizresults,
        userquizdatas,
        questions
    )


    if resultado.empty:

        print(
            "\n❌ No se generó información."
        )

        return


    # --------------------------------------------------------
    # OBTENER DETALLE POR USUARIO
    # --------------------------------------------------------

    detalle_usuarios = obtener_detalle_usuarios(
        quizzes,
        quizresults,
        userquizdatas,
        users
    )


    # --------------------------------------------------------
    # RESULTADO RESUMEN
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "📊 RESUMEN FINAL DE QUIZZES"
    )

    print(
        "=" * 70
    )

    print(
        resultado.to_string(
            index=False
        )
    )


    # --------------------------------------------------------
    # RESULTADO DETALLE
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "👥 DETALLE POR USUARIO"
    )

    print(
        "=" * 70
    )

    print(
        f"\nTotal registros: {len(detalle_usuarios)}"
    )


    if not detalle_usuarios.empty:

        print(
            detalle_usuarios.to_string(
                index=False
            )
        )

    else:

        print(
            "\n⚠️ No se encontraron usuarios."
        )


    # --------------------------------------------------------
    # GUARDAR RESUMEN
    # --------------------------------------------------------

    guardar_csv(
        resultado,
        RUTA_SALIDA_RESUMEN
    )


    # --------------------------------------------------------
    # GUARDAR DETALLE
    # --------------------------------------------------------

    guardar_csv(
        detalle_usuarios,
        RUTA_SALIDA_DETALLE
    )


    # --------------------------------------------------------
    # MOSTRAR RESUMEN
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "🪟 ABRIENDO RESUMEN"
    )

    print(
        "=" * 70
    )


    mostrar_dataframe(
        resultado,
        "Quizzes - Resumen",
        "Completación de quizzes"
    )


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    main()