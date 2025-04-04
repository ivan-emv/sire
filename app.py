
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime
import re

# --------- Función para guardar en Google Sheets ---------
def guardar_en_google_sheets(datos_generales, lista_incidencias):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1aaGedbCfPfLqktmNQEVoiC0cphs-iKlmz9IKGcKNvUE").worksheet("DATOS")
        headers = [
            "fecha_inicio", "fecha_registro", "momento_viaje", "localizador", "nombre_usuario",
            "operador", "ciudad", "tipo_contacto", "area", "hotel", "tipo_traslado",
            "trayecto", "guia", "tipo_incidencia", "comentario", "resolucion", "monto", "resultado"
        ]
        for incidencia in lista_incidencias:
            fila = {**datos_generales, **incidencia}
            row = [fila.get(col, "") for col in headers]
            sheet.append_row(row)
        st.success("✅ Los datos se guardaron correctamente en Google Sheets.")
    except Exception as e:
        st.error(f"❌ Error al guardar en Google Sheets: {e}")

# --------- Selector de Modo ---------
st.set_page_config(page_title="Gestión de Incidencias - EMV SIRE 2025", layout="wide")
st.title("Gestión de Incidencias - EMV SIRE 2025")
modo = st.sidebar.radio("Selecciona una opción", ["📝 Carga de Incidencias", "🔍 Búsqueda de Registros"])
if modo == "📝 Carga de Incidencias":
    st.subheader("Datos Generales del Servicio")

    @st.cache_data(show_spinner=False)
    def cargar_datos_desde_google_sheets():
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        sheet_id = "1FyWpAjXMkuOW4TM71Z521lFyTX6nUQ8hNE8RGY3cnS4"
        datos = {}
        for nombre in ["Ciudades", "Hoteles", "Guias", "Operadores", "Trayectos", "Usuarios"]:
            worksheet = client.open_by_key(sheet_id).worksheet(nombre)
            datos[nombre] = worksheet.get_all_records()

        return datos

    datos_bd = cargar_datos_desde_google_sheets()

    USUARIOS = [u["Nombre"] for u in datos_bd["Usuarios"] if "Nombre" in u]
    CIUDADES = [c["Ciudad"] for c in datos_bd["Ciudades"] if "Ciudad" in c]
    HOTELES = [h["Nombre Hotel"] for h in datos_bd["Hoteles"] if "Nombre Hotel" in h]
    GUIAS = [g["Nombre del Guia"] for g in datos_bd["Guias"] if "Nombre del Guia" in g]
    OPERADORES = [o["Nombre del Operador"] for o in datos_bd["Operadores"] if "Nombre del Operador" in o]
    TRAYECTOS = [t["Trayecto"] for t in datos_bd["Trayectos"] if "Trayecto" in t]
    RESOLUCIONES = [
        "Reembolso Parcial/Partial Reimbursement", "Reembolso Total/Total Reimbursement",
        "Compensación/Compensation", "Descuento Próximo Viaje/Next Trip Discount",
        "Cambio Itinerario/Itinerary Change", "En Estudio/Pending",
        "Se informa al Pasajero/Passenger Informed", "Se informa al Operador/Operator Informed",
        "Se informa al Minorista/Agency Informed", "Se informa al Guía/Guide Informed",
        "Se informa al Transferista/TSP Informed", "Se informa al Receptivo/Local Provider Informed",
        "Se informa a Departamento/Department Informed"]

    # Aquí iría el formulario completo omitido por brevedad

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
            usuario_sel = st.selectbox("Selecciona el Usuario", usuarios)
        with col2:
            localizador_sel = st.text_input("Introduce el Localizador")

        filtrado = df_busqueda[
            (df_busqueda["nombre_usuario"] == usuario_sel) &
            (df_busqueda["localizador"] == localizador_sel)
        ]

        if not filtrado.empty:
            st.success(f"Se encontraron {len(filtrado)} registros para el usuario '{usuario_sel}' y localizador '{localizador_sel}'.")
            st.dataframe(filtrado, use_container_width=True)
        else:
            st.info("No se encontraron registros con esos criterios.")
