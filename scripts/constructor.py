import os
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from conexion import db

load_dotenv()

SAMPLE_SIZE = int(os.getenv("SAMPLE_SIZE", 5000))

CACHE_DIR = Path("data/cache")

CACHE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ==========================================
# CARGAR COLECCIÓN
# ==========================================

def cargar_coleccion(nombre, limite=SAMPLE_SIZE):

    archivo_cache = CACHE_DIR / f"{nombre}.csv"


    # ==========================
    # LEER CACHE
    # ==========================

    if archivo_cache.exists():

        print(f"📂 Leyendo cache {nombre}...")

        df = pd.read_csv(
            archivo_cache
        )

        print(
            f"{nombre}: {df.shape}"
        )

        return df



    # ==========================
    # CARGAR MONGODB
    # ==========================

    print(f"🌐 Cargando MongoDB {nombre}...")


    df = pd.DataFrame(
        list(
            db[nombre]
            .find()
            .limit(limite)
        )
    )


    if "_id" in df.columns:

        df["_id"] = (
            df["_id"]
            .astype(str)
        )


    df.replace(
        "",
        pd.NA,
        inplace=True
    )


    df.reset_index(
        drop=True,
        inplace=True
    )


    # ==========================
    # GUARDAR CACHE
    # ==========================

    df.to_csv(
        archivo_cache,
        index=False,
        encoding="utf-8"
    )


    print(
        f"💾 Cache creado: {archivo_cache}"
    )


    print(
        f"{nombre}: {df.shape}"
    )



    return df



# ==========================================
# LIMPIEZA DE LLAVES
# ==========================================

def limpiar_tablas(tablas):

    relaciones = {

        "users": [
            "_id"
        ],

        "cvs": [
            "_id",
            "user"
        ],

        "educations": [
            "_id",
            "cv"
        ],

        "workexperiences": [
            "_id",
            "cv"
        ],

        "companies": [
            "_id"
        ],

        "jobs": [
            "_id",
            "companyId"
        ],

        "applications": [
            "_id",
            "job",
            "user",
            "cv",
            "applicant"
        ],

        "courseenrollments": [
            "_id",
            "user",
            "course"
        ],

        "courses": [
            "_id",
            "createdBy"
        ],

        "aiconversations": [
            "_id",
            "user"
        ],

        "aimessages": [
            "_id",
            "user",
            "conversation"
        ],

        "events": [
            "_id",
            "createdBy"
        ],

        "eventguests": [
            "_id",
            "event",
            "userEmail"
        ]
    }


    for tabla, columnas in relaciones.items():

        for columna in columnas:

            if columna in tablas[tabla].columns:

                tablas[tabla][columna] = (
                    tablas[tabla][columna]
                    .fillna("")
                    .astype(str)
                )


    return tablas

# ==========================================
# CONSTRUCTOR
# ==========================================

def construir_dataset():


    # ==========================
    # CARGAR TABLAS
    # ==========================

    tablas = {

        "users": cargar_coleccion("users"),

        "cvs": cargar_coleccion("cvs"),

        "educations": cargar_coleccion("educations"),

        "workexperiences": cargar_coleccion("workexperiences"),

        "companies": cargar_coleccion("companies"),

        "jobs": cargar_coleccion("jobs"),

        "applications": cargar_coleccion("applications"),

        "courseenrollments": cargar_coleccion("courseenrollments"),

        "courses": cargar_coleccion("courses"),

        "aiconversations": cargar_coleccion("aiconversations"),

        "aimessages": cargar_coleccion("aimessages"),

        "events": cargar_coleccion("events"),

        "eventguests": cargar_coleccion("eventguests")
    }


    # ==========================
    # LIMPIEZA
    # ==========================

    tablas = limpiar_tablas(tablas)



    # ==========================================
    # MERGES GENERALES
    # ==========================================


    # USERS + CVS

    df_users_cv = pd.merge(
        tablas["users"],
        tablas["cvs"],
        left_on="_id",
        right_on="user",
        how="left",
        suffixes=("_user", "_cv")
    )



    # CVS + EDUCATIONS

    df_cvs_education = pd.merge(
        tablas["cvs"],
        tablas["educations"],
        left_on="_id",
        right_on="cv",
        how="left",
        suffixes=("_cv", "_education")
    )



    # CVS + WORK EXPERIENCES

    df_cvs_work = pd.merge(
        tablas["cvs"],
        tablas["workexperiences"],
        left_on="_id",
        right_on="cv",
        how="left",
        suffixes=("_cv", "_work")
    )



    # APPLICATIONS + JOBS

    df_applications_jobs = pd.merge(
        tablas["applications"],
        tablas["jobs"],
        left_on="job",
        right_on="_id",
        how="left",
        suffixes=("_application", "_job")
    )



    # APPLICATIONS + USERS

    df_applications_users = pd.merge(
        tablas["applications"],
        tablas["users"],
        left_on="user",
        right_on="_id",
        how="left",
        suffixes=("_application", "_user")
    )



    # ==========================================
    # DATASET POSTULANTES
    # ==========================================


    df_postulantes_final = tablas["users"].copy()



    # POSTULANTES + CV

    df_postulantes_cv = pd.merge(
        df_postulantes_final,
        tablas["cvs"],
        left_on="_id",
        right_on="user",
        how="left",
        suffixes=("_postulante", "_cv")
    )



    # POSTULANTES + EDUCACION

    df_postulantes_education = pd.merge(
        df_postulantes_cv,
        tablas["educations"],
        left_on="_id_cv",
        right_on="cv",
        how="left",
        suffixes=("", "_education")
    )



    # POSTULANTES + EXPERIENCIA

    df_postulantes_work = pd.merge(
        df_postulantes_cv,
        tablas["workexperiences"],
        left_on="_id_cv",
        right_on="cv",
        how="left",
        suffixes=("", "_work")
    )



    # ==========================================
    # CURSOS
    # ==========================================


    cursos_usuario = (
        tablas["courseenrollments"]
        .groupby("user")
        .agg(
            cantidad_cursos=("course", "count")
        )
        .reset_index()
    )


    df_postulantes_cursos = pd.merge(
        df_postulantes_work,
        cursos_usuario,
        left_on="_id",
        right_on="user",
        how="left"
    )


    df_postulantes_cursos["cantidad_cursos"] = (
        df_postulantes_cursos["cantidad_cursos"]
        .fillna(0)
        .astype(int)
    )



    # ==========================================
    # USO DE IA
    # ==========================================


    usuarios_ia = pd.concat(
        [
            tablas["aiconversations"][["user"]],
            tablas["aimessages"][["user"]]
        ],
        ignore_index=True
    )


    usuarios_ia = (
        usuarios_ia
        .drop_duplicates()
        .assign(uso_ia=True)
    )


    df_postulantes_ia = pd.merge(
        df_postulantes_cursos,
        usuarios_ia,
        left_on="_id",
        right_on="user",
        how="left"
    )


    df_postulantes_ia["uso_ia"] = (
        df_postulantes_ia["uso_ia"]
        .fillna(False)
    )



    # ==========================================
    # EVENTOS
    # ==========================================


    eventos_usuario = tablas["eventguests"][
        [
            "event",
            "userEmail",
            "status",
            "registrationDate"
        ]
    ].copy()



    df_postulantes_eventos = pd.merge(
        df_postulantes_ia,
        eventos_usuario,
        left_on="email_postulante",
        right_on="userEmail",
        how="left"
    )

    df_postulantes_dashboard = (
        df_postulantes_eventos
        .groupby("_id_postulante", as_index=False)
        .agg(
             email=("email_postulante","first"),
             nombre=("firstName_postulante","first"),
             apellido=("lastName_postulante","first"),
             ubicacion=("location_postulante","first"),
              profesion=("profession","first"),
              tiene_cv=("_id_cv", lambda x: x.notna().any()),
              cantidad_cursos=("cantidad_cursos","max"),
              uso_ia=("uso_ia","max"),
              cantidad_eventos=("event","count")
              )
        )

    df_postulantes_dashboard["participo_evento"] = (
        df_postulantes_dashboard["cantidad_eventos"] > 0
        )

    # GUARDAR DATASET DASHBOARD EN CACHE

    df_postulantes_dashboard.to_csv(
         CACHE_DIR / "postulantes_dashboard.csv",
         index=False,
         encoding="utf-8"

    )

    print(
        "💾 Cache dashboard creado"

    )











    print(
         "Dataset dashboard postulantes:",
         df_postulantes_dashboard.shape

         )




        # ==========================================
    # VALIDACIONES
    # ==========================================

    print("\n========== RESULTADOS MERGES ==========")

    print("Usuarios + CV:", df_users_cv.shape)

    print("CV + Educación:", df_cvs_education.shape)

    print("CV + Experiencia:", df_cvs_work.shape)

    print("Applications + Jobs:", df_applications_jobs.shape)

    print("Applications + Users:", df_applications_users.shape)

    print("Postulantes + CV:", df_postulantes_cv.shape)

    print("Postulantes + Educación:", df_postulantes_education.shape)

    print("Postulantes + Experiencia:", df_postulantes_work.shape)

    print("Postulantes + Cursos:", df_postulantes_cursos.shape)

    print("Postulantes + IA:", df_postulantes_ia.shape)

    print("Postulantes + Eventos:", df_postulantes_eventos.shape)



    print("\n✅ Constructor terminado correctamente")



    # ==========================================
    # RETORNO
    # ==========================================

    return {


        # TABLAS ORIGINALES

        "users": tablas["users"],

        "cvs": tablas["cvs"],

        "educations": tablas["educations"],

        "workexperiences": tablas["workexperiences"],

        "companies": tablas["companies"],

        "jobs": tablas["jobs"],

        "applications": tablas["applications"],

        "courseenrollments": tablas["courseenrollments"],

        "courses": tablas["courses"],

        "aiconversations": tablas["aiconversations"],

        "aimessages": tablas["aimessages"],

        "events": tablas["events"],

        "eventguests": tablas["eventguests"],

        "postulantes_dashboard": df_postulantes_dashboard,



        # MERGES GENERALES

        "users_cv": df_users_cv,

        "cvs_education": df_cvs_education,

        "cvs_work": df_cvs_work,

        "applications_jobs": df_applications_jobs,

        "applications_users": df_applications_users,



        # DATASET DASHBOARD POSTULANTES

        "postulantes_cv": df_postulantes_cv,

        "postulantes_education": df_postulantes_education,

        "postulantes_work": df_postulantes_work,

        "postulantes_cursos": df_postulantes_cursos,

        "postulantes_ia": df_postulantes_ia,

        "postulantes_eventos": df_postulantes_eventos

    }



# ==========================================
# EJECUCIÓN DE PRUEBA
# ==========================================

if __name__ == "__main__":


    tablas = construir_dataset()


    print("\n========== RESUMEN FINAL ==========\n")


    for nombre, df in tablas.items():

        print(f"{nombre}: {df.shape}")




# ==========================================
    # VALIDACIÓN DATASET DASHBOARD
    # ==========================================

    df = tablas["postulantes_dashboard"]

    print("\n========== VALIDACIÓN POSTULANTES DASHBOARD ==========")

    print("\nDimensiones:")
    print(df.shape)

    print("\nUsuarios únicos:")
    print(df["_id_postulante"].nunique())

    print("\nDuplicados:")
    print(df["_id_postulante"].duplicated().sum())

    print("\nColumnas:")
    print(df.columns.tolist())