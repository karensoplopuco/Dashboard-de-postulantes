# ============================================================
# scripts/explorar_quizzes.py
# EXPLORACIÓN DE DATOS DE QUIZZES
# ============================================================

print("🚀 explorar_quizzes.py se está ejecutando")
import pandas as pd

from scripts.conexion import db


# ============================================================
# CONFIGURACIÓN
# ============================================================

COLECCIONES = [
    "quizzes",
    "quizresults",
    "userquizdatas",
    "questions"
]


# ============================================================
# FUNCIÓN PARA MOSTRAR COLECCIÓN
# ============================================================

def explorar_coleccion(nombre_coleccion):

    print("\n")
    print("=" * 70)
    print(f"📚 COLECCIÓN: {nombre_coleccion}")
    print("=" * 70)

    try:

        coleccion = db[nombre_coleccion]

        documentos = list(
            coleccion.find({})
        )

        if not documentos:

            print("⚠️ La colección está vacía.")
            return

        df = pd.DataFrame(documentos)

        print(f"\n📊 Registros: {len(df):,}")
        print(f"📐 Dimensiones: {df.shape}")

        print("\n📋 COLUMNAS:")
        for columna in df.columns:

            print(
                f"   - {columna}"
                f" → {df[columna].dtype}"
            )

        print("\n🔎 PRIMEROS 5 REGISTROS:")

        with pd.option_context(
            "display.max_columns", None,
            "display.max_colwidth", 80,
            "display.width", 200
        ):

            print(
                df.head(5).to_string(
                    index=False
                )
            )

        print("\n🔑 CAMPOS RELACIONADOS CON QUIZ:")

        palabras_quiz = [
            "quiz",
            "question",
            "result",
            "answer",
            "score",
            "complete",
            "completed",
            "status",
            "progress",
            "user"
        ]

        encontrados = []

        for columna in df.columns:

            columna_lower = str(
                columna
            ).lower()

            if any(
                palabra in columna_lower
                for palabra in palabras_quiz
            ):

                encontrados.append(
                    columna
                )

        if encontrados:

            for columna in encontrados:

                print(
                    f"   ⭐ {columna}"
                )

        else:

            print(
                "   No se encontraron "
                "campos relacionados."
            )

    except Exception as e:

        print(
            f"❌ Error explorando "
            f"{nombre_coleccion}: {e}"
        )


# ============================================================
# EJECUCIÓN
# ============================================================

def main():

    print("=" * 70)
    print("🔍 EXPLORADOR DE QUIZZES")
    print("=" * 70)

    print(
        "\n📚 Colecciones que se analizarán:"
    )

    for coleccion in COLECCIONES:

        print(
            f"   - {coleccion}"
        )

    # --------------------------------------------------------
    # EXPLORAR CADA COLECCIÓN
    # --------------------------------------------------------

    for nombre_coleccion in COLECCIONES:

        explorar_coleccion(
            nombre_coleccion
        )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("✅ EXPLORACIÓN TERMINADA")
    print("=" * 70)


if __name__ == "__main__":

    main()