from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional, List

class Categoria(str, Enum):
    extintores = "extintores"
    epp = "epp"

class EstadoHallazgo(str, Enum):
    pendiente_validacion = "pendiente_validacion"
    validado = "validado"
    corregido = "corregido"
    en_gestion = "en_gestion"
    cerrado = "cerrado"

class VisionResult(BaseModel):
    categoria: Categoria
    datos: dict
    confianza_general: float

class Incumplimiento(BaseModel):
    tipo: str
    riesgo: str
    norma: str
    requiere_revision_manual: bool = False

class RulesResult(BaseModel):
    nivel_riesgo: str
    incumplimientos: List[Incumplimiento]
    acciones_sugeridas: List[str]

class InspeccionOut(BaseModel):
    id: str
    empresa_id: str
    sede_id: str
    categoria: str
    foto_url: str
    resultado_ia: VisionResult
    resultado_reglas: RulesResult
    hallazgo_texto: str
    estado: str
    responsable_id: Optional[str] = None
    fecha_limite: Optional[datetime] = None
    validado_por: Optional[str] = None
    fecha_validacion: Optional[datetime] = None
    creado_en: datetime

class ValidacionRequest(BaseModel):
    accion: str  # "validar" o "corregir"
    hallazgo_texto_corregido: Optional[str] = None
    nivel_riesgo_corregido: Optional[str] = None
    responsable_id: Optional[str] = None
    fecha_limite: Optional[datetime] = None
