import os
import pandas as pd
from dotenv import load_dotenv
from conexion import db

load_dotenv()

SAMPLE_SIZE = int(os.getenv("SAMPLE_SIZE", 5000))


# ==========================================
# FUNCIÓN PARA CARGAR UNA COLECCIÓN
# ==========================================

def cargar_coleccion(nombre, limite=SAMPLE_SIZE):
    """
    Carga una colección desde MongoDB y realiza
    la limpieza mínima inicial.
    """

    print(f"Cargando {nombre}...")

    df = pd.DataFrame(
        list(
            db[nombre]
            .find()
            .limit(limite)
        )
    )

    # --------------------------
    # Limpieza mínima
    # --------------------------

    if "_id" in df.columns:
        df["_id"] = df["_id"].astype(str)

    df.replace("", pd.NA, inplace=True)

    df.reset_index(drop=True, inplace=True)

    print(f"{nombre}: {df.shape}")

    return df


# ==========================================
# LIMPIEZA DE LLAVES DE RELACIÓN
# ==========================================

def limpiar_tablas(tablas):

    # USERS
    if "_id" in tablas["users"].columns:
        tablas["users"]["_id"] = tablas["users"]["_id"].astype(str)

    # CVS
    if "_id" in tablas["cvs"].columns:
        tablas["cvs"]["_id"] = tablas["cvs"]["_id"].astype(str)

    if "user" in tablas["cvs"].columns:
        tablas["cvs"]["user"] = (
            tablas["cvs"]["user"]
            .fillna("")
            .astype(str)
        )

    # EDUCATIONS
    if "_id" in tablas["educations"].columns:
        tablas["educations"]["_id"] = tablas["educations"]["_id"].astype(str)

    if "cv" in tablas["educations"].columns:
        tablas["educations"]["cv"] = (
            tablas["educations"]["cv"]
            .fillna("")
            .astype(str)
        )

    # WORK EXPERIENCES
    if "_id" in tablas["workexperiences"].columns:
        tablas["workexperiences"]["_id"] = tablas["workexperiences"]["_id"].astype(str)

    if "cv" in tablas["workexperiences"].columns:
        tablas["workexperiences"]["cv"] = (
            tablas["workexperiences"]["cv"]
            .fillna("")
            .astype(str)
        )

    # COMPANIES
    if "_id" in tablas["companies"].columns:
        tablas["companies"]["_id"] = tablas["companies"]["_id"].astype(str)

    # JOBS
    if "_id" in tablas["jobs"].columns:
        tablas["jobs"]["_id"] = tablas["jobs"]["_id"].astype(str)

    if "companyId" in tablas["jobs"].columns:
        tablas["jobs"]["companyId"] = (
            tablas["jobs"]["companyId"]
            .fillna("")
            .astype(str)
        )

    # APPLICATIONS
    if "_id" in tablas["applications"].columns:
        tablas["applications"]["_id"] = tablas["applications"]["_id"].astype(str)

    for columna in ["job", "applicant", "user", "cv"]:

        if columna in tablas["applications"].columns:

            tablas["applications"][columna] = (
                tablas["applications"][columna]
                .fillna("")
                .astype(str)
            )

    return tablas
    
    # COURSE ENROLLMENTS
  

    if "_id" in tablas["courseenrollments"].columns:
        tablas["courseenrollments"]["_id"] = (
            tablas["courseenrollments"]["_id"]
            .astype(str)
        )

    for columna in ["course", "user"]:
        if columna in tablas["courseenrollments"].columns:
            tablas["courseenrollments"][columna] = (
                tablas["courseenrollments"][columna]
                .fillna("")
                .astype(str)
            )

  
    # COURSES
    

    if "_id" in tablas["courses"].columns:
        tablas["courses"]["_id"] = (
            tablas["courses"]["_id"]
            .astype(str)
        )

    if "createdBy" in tablas["courses"].columns:
        tablas["courses"]["createdBy"] = (
            tablas["courses"]["createdBy"]
            .fillna("")
            .astype(str)
        )

    
    # AI CONVERSATIONS
   

    if "_id" in tablas["aiconversations"].columns:
        tablas["aiconversations"]["_id"] = (
            tablas["aiconversations"]["_id"]
            .astype(str)
        )

    if "user" in tablas["aiconversations"].columns:
        tablas["aiconversations"]["user"] = (
            tablas["aiconversations"]["user"]
            .fillna("")
            .astype(str)
        )

   
    # AI MESSAGES
  

    if "_id" in tablas["aimessages"].columns:
        tablas["aimessages"]["_id"] = (
            tablas["aimessages"]["_id"]
            .astype(str)
        )

    for columna in ["conversation", "user"]:
        if columna in tablas["aimessages"].columns:
            tablas["aimessages"][columna] = (
                tablas["aimessages"][columna]
                .fillna("")
                .astype(str)
            )

   
    # EVENTS


    if "_id" in tablas["events"].columns:
        tablas["events"]["_id"] = (
            tablas["events"]["_id"]
            .astype(str)
        )

    if "createdBy" in tablas["events"].columns:
        tablas["events"]["createdBy"] = (
            tablas["events"]["createdBy"]
            .fillna("")
            .astype(str)
        )

    if "communityId" in tablas["events"].columns:
        tablas["events"]["communityId"] = (
            tablas["events"]["communityId"]
            .fillna("")
            .astype(str)
        )

   
    # EVENT GUESTS
    

    if "_id" in tablas["eventguests"].columns:
        tablas["eventguests"]["_id"] = (
            tablas["eventguests"]["_id"]
            .astype(str)
        )

    if "event" in tablas["eventguests"].columns:
        tablas["eventguests"]["event"] = (
            tablas["eventguests"]["event"]
            .fillna("")
            .astype(str)
        )

# ==========================================
# CONSTRUCTOR
# ==========================================

def construir_dataset():

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

    tablas = limpiar_tablas(tablas)

    print("\n✅ Todas las colecciones fueron cargadas y limpiadas correctamente.")

    return tablas


# ==========================================
# PRUEBA DEL CONSTRUCTOR
# ==========================================

if __name__ == "__main__":

    tablas = construir_dataset()

    print("\n========== RESUMEN ==========\n")

    for nombre, df in tablas.items():

        print(f"{nombre}: {df.shape}")