from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.security import UsuarioActual, get_current_user
from app.db import storage
from app.db.session import get_db
from app.models.schemas import Categoria, EstadoHallazgo, InspeccionOut, ValidacionRequest
from app.services import redactor, rules_engine, vision_engine
from app.services.almacenamiento_fotos import subir_foto

router = APIRouter(prefix="/api/v1/inspecciones", tags=["inspecciones"])

@router.post("", response_model=InspeccionOut, status_code=201)
async def crear_inspeccion(
    sede_id: str = Form(...),
    categoria: Categoria = Form(...),
    ubicacion_descripcion: str = Form(...),
    foto: UploadFile = File(...),
    usuario: UsuarioActual = Depends(get_current_user),
    creado_en=datetime.now(timezone.utc),
    db: Session = Depends(get_db),
):
    """Crea una inspección: foto → IA → reglas → BD."""
    
    foto_bytes = await foto.read()
    
    if len(foto_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Imagen muy grande (máx 10MB)")

    activo = storage.obtener_o_crear_activo(
        db, empresa_id=usuario.empresa_id, sede_id=sede_id,
        categoria=categoria.value, ubicacion_descripcion=ubicacion_descripcion,
    )

    foto_url = await subir_foto(foto_bytes, empresa_id=usuario.empresa_id)

    try:
        resultado_ia = await vision_engine.analizar_foto(foto_bytes, categoria)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error IA: {str(e)}")

    resultado_reglas = rules_engine.evaluar(resultado_ia)
    hallazgo_texto = await redactor.redactar_hallazgo(categoria, resultado_reglas)

    return storage.guardar_inspeccion(
        db, activo=activo, foto_url=foto_url,
        resultado_ia=resultado_ia, resultado_reglas=resultado_reglas,
        hallazgo_texto=hallazgo_texto,
        creado_en=datetime.now(timezone.utc)
    )

@router.get("", response_model=list[InspeccionOut])
async def listar_inspecciones(
    estado: EstadoHallazgo | None = Query(default=None),
    usuario: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista inspecciones de la empresa."""
    return storage.listar_inspecciones(db, empresa_id=usuario.empresa_id, estado=estado.value if estado else None)

@router.get("/{inspeccion_id}", response_model=InspeccionOut)
async def obtener_inspeccion(
    inspeccion_id: str,
    usuario: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene detalle de una inspección."""
    inspeccion = storage.obtener_inspeccion(db, inspeccion_id, empresa_id=usuario.empresa_id)
    if inspeccion is None:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    return inspeccion

@router.patch("/{inspeccion_id}/validar", response_model=InspeccionOut)
async def validar_inspeccion(
    inspeccion_id: str,
    validacion: ValidacionRequest,
    usuario: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """El auditor valida o corrige un hallazgo."""
    
    campos = {}
    
    if validacion.accion == "corregir":
        if validacion.hallazgo_texto_corregido:
            campos["hallazgo_texto"] = validacion.hallazgo_texto_corregido
        if validacion.nivel_riesgo_corregido:
            campos["nivel_riesgo"] = validacion.nivel_riesgo_corregido
        campos["estado"] = EstadoHallazgo.corregido.value
    else:
        campos["estado"] = EstadoHallazgo.validado.value

    campos["validado_por"] = usuario.id
    campos["fecha_validacion"] = datetime.utcnow()

    if validacion.responsable_id:
        campos["responsable_id"] = validacion.responsable_id
        campos["fecha_limite"] = validacion.fecha_limite
        campos["estado"] = EstadoHallazgo.en_gestion.value

    inspeccion = storage.actualizar_validacion(
        db, inspeccion_id, empresa_id=usuario.empresa_id, **campos,
    )
    if inspeccion is None:
        raise HTTPException(status_code=404, detail="Inspección no encontrada")
    return inspeccion
