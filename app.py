# Versión mejorada con control condicional total y fecha formateada dentro del input
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
    if "fecha_input" not in st.session_state:
        st.session_state.fecha_input = ""

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

        st.session_state.fecha_input = st.text_input(
            "Fecha de Inicio del Viaje (DD/MM/YYYY)",
            value=formatear_fecha(st.session_state.fecha_input),
            max_chars=10,
            key="fecha_input"
        )

        momento_viaje = st.selectbox("Momento del viaje", ["Pre Viaje", "En Ruta", "Post Viaje"])
        localizador = st.text_input("Localizador (código único de reserva)")
    with col2:
        nombre_usuario = st.selectbox("Nombre del Usuario", USUARIOS)
        operador = st.selectbox("Operador", OPERADORES)

    submitted_gen = st.form_submit_button("Confirmar datos generales")
    if submitted_gen:
        st.session_state.datos_generales = {
            "fecha_inicio": st.session_state.fecha_input,
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

    tipo_contacto = st.radio("Tipo de contacto", ["Información", "Reclamación", "Otro"])

    if tipo_contacto == "Información":
        area_info = st.selectbox("Área Relacionada", [
            "Traslados/Transfers", "Hotel", "Seguro/Insurance", "Itinerario/Itinerary",
            "Equipaje/Luggage", "Felicitación Circuito", "Info Guía/Guide Info",
            "Punto Encuentro/Meeting Point", "Comercial/Commercial", "Enfermedad/Sickness",
            "Opcionales/Optional Tours", "Otros/Other"])

        with st.form(key=f"form_info_{len(st.session_state.incidencias)}"):
            if area_info == "Hotel":
                st.selectbox("Hotel", HOTELES)
            elif area_info == "Traslados/Transfers":
                st.selectbox("Tipo de Traslado", [
                    "Llegada/Arrival", "Salida/Departure",
                    "Llegada/Arrival-Pto", "Salida/Departure-Pto", "NO APLICA / DOESN´T APPLY"])

            comentario = st.text_area("Comentario (máx. 500 caracteres)", max_chars=500)
            resolucion = st.text_input("Resolución")

            col1, col2 = st.columns([1, 1])
            agregar = col1.form_submit_button("➕ Agregar otro caso")
            finalizar = col2.form_submit_button("✅ Finalizar")

            if agregar or finalizar:
                st.session_state.incidencias.append({
                    "tipo_contacto": tipo_contacto,
                    "area": area_info,
                    "comentario": comentario,
                    "resolucion": resolucion
                })
                st.success("Incidencia agregada correctamente.")

            if finalizar:
                st.markdown("---")
                st.subheader("Resumen del Registro")
                st.write("**Datos generales:**", st.session_state.datos_generales)
                st.write("**Incidencias cargadas:**", st.session_state.incidencias)
                st.success("✅ Registro finalizado. Puedes cerrar la ventana o comenzar un nuevo reporte.")
                st.session_state.clear()

    # Aquí se podrá continuar la lógica para Reclamación y Otro con sus respectivas condiciones
