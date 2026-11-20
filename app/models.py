"""Modelos ORM (SQLAlchemy, estilo declarativo).

Un ORM mapea cada clase a una tabla y cada atributo a una columna, de modo que
se trabaja con objetos en lugar de escribir SQL. Los modelos definen cómo se
guarda el dato en la BD; los schemas (schemas.py) definen cómo viaja por HTTP.

Relaciones 1—N: Project -> Task, Category -> Task, User -> Task.
No hay relación entre User y Project porque todos los usuarios pueden acceder
a todos los proyectos.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from pydantic import BaseModel

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")  # "user" o "admin"
    email: Mapped[str] = mapped_column(String(120), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Tareas asignadas al usuario. Sin cascade de borrado: eliminar un usuario
    # no debe eliminar sus tareas.
    tasks: Mapped[list["Task"]] = relationship(back_populates="assignee")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # DECISIÓN (Práctica 1.6): BORRADO EN CASCADA.
    # Una tarea no tiene sentido sin proyecto (project_id es obligatorio), así
    # que al borrar el proyecto se borran sus tareas.
    # - ORM: cascade="all, delete-orphan"
    # - BD:  ondelete="CASCADE" en Task.project_id
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    # DECISIÓN (Práctica 1.6): BLOQUEO.
    # La categoría es solo una etiqueta: borrarla no debe destruir tareas ni
    # dejarlas huérfanas. Si tiene tareas, el router responde 409. Como red de
    # seguridad, la BD usa ondelete="RESTRICT" en Task.category_id.
    tasks: Mapped[list["Task"]] = relationship(back_populates="category")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # FK obligatoria a Project (criterio de aceptación).
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE")
    )
    # FKs opcionales: una tarea puede no tener categoría ni responsable.
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT")
    )
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    # Lado "muchos" de cada relación. back_populates enlaza los dos lados: al
    # asignar task.project = p, SQLAlchemy actualiza también p.tasks.
    project: Mapped["Project"] = relationship(back_populates="tasks")
    category: Mapped[Optional["Category"]] = relationship(back_populates="tasks")
    assignee: Mapped[Optional["User"]] = relationship(back_populates="tasks")