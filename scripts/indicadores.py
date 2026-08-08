def calcular_kpis_postulantes(df):

    total = df["_id_postulante"].nunique()

    con_cv = df["tiene_cv"].sum()

    activos = (
        df["isActive"].sum()
        if "isActive" in df.columns
        else 0
    )

    uso_ia = df["uso_ia"].sum()

    cursos = (
        df["cantidad_cursos"] > 0
    ).sum()

    eventos = (
        df["participo_evento"].sum()
    )

    return {
        "total_postulantes": total,
        "porcentaje_cv": (con_cv / total * 100) if total else 0,
        "porcentaje_activos": (activos / total * 100) if total else 0,
        "porcentaje_ia": (uso_ia / total * 100) if total else 0,
        "porcentaje_cursos": (cursos / total * 100) if total else 0,
        "porcentaje_eventos": (eventos / total * 100) if total else 0
    }