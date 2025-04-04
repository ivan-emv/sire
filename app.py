
from PIL import Image
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime
import re

st.set_page_config(page_title="Gestión de Incidencias - EMV SIRE 2025", layout="wide")

col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    st.image("a1.png", width=500)
with col_titulo:
    st.markdown("<h1 style='margin-top: 25px;'>Gestión de Incidencias - EMV SIRE 2025</h1>", unsafe_allow_html=True)

# Aquí iría el resto del código, y al final:

# --------- Búsqueda de Registros ---------
elif modo == "🔍 Búsqueda de Registros":
    st.header("🔍 Consulta de Incidencias por Usuario y Localizador")

    @st.cache_data(show_spinner=False)
    def cargar_datos_busqueda():
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        hoja = client.open_by_key("1aaGedbCfPfLqktmNQEVoiC0cphs-iKlmz9IKGcKNvUE").worksheet("DATOS")
        datos = hoja.get_all_records()
        return pd.DataFrame(datos)

    df_busqueda = cargar_datos_busqueda()

    if df_busqueda.empty:
        st.warning("No hay registros disponibles en la base de datos.")
    else:
        usuarios = sorted(df_busqueda["nombre_usuario"].dropna().unique())

        col1, col2 = st.columns(2)
        with col1:
            usuario_sel = st.selectbox("Selecciona el Usuario", [""] + list(usuarios))
        with col2:
            localizador_sel = st.text_input("Introduce el Localizador")

        filtro_usuario = usuario_sel.strip() != ""
        filtro_localizador = localizador_sel.strip() != ""

        if filtro_usuario and filtro_localizador:
            filtrado = df_busqueda[
                (df_busqueda["nombre_usuario"] == usuario_sel) &
                (df_busqueda["localizador"] == localizador_sel)
            ]
        elif filtro_usuario:
            filtrado = df_busqueda[df_busqueda["nombre_usuario"] == usuario_sel]
        elif filtro_localizador:
            filtrado = df_busqueda[df_busqueda["localizador"] == localizador_sel]
        else:
            filtrado = df_busqueda.copy()  # Mostrar todo si no hay filtros

        if not filtrado.empty:
            st.success(f"Se encontraron {len(filtrado)} registros.")
            st.dataframe(filtrado, use_container_width=True)
        else:
            st.info("No se encontraron registros con esos criterios.")
