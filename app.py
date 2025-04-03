# Versión con 'Resolución' en Información como desplegable con opciones definidas
import streamlit as st
import datetime
import re

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
        st.session_state.datos_generales = {}
    if "clean_form" not in st.session_state:
        st.session_state.clean_form = False

init_session()

st.set_page_config(page_title="Carga de Incidencias - EMV SIRE", layout="wide")
st.title("📝 Formulario de Incidencias EMV-SIRE 2025")

# --------- Datos Generales ---------
# ... [sin cambios aquí para brevedad]

# --------- Registro de Incidencias (Dinámico) ---------
if st.session_state.datos_generales:
    st.markdown("---")
    st.subheader("Registrar Nueva Incidencia")

    tipo_contacto = st.radio("Tipo de contacto", ["Información", "Reclamación", "Otro"], key="tipo_contacto")
    incidencia = {"tipo_contacto": tipo_contacto}

    if tipo_contacto == "Información":
        area_info = st.selectbox("Área Relacionada", [
            "Traslados/Transfers", "Hotel", "Seguro/Insurance", "Itinerario/Itinerary",
            "Equipaje/Luggage", "Felicitación Circuito", "Info Guía/Guide Info",
            "Punto Encuentro/Meeting Point", "Comercial/Commercial", "Enfermedad/Sickness",
            "Opcionales/Optional Tours", "Otros/Other"], key="area_info")
        incidencia["area"] = area_info

        if area_info == "Hotel":
            incidencia["hotel"] = st.selectbox("Hotel", HOTELES)
        elif area_info == "Traslados/Transfers":
            incidencia["tipo_traslado"] = st.selectbox("Tipo de Traslado", [
                "Llegada/Arrival", "Salida/Departure",
                "Llegada/Arrival-Pto", "Salida/Departure-Pto", "NO APLICA / DOESN´T APPLY"])

        incidencia["comentario"] = st.text_area("Comentario (máx. 500 caracteres)", max_chars=500)
        incidencia["resolucion"] = st.selectbox("Resolución", RESOLUCIONES)

# ... [resto del código sigue sin cambios salvo si hay más uso de resoluciones que también se puede reemplazar por la lista 'RESOLUCIONES']
