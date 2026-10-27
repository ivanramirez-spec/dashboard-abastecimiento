import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración básica de la página
st.set_page_config(page_title="Dashboard Abastecimiento", layout="wide")
st.title("📊 Dashboard de Informe de Abastecimiento")

# 1. Cargar los datos
@st.cache_data
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1m-055kh4cYYoDX6DTuZf65hyRDlQuYgLaFye5gd3tD8/edit?usp=sharing" 
    csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv&gid=346493533")
    df = pd.read_csv(csv_url)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al cargar los datos. Detalle: {e}")
    st.stop()

# Buscar dinámicamente la columna de "Componente" por si tiene otro nombre exacto
col_componente = None
for col in df.columns:
    if "componente" in col.lower():
        col_componente = col
        break

# 2. Crear Filtros en la barra lateral
st.sidebar.header("Filtros")
meses = st.sidebar.multiselect("Selecciona Mes / Año", options=df["Mes / Año"].dropna().unique())
almacenes = st.sidebar.multiselect("Selecciona Almacén", options=df["Almacén"].dropna().unique())
proveedores = st.sidebar.multiselect("Selecciona Proveedor", options=df["Proveedor (Razón Social)"].dropna().unique())

# Filtro de componente (si existe la columna)
componentes = []
if col_componente:
    componentes = st.sidebar.multiselect(f"Selecciona {col_componente}", options=df[col_componente].dropna().unique())

# Filtrar el dataframe
df_filtrado = df.copy()
if meses:
    df_filtrado = df_filtrado[df_filtrado["Mes / Año"].isin(meses)]
if almacenes:
    df_filtrado = df_filtrado[df_filtrado["Almacén"].isin(almacenes)]
if proveedores:
    df_filtrado = df_filtrado[df_filtrado["Proveedor (Razón Social)"].isin(proveedores)]
if col_componente and componentes:
    df_filtrado = df_filtrado[df_filtrado[col_componente].isin(componentes)]

# 3. Mostrar KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Registros", len(df_filtrado))
col2.metric("Proveedores Únicos", df_filtrado["Proveedor (Razón Social)"].nunique())
if col_componente:
    col3.metric(f"{col_componente}s Diferentes", df_filtrado[col_componente].nunique())
else:
    col3.metric("Ubicaciones Diferentes", df_filtrado["Tipo Ubicación"].nunique())

st.divider()

# 4. Gráficos Interactivos
st.subheader("Análisis Gráfico")
opciones_graficos = ["Proveedor (Razón Social)", "Tipo Ubicación"]
if col_componente:
    opciones_graficos.append(col_componente)

agrupar_por = st.selectbox("Visualizar gráficos por:", opciones_graficos)

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    datos_bar = df_filtrado[agrupar_por].value_counts().reset_index().head(10)
    datos_bar.columns = [agrupar_por, "Cantidad de Compras"]
    fig_bar = px.bar(datos_bar, x="Cantidad de Compras", y=agrupar_por, orientation='h', title=f"Top 10 por {agrupar_por}")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_graf2:
    datos_pie = df_filtrado[agrupar_por].value_counts().reset_index()
    datos_pie.columns = [agrupar_por, "Cantidad de Compras"]
    fig_pie = px.pie(datos_pie, names=agrupar_por, values="Cantidad de Compras", hole=0.4, title=f"Distribución por {agrupar_por}")
    st.plotly_chart(fig_pie, use_container_width=True)

# 5. Mostrar la tabla de datos COMPLETA
st.subheader("Detalle Completo de Abastecimiento (Incluye Valores y Análisis)")
# Al no especificar columnas adentro del dataframe, Streamlit mostrará TODAS las que tengas en Excel
st.dataframe(df_filtrado, use_container_width=True)
