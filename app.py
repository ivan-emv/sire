
import streamlit as st
import datetime
import re

RESOLUCIONES = [
    "Reembolso Parcial/Partial Reimbursement", "Reembolso Total/Total Reimbursement",
    "Compensación/Compensation", "Descuento Próximo Viaje/Next Trip Discount",
    "Cambio Itinerario/Itinerary Change", "En Estudio/Pending",
    "Se informa al Pasajero/Passenger Informed", "Se informa al Operador/Operator Informed",
    "Se informa al Minorista/Agency Informed", "Se informa al Guía/Guide Informed",
    "Se informa al Transferista/TSP Informed", "Se informa al Receptivo/Local Provider Informed",
    "Se informa a Departamento/Department Informed"
]

# Inicializar sesión
def init_session():
    if "incidencias" not in st.session_state:
        st.session_state.incidencias = []
    if "datos_generales" not in st.session_state:
        st.session_state.datos_generales = {}
    if "form_counter" not in st.session_state:
        st.session_state.form_counter = 0
    if "admin_autenticado" not in st.session_state:
        st.session_state.admin_autenticado = False

init_session()
st.set_page_config(page_title="Carga de Incidencias - EMV SIRE", layout="wide")

# Estilo para ocultar menú Streamlit
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    st.image("a1.png", width=500)
with col_titulo:
    st.markdown("<h1 style='margin-top: 25px;'>Gestión de Incidencias - EMV SIRE 2025</h1>", unsafe_allow_html=True)

modo = st.sidebar.radio("Selecciona una opción", [
    "📝 Carga de Incidencias",
    "🔍 Búsqueda de Registros"
] + (["🛠️ Gestión de Registros"] if st.session_state.admin_autenticado else []))

# --- GESTIÓN DE REGISTROS (EDICIÓN) ---
if modo == "🛠️ Gestión de Registros" and st.session_state.admin_autenticado:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    import pandas as pd

    st.header("🛠️ Gestión de Registros (Administrador)")

    # Cargar base de datos
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    hoja = client.open_by_key("1aaGedbCfPfLqktmNQEVoiC0cphs-iKlmz9IKGcKNvUE").worksheet("DATOS")
    datos = hoja.get_all_records()
    df_admin = pd.DataFrame(datos)

    if df_admin.empty:
        st.warning("No hay registros en la base de datos.")
    else:
        st.success(f"Se encontraron {len(df_admin)} registros.")
        st.dataframe(df_admin, use_container_width=True)

        selected_row = st.number_input("Selecciona el número de fila a editar (desde 1):", min_value=1, max_value=len(df_admin), step=1)
        if st.button("📝 Editar fila seleccionada"):
            index = selected_row - 1
            registro = df_admin.iloc[index].to_dict()
            st.subheader("Editar Registro")

            with st.form("editar_registro_form"):
                columnas = list(registro.keys())
                nuevos_valores = {}
                for campo in columnas:
                    nuevos_valores[campo] = st.text_input(campo, value=str(registro[campo]))
                if st.form_submit_button("💾 Guardar Cambios"):
                    hoja.update(f"A{selected_row + 1}", [[nuevos_valores.get(col, "") for col in columnas]])
                    st.success("✅ Registro actualizado correctamente.")
                    st.rerun()
