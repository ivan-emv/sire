
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

st.set_page_config(page_title="Consulta de Incidencias - EMV SIRE", layout="wide")
st.title("🔍 Consulta de Incidencias por Usuario y Localizador")

# --------- Autenticación y carga desde Google Sheet ---------
@st.cache_data(show_spinner=False)
def cargar_datos():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    hoja = client.open_by_key("1aaGedbCfPfLqktmNQEVoiC0cphs-iKlmz9IKGcKNvUE").worksheet("DATOS")
    datos = hoja.get_all_records()
    return pd.DataFrame(datos)

df = cargar_datos()

if df.empty:
    st.warning("No hay registros disponibles en la base de datos.")
    st.stop()

# --------- Filtros de búsqueda ---------
usuarios = sorted(df["nombre_usuario"].dropna().unique())
localizadores = sorted(df["localizador"].dropna().unique())

col1, col2 = st.columns(2)
with col1:
    usuario_sel = st.selectbox("Selecciona el Usuario", usuarios)
with col2:
    localizador_sel = st.selectbox("Selecciona el Localizador", localizadores)

# --------- Resultado filtrado ---------
filtrado = df[
    (df["nombre_usuario"] == usuario_sel) &
    (df["localizador"] == localizador_sel)
]

if not filtrado.empty:
    st.success(f"Se encontraron {len(filtrado)} registros para el usuario '{usuario_sel}' y localizador '{localizador_sel}'.")
    st.dataframe(filtrado, use_container_width=True)
else:
    st.info("No se encontraron registros con esos criterios.")
