import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base

def _uuid():
    return str(uuid.uuid4())

class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    nombre = Column(String, nullable=False)
    nit = Column(String, unique=True, nullable=False)
    plan = Column(String, default="piloto")
    modulos_activos = Column(JSON, default=list)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    sedes = relationship("Sede", back_populates="empresa")
    usuarios = relationship("Usuario", back_populates="empresa")

class Sede(Base):
    __tablename__ = "sedes"
    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    empresa_id = Column(UUID(as_uuid=False), ForeignKey("empresas.id"), nullable=False)
    nombre = Column(String, nullable=False)
    ciudad = Column(String)
    direccion = Column(String)
    empresa = relationship("Empresa", back_populates="sedes")
    activos = relationship("Activo", back_populates="sede")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    empresa_id = Column(UUID(as_uuid=False), ForeignKey("empresas.id"), nullable=False)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    rol = Column(String, nullable=False)
    sede_id = Column(UUID(as_uuid=False), ForeignKey("sedes.id"), nullable=True)
    empresa = relationship("Empresa", back_populates="usuarios")

class Activo(Base):
    __tablename__ = "activos"
    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    empresa_id = Column(UUID(as_uuid=False), ForeignKey("empresas.id"), nullable=False)
    sede_id = Column(UUID(as_uuid=False), ForeignKey("sedes.id"), nullable=False)
    categoria = Column(String, nullable=False)
    codigo_interno = Column(String, nullable=False)
    ubicacion_descripcion = Column(String)
    qr_generado = Column(Boolean, default=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    sede = relationship("Sede", back_populates="activos")
    inspecciones = relationship("Inspeccion", back_populates="activo")

class Inspeccion(Base):
    __tablename__ = "inspecciones"
    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    activo_id = Column(UUID(as_uuid=False), ForeignKey("activos.id"), nullable=False)
    fotos_urls = Column(JSON, default=list)
    resultado_ia = Column(JSON)
    resultado_reglas = Column(JSON)
    hallazgo_texto = Column(Text)
    nivel_riesgo = Column(String)
    estado = Column(String, default="pendiente_validacion")
    responsable_id = Column(UUID(as_uuid=False), ForeignKey("usuarios.id"), nullable=True)
    fecha_limite = Column(DateTime, nullable=True)
    validado_por = Column(UUID(as_uuid=False), ForeignKey("usuarios.id"), nullable=True)
    fecha_validacion = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
    activo = relationship("Activo", back_populates="inspecciones")

class HistorialInspeccion(Base):
    __tablename__ = "historial_inspeccion"
    id = Column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    inspeccion_id = Column(UUID(as_uuid=False), ForeignKey("inspecciones.id"), nullable=False)
    evento = Column(String, nullable=False)
    usuario_id = Column(UUID(as_uuid=False), ForeignKey("usuarios.id"), nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    detalle = Column(Text, nullable=True)
