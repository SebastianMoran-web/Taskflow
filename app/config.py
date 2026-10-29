"""
Configuración de la aplicación leída de variables de entorno.
 
Sacar los orígenes CORS a una variable de entorno permite usar un origen
distinto en desarrollo, pruebas y producción sin tocar el código.
"""
import os 

def _parse_origins(raw: str) -> list[str]:

    return[origin.strip() for origin in raw.split(",") if origin.strip()]

CORS_ORIGINS: list[str] = _parse_origins(

    os.getenv("CORS_ORIGINS", "http://localhost:5173")

)