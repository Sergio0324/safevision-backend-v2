"""Capa de persistencia en PostgreSQL."""

from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.db.models import Activo, Inspeccion
from app.models.schemas import InspeccionOut, VisionResult, RulesResult


def obtener_o_crear_activo(
    db: Session, empresa_id: str, sede_id: str, categoria: str, ubicacion_descripcion: str,
) -> Activo:
    """Busca un activo con esa descripción, o crea uno nuevo."""
    activo = (
        db.query(Activo)
        .filter_by(
            empresa_id=empresa_id, sede_id=sede_id,
            categoria=categoria, ubicacion_descripcion=ubicacion_descripcion
        )
        .first()
    )
    if activo:
        return activo

    total = db.query(Activo).filter_by(empresa_id=empresa_id, categoria=categoria).count()
    codigo = f"{categoria[:3].upper()}-{total + 1:03d}"

    activo = Activo(
        empresa_id=empresa_id, sede_id=sede_id, categoria=categoria,
        codigo_interno=codigo, ubicacion_descripcion=ubicacion_descripcion,
    )
    db.add(activo)
    db.commit()
    db.refresh(activo)
    return activo

def guardar_inspeccion(
    db: Session, activo: Activo, foto_url: str,
    resultado_ia: VisionResult, resultado_reglas: RulesResult, hallazgo_texto: str,
creado_en: datetime) -> InspeccionOut:
    """Guarda la inspección completa en la BD."""
    inspeccion = Inspeccion(
        activo_id=activo.id,
        fotos_urls=[foto_url],
        resultado_ia=resultado_ia.model_dump(),
        resultado_reglas=resultado_reglas.model_dump(),
        hallazgo_texto=hallazgo_texto,
        nivel_riesgo=resultado_reglas.nivel_riesgo,
        creado_en=datetime.now(timezone.utc),
        estado="pendiente_validacion",
    )
    db.add(inspeccion)
    db.commit()
    db.refresh(inspeccion)
    return _a_inspeccion_out(inspeccion, activo)

def obtener_inspeccion(db: Session, inspeccion_id: str, empresa_id: str):
    """Obtiene una inspección (con control de tenant)."""
    inspeccion = db.query(Inspeccion).filter_by(id=inspeccion_id).first()
    if inspeccion is None or inspeccion.activo.empresa_id != empresa_id:
        return None
    return _a_inspeccion_out(inspeccion, inspeccion.activo)

def listar_inspecciones(db: Session, empresa_id: str, estado: str | None = None):
    """Lista inspecciones de una empresa."""
    query = db.query(Inspeccion).join(Activo).filter(Activo.empresa_id == empresa_id)
    if estado:
        query = query.filter(Inspeccion.estado == estado)
    return [_a_inspeccion_out(i, i.activo) for i in query.all()]

def actualizar_validacion(db: Session, inspeccion_id: str, empresa_id: str, **cambios):
    """Actualiza la validación de una inspección."""
    inspeccion = db.query(Inspeccion).filter_by(id=inspeccion_id).first()
    if inspeccion is None or inspeccion.activo.empresa_id != empresa_id:
        return None
    for campo, valor in cambios.items():
        setattr(inspeccion, campo, valor)
    db.commit()
    db.refresh(inspeccion)
    return _a_inspeccion_out(inspeccion, inspeccion.activo)

def _a_inspeccion_out(inspeccion: Inspeccion, activo: Activo) -> InspeccionOut:
    """Convierte modelo BD a esquema de respuesta."""
    return InspeccionOut(
        id=inspeccion.id,
        empresa_id=activo.empresa_id,
        sede_id=activo.sede_id,
        categoria=activo.categoria,
        foto_url=inspeccion.fotos_urls[0] if inspeccion.fotos_urls else "",
        resultado_ia=VisionResult(**inspeccion.resultado_ia),
        resultado_reglas=RulesResult(**inspeccion.resultado_reglas),
        hallazgo_texto=inspeccion.hallazgo_texto,
        estado=inspeccion.estado,
        responsable_id=inspeccion.responsable_id,
        fecha_limite=inspeccion.fecha_limite,
        validado_por=inspeccion.validado_por,
        fecha_validacion=inspeccion.fecha_validacion,
        creado_en=inspeccion.creado_en,
    )
