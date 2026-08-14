# ============================================================
# EXPLORAR CURSOS Y COURSEENROLLMENTS
# ============================================================

import pandas as pd

from scripts.conexion import db


# ============================================================
# CONEXIÓN
# ============================================================

print("✅ Conexión a MongoDB correcta")
print(f"📂 Base de datos: {db.name}")


# ============================================================
# LEER COURSES
# ============================================================

print("\n" + "=" * 70)
print("📚 COLECCIÓN: courses")
print("=" * 70)

courses = pd.DataFrame(
    list(
        db["courses"].find({})
    )
)

print(f"\nCantidad de registros: {len(courses)}")
print(f"Dimensiones: {courses.shape}")


# ============================================================
# COLUMNAS COURSES
# ============================================================

print("\nColumnas:")

for columna in courses.columns:
    print(f"  - {columna}")


# ============================================================
# EJEMPLOS COURSES
# ============================================================

print("\nPrimeros registros:")

if not courses.empty:
    print(
        courses.head(5).to_string()
    )
else:
    print("⚠️ La colección courses está vacía.")


# ============================================================
# LEER COURSEENROLLMENTS
# ============================================================

print("\n" + "=" * 70)
print("📚 COLECCIÓN: courseenrollments")
print("=" * 70)

courseenrollments = pd.DataFrame(
    list(
        db["courseenrollments"].find({})
    )
)

print(f"\nCantidad de registros: {len(courseenrollments)}")
print(f"Dimensiones: {courseenrollments.shape}")


# ============================================================
# COLUMNAS COURSEENROLLMENTS
# ============================================================

print("\nColumnas:")

for columna in courseenrollments.columns:
    print(f"  - {columna}")


# ============================================================
# EJEMPLOS COURSEENROLLMENTS
# ============================================================

print("\nPrimeros registros:")

if not courseenrollments.empty:
    print(
        courseenrollments.head(10).to_string()
    )
else:
    print("⚠️ La colección courseenrollments está vacía.")


# ============================================================
# TIPOS DE DATOS
# ============================================================

print("\n" + "=" * 70)
print("🔎 TIPOS DE DATOS - COURSES")
print("=" * 70)

print(courses.dtypes)


print("\n" + "=" * 70)
print("🔎 TIPOS DE DATOS - COURSEENROLLMENTS")
print("=" * 70)

print(courseenrollments.dtypes)


# ============================================================
# VALORES NULOS
# ============================================================

print("\n" + "=" * 70)
print("🔎 VALORES NULOS - COURSES")
print("=" * 70)

if not courses.empty:
    print(
        courses.isna()
        .sum()
        .sort_values(ascending=False)
        .head(20)
    )


print("\n" + "=" * 70)
print("🔎 VALORES NULOS - COURSEENROLLMENTS")
print("=" * 70)

if not courseenrollments.empty:
    print(
        courseenrollments.isna()
        .sum()
        .sort_values(ascending=False)
        .head(20)
    )


print("\n" + "=" * 70)
print("✅ EXPLORACIÓN TERMINADA")
print("=" * 70)