import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Data Governance Monitor",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Data Governance Monitor")

st.subheader("Snowflake | Data Quality & Governance")

st.write(
    "Dashboard de monitoreo y auditoría "
    "de procesos de datos en Snowflake."
)

st.success("¡Nuestra aplicación está funcionando correctamente!")


from snowflake.snowpark.context import get_active_session

# Obtener la sesión activa de Snowflake
session = get_active_session()

# Consultar nuestra vista de auditoría
query = """
    SELECT
        QUERY_ID,
        USER_NAME,
        ROLE_NAME,
        TO_DATE(START_TIME) AS ERROR_DATE,
        ERROR_CATEGORY,
        ERROR_CODE,
        ERROR_MESSAGE
    FROM FLIGHT_DATA_DB.AUDIT.V_QUERY_ERROR_MONITOR
    ORDER BY START_TIME DESC
"""

# Ejecutar la consulta
df = session.sql(query).to_pandas()

# ==========================================
# FILTRO INTERACTIVO POR CATEGORÍA
# ==========================================

st.sidebar.header("🔎 Filtros")

categorias = df["ERROR_CATEGORY"].unique().tolist()

categorias_seleccionadas = st.sidebar.multiselect(
    "Selecciona las categorías de error",
    options=categorias,
    default=categorias
)

# ==========================================
# FILTRO INTERACTIVO POR ROL
# ==========================================

# Obtener los roles disponibles
roles = df["ROLE_NAME"].dropna().unique().tolist()

# Crear filtro en el panel lateral
roles_seleccionados = st.sidebar.multiselect(
    "Selecciona los roles de Snowflake",
    options=roles,
    default=roles
)

# ==========================================
# FILTRO INTERACTIVO POR FECHA
# ==========================================

# Convertir la columna a tipo fecha
df["ERROR_DATE"] = pd.to_datetime(
    df["ERROR_DATE"]
).dt.date

# Obtener fechas mínima y máxima
fecha_min = df["ERROR_DATE"].min()
fecha_max = df["ERROR_DATE"].max()

# Crear selector de rango de fechas
rango_fechas = st.sidebar.date_input(
    "Selecciona el rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# Aplicar filtros de categoría y rol
df = df[
    df["ERROR_CATEGORY"].isin(categorias_seleccionadas)
    & df["ROLE_NAME"].isin(roles_seleccionados)
]

# Aplicar filtro por rango de fechas
if len(rango_fechas) == 2:
    fecha_inicio, fecha_fin = rango_fechas

    df = df[
        (df["ERROR_DATE"] >= fecha_inicio)
        & (df["ERROR_DATE"] <= fecha_fin)
    ]

# ==========================================
# KPI - Indicadores de auditoría
# ==========================================

st.subheader("📊 Indicadores de auditoría")

# ==========================================
# KPI - Indicadores de auditoría
# ==========================================

# Total de errores registrados
total_errors = len(df)

# Posibles errores de permisos
permission_errors = (
    df["ERROR_CATEGORY"] == "POSIBLE ERROR DE PERMISOS"
).sum()

# Errores de sintaxis
syntax_errors = (
    df["ERROR_CATEGORY"] == "ERROR DE SINTAXIS"
).sum()

# Crear tres columnas
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total de errores",
        value=total_errors
    )

with col2:
    st.metric(
        label="Posibles errores de permisos",
        value=permission_errors
    )

with col3:
    st.metric(
        label="Errores de sintaxis",
        value=syntax_errors
    )

# Agrupar errores por categoría
df_chart = (
    df.groupby("ERROR_CATEGORY")
    .size()
    .reset_index(name="TOTAL_ERRORS")
)

# Mostrar gráfica
st.bar_chart(
    df_chart,
    x="ERROR_CATEGORY",
    y="TOTAL_ERRORS",
    x_label="Categoría de error",
    y_label="Número de errores"
)

# ==========================================
# EVOLUCIÓN DIARIA DE ERRORES
# ==========================================

st.subheader("📅 Evolución diaria de errores")

# Agrupar registros por fecha
df_daily = (
    df.groupby("ERROR_DATE")
    .size()
    .reset_index(name="TOTAL_ERRORS")
    .sort_values("ERROR_DATE")
)

# Convertir fechas a texto para mostrarlas por día
df_daily["ERROR_DATE_LABEL"] = (
    df_daily["ERROR_DATE"].astype(str)
)

st.bar_chart(
    df_daily,
    x="ERROR_DATE_LABEL",
    y="TOTAL_ERRORS",
    x_label="Fecha",
    y_label="Número de errores"
)

# Mostrar resultados
st.subheader("📊 Errores por categoría")

st.dataframe(df, width="stretch")
