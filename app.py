# Versión completa con lógica condicional para Información, Reclamación y Otro
import streamlit as st
import datetime
import re

# --------- Datos simulados ---------
USUARIOS = ["Usuario A", "Usuario B", "Usuario C"]
OPERADORES = ["Operador A", "Operador B", "Operador C"]
HOTELES = ["Hotel Alpha", "Hotel Beta", "Hotel Gamma"]
GUIAS = ["Guía 1", "Guía 2", "Guía 3"]
TRAYECTOS = ["Trayecto Madrid - París", "Trayecto Roma - Florencia", "Trayecto Berlín - Praga"]

# --------- Inicializar sesión ---------
def init_session():
    if "incidencias" not in st.session_state:
        st.session_state.incidencias = []
        st.session_state.datos_generales = {}

init_session()

st.set_page_config(page_title="Carga de Incidencias - EMV SIRE", layout="wide")
st.title("📝 Formulario de Incidencias EMV-SIRE 2025")

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

# --------- Formulario de Incidencias ---------
if st.session_state.datos_generales:
    st.markdown("---")
    st.subheader("Registrar Nueva Incidencia")

    tipo_contacto = st.radio("Tipo de contacto", ["Información", "Reclamación", "Otro"], key="tipo_contacto")

    with st.form(key=f"form_incidencia_{len(st.session_state.incidencias)}"):

        if tipo_contacto == "Información":
            area_info = st.selectbox("Área Relacionada", [
                "Traslados/Transfers", "Hotel", "Seguro/Insurance", "Itinerario/Itinerary",
                "Equipaje/Luggage", "Felicitación Circuito", "Info Guía/Guide Info",
                "Punto Encuentro/Meeting Point", "Comercial/Commercial", "Enfermedad/Sickness",
                "Opcionales/Optional Tours", "Otros/Other"])

            if area_info == "Hotel":
                st.selectbox("Hotel", HOTELES)
            elif area_info == "Traslados/Transfers":
                st.selectbox("Tipo de Traslado", [
                    "Llegada/Arrival", "Salida/Departure",
                    "Llegada/Arrival-Pto", "Salida/Departure-Pto", "NO APLICA / DOESN´T APPLY"])

            comentario = st.text_area("Comentario (máx. 500 caracteres)", max_chars=500)
            resolucion = st.text_input("Resolución")

        elif tipo_contacto == "Reclamación":
            area_reclamo = st.selectbox("Área Relacionada", ["Hoteles", "Guías", "Traslados", "Generales"])

            if area_reclamo == "Hoteles":
                st.selectbox("Tipo de Incidencia", [
                    "Desayuno/Breakfast", "Limpieza-Bichos/Cleanliness-Bugs", "Comodidad/Comfort",
                    "Ubicación/Location", "Mantenimiento General/Overall Maintenance",
                    "Habitación/Room", "Robo-Hurto/Theft-Robbery", "Falta Reserva/Reservation Missing",
                    "Noches Adicionales/Additional Nights", "Otro/Other"])
                st.selectbox("Hotel", HOTELES)
                st.text_area("Comentario Hotel", max_chars=500)
                resolucion = st.selectbox("Resolución Hotel", [
                    "Reembolso Parcial/Partial Reimbursement", "Reembolso Total/Total Reimbursement",
                    "Compensación/Compensation", "Descuento Próximo Viaje/Next Trip Discount",
                    "Cambio Itinerario/Itinerary Change", "Cambio Habitación-Hotel/Room-Hotel Change",
                    "Se informa al Pasajero/Passenger Informed", "Se informa al Operador/Operator Informed",
                    "Se informa al Minorista/Agency Informed", "Se informa al Guía/Guide Informed",
                    "Se informa al Transferista/TSP Informed", "Se informa al Receptivo/Local Provider Informed",
                    "Se informa a Departamento/Department Informed"])
                if resolucion.startswith("Reembolso") or resolucion == "Compensación/Compensation":
                    st.number_input("Monto compensación (€)", min_value=0.0, format="%.2f")
                st.selectbox("Resultado Hotel", [
                    "ERROR EMV", "ERROR OPERADOR/AGENTE VIAJES", "ERROR CLIENTE", "ERROR RECEPTIVO",
                    "FUERZA MAYOR", "ASISTENCIA / AYUDA", "MOTIVOS COMERCIALES",
                    "QUEJA GENERALIZADA", "FELICITACIÓN"])

            elif area_reclamo == "Guías":
                st.selectbox("Tipo de Incidencia", [
                    "Actitud/Attitude", "Felicitación/Congratulation", "Conocimiento/Knowledge",
                    "Idioma/Language", "Guía Local - Mal Servicio/Local Guide - Poor Service",
                    "Pérdida Equipaje/Loss of Luggage", "Versiones Contradictorias/Contradictory Versions",
                    "Otro/Other"])
                st.selectbox("Trayecto", TRAYECTOS)
                st.selectbox("Nombre del Guía", GUIAS)
                st.text_area("Comentario Guía", max_chars=500)
                resolucion = st.selectbox("Resolución Guías", [
                    "Reembolso Parcial/Partial Reimbursement", "Reembolso Total/Total Reimbursement",
                    "Compensación/Compensation", "Descuento Próximo Viaje/Next Trip Discount",
                    "Cambio Itinerario/Itinerary Change", "Se informa al Pasajero/Passenger Informed",
                    "Se informa al Operador/Operator Informed", "Se informa al Minorista/Agency Informed",
                    "Se informa al Guía/Guide Informed", "Se informa al Transferista/TSP Informed",
                    "Se informa al Receptivo/Local Provider Informed", "Se informa a Departamento/Department Informed"])
                if resolucion.startswith("Reembolso") or resolucion == "Compensación/Compensation":
                    st.number_input("Monto compensación (€)", min_value=0.0, format="%.2f")
                st.selectbox("Resultado Guías", [
                    "ERROR EMV", "ERROR OPERADOR/AGENTE VIAJES", "ERROR CLIENTE", "ERROR RECEPTIVO",
                    "FUERZA MAYOR", "ASISTENCIA / AYUDA", "MOTIVOS COMERCIALES",
                    "QUEJA GENERALIZADA", "FELICITACIÓN"])

        elif tipo_contacto == "Otro":
            st.text_area("Comentario Otros", max_chars=500)
            st.selectbox("Resolución Otros", [
                "Reembolso Parcial/Partial Reimbursement", "Reembolso Total/Total Reimbursement",
                "Compensación/Compensation", "Descuento Próximo Viaje/Next Trip Discount",
                "Cambio Itinerario/Itinerary Change", "En Estudio/Pending",
                "Se informa al Pasajero/Passenger Informed", "Se informa al Operador/Operator Informed",
                "Se informa al Minorista/Agency Informed", "Se informa al Guía/Guide Informed",
                "Se informa al Transferista/TSP Informed", "Se informa al Receptivo/Local Provider Informed",
                "Se informa a Departamento/Department Informed"])

        col1, col2 = st.columns([1, 1])
        agregar = col1.form_submit_button("➕ Agregar otro caso")
        finalizar = col2.form_submit_button("✅ Finalizar")

        if agregar or finalizar:
            st.session_state.incidencias.append({"tipo_contacto": tipo_contacto, "detalle": "Incidencia registrada"})
            st.success("Incidencia agregada correctamente.")

        if finalizar:
            st.markdown("---")
            st.subheader("Resumen del Registro")
            st.write("**Datos generales:**", st.session_state.datos_generales)
            st.write("**Incidencias cargadas:**", st.session_state.incidencias)
            st.success("✅ Registro finalizado. Puedes cerrar la ventana o comenzar un nuevo reporte.")
            st.session_state.clear()
