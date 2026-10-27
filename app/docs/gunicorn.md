# Práctica 1.3 — Instalación básica de Gunicorn (TaskFlow)

## 1. Pasos ejecutados

Entorno: máquina virtual Ubuntu, proyecto en `/Taskflow`, backend FastAPI en `/Taskflow/app/main.py`.

### 1.1 Instalar Python 3.13

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev
python3.13 --version
```

Se usa el PPA `deadsnakes` porque el Python por defecto de Ubuntu no es 3.13.

### 1.2 Crear y activar el entorno virtual

```bash
cd /Taskflow
python3.13 -m venv .venv
source .venv/bin/activate
```

El prompt muestra `(.venv)` cuando el entorno está activo.

### 1.3 Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
gunicorn --version
```

### 1.4 Arrancar Gunicorn

Desde `/Taskflow` (la carpeta que contiene `app/`):

```bash
gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
```

### 1.5 Verificar (desde otra terminal de la VM)

```bash
curl http://127.0.0.1:8000/health
```

Respuesta: `{"status":"ok"}`


## 2. Evidencias de funcionamiento

**Gunicorn arrancado** (terminal 1, debe verse `Listening at: http://127.0.0.1:8000` y `Application startup complete`):

![Gunicorn en ejecución](gunicorn-arranque.png)

**Verificación con curl** (terminal 2, dentro de la VM):

![Respuesta de /health](gunicorn-health.png)

```text
sebas@sebas:~$ curl http://127.0.0.1:8000/health
{"status":"ok"}
```

**Endpoint /version** 

![Respuesta de /version](gunicorn-version.png)

**Endpoint /ping**

![Respuesta ping](gunicorn-ping.png)

## 3. Qué hace el comando

```bash
gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
```

| Parte | Significado |
|---|---|
| `gunicorn` | Servidor de aplicaciones (gestor de procesos) para Python |
| `app.main:app` | Carga el módulo `app/main.py` y usa la variable `app` dentro de él (el objeto `FastAPI()`). Formato: `módulo.archivo:variable` |
| `--worker-class uvicorn.workers.UvicornWorker` | Indica qué tipo de worker ejecuta la aplicación: uno basado en Uvicorn |
| `--bind 127.0.0.1:8000` | Escucha en el puerto 8000 solo en la interfaz local; no es accesible desde fuera de la VM |

Gunicorn arranca un proceso maestro que crea workers. Cada worker carga la aplicación y atiende las peticiones.

### Por qué UvicornWorker es obligatorio: WSGI vs ASGI

- **WSGI** es el estándar clásico y **síncrono** entre servidores y aplicaciones Python. La aplicación es una función `app(environ, start_response)` que atiende una petición y devuelve la respuesta.
- **ASGI** es el estándar moderno y **asíncrono**. La aplicación es una función `app(scope, receive, send)`.
- **FastAPI es una aplicación ASGI.**
- **Gunicorn por sí solo solo entiende WSGI.** Sus workers por defecto (`sync`) llaman a la aplicación con la interfaz WSGI, y una app ASGI no responde a esa llamada, así que fallaría.
- **`UvicornWorker` hace de traductor**: es un worker de Gunicorn que internamente ejecuta Uvicorn, que sí habla ASGI. Así Gunicorn gestiona los procesos y Uvicorn ejecuta la aplicación FastAPI.

Sin `--worker-class uvicorn.workers.UvicornWorker`, Gunicorn no puede servir FastAPI correctamente.

## 4. ¿Por qué Gunicorn y no solo Uvicorn?

Uvicorn ya sirve FastAPI por sí solo (`uvicorn app.main:app`), pero está pensado sobre todo como servidor de aplicación, no como gestor de procesos robusto. Gunicorn aporta lo que falta para producción:

- **Varios procesos (workers)** para aprovechar todos los núcleos de CPU y atender más peticiones en paralelo (`--workers N`).
- **Supervisión**: si un worker se cae o se cuelga, el proceso maestro lo detecta y lo reemplaza automáticamente.
- **Reinicios sin cortar el servicio**: se pueden recargar workers y configuración (señal `HUP`) sin parar la aplicación.
- **Control y madurez**: timeouts, reciclado de workers, logs y señales de sistema bien probados durante años, y fácil integración con `systemd`.

En resumen: **Gunicorn gestiona los procesos y Uvicorn ejecuta el código asíncrono**. Se combinan para tener la velocidad de ASGI con la estabilidad de un gestor de procesos de producción.