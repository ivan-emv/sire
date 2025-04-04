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
    "Se informa a Departamento/Department Informed"]


# --------- Inicializar sesión ---------
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

# 🔧 Ocultar la barra superior y el menú de Streamlit
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

# --------- Selector de Modo ---------

modo = st.sidebar.radio("Selecciona una opción", [
    "📝 Carga de Incidencias",
    "🔍 Búsqueda de Registros"
] + (["🛠️ Gestión de Registros"] if st.session_state.admin_autenticado else []))

if modo == "📝 Carga de Incidencias":
    
    
    
    
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
        for nombre in ["Ciudades", "Hoteles", "Guias", "Operadores", "Trayectos", "Usuarios", "ADMIN"]:
            worksheet = client.open_by_key(sheet_id).worksheet(nombre)
            datos[nombre] = worksheet.get_all_records()

        return datos

    # Botón para forzar recarga de datos desde Google Sheets
    if st.sidebar.button("🔄 Actualizar Datos"):
        st.cache_data.clear()

    datos_bd = cargar_datos_desde_google_sheets()

    # --------- Autenticación de Administrador ---------
    def autenticar_admin(usuario, password):
        admin_users = datos_bd.get("ADMIN", [])
        for admin in admin_users:
            if admin.get("Usuario") == usuario and admin.get("Password") == password:
                return True
        return False

    if "admin_autenticado" not in st.session_state:
        st.session_state.admin_autenticado = False
    if "admin_usuario" not in st.session_state:
        st.session_state.admin_usuario = ""

    if not st.session_state.admin_autenticado:
        with st.sidebar.expander("🔐 Acceso Administrador"):
            admin_user = st.text_input("Usuario")
            admin_pass = st.text_input("Contraseña", type="password")
            if st.button("Iniciar Sesión"):
                if autenticar_admin(admin_user, admin_pass):
                    st.session_state.admin_autenticado = True
                    st.session_state.admin_usuario = admin_user
                    st.success(f"Acceso concedido. Bienvenido, {admin_user}.")
                else:
                    st.error("Credenciales incorrectas.")
    else:
        st.sidebar.success(f"🔓 Acceso Administrador: {st.session_state.admin_usuario}")


    # Preparar los listados con los formatos solicitados
    USUARIOS = [u["Nombre"] for u in datos_bd["Usuarios"] if "Nombre" in u]
    CIUDADES = [c["Ciudad"] for c in datos_bd["Ciudades"] if "Ciudad" in c]
    HOTELES = [h["Nombre Hotel"] for h in datos_bd["Hoteles"] if "Nombre Hotel" in h]
    GUIAS = [g["Nombre del Guia"] for g in datos_bd["Guias"] if "Nombre del Guia" in g]
    OPERADORES = [o["Nombre del Operador"] for o in datos_bd["Operadores"] if "Nombre del Operador" in o]
    TRAYECTOS = [t["Trayecto"] for t in datos_bd["Trayectos"] if "Trayecto" in t]

    USUARIOS = [u["Nombre"] for u in datos_bd["Usuarios"] if "Nombre" in u]
    CIUDADES = [c["Ciudad"] for c in datos_bd["Ciudades"] if "Ciudad" in c]
    HOTELES = [h["Nombre Hotel"] for h in datos_bd["Hoteles"] if "Nombre Hotel" in h]
    GUIAS = [g["Nombre del Guia"] for g in datos_bd["Guias"] if "Nombre del Guia" in g]
    OPERADORES = [o["Nombre del Operador"] for o in datos_bd["Operadores"] if "Nombre del Operador" in o]
    TRAYECTOS = [t["Trayecto"] for t in datos_bd["Trayectos"] if "Trayecto" in t]
    
    
    # --------- Función para guardar en Google Sheets ---------
    def guardar_en_google_sheets(datos_generales, lista_incidencias):
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
    
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
            ciudad = st.selectbox("Ciudad", CIUDADES)
            operador = st.selectbox("Operador", OPERADORES)

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
            area_reclamo = st.selectbox("Área Relacionada", ["Hotel", "Guías/Guides", "Traslados/Transfers", "Generales/General"], key=f"area_reclamo_{idx}")
            incidencia["area"] = area_reclamo
    
            if area_reclamo == "Hotel":
                incidencia["tipo_incidencia"] = st.selectbox("Tipo de Incidencia", [
                    "Desayuno/Breakfast", "Limpieza-Bichos/Cleanliness-Bugs", "Comodidad/Comfort",
                    "Ubicación/Location", "Mantenimiento General/Overall Maintenance",
                    "Habitación/Room", "Robo-Hurto/Theft-Robbery", "Falta Reserva/Reservation Missing",
                    "Noches Adicionales/Additional Nights", "Otro/Other"], key=f"tipo_hotel_{idx}")
                incidencia["hotel"] = st.selectbox("Hotel", HOTELES, key=f"hotel_reclamo_{idx}")
                incidencia["comentario"] = st.text_area("Comentario Hotel", max_chars=500, key=f"comentario_hotel_{idx}")
    
            elif area_reclamo == "Guías/Guides":
                incidencia["tipo_incidencia"] = st.selectbox("Tipo de Incidencia", [
                    "Actitud/Attitude", "Felicitación/Congratulation", "Conocimiento/Knowledge",
                    "Idioma/Language", "Guía Local - Mal Servicio/Local Guide - Poor Service",
                    "Pérdida Equipaje/Loss of Luggage", "Versiones Contradictorias/Contradictory Versions",
                    "Otro/Other"], key=f"tipo_guia_{idx}")
                incidencia["trayecto"] = st.selectbox("Trayecto", TRAYECTOS, key=f"trayecto_guia_{idx}")
                incidencia["guia"] = st.selectbox("Nombre del Guía", GUIAS, key=f"guia_{idx}")
                incidencia["comentario"] = st.text_area("Comentario Guía", max_chars=500, key=f"comentario_guia_{idx}")
    
            elif area_reclamo == "Traslados/Transfers":
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
    
            elif area_reclamo == "Generales/General":
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

            st.write("🧾 Datos generales:", st.session_state.datos_generales)
            st.write("📦 Incidencias:", st.session_state.incidencias)

            try:
                guardar_en_google_sheets(st.session_state.datos_generales, st.session_state.incidencias)
            except Exception as e:
                st.error(f"❌ Error al guardar en Google Sheets: {e}")

            st.markdown("---")
            st.subheader("Resumen del Registro")
            st.write("**Datos generales:**", st.session_state.datos_generales)
            st.write("**Incidencias cargadas:**", st.session_state.incidencias)
            st.success("✅ Registro finalizado. Puedes cerrar la ventana o comenzar un nuevo reporte.")
            st.session_state.clear()
            st.rerun()

    
    
    
    
    # --------- Búsqueda de Registros ---------
elif modo == "🔍 Búsqueda de Registros":

    st.header("🔍 Consulta de Incidencias por Usuario y Localizador")
    with st.expander("🔎 FILTROS", expanded=False):
        st.write("Opciones de filtro")

    st.header("🔍 Consulta de Incidencias por Usuario y Localizador")

    # @st.cache_data (eliminado para forzar recarga dinámica)(show_spinner=False)
    def cargar_datos_busqueda():
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        import pandas as pd
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
        localizadores = sorted(df_busqueda["localizador"].dropna().unique())

        col1, col2 = st.columns(2)
        with col1:
            usuario_sel = st.selectbox("Selecciona el Usuario", [""] + list(usuarios))
        with col2:
            localizador_sel = st.text_input("Escribe el Localizador")

        # --------- Filtrado flexible por Usuario y/o Localizador ---------
        filtro_usuario = usuario_sel.strip() != ""
        filtro_localizador = localizador_sel.strip() != ""

        # --------- Filtros adicionales ---------.unique()))


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
            filtrado = df_busqueda.copy()  # Mostrar todo si no se completa ningún filtro

        
        if momento_sel:
            filtrado = filtrado[filtrado["momento_viaje"] == momento_sel]
        if operador_sel:
            filtrado = filtrado[filtrado["operador"] == operador_sel]
        if ciudad_sel:
            filtrado = filtrado[filtrado["ciudad"] == ciudad_sel]
        if tipo_contacto_sel:
            filtrado = filtrado[filtrado["tipo_contacto"] == tipo_contacto_sel]
        if area_sel:
            filtrado = filtrado[filtrado["area"] == area_sel]
        if tipo_traslado_sel:
            filtrado = filtrado[filtrado["tipo_traslado"] == tipo_traslado_sel]
        if hotel_sel:
            filtrado = filtrado[filtrado["hotel"] == hotel_sel]
        if trayecto_sel:
            filtrado = filtrado[filtrado["trayecto"] == trayecto_sel]
        if resolucion_sel:
            filtrado = filtrado[filtrado["resolucion"] == resolucion_sel]
        if resultado_sel:
            filtrado = filtrado[filtrado["resultado"] == resultado_sel]

        # --------- Mostrar resultados ---------
        if not filtrado.empty:
            st.success(f"Se encontraron {len(filtrado)} registros.")
            st.dataframe(filtrado, use_container_width=True)
        else:
            st.info("No se encontraron registros con esos criterios.")



# --------- Gestión de Registros (solo para administradores) ---------
elif modo == "🛠️ Gestión de Registros" and st.session_state.admin_autenticado:
    st.header("🛠️ Gestión de Registros (Administrador)")
    with st.expander("🔎 FILTROS", expanded=False):
    st.write("Opciones de filtro")

    st.header("🛠️ Gestión de Registros (Administrador)")

    def cargar_datos_admin():
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        import pandas as pd
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        hoja = client.open_by_key("1aaGedbCfPfLqktmNQEVoiC0cphs-iKlmz9IKGcKNvUE").worksheet("DATOS")
        datos = hoja.get_all_records()
        return pd.DataFrame(datos), hoja

    df_admin, hoja_admin = cargar_datos_admin()

    if df_admin.empty:
        st.warning("No hay registros en la base de datos.")
    else:
        st.success(f"Se encontraron {len(df_admin)} registros en la base de datos.")

        # --------- Filtros similares a 'Búsqueda de Registros' ---------
        usuarios = sorted(df_admin["nombre_usuario"].dropna().unique())
        localizadores = sorted(df_admin["localizador"].dropna().unique())

        col1, col2 = st.columns(2)
        with col1:
            usuario_sel = st.selectbox("Selecciona el Usuario", [""] + list(usuarios), key="admin_usuario")
        with col2:
            localizador_sel = st.text_input("Escribe el Localizador", key="admin_localizador")

        filtro_usuario = usuario_sel.strip() != ""
        filtro_localizador = localizador_sel.strip() != ""

        col3, col4, col5 = st.columns(3)
        with col3:
            momento_sel = st.selectbox("Momento del Viaje", [""] + sorted(df_admin["momento_viaje"].dropna().unique()), key="admin_momento")
        with col4:
            operador_sel = st.selectbox("Operador", [""] + sorted(df_admin["operador"].dropna().unique()), key="admin_operador")
        with col5:
            ciudad_sel = st.selectbox("Ciudad", [""] + sorted(df_admin["ciudad"].dropna().unique()), key="admin_ciudad")

        col6, col7, col8 = st.columns(3)
        with col6:
            tipo_contacto_sel = st.selectbox("Tipo de Contacto", [""] + sorted(df_admin["tipo_contacto"].dropna().unique()), key="admin_tipo_contacto")
        with col7:
            area_sel = st.selectbox("Área Relacionada", [""] + sorted(df_admin["area"].dropna().unique()), key="admin_area")
        with col8:
            trayecto_sel = st.selectbox("Trayecto", [""] + sorted(df_admin["trayecto"].dropna().unique()), key="admin_trayecto")

        tipo_traslado_sel = ""
        hotel_sel = ""
        if area_sel.strip() == "Traslados/Transfers":
            tipo_traslado_sel = st.selectbox("Tipo de Traslado", [""] + sorted(df_admin["tipo_traslado"].dropna().unique()), key="admin_tipo_traslado")
        if area_sel.strip() == "Hoteles":
            hotel_sel = st.selectbox("Nombre del Hotel", [""] + sorted(df_admin["hotel"].dropna().unique()), key="admin_hotel")

        col9, col10 = st.columns(2)
        with col9:
            resolucion_sel = st.selectbox("Resolución", [""] + sorted(df_admin["resolucion"].dropna().unique()), key="admin_resolucion")
        with col10:
            resultado_sel = st.selectbox("Resultado", [""] + sorted(df_admin["resultado"].dropna().unique()), key="admin_resultado")

        filtrado = df_admin.copy()
        if filtro_usuario:
            filtrado = filtrado[filtrado["nombre_usuario"] == usuario_sel]
        if filtro_localizador:
            filtrado = filtrado[filtrado["localizador"] == localizador_sel]
        if momento_sel:
            filtrado = filtrado[filtrado["momento_viaje"] == momento_sel]
        if operador_sel:
            filtrado = filtrado[filtrado["operador"] == operador_sel]
        if ciudad_sel:
            filtrado = filtrado[filtrado["ciudad"] == ciudad_sel]
        if tipo_contacto_sel:
            filtrado = filtrado[filtrado["tipo_contacto"] == tipo_contacto_sel]
        if area_sel:
            filtrado = filtrado[filtrado["area"] == area_sel]
        if tipo_traslado_sel:
            filtrado = filtrado[filtrado["tipo_traslado"] == tipo_traslado_sel]
        if hotel_sel:
            filtrado = filtrado[filtrado["hotel"] == hotel_sel]
        if trayecto_sel:
            filtrado = filtrado[filtrado["trayecto"] == trayecto_sel]
        if resolucion_sel:
            filtrado = filtrado[filtrado["resolucion"] == resolucion_sel]
        if resultado_sel:
            filtrado = filtrado[filtrado["resultado"] == resultado_sel]

        st.markdown("---")
        st.dataframe(filtrado, use_container_width=True)

        st.dataframe(df_admin, use_container_width=True)
        st.info("🧱 Próxima fase: edición en línea o eliminación de registros.")
