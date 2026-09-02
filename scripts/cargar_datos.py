import os
import pandas as pd
from dotenv import load_dotenv
from conexion import db

from transformaciones import (
    transformar_users,
    transformar_cvs,
    transformar_educacion,
    transformar_experiencia
)

from cruces import realizar_cruces


# ============================================================
# CONFIGURACIÓN
# ============================================================

load_dotenv()

SAMPLE_SIZE = int(os.getenv("SAMPLE_SIZE", 5000))


# ============================================================
# CARGAR UNA COLECCIÓN
# ============================================================

def cargar_coleccion(nombre):

    print(f"📥 Cargando {nombre}...")

    try:

        df = pd.DataFrame(
            list(
                db[nombre]
                .find()
                .limit(SAMPLE_SIZE)
            )
        )

        print(f"✅ {nombre}: {df.shape}")

        return df

    except Exception as e:

        print(f"❌ Error cargando {nombre}: {e}")

        return pd.DataFrame()


# ============================================================
# CARGAR TODAS LAS COLECCIONES
# ============================================================

def cargar_todas_las_colecciones():

    colecciones = [
        "users",
        "cvs",
        "educations",
        "workexperiences",
        "companies",
        "jobs",
        "applications",
        "courseenrollments",
        "courses",
        "aiconversations",
        "aimessages",
        "events",
        "eventguests",
        "employabilities",
        "jobcompatibilityanalyses",
        "usercredits",
        "creditoperations"
    ]

    datos = {}

    print("\n" + "=" * 60)
    print("CARGANDO COLECCIONES DE MONGODB")
    print("=" * 60)

    for nombre in colecciones:

        datos[nombre] = cargar_coleccion(nombre)

    print("\n✅ Todas las colecciones fueron cargadas correctamente.")

    return datos


# ============================================================
# PROCESAR DATOS
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # CARGAR DATOS
    # --------------------------------------------------------

    datos = cargar_todas_las_colecciones()


    # --------------------------------------------------------
    # TRANSFORMAR USERS
    # --------------------------------------------------------

    df_users = transformar_users(
        datos["users"]
    )


    # --------------------------------------------------------
    # TRANSFORMAR CVS
    # --------------------------------------------------------

    df_cvs = transformar_cvs(
        datos["cvs"]
    )


    # --------------------------------------------------------
    # TRANSFORMAR EDUCACIÓN
    # --------------------------------------------------------

    df_educations = transformar_educacion(
        datos["educations"]
    )


    # --------------------------------------------------------
    # TRANSFORMAR EXPERIENCIA
    # --------------------------------------------------------

    df_work = transformar_experiencia(
        datos["workexperiences"]
    )


    # ========================================================
    # REALIZAR CRUCES
    # ========================================================

    cruces = realizar_cruces(
        df_users=df_users,
        df_cvs=df_cvs,
        df_educations=df_educations,
        df_work=df_work,
        df_applications=datos["applications"]
    )


    # ========================================================
    # GUARDAR RESULTADOS DE LOS CRUCES
    # ========================================================

    df_users_cv = cruces["users_cv"]

    df_users_education = cruces["users_education"]

    df_users_work = cruces["users_work"]

    df_applications_users = cruces["applications_users"]


    # ========================================================
    # RESULTADOS
    # ========================================================

    print("\n" + "=" * 60)
    print("TRANSFORMACIONES COMPLETADAS")
    print("=" * 60)

    print("Users:", df_users.shape)
    print("CVs:", df_cvs.shape)
    print("Educación:", df_educations.shape)
    print("Experiencia:", df_work.shape)


    print("\n" + "=" * 60)
    print("CRUCES COMPLETADOS")
    print("=" * 60)

    print("Users + CVs:", df_users_cv.shape)

    print(
        "Users + Educación:",
        df_users_education.shape
    )

    print(
        "Users + Experiencia:",
        df_users_work.shape
    )

    print(
        "Applications + Users:",
        df_applications_users.shape
    )