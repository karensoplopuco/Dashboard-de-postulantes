# ============================================================
# CRUCE BCP -> COLECCIÓN CVS
# ============================================================
#
# Busca participantes BCP directamente en MongoDB, colección:
#
#     cvs
#
# Campos utilizados:
#     email
#     firstName
#     lastName
#     profession
#
# Estrategia:
#
# 1. Coincidencia por email normalizado.
# 2. Si no existe, coincidencia por firstName + lastName.
#
# NO utiliza postulantes_individual.csv
# NO utiliza coincidencias aproximadas.
#
# ============================================================

import re
import unicodedata
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv

# ============================================================
# CONEXIÓN DEL PROYECTO
# ============================================================

try:

    from conexion import (
        get_db,
        comprobar_conexion,
    )

except ImportError:

    from scripts.conexion import (
        get_db,
        comprobar_conexion,
    )


# ============================================================
# CONFIGURACIÓN
# ============================================================

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = BASE_DIR / ".env"

DATA_DIR = BASE_DIR / "data"

ARCHIVO_SALIDA = (
    DATA_DIR
    / "cache"
    / "carreras_bcp.xlsx"
)

load_dotenv(
    dotenv_path=ENV_PATH
)


# ============================================================
# PARTICIPANTES BCP
# ============================================================

PARTICIPANTES_BCP = [

    {
        "email": "dochoafab@gmail.com",
        "nombre": "Daniela Fabiana Ochoa Chumbiauca",
    },

    {
        "email": "zaratefranco77@gmail.com",
        "nombre": "Franco Gallardo",
    },

    {
        "email": "martinez.sanchezmle@gmail.com",
        "nombre": "Maximo Martinez",
    },

    {
        "email": "melinabaluarte@gmail.com",
        "nombre": "Melina Baluarte",
    },

    {
        "email": "miguelangel.cecairosl@gmail.com",
        "nombre": "Miguel Angel Cecairos",
    },

    {
        "email": "iraidayzaciga180706@gmail.com",
        "nombre": "Andrea Iraida Yzaciga De Los Santos",
    },

    {
        "email": "nikole.ale05@gmail.com",
        "nombre": "Nikole Rodriguez Saravia",
    },

    {
        "email": "jcirilo137@gmail.com",
        "nombre": "Julio Alonso Cirilo Mel",
    },

    {
        "email": "rvgi110606@gmail.com",
        "nombre": "Rai Garcia",
    },

    {
        "email": "enzo.espinoza.a@uni.pe",
        "nombre": "Enzo Joan Espinoza Armas",
    },

    {
        "email": "orevalverdeaaronpablo@gmail.com",
        "nombre": "Aaron Pablo Ore Valverde",
    },

    {
        "email": "matiasantoniotrujillo@gmail.com",
        "nombre": "Matias Antonio Trujillo Godoy",
    },

    {
        "email": "juanavls62@gmail.com",
        "nombre": "Juana Victoria Lopez Saenz",
    },

    {
        "email": "matiaz.chevez.c@uni.pe",
        "nombre": "MATIAZ ENRIQUE CHEVEZ COLLAHUACHO",
    },

    {
        "email": "camila.tapia0608@gmail.com",
        "nombre": "Camila Tapia Arévalo",
    },

    {
        "email": "michaellpalacios2000@gmail.com",
        "nombre": "Michaell Palacios",
    },

    {
        "email": "josephrgr2716@gmail.com",
        "nombre": "Joseph Sin apellido",
    },

    {
        "email": "isaacmachucaperez@gmail.com",
        "nombre": "Machuca Perez Isaac Martín",
    },

    {
        "email": "joseph.barja28@gmail.com",
        "nombre": "Joseph Barja",
    },

    {
        "email": "ruben.cornejo.a@uni.pe",
        "nombre": "RUBEN ALESSANDRO CORNEJO AZAÑA",
    },

    {
        "email": "antwnyab@gmail.com",
        "nombre": "Antony A.",
    },

    {
        "email": "alonsoolizarate21@gmail.com",
        "nombre": "Alonso Suraj Oli Zárate",
    },

    {
        "email": "isatamani.design@gmail.com",
        "nombre": "Isa Tamani",
    },

    {
        "email": "sebasrc1901@gmail.com",
        "nombre": "Sebastian Santiago Rivera Camargo",
    },

    {
        "email": "tiradommario@gmail.com",
        "nombre": "Mario Tirado Malca",
    },

    {
        "email": "angelinaconcepcion159@gmail.com",
        "nombre": "Angelina Concepcion",
    },

    {
        "email": "sabrinajrb200105@gmail.com",
        "nombre": "Jennyfer Sabrina Rojas Bayona",
    },

    {
        "email": "claudia.anchantele@gmail.com",
        "nombre": "Claudia Anchante",
    },

    {
        "email": "jefferson.figueroa@utec.edu.pe",
        "nombre": "Jefferson Jandet Figueroa Perez",
    },

    {
        "email": "jose.tincopa@tecsup.edu.pe",
        "nombre": "Jose Luis Tincopa Paz",
    },

    {
        "email": "karlahuarcayacar@gmail.com",
        "nombre": "Karla Huarcaya Carpio",
    },

    {
        "email": "angeligabrielarojasvilela@gmail.com",
        "nombre": "Angeli Gabriela Rojas Vilela",
    },

    {
        "email": "meljovitmw26@gmail.com",
        "nombre": "Meljovit Wholker Riofano Avellaneda",
    },

    {
        "email": "danielfrancocrispin@gmail.com",
        "nombre": "Daniel Crispín Ramos",
    },

    {
        "email": "emirgodinezv23@gmail.com",
        "nombre": "Emir Godinez",
    },

    {
        "email": "sandyallaucaramos@gmail.com",
        "nombre": "Sandy Allauca",
    },

    {
        "email": "gimena.pastorh@gmail.com",
        "nombre": "Gimena Pastor Herhuay",
    },

    {
        "email": "kelly.carhuancho@utec.edu.pe",
        "nombre": "Kelly Shirley Carhuancho Mayta",
    },

    {
        "email": "alejandrololofa@gmail.com",
        "nombre": "Alejandro Lolo Fernandez Acaro",
    },

    {
        "email": "josuecallirgosrojas@gmail.com",
        "nombre": "Josué Abraham Callirgos Rojas",
    },

    {
        "email": "alex.casapaico@tecsup.edu.pe",
        "nombre": "Alex Luis Casapaico Aquino",
    },

    {
        "email": "fesc1198@gmail.com",
        "nombre": "Frank Sanchez",
    },

    {
        "email": "melissaimannoriega@gmail.com",
        "nombre": "Melissa Iman Noriega",
    },

    {
        "email": "frankli.zena.z@uni.pe",
        "nombre": "FRANKLI ZEÑA ZEÑA",
    },

    {
        "email": "jose.aronic21@gmail.com",
        "nombre": "José Maria Antonio Aroni Cardenas",
    },

    {
        "email": "ahenrypriveros@gmail.com",
        "nombre": "Anthony Ponte",
    },

    {
        "email": "sanchezaldazabalsalvatore@gmail.com",
        "nombre": "Salvatore Smith Sánchez Aldazabal",
    },

    {
        "email": "cristianvillegas000@gmail.com",
        "nombre": "Cristian Villegas",
    },

    {
        "email": "miguelvalenciacorrea2023@gmail.com",
        "nombre": "Miguel Angel Gabriel Valencia Correa",
    },

    {
        "email": "yunior.borjas@unmsm.edu.pe",
        "nombre": "Yunior Borjas",
    },

    {
        "email": "quispevasquezfiorela@gmail.com",
        "nombre": "Fiorela Quispe Vasquez",
    },

]


# ============================================================
# NORMALIZAR TEXTO
# ============================================================

def normalizar_texto(valor):

    """
    Normaliza nombres y apellidos.

    Ejemplo:

        "José María"
            ->
        "jose maria"

    También elimina tildes y espacios repetidos.
    """

    if valor is None:
        return ""

    try:

        if pd.isna(valor):
            return ""

    except Exception:

        pass

    texto = str(valor).strip().lower()

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = "".join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# ============================================================
# NORMALIZAR EMAIL
# ============================================================

def normalizar_email(valor):

    if valor is None:
        return ""

    try:

        if pd.isna(valor):
            return ""

    except Exception:

        pass

    return str(valor).strip().lower()


# ============================================================
# SEPARAR NOMBRE COMPLETO
# ============================================================

def separar_nombre(nombre_completo):

    """
    Convierte:

        Daniela Fabiana Ochoa Chumbiauca

    en:

        firstName = Daniela
        lastName  = Fabiana Ochoa Chumbiauca

    Para los casos normales de 2 palabras:

        Franco Gallardo

        firstName = Franco
        lastName  = Gallardo

    """

    nombre = normalizar_texto(
        nombre_completo
    )

    partes = nombre.split()

    if len(partes) == 0:

        return "", ""

    if len(partes) == 1:

        return partes[0], ""

    first_name = partes[0]

    last_name = " ".join(
        partes[1:]
    )

    return (
        first_name,
        last_name
    )


# ============================================================
# PREPARAR NOMBRE BCP
# ============================================================

def preparar_nombre_bcp(
    nombre_completo
):

    """
    Genera diferentes formas para comparar
    nombre y apellido.

    """

    nombre_normalizado = normalizar_texto(
        nombre_completo
    )

    partes = nombre_normalizado.split()

    if not partes:

        return {
            "nombre_normalizado": "",
            "first_name": "",
            "last_name": "",
            "tokens": set(),
        }

    first_name = partes[0]

    last_name = " ".join(
        partes[1:]
    )

    return {
        "nombre_normalizado": nombre_normalizado,
        "first_name": first_name,
        "last_name": last_name,
        "tokens": set(partes),
    }


# ============================================================
# CONEXIÓN MONGODB
# ============================================================

def conectar_mongodb():

    print("\n" + "=" * 70)
    print("CONEXIÓN A MONGODB")
    print("=" * 70)

    print("\nComprobando conexión...")

    resultado = comprobar_conexion()

    if not resultado:

        raise ConnectionError(
            "No se pudo comprobar la conexión con MongoDB."
        )

    print(
        "[OK] MongoDB conectado correctamente"
    )

    db = get_db()

    print(
        f"[OK] Base de datos: {db.name}"
    )

    return db


# ============================================================
# COMPROBAR COLECCIÓN CVS
# ============================================================

def obtener_coleccion_cvs(db):

    colecciones = db.list_collection_names()

    print("\nColecciones disponibles:")

    for nombre in colecciones:

        print(
            f" - {nombre}"
        )

    if "cvs" not in colecciones:

        raise ValueError(
            "\nNo existe la colección 'cvs' en MongoDB."
        )

    print(
        "\n[OK] Colección 'cvs' encontrada"
    )

    return db["cvs"]


# ============================================================
# LEER CVS
# ============================================================

def cargar_cvs(collection):

    print("\n" + "=" * 70)
    print("LEYENDO COLECCIÓN CVS")
    print("=" * 70)

    projection = {

        "_id": 1,

        "email": 1,

        "firstName": 1,

        "lastName": 1,

        "profession": 1,

    }

    documentos = list(
        collection.find(
            {},
            projection
        )
    )

    print(
        f"\nRegistros encontrados en cvs: "
        f"{len(documentos):,}"
    )

    if not documentos:

        raise ValueError(
            "La colección 'cvs' no contiene registros."
        )

    df = pd.DataFrame(
        documentos
    )

    print("\nColumnas encontradas:")

    for numero, columna in enumerate(
        df.columns,
        start=1
    ):

        print(
            f"{numero:02d}. {columna}"
        )

    columnas_obligatorias = [
        "email",
        "firstName",
        "lastName",
        "profession",
    ]

    faltantes = [
        columna
        for columna in columnas_obligatorias
        if columna not in df.columns
    ]

    if faltantes:

        raise ValueError(
            "\nFaltan columnas obligatorias "
            f"en cvs: {faltantes}"
        )

    return df


# ============================================================
# PREPARAR CVS
# ============================================================

def preparar_cvs(df):

    print("\n" + "=" * 70)
    print("PREPARANDO ÍNDICES DE CVS")
    print("=" * 70)

    df = df.copy()

    # --------------------------------------------------------
    # Email normalizado
    # --------------------------------------------------------

    df["email_normalizado"] = (
        df["email"]
        .apply(normalizar_email)
    )

    # --------------------------------------------------------
    # Nombre normalizado
    # --------------------------------------------------------

    df["firstName_normalizado"] = (
        df["firstName"]
        .apply(normalizar_texto)
    )

    df["lastName_normalizado"] = (
        df["lastName"]
        .apply(normalizar_texto)
    )

    df["nombre_completo_normalizado"] = (
        df["firstName_normalizado"]
        + " "
        + df["lastName_normalizado"]
    ).str.strip()

    # --------------------------------------------------------
    # Índice por email
    # --------------------------------------------------------

    indice_email = {}

    for _, fila in df.iterrows():

        email = fila[
            "email_normalizado"
        ]

        if not email:
            continue

        if email not in indice_email:

            indice_email[email] = []

        indice_email[email].append(
            fila
        )

    # --------------------------------------------------------
    # Índice por nombre + apellido
    # --------------------------------------------------------

    indice_nombre = {}

    for _, fila in df.iterrows():

        first_name = fila[
            "firstName_normalizado"
        ]

        last_name = fila[
            "lastName_normalizado"
        ]

        if not first_name or not last_name:
            continue

        clave = (
            first_name,
            last_name
        )

        if clave not in indice_nombre:

            indice_nombre[clave] = []

        indice_nombre[clave].append(
            fila
        )

    print(
        f"\nÍndice de emails: "
        f"{len(indice_email):,}"
    )

    print(
        f"Índice nombre + apellido: "
        f"{len(indice_nombre):,}"
    )

    return (
        df,
        indice_email,
        indice_nombre
    )


# ============================================================
# BUSCAR PARTICIPANTE
# ============================================================

def buscar_participante(
    participante,
    indice_email,
    indice_nombre
):

    email_bcp = normalizar_email(
        participante["email"]
    )

    datos_nombre = preparar_nombre_bcp(
        participante["nombre"]
    )

    first_name_bcp = (
        datos_nombre["first_name"]
    )

    last_name_bcp = (
        datos_nombre["last_name"]
    )

    # ========================================================
    # 1. BUSCAR POR EMAIL
    # ========================================================

    candidatos_email = indice_email.get(
        email_bcp,
        []
    )

    if candidatos_email:

        # Si existe exactamente un registro
        if len(candidatos_email) == 1:

            fila = candidatos_email[0]

            return {
                "fila": fila,
                "metodo": "EMAIL",
                "confianza": "ALTA",
            }

        # ----------------------------------------------------
        # Si hay varios emails iguales, intentamos
        # confirmar mediante nombre.
        # ----------------------------------------------------

        for fila in candidatos_email:

            first_name_cvs = normalizar_texto(
                fila.get("firstName")
            )

            last_name_cvs = normalizar_texto(
                fila.get("lastName")
            )

            if (
                first_name_cvs
                == first_name_bcp
                and
                last_name_cvs
                == last_name_bcp
            ):

                return {
                    "fila": fila,
                    "metodo": "EMAIL + NOMBRE_APELLIDO",
                    "confianza": "ALTA",
                }

        # Si email existe pero hay duplicados
        # y no pudimos resolver por nombre,
        # tomamos el primero pero lo marcamos.

        return {
            "fila": candidatos_email[0],
            "metodo": "EMAIL_DUPLICADO",
            "confianza": "MEDIA",
        }

    # ========================================================
    # 2. BUSCAR POR NOMBRE + APELLIDO
    # ========================================================

    if first_name_bcp and last_name_bcp:

        clave_nombre = (
            first_name_bcp,
            last_name_bcp
        )

        candidatos_nombre = (
            indice_nombre.get(
                clave_nombre,
                []
            )
        )

        if candidatos_nombre:

            if len(candidatos_nombre) == 1:

                return {
                    "fila": candidatos_nombre[0],
                    "metodo": "NOMBRE_APELLIDO",
                    "confianza": "ALTA",
                }

            # Si hay más de uno, intentamos
            # encontrar coincidencia adicional
            # por email.

            for fila in candidatos_nombre:

                email_cvs = normalizar_email(
                    fila.get("email")
                )

                if email_cvs == email_bcp:

                    return {
                        "fila": fila,
                        "metodo": "EMAIL + NOMBRE_APELLIDO",
                        "confianza": "ALTA",
                    }

            return {
                "fila": candidatos_nombre[0],
                "metodo": "NOMBRE_APELLIDO_DUPLICADO",
                "confianza": "MEDIA",
            }

    # ========================================================
    # 3. NO ENCONTRADO
    # ========================================================

    return None


# ============================================================
# REALIZAR CRUCE
# ============================================================

def realizar_cruce(
    participantes,
    indice_email,
    indice_nombre
):

    print("\n" + "=" * 70)
    print("REALIZANDO CRUCE BCP -> CVS")
    print("=" * 70)

    resultados = []

    encontrados = []

    no_encontrados = []

    for participante in participantes:

        resultado = buscar_participante(
            participante,
            indice_email,
            indice_nombre
        )

        if resultado is None:

            registro = {

                "email_bcp": participante["email"],

                "nombre_bcp": participante["nombre"],

                "email_cvs": "",

                "firstName_cvs": "",

                "lastName_cvs": "",

                "profession": "",

                "metodo_cruce": "NO ENCONTRADO",

                "confianza": "",

                "encontrado": False,

            }

            no_encontrados.append(
                registro
            )

            resultados.append(
                registro
            )

            continue

        fila = resultado["fila"]

        registro = {

            "email_bcp": participante["email"],

            "nombre_bcp": participante["nombre"],

            "email_cvs": fila.get(
                "email",
                ""
            ),

            "firstName_cvs": fila.get(
                "firstName",
                ""
            ),

            "lastName_cvs": fila.get(
                "lastName",
                ""
            ),

            "profession": fila.get(
                "profession",
                ""
            ),

            "metodo_cruce": resultado[
                "metodo"
            ],

            "confianza": resultado[
                "confianza"
            ],

            "encontrado": True,

        }

        encontrados.append(
            registro
        )

        resultados.append(
            registro
        )

    df_resultado = pd.DataFrame(
        resultados
    )

    df_encontrados = pd.DataFrame(
        encontrados
    )

    df_no_encontrados = pd.DataFrame(
        no_encontrados
    )

    return (
        df_resultado,
        df_encontrados,
        df_no_encontrados
    )


# ============================================================
# MOSTRAR RESUMEN
# ============================================================

def mostrar_resumen(
    participantes,
    df_encontrados,
    df_no_encontrados
):

    total = len(
        participantes
    )

    encontrados = len(
        df_encontrados
    )

    no_encontrados = len(
        df_no_encontrados
    )

    porcentaje = (
        encontrados / total * 100
        if total
        else 0
    )

    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)

    print(
        f"\nParticipantes BCP:       {total:,}"
    )

    print(
        f"Encontrados en cvs:      {encontrados:,}"
    )

    print(
        f"No encontrados:           {no_encontrados:,}"
    )

    print(
        f"Porcentaje encontrado:    {porcentaje:.2f}%"
    )

    # --------------------------------------------------------
    # Métodos
    # --------------------------------------------------------

    if not df_encontrados.empty:

        print(
            "\nMétodos de coincidencia:"
        )

        conteo = (
            df_encontrados[
                "metodo_cruce"
            ]
            .value_counts()
        )

        for metodo, cantidad in conteo.items():

            print(
                f"  - {metodo}: {cantidad}"
            )


# ============================================================
# MOSTRAR ENCONTRADOS
# ============================================================

def mostrar_encontrados(
    df_encontrados
):

    print("\n" + "=" * 70)
    print("PARTICIPANTES ENCONTRADOS")
    print("=" * 70)

    if df_encontrados.empty:

        print(
            "\nNo se encontraron participantes."
        )

        return

    for _, fila in df_encontrados.iterrows():

        print(
            "\n- "
            f"{fila['email_bcp']}"
            " | "
            f"{fila['nombre_bcp']}"
        )

        print(
            "  CVS:"
            f" {fila['firstName_cvs']}"
            f" {fila['lastName_cvs']}"
        )

        print(
            "  Email CVS:"
            f" {fila['email_cvs']}"
        )

        print(
            "  Profesión:"
            f" {fila['profession']}"
        )

        print(
            "  Método:"
            f" {fila['metodo_cruce']}"
        )


# ============================================================
# MOSTRAR NO ENCONTRADOS
# ============================================================

def mostrar_no_encontrados(
    df_no_encontrados
):

    print("\n" + "=" * 70)
    print("PARTICIPANTES NO ENCONTRADOS")
    print("=" * 70)

    if df_no_encontrados.empty:

        print(
            "\n[OK] Todos los participantes fueron encontrados."
        )

        return

    for _, fila in df_no_encontrados.iterrows():

        print(
            f"- {fila['email_bcp']}"
            f" | {fila['nombre_bcp']}"
        )


# ============================================================
# CREAR EXCEL
# ============================================================

def crear_excel(
    df_resultado,
    df_encontrados,
    df_no_encontrados,
    participantes
):

    print("\n" + "=" * 70)
    print("CREANDO EXCEL")
    print("=" * 70)

    ARCHIVO_SALIDA.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Hoja de todos los participantes
    # --------------------------------------------------------

    df_todos = pd.DataFrame(
        participantes
    )

    df_todos = df_todos.rename(
        columns={
            "email": "email_bcp",
            "nombre": "nombre_bcp",
        }
    )

    # --------------------------------------------------------
    # Resumen
    # --------------------------------------------------------

    total = len(
        participantes
    )

    encontrados = len(
        df_encontrados
    )

    no_encontrados = len(
        df_no_encontrados
    )

    porcentaje = (
        encontrados / total * 100
        if total
        else 0
    )

    df_resumen = pd.DataFrame({

        "indicador": [

            "Participantes BCP",

            "Encontrados en cvs",

            "No encontrados",

            "Porcentaje encontrado",

        ],

        "valor": [

            total,

            encontrados,

            no_encontrados,

            f"{porcentaje:.2f}%",

        ]

    })

    # --------------------------------------------------------
    # Excel
    # --------------------------------------------------------

    with pd.ExcelWriter(
        ARCHIVO_SALIDA,
        engine="openpyxl"
    ) as writer:

        # --------------------------------------------
        # TODOS
        # --------------------------------------------

        df_resultado.to_excel(
            writer,
            sheet_name="todos",
            index=False
        )

        # --------------------------------------------
        # ENCONTRADOS
        # --------------------------------------------

        df_encontrados.to_excel(
            writer,
            sheet_name="encontrados",
            index=False
        )

        # --------------------------------------------
        # NO ENCONTRADOS
        # --------------------------------------------

        df_no_encontrados.to_excel(
            writer,
            sheet_name="no_encontrados",
            index=False
        )

        # --------------------------------------------
        # PARTICIPANTES BCP
        # --------------------------------------------

        df_todos.to_excel(
            writer,
            sheet_name="participantes_bcp",
            index=False
        )

        # --------------------------------------------
        # RESUMEN
        # --------------------------------------------

        df_resumen.to_excel(
            writer,
            sheet_name="resumen",
            index=False
        )

        # --------------------------------------------
        # AJUSTAR ANCHO
        # --------------------------------------------

        for worksheet in writer.book.worksheets:

            for columna in worksheet.columns:

                max_length = 0

                letra = columna[0].column_letter

                for celda in columna:

                    try:

                        valor = str(
                            celda.value
                        )

                        if len(valor) > max_length:

                            max_length = len(
                                valor
                            )

                    except Exception:

                        pass

                worksheet.column_dimensions[
                    letra
                ].width = min(
                    max_length + 2,
                    60
                )

            # Congelar encabezado

            worksheet.freeze_panes = "A2"

    print(
        "\n" + "=" * 70
    )

    print(
        "ARCHIVO CREADO CORRECTAMENTE"
    )

    print(
        "=" * 70
    )

    print(
        f"\n{ARCHIVO_SALIDA}"
    )

    print(
        "\nHojas creadas:"
    )

    print(
        "1. todos"
    )

    print(
        "2. encontrados"
    )

    print(
        "3. no_encontrados"
    )

    print(
        "4. participantes_bcp"
    )

    print(
        "5. resumen"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print("CRUCE BCP -> COLECCIÓN CVS")
    print("=" * 70)

    # --------------------------------------------------------
    # PARTICIPANTES
    # --------------------------------------------------------

    print(
        "\nParticipantes BCP configurados:"
    )

    for participante in PARTICIPANTES_BCP:

        print(
            f"- {participante['email']}"
            f" | {participante['nombre']}"
        )

    print(
        f"\nTotal participantes BCP: "
        f"{len(PARTICIPANTES_BCP)}"
    )

    # --------------------------------------------------------
    # MONGODB
    # --------------------------------------------------------

    db = conectar_mongodb()

    collection = obtener_coleccion_cvs(
        db
    )

    # --------------------------------------------------------
    # CVS
    # --------------------------------------------------------

    df_cvs = cargar_cvs(
        collection
    )

    (
        df_cvs,
        indice_email,
        indice_nombre
    ) = preparar_cvs(
        df_cvs
    )

    # --------------------------------------------------------
    # CRUCE
    # --------------------------------------------------------

    (
        df_resultado,
        df_encontrados,
        df_no_encontrados
    ) = realizar_cruce(
        PARTICIPANTES_BCP,
        indice_email,
        indice_nombre
    )

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    mostrar_resumen(
        PARTICIPANTES_BCP,
        df_encontrados,
        df_no_encontrados
    )

    # --------------------------------------------------------
    # ENCONTRADOS
    # --------------------------------------------------------

    mostrar_encontrados(
        df_encontrados
    )

    # --------------------------------------------------------
    # NO ENCONTRADOS
    # --------------------------------------------------------

    mostrar_no_encontrados(
        df_no_encontrados
    )

    # --------------------------------------------------------
    # EXCEL
    # --------------------------------------------------------

    crear_excel(
        df_resultado,
        df_encontrados,
        df_no_encontrados,
        PARTICIPANTES_BCP
    )

    print(
        "\nProceso terminado."
    )


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    main()