"""Conexión a la base de datos: engine, SessionLocal, Base y get_db()."""
from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL, DB_TIMEOUT

# check_same_thread=False: SQLite no deja usar una conexión desde un hilo
# distinto al que la creó. FastAPI ejecuta los endpoints síncronos en un pool
# de hilos, así que hay que desactivarlo. Es seguro porque cada petición usa
# su propia sesión (get_db) y nunca se comparte entre hilos.
# timeout: segundos que espera SQLite si la BD está bloqueada por otra escritura.
connect_args = (
    {"check_same_thread": False, "timeout": DB_TIMEOUT}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

# Pooling: el engine mantiene un conjunto de conexiones reutilizables (pool)
# en lugar de abrir una nueva por petición.
# pool_pre_ping: comprueba la conexión antes de usarla y abre otra si murió.
# pool_timeout: segundos que espera una petición por una conexión libre del
# pool antes de dar error.
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_timeout=30,
)

# expire_on_commit=False: por defecto, tras un commit SQLAlchemy caduca los
# atributos del objeto y los relee de la BD al usarlos. FastAPI serializa la
# respuesta después del endpoint, lo que provocaría consultas extra. Con False
# el objeto conserva sus valores tras el commit.
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

@event.listens_for(engine, "connect")
def _fk_on(dbapi_conn, _):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()


class Base(DeclarativeBase):
    """Clase base de la que heredan todos los modelos."""


def get_db() -> Generator[Session, None, None]:
    """Da una sesión por petición y garantiza que se cierra.

    FastAPI ejecuta el código hasta el yield antes del endpoint, y el finally
    al terminar la petición, tanto si fue bien como si hubo una excepción.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


