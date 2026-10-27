import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración básica de la página
st.set_page_config(page_title="Dashboard Abastecimiento", layout="wide")
st.title("📊 Dashboard de Informe de Abastecimiento")

# 1. Cargar los datos desde Google Sheets
@st.cache_data
def load_data():
    # PEGA TU ENLACE AQUÍ:
    sheet_url = "https://docs.google.com/spreadsheets/d/1m-055kh4cYYoDX6DTuZf65hyRDlQuYgLaFye5gd3tD8/edit?usp=sharing" 
    
    # Truco para convertir el enlace de edición a enlace de descarga CSV
    csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv&gid=346493533")
    # Nota: Si usas otra hoja, asegúrate de cambiar el 'gid' al número correcto que sale en la URL de tu navegador.
    
    df = pd.read_csv(csv_url)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al cargar los datos. Verifica el enlace de Google Sheets. Detalle: {e}")
    st.stop()

# 2. Crear Filtros en la barra lateral
st.sidebar.header("Filtros")
meses = st.sidebar.multiselect("Selecciona Mes / Año", options=df["Mes / Año"].dropna().unique())
almacenes = st.sidebar.multiselect("Selecciona Almacén", options=df["Almacén"].dropna().unique())

# Filtrar el dataframe basado en la selección
df_filtrado = df.copy()
if meses:
    df_filtrado = df_filtrado[df_filtrado["Mes / Año"].isin(meses)]
if almacenes:
    df_filtrado = df_filtrado[df_filtrado["Almacén"].isin(almacenes)]

# 3. Mostrar KPIs (Tarjetas de resumen)
col1, col2, col3 = st.columns(3)
col1.metric("Total Registros", len(df_filtrado))
col2.metric("Proveedores Únicos", df_filtrado["Proveedor (Razón Social)"].nunique())
col3.metric("Ubicaciones Diferentes", df_filtrado["Tipo Ubicación"].nunique())

st.divider()

# 4. Gráficos
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Top Proveedores (Cantidad de Compras)")
    top_proveedores = df_filtrado["Proveedor (Razón Social)"].value_counts().reset_index().head(10)
    top_proveedores.columns = ["Proveedor", "Cantidad"]
    fig_prov = px.bar(top_proveedores, x="Cantidad", y="Proveedor", orientation='h')
    st.plotly_chart(fig_prov, use_container_width=True)

with col_graf2:
    st.subheader("Distribución por Tipo de Ubicación")
    dist_ubicacion = df_filtrado["Tipo Ubicación"].value_counts().reset_index()
    dist_ubicacion.columns = ["Ubicación", "Cantidad"]
    fig_ubic = px.pie(dist_ubicacion, names="Ubicación", values="Cantidad", hole=0.4)
    st.plotly_chart(fig_ubic, use_container_width=True)

# 5. Mostrar la tabla de datos
st.subheader("Detalle de Abastecimiento")
st.dataframe(df_filtrado[["Mes / Año", "Almacén", "Tipo Ubicación", "Proveedor (Razón Social)", "Material", "Descripción"]], use_container_width=True)
