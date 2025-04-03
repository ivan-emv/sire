# Versión con lógica condicional dinámica fuera de formularios para visibilidad inmediata
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
        incidencia["resolucion"] = st.text_input("Resolución")

    elif tipo_contacto == "Reclamación":
        area_reclamo = st.selectbox("Área Relacionada", ["Hoteles", "Guías"], key="area_reclamo")
        incidencia["area"] = area_reclamo

        if area_reclamo == "Hoteles":
            incidencia["tipo_incidencia"] = st.selectbox("Tipo de Incidencia", [
                "Desayuno/Breakfast", "Limpieza-Bichos/Cleanliness-Bugs", "Comodidad/Comfort",
                "Ubicación/Location", "Mantenimiento General/Overall Maintenance",
                "Habitación/Room", "Robo-Hurto/Theft-Robbery", "Falta Reserva/Reservation Missing",
                "Noches Adicionales/Additional Nights", "Otro/Other"])
            incidencia["hotel"] = st.selectbox("Hotel", HOTELES)
            incidencia["comentario"] = st.text_area("Comentario Hotel", max_chars=500)
            incidencia["resolucion"] = st.selectbox("Resolución Hotel", [
                "Reembolso Parcial/Partial Reimbursement", "Reembolso Total/Total Reimbursement",
                "Compensación/Compensation", "Descuento Próximo Viaje/Next Trip Discount",
                "Cambio Itinerario/Itinerary Change", "Cambio Habitación-Hotel/Room-Hotel Change",
                "Se informa al Pasajero/Passenger Informed", "Se informa al Operador/Operator Informed",
                "Se informa al Minorista/Agency Informed", "Se informa al Guía/Guide Informed",
                "Se informa al Transferista/TSP Informed", "Se informa al Receptivo/Local Provider Informed",
                "Se informa a Departamento/Department Informed"])
            if incidencia["resolucion"].startswith("Reembolso") or incidencia["resolucion"] == "Compensación/Compensation":
                incidencia["monto"] = st.number_input("Monto compensación (€)", min_value=0.0, format="%.2f")
            incidencia["resultado"] = st.selectbox("Resultado Hotel", [
                "ERROR EMV", "ERROR OPERADOR/AGENTE VIAJES", "ERROR CLIENTE", "ERROR RECEPTIVO",
                "FUERZA MAYOR", "ASISTENCIA / AYUDA", "MOTIVOS COMERCIALES",
                "QUEJA GENERALIZADA", "FELICITACIÓN"])

        elif area_reclamo == "Guías":
            incidencia["tipo_incidencia"] = st.selectbox("Tipo de Incidencia", [
                "Actitud/Attitude", "Felicitación/Congratulation", "Conocimiento/Knowledge",
                "Idioma/Language", "Guía Local - Mal Servicio/Local Guide - Poor Service",
                "Pérdida Equipaje/Loss of Luggage", "Versiones Contradictorias/Contradictory Versions",
                "Otro/Other"])
            incidencia["trayecto"] = st.selectbox("Trayecto", TRAYECTOS)
            incidencia["guia"] = st.selectbox("Nombre del Guía", GUIAS)
            incidencia["comentario"] = st.text_area("Comentario Guía", max_chars=500)
            incidencia["resolucion"] = st.selectbox("Resolución Guías", [
                "Reembolso Parcial/Partial Reimbursement", "Reembolso Total/Total Reimbursement",
                "Compensación/Compensation", "Descuento Próximo Viaje/Next Trip Discount",
                "Cambio Itinerario/Itinerary Change", "Se informa al Pasajero/Passenger Informed",
                "Se informa al Operador/Operator Informed", "Se informa al Minorista/Agency Informed",
                "Se informa al Guía/Guide Informed", "Se informa al Transferista/TSP Informed",
                "Se informa al Receptivo/Local Provider Informed", "Se informa a Departamento/Department Informed"])
            if incidencia["resolucion"].startswith("Reembolso") or incidencia["resolucion"] == "Compensación/Compensation":
                incidencia["monto"] = st.number_input("Monto compensación (€)", min_value=0.0, format="%.2f")
            incidencia["resultado"] = st.selectbox("Resultado Guías", [
                "ERROR EMV", "ERROR OPERADOR/AGENTE VIAJES", "ERROR CLIENTE", "ERROR RECEPTIVO",
                "FUERZA MAYOR", "ASISTENCIA / AYUDA", "MOTIVOS COMERCIALES",
                "QUEJA GENERALIZADA", "FELICITACIÓN"])

    elif tipo_contacto == "Otro":
        incidencia["comentario"] = st.text_area("Comentario Otros", max_chars=500)
        incidencia["resolucion"] = st.selectbox("Resolución Otros", [
            "Reembolso Parcial/Partial Reimbursement", "Reembolso Total/Total Reimbursement",
            "Compensación/Compensation", "Descuento Próximo Viaje/Next Trip Discount",
            "Cambio Itinerario/Itinerary Change", "En Estudio/Pending",
            "Se informa al Pasajero/Passenger Informed", "Se informa al Operador/Operator Informed",
            "Se informa al Minorista/Agency Informed", "Se informa al Guía/Guide Informed",
            "Se informa al Transferista/TSP Informed", "Se informa al Receptivo/Local Provider Informed",
            "Se informa a Departamento/Department Informed"])

    col1, col2 = st.columns([1, 1])
    if col1.button("➕ Agregar otro caso"):
        st.session_state.incidencias.append(incidencia)
        st.success("Incidencia agregada correctamente.")

    if col2.button("✅ Finalizar"):
        st.session_state.incidencias.append(incidencia)
        st.markdown("---")
        st.subheader("Resumen del Registro")
        st.write("**Datos generales:**", st.session_state.datos_generales)
        st.write("**Incidencias cargadas:**", st.session_state.incidencias)
        st.success("✅ Registro finalizado. Puedes cerrar la ventana o comenzar un nuevo reporte.")
        st.session_state.clear()
