import os
from dotenv import load_dotenv
from supabase import create_client
from passlib.context import CryptContext

# --- Cargar variables del .env --- #
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- Conexión a Supabase --- #
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Seguridad para contraseñas --- #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Función para autenticar usuario (login) --- #
def autenticar_usuario(username: str, password: str):
    resultado = supabase.table("usuarios").select("*").eq("username", username).execute()
    datos = resultado.data

    if not datos:
        return None

    user = datos[0]
    hash_guardado = user.get("hashed_password")

    if not pwd_context.verify(password, hash_guardado):
        return None

    return user  # Si pasó ambas validaciones, retorna el usuario

# --- Función para obtener usuario desde cookie (nombre de usuario) --- #
def obtener_usuario_desde_cookie(username_cookie: str):
    resultado = supabase.table("usuarios").select("*").eq("username", username_cookie).execute()
    datos = resultado.data

    if not datos:
        return None

    return datos[0]
