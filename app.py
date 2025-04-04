import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Autenticación con secrets de Streamlit
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Acceder a la hoja
sheet = client.open_by_key("1kBLQAdhYbnP8HTUgpr_rmmGEaOdyMU2tI97ogegrGxY").worksheet("PRUEBA")

# Lista de encabezados sugeridos
encabezados = [
    "fecha_inicio", "fecha_registro", "momento_viaje", "localizador", "nombre_usuario", "operador",
    "tipo_contacto", "area", "hotel", "tipo_traslado", "trayecto", "guia",
    "tipo_incidencia", "comentario", "resolucion", "monto", "resultado"
]

# Reemplazar encabezado actual
sheet.delete_rows(1)
sheet.insert_row(encabezados, 1)
