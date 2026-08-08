from app.models.schemas import VisionResult, RulesResult, Incumplimiento

def evaluar(resultado_ia: VisionResult) -> RulesResult:
    """Aplica las reglas de negocio según la categoría."""
    
    if resultado_ia.categoria.value == "extintores":
        return _evaluar_extintores(resultado_ia.datos)
    elif resultado_ia.categoria.value == "epp":
        return _evaluar_epp(resultado_ia.datos)
    else:
        return RulesResult(nivel_riesgo="no_evaluado", incumplimientos=[], acciones_sugeridas=[])

def _evaluar_extintores(datos: dict) -> RulesResult:
    """Reglas para extintores según normas colombianas."""
    incumplimientos = []
    nivel_maximo = "bajo"
    
    # No existe
    if not datos.get("existe"):
        incumplimientos.append(Incumplimiento(
            tipo="no_existe", riesgo="critico", norma="Decreto 1072 Art. 2.2.4.6.24"
        ))
        nivel_maximo = "critico"
    
    # Manómetro en rojo
    if datos.get("manometro") == "rojo":
        incumplimientos.append(Incumplimiento(
            tipo="manometro_rojo", riesgo="critico", norma="Resolución 0312 de 2019"
        ))
        nivel_maximo = "critico"
    
    # Fuga
    if "fuga" in datos.get("estado_fisico", []):
        incumplimientos.append(Incumplimiento(
            tipo="fuga", riesgo="critico", norma="NTC 2885"
        ))
        nivel_maximo = "critico"
    
    # Sin pasador / sin sello / obstruido
    if datos.get("pasador_seguridad") == "ausente":
        incumplimientos.append(Incumplimiento(
            tipo="sin_pasador", riesgo="alto", norma="Decreto 1072"
        ))
        if nivel_maximo not in ["critico"]:
            nivel_maximo = "alto"
    
    if datos.get("sello_inviolabilidad") == "ausente":
        incumplimientos.append(Incumplimiento(
            tipo="sin_sello", riesgo="alto", norma="NTC 2885"
        ))
        if nivel_maximo not in ["critico"]:
            nivel_maximo = "alto"
    
    if "obstruido" in datos.get("estado_fisico", []):
        incumplimientos.append(Incumplimiento(
            tipo="obstruido", riesgo="alto", norma="Decreto 1072"
        ))
        if nivel_maximo not in ["critico"]:
            nivel_maximo = "alto"
    
    # En el piso / sin soporte / sin señalización
    if "en_el_piso" in datos.get("estado_fisico", []) or "sin_soporte" in datos.get("estado_fisico", []):
        incumplimientos.append(Incumplimiento(
            tipo="sin_soporte", riesgo="medio", norma="Resolución 0312"
        ))
        if nivel_maximo == "bajo":
            nivel_maximo = "medio"
    
    if datos.get("senalizacion") == "ausente":
        incumplimientos.append(Incumplimiento(
            tipo="sin_senalizacion", riesgo="medio", norma="Resolución 0312"
        ))
        if nivel_maximo == "bajo":
            nivel_maximo = "medio"
    
    # Corrosión
    if "corrosion" in datos.get("estado_fisico", []):
        incumplimientos.append(Incumplimiento(
            tipo="corrosion", riesgo="bajo", norma="NTC 2885"
        ))
    
    acciones = [f"Revisar {inc.tipo}" for inc in incumplimientos]
    
    return RulesResult(
        nivel_riesgo=nivel_maximo,
        incumplimientos=incumplimientos,
        acciones_sugeridas=acciones
    )

def _evaluar_epp(datos: dict) -> RulesResult:
    """Reglas para EPP."""
    incumplimientos = []
    nivel_maximo = "bajo"
    
    riesgo_escena = datos.get("riesgo_visible", "no_determinable")
    if riesgo_escena == "no_determinable":
        incumplimientos.append(Incumplimiento(
            tipo="riesgo_no_determinable", riesgo="medio", norma="Resolución 2400/1979",
            requiere_revision_manual=True
        ))
        nivel_maximo = "medio"
    
    acciones = [f"Revisar EPE en la escena - riesgo: {riesgo_escena}"]
    
    return RulesResult(
        nivel_riesgo=nivel_maximo,
        incumplimientos=incumplimientos,
        acciones_sugeridas=acciones
    )
