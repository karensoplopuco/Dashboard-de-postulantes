import os
import pandas as pd
from dotenv import load_dotenv
from conexion import db

load_dotenv()

SAMPLE_SIZE = int(os.getenv("SAMPLE_SIZE", 5000))


def cargar_coleccion(nombre):
    print(f"Cargando {nombre}...")

    df = pd.DataFrame(
        list(
            db[nombre]
            .find()
            .limit(SAMPLE_SIZE)
        )
    )

    print(f"{nombre}: {df.shape}")
    return df


# ==========================================
# COLECCIONES
# ==========================================

df_users = cargar_coleccion("users")
df_cvs = cargar_coleccion("cvs")
df_educations = cargar_coleccion("educations")
df_work = cargar_coleccion("workexperiences")
df_companies = cargar_coleccion("companies")
df_jobs = cargar_coleccion("jobs")
df_applications = cargar_coleccion("applications")

df_courseenrollments = cargar_coleccion("courseenrollments")
df_courses = cargar_coleccion("courses")

df_aiconversations = cargar_coleccion("aiconversations")
df_aimessages = cargar_coleccion("aimessages")

df_events = cargar_coleccion("events")
df_eventguests = cargar_coleccion("eventguests")


print("\nTodas las colecciones fueron cargadas correctamente.")