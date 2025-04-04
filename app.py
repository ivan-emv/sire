import streamlit as st

def generar_encabezados_google_sheets():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    # Autenticación
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # Acceder al documento y hoja
    sheet = client.open_by_key("1kBLQAdhYbnP8HTUgpr_rmmGEaOdyMU2tI97ogegrGxY").worksheet("PRUEBA")

    # Encabezados alineados con los campos del formulario
    encabezados = [
        "fecha_inicio", "fecha_registro", "momento_viaje", "localizador", "nombre_usuario", "operador",
        "tipo_contacto", "area", "hotel", "tipo_traslado", "trayecto", "guia",
        "tipo_incidencia", "comentario", "resolucion", "monto", "resultado"
    ]

    # Reemplazar la primera fila por los encabezados
    sheet.delete_rows(1)
    sheet.insert_row(encabezados, 1)

    st.success("✅ Encabezados generados correctamente en la hoja 'PRUEBA'.")

# Mostrar botón en la interfaz
if st.sidebar.button("🔄 Generar encabezados en hoja"):
    generar_encabezados_google_sheets()
