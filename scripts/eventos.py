import pandas as pd


# ==========================================
# CLASIFICAR EVENTOS
# ==========================================

def clasificar_evento(titulo):

    if pd.isna(titulo):
        return "Sin clasificar"

    titulo = str(titulo).lower()

    if "taller" in titulo:
        return "Taller"

    elif "despega" in titulo:
        return "Feria laboral"

    elif "hub" in titulo:
        return "Networking"

    elif "webinar" in titulo:
        return "Webinar"

    else:
        return "Sin clasificar"


# ==========================================
# PARTICIPACIÓN POR TIPO DE EVENTO
# ==========================================

def resumen_eventos(df):

    df = df.copy()

    df["Tipo_evento"] = (
        df["title"]
        .apply(clasificar_evento)
    )

    resumen = (
        df[
            df["Tipo_evento"] != "Sin clasificar"
        ]
        .groupby("Tipo_evento")["_id_user"]
        .nunique()
        .reset_index(
            name="Cantidad_postulantes"
        )
    )

    return resumen