"""
Configuración de la aplicación leída de variables de entorno.
 
Sacar los orígenes CORS a una variable de entorno permite usar un origen
distinto en desarrollo, pruebas y producción sin tocar el código.
"""
import os 

def _parse_origins(raw: str) -> list[str]:
    """Convierte 'a,b,c' en ['a', 'b', 'c'] ignorando espacios y vacíos."""
    return [origin.strip() for origin in raw.split(",") if origin.strip()]
 
 
# En desarrollo basta el valor por defecto (el frontend de Vite).
# En producción: CORS_ORIGINS="https://miapp.com,https://admin.miapp.com"
CORS_ORIGINS: list[str] = _parse_origins(
    os.getenv("CORS_ORIGINS", "http://localhost:5173")
)
 
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")
DB_TIMEOUT: int = int(os.getenv("DB_TIMEOUT", "30"))