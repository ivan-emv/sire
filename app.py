import streamlit as st
import datetime

# Inicialización de sesión para múltiples incidencias
def init_session():
    if "incidencias" not in st.session_state:
        st.session_state.incidencias = []
        st.session_state.datos_generales = {}

init_session()

st.set_page_config(page_title="Carga de Incidencias - EMV SIRE", layout="wide")
st.title("📝 Formulario de Incidencias EMV-SIRE 2025")

# BLOQUE 1: Datos generales (solo una vez)
st.subheader("Datos Generales del Servicio")
with st.form(key="form_datos_generales"):
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha de Inicio del Viaje")
        momento_viaje = st.selectbox("Momento del viaje", ["Pre Viaje", "En Ruta", "Post Viaje"])
        localizador = st.text_input("Localizador (código único de reserva)")
    with col2:
        nombre_usuario = st.text_input("Nombre del Usuario que reporta")
        operador = st.selectbox("Operador responsable", ["Operador 1", "Operador 2", "Operador 3"])  # Simulado

    submitted_gen = st.form_submit_button("Confirmar datos generales")
    if submitted_gen:
        fecha_inicio_str = fecha_inicio.strftime("%d/%m/%Y")
        st.session_state.datos_generales = {
            "fecha_inicio": fecha_inicio_str,
            "fecha_registro": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "momento_viaje": momento_viaje,
            "localizador": localizador,
            "nombre_usuario": nombre_usuario,
            "operador": operador,
        }
        st.success("✅ Datos generales registrados correctamente.")

# BLOQUE 2: Carga de incidencias si ya hay datos generales confirmados
if st.session_state.datos_generales:
    st.markdown("---")
    st.subheader("Registrar Incidencia")
    with st.form(key="form_incidencia"):
        tipo_contacto = st.radio("Tipo de contacto", ["Información", "Reclamación", "Otro"])
        area = st.selectbox("Área relacionada", ["Hoteles", "Guías", "Traslados", "Generales"])

        tipo_incidencia = st.selectbox("Tipo de Incidencia", ["Tipo 1", "Tipo 2", "Compensación", "Reembolso"])
        comentario = st.text_area("Comentario")

        if area == "Hoteles":
            hotel = st.selectbox("Hotel", ["Hotel 1", "Hotel 2", "Hotel 3"])
        elif area == "Guías":
            trayecto = st.text_input("Trayecto afectado")
            guia = st.selectbox("Guía", ["Guía 1", "Guía 2", "Guía 3"])
        elif area == "Traslados":
            traslado_tipo = st.selectbox("Tipo de traslado", ["TRF - Aeropuerto", "BUS - Trayecto"])
            if traslado_tipo.startswith("TRF"):
                traslado_comentario = st.text_area("Comentario del traslado")
            else:
                trayecto = st.text_input("Trayecto afectado")
                traslado_comentario = st.text_area("Comentario del bus")
        elif area == "Generales":
            motivo = st.selectbox("Motivo general", ["ITINERARIO - Cambio", "GENERAL - Otro"])
            if motivo.startswith("ITINERARIO"):
                trayecto = st.text_input("Trayecto afectado")
                comentario = st.text_area("Comentario del itinerario")
            else:
                comentario = st.text_area("Comentario general")

        resolucion = st.text_area("Resolución del caso")
        if tipo_incidencia in ["Compensación", "Reembolso"]:
            monto = st.number_input("Monto asociado (€)", min_value=0.0, format="%.2f")
        else:
            monto = None
        resultado = st.text_input("Resultado (responsable de la incidencia)")

        col_add, col_end = st.columns([1, 1])
        agregar = col_add.form_submit_button("➕ Agregar otro caso")
        finalizar = col_end.form_submit_button("✅ Finalizar")

        if agregar or finalizar:
            incidencia = {
                "tipo_contacto": tipo_contacto,
                "area": area,
                "tipo_incidencia": tipo_incidencia,
                "comentario": comentario,
                "resolucion": resolucion,
                "monto": monto,
                "resultado": resultado,
            }
            st.session_state.incidencias.append(incidencia)
            st.success("Incidencia agregada correctamente.")

        if finalizar:
            st.markdown("---")
            st.subheader("Resumen del Registro")
            st.write("**Datos generales:**", st.session_state.datos_generales)
            st.write("**Incidencias cargadas:**", st.session_state.incidencias)
            # Aquí iría la lógica para guardar en base de datos o exportar
            st.success("✅ Registro finalizado. Puedes cerrar la ventana o comenzar un nuevo reporte.")
            st.session_state.clear()
