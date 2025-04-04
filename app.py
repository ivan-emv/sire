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
    if "datos_generales" not in st.session_state:
        st.session_state.datos_generales = {}
    if "form_counter" not in st.session_state:
        st.session_state.form_counter = 0

init_session()

st.set_page_config(page_title="Carga de Incidencias - EMV SIRE", layout="wide")
st.title("📝 Formulario de Incidencias EMV-SIRE 2025")


# --------- Cargar bases desde Google Sheets ---------
@st.cache_data(show_spinner=False)
def cargar_datos_desde_google_sheets():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

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

# Cargar los datos
datos_bd = cargar_datos_desde_google_sheets()

# Preparar los listados con los formatos solicitados
USUARIOS = [u["Nombre"] for u in datos_bd["Usuarios"] if "Nombre" in u]
CIUDADES = [c["Ciudad"] for c in datos_bd["Ciudades"] if "Ciudad" in c]
HOTELES = [h["Nombre Hotel"] for h in datos_bd["Hoteles"] if "Nombre Hotel" in h]
GUIAS = [g["Nombre del Guia"] for g in datos_bd["Guias"] if "Nombre del Guia" in g]
OPERADORES = [o["Nombre del Operador"] for o in datos_bd["Operadores"] if "Nombre del Operador" in o]
TRAYECTOS = [t["Trayecto"] for t in datos_bd["Trayectos"] if "Trayecto" in t]


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
        ciudad = st.selectbox("Ciudad", CIUDADES)

    submitted_gen = st.form_submit_button("Confirmar datos generales")
    if submitted_gen:
        st.session_state.datos_generales = {
            "fecha_inicio": fecha_formateada,
            "fecha_registro": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "ciudad": ciudad,
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

    if tipo_contacto == "Información":
        area_info = st.selectbox("Área Relacionada", [
            "Traslados/Transfers", "Hotel", "Seguro/Insurance", "Itinerario/Itinerary",
            "Equipaje/Luggage", "Felicitación Circuito", "Info Guía/Guide Info",
            "Punto Encuentro/Meeting Point", "Comercial/Commercial", "Enfermedad/Sickness",
            "Opcionales/Optional Tours", "Otros/Other"], key=f"area_info_{idx}")
        incidencia["area"] = area_info

        if area_info == "Hotel":
            incidencia["hotel"] = st.selectbox("Hotel", HOTELES, key=f"hotel_{idx}")
        elif area_info == "Traslados/Transfers":
            incidencia["tipo_traslado"] = st.selectbox("Tipo de Traslado", [
                "Llegada/Arrival", "Salida/Departure",
                "Llegada/Arrival-Pto", "Salida/Departure-Pto", "NO APLICA / DOESN´T APPLY"], key=f"tipo_traslado_{idx}")

        incidencia["comentario"] = st.text_area("Comentario (máx. 500 caracteres)", max_chars=500, key=f"comentario_{idx}")
        incidencia["resolucion"] = st.selectbox("Resolución", RESOLUCIONES, key=f"resolucion_info_{idx}")

    elif tipo_contacto == "Reclamación":
        area_reclamo = st.selectbox("Área Relacionada", ["Hoteles", "Guías", "Traslados", "Generales"], key=f"area_reclamo_{idx}")
        incidencia["area"] = area_reclamo

        if area_reclamo == "Hoteles":
            incidencia["tipo_incidencia"] = st.selectbox("Tipo de Incidencia", [
                "Desayuno/Breakfast", "Limpieza-Bichos/Cleanliness-Bugs", "Comodidad/Comfort",
                "Ubicación/Location", "Mantenimiento General/Overall Maintenance",
                "Habitación/Room", "Robo-Hurto/Theft-Robbery", "Falta Reserva/Reservation Missing",
                "Noches Adicionales/Additional Nights", "Otro/Other"], key=f"tipo_hotel_{idx}")
            incidencia["hotel"] = st.selectbox("Hotel", HOTELES, key=f"hotel_reclamo_{idx}")
            incidencia["comentario"] = st.text_area("Comentario Hotel", max_chars=500, key=f"comentario_hotel_{idx}")

        elif area_reclamo == "Guías":
            incidencia["tipo_incidencia"] = st.selectbox("Tipo de Incidencia", [
                "Actitud/Attitude", "Felicitación/Congratulation", "Conocimiento/Knowledge",
                "Idioma/Language", "Guía Local - Mal Servicio/Local Guide - Poor Service",
                "Pérdida Equipaje/Loss of Luggage", "Versiones Contradictorias/Contradictory Versions",
                "Otro/Other"], key=f"tipo_guia_{idx}")
            incidencia["trayecto"] = st.selectbox("Trayecto", TRAYECTOS, key=f"trayecto_guia_{idx}")
            incidencia["guia"] = st.selectbox("Nombre del Guía", GUIAS, key=f"guia_{idx}")
            incidencia["comentario"] = st.text_area("Comentario Guía", max_chars=500, key=f"comentario_guia_{idx}")

        elif area_reclamo == "Traslados":
            tipo_incidencia = st.selectbox("Tipo de Incidencia", [
                "TRF - No Show - PAX", "TRF - No Show - Transfer", "TRF - Pendiente Datos/Pending data",
                "TRF - Error EMV/EMV´s error", "TRF - Actitud Chófer/Driver´s Attitude",
                "TRF - Versiones Contradictorias/Contradictory Versions", "TRF - No Incluido-Solicitado/Not Included-Requested",
                "TRF - Retraso PAX no notificado/Unnotified PAX Delay", "TRF - Felicitación/Congratulation",
                "TRF - Otro/Other", "BUS - Accidente/Accident", "BUS - Mantenimiento-Falla/Breakdown-Maintenance",
                "BUS - Hurto-Robo en Cabina/Theft-Robbery in the Cabin", "BUS - Comodidad - AC / Comfort - AC",
                "BUS - Actitud Chofer/Driver's Attitude", "BUS - Felicitación/Congratulation", "BUS - Otro/Other"], key=f"tipo_traslados_{idx}")
            incidencia["tipo_incidencia"] = tipo_incidencia
            if tipo_incidencia.startswith("BUS"):
                incidencia["trayecto"] = st.selectbox("Trayecto", TRAYECTOS, key=f"trayecto_bus_{idx}")
            else:
                incidencia["tipo_traslado"] = st.selectbox("Tipo de Traslado", ["Llegada/Arrival", "Salida/Departure", "Llegada/Arrival-Pto", "Salida/Departure-Pto"], key=f"tipo_traslado_trf_{idx}")
            incidencia["comentario"] = st.text_area("Comentario Traslados", max_chars=500, key=f"comentario_traslados_{idx}")

        elif area_reclamo == "Generales":
            tipo_incidencia = st.selectbox("Tipo de Incidencia", [
                "Itinerario - Fuerza Mayor/Force Majeure", "Itinerario - Muchos Idiomas/Several Languages",
                "Itinerario - Parada en Tiendas/Shop Stops", "Itinerario - Itinerario no Seguido/Unfollowed Timetable",
                "Itinerario - Otro/Other", "Asistencia - No relacionado a EMV/No relation to EMV",
                "Bote/Ferry/Crucero - Cambio Itinerario/Itinerary change", "Booking - Error Agente/Agent Error (AGT/TTOO)",
                "Seguro-Call Center - Info Incorrecta/Inaccurate Info", "Equipaje - Demora-Pérdida-Daño/Delay-Loss-Damage",
                "Comidas - Calidad-Cantidad/Quality-Quantity", "Opcionales - No Realizado/Not done",
                "Personal - Enfermedad-Lesión/Illness-Injury", "Otros - General"], key=f"tipo_generales_{idx}")
            incidencia["tipo_incidencia"] = tipo_incidencia
            if tipo_incidencia.startswith("Itinerario"):
                incidencia["trayecto"] = st.selectbox("Trayecto", TRAYECTOS, key=f"trayecto_itinerario_{idx}")
            incidencia["comentario"] = st.text_area("Comentario Generales", max_chars=500, key=f"comentario_generales_{idx}")

        incidencia["resolucion"] = st.selectbox("Resolución", RESOLUCIONES, key=f"resolucion_reclamo_{idx}")
        if incidencia["resolucion"].startswith("Reembolso") or incidencia["resolucion"] == "Compensación/Compensation":
            incidencia["monto"] = st.text_input("Monto compensación o tipo de compensación", key=f"monto_{idx}")
        incidencia["resultado"] = st.selectbox("Resultado", [
            "ERROR EMV", "ERROR OPERADOR/AGENTE VIAJES", "ERROR CLIENTE", "ERROR RECEPTIVO",
            "FUERZA MAYOR", "ASISTENCIA / AYUDA", "MOTIVOS COMERCIALES",
            "QUEJA GENERALIZADA", "FELICITACIÓN"], key=f"resultado_{idx}")

    elif tipo_contacto == "Otro":
        incidencia["comentario"] = st.text_area("Comentario Otros", max_chars=500, key=f"comentario_otro_{idx}")
        incidencia["resolucion"] = st.selectbox("Resolución Otros", RESOLUCIONES, key=f"resolucion_otro_{idx}")

    col1, col2 = st.columns([1, 1])
    if col1.button("➕ Agregar otro caso"):
        st.session_state.incidencias.append(incidencia)
        st.success("Incidencia agregada correctamente.")
        st.session_state.form_counter += 1
        st.rerun()

    if col2.button("✅ Finalizar"):
        st.session_state.incidencias.append(incidencia)
        st.markdown("---")
        st.subheader("Resumen del Registro")
        st.write("**Datos generales:**", st.session_state.datos_generales)
        st.write("**Incidencias cargadas:**", st.session_state.incidencias)
        st.success("✅ Registro finalizado. Puedes cerrar la ventana o comenzar un nuevo reporte.")
        st.session_state.clear()
        st.rerun()
