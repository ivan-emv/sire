import streamlit as st
import datetime
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --------- Datos simulados ---------
USUARIOS = ["Usuario A", "Usuario B", "Usuario C"]
OPERADORES = ["Operador A", "Operador B", "Operador C"]
HOTELES = ["Hotel Alpha", "Hotel Beta", "Hotel Gamma"]
GUIAS = ["Guía 1", "Guía 2", "Guía 3"]
TRAYECTOS = ["Trayecto Madrid - París", "Trayecto Roma - Florencia", "Trayecto Berlín - Praga"]
RESOLUCIONES = [
    "Reembolso Parcial/Partial Reimbursement", "Reembolso Total/Total Reimbursement",
    "Compensación/Compensation", "Descuento Próximo Viaje/Next Trip Discount",
    "Cambio Itinerario/Itinerary Change", "En Estudio/Pending",
    "Se informa al Pasajero/Passenger Informed", "Se informa al Operador/Operator Informed",
    "Se informa al Minorista/Agency Informed", "Se informa al Guía/Guide Informed",
    "Se informa al Transferista/TSP Informed", "Se informa al Receptivo/Local Provider Informed",
    "Se informa a Departamento/Department Informed"]

# --------- Inicializar sesión ---------
def init_session():
    if "incidencias" not in st.session_state:
        st.session_state.incidencias = []
    if "datos_generales" not in st.session_state:
        st.session_state.datos_generales = {}
    if "form_counter" not in st.session_state:
        st.session_state.form_counter = 0

init_session()

st.set_page_config(page_title="Carga de Incidencias - EMV SIRE", layout="wide")
st.title("📝 Formulario de Incidencias EMV-SIRE 2025")

# --------- Función para guardar en Google Sheets ---------
def guardar_en_google_sheets(datos_generales, lista_incidencias):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1kBLQAdhYbnP8HTUgpr_rmmGEaOdyMU2tI97ogegrGxY").worksheet("PRUEBA")

    for incidencia in lista_incidencias:
        fila = {**datos_generales, **incidencia}
        sheet.append_row([fila.get(col, "") for col in sheet.row_values(1)])

# --------- Datos Generales ---------
st.subheader("Datos Generales del Servicio")
with st.form(key="form_datos_generales"):
    col1, col2 = st.columns(2)
    with col1:
        def formatear_fecha(texto):
            texto = re.sub(r"[^0-9]", "", texto)
            if len(texto) > 4:
                texto = texto[:2] + "/" + texto[2:4] + "/" + texto[4:8]
            elif len(texto) > 2:
                texto = texto[:2] + "/" + texto[2:4]
            return texto

        entrada_usuario = st.text_input("Fecha de Inicio del Viaje (DD/MM/YYYY)", max_chars=10)
        fecha_formateada = formatear_fecha(entrada_usuario)

        momento_viaje = st.selectbox("Momento del viaje", ["Pre Viaje", "En Ruta", "Post Viaje"])
        localizador = st.text_input("Localizador (código único de reserva)")
    with col2:
        nombre_usuario = st.selectbox("Nombre del Usuario", USUARIOS)
        operador = st.selectbox("Operador", OPERADORES)

    submitted_gen = st.form_submit_button("Confirmar datos generales")
    if submitted_gen:
        st.session_state.datos_generales = {
            "fecha_inicio": fecha_formateada,
            "fecha_registro": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "momento_viaje": momento_viaje,
            "localizador": localizador,
            "nombre_usuario": nombre_usuario,
            "operador": operador,
        }
        st.success("✅ Datos generales registrados correctamente.")

# --------- Registro de Incidencias ---------
if st.session_state.datos_generales:
    st.markdown("---")
    st.subheader("Registrar Nueva Incidencia")

    idx = st.session_state.form_counter
    tipo_contacto = st.radio("Tipo de contacto", ["Información", "Reclamación", "Otro"], key=f"tipo_contacto_{idx}")
    incidencia = {"tipo_contacto": tipo_contacto}

    area = st.text_input("Área Relacionada", key=f"area_{idx}")
    incidencia["area"] = area
    comentario = st.text_area("Comentario", max_chars=500, key=f"comentario_{idx}")
    incidencia["comentario"] = comentario
    resolucion = st.selectbox("Resolución", RESOLUCIONES, key=f"resolucion_{idx}")
    incidencia["resolucion"] = resolucion

    if resolucion.startswith("Reembolso") or resolucion == "Compensación/Compensation":
        monto = st.text_input("Monto compensación o tipo de compensación", key=f"monto_{idx}")
        incidencia["monto"] = monto

    resultado = st.text_input("Resultado", key=f"resultado_{idx}")
    incidencia["resultado"] = resultado

    col1, col2 = st.columns([1, 1])
    if col1.button("➕ Agregar otro caso"):
        st.session_state.incidencias.append(incidencia)
        st.success("Incidencia agregada correctamente.")
        st.session_state.form_counter += 1
        st.rerun()

    if col2.button("✅ Finalizar"):
        st.session_state.incidencias.append(incidencia)

        try:
            guardar_en_google_sheets(st.session_state.datos_generales, st.session_state.incidencias)
            st.success("✅ Los datos han sido guardados correctamente en Google Sheets.")
        except Exception as e:
            st.error(f"❌ Error al guardar en Google Sheets: {e}")

        st.markdown("---")
        st.subheader("Resumen del Registro")
        st.write("**Datos generales:**", st.session_state.datos_generales)
        st.write("**Incidencias cargadas:**", st.session_state.incidencias)
        st.session_state.clear()
        st.rerun()
