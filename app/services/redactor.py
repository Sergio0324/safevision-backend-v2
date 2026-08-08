from app.models.schemas import Categoria, RulesResult

async def redactar_hallazgo(categoria: Categoria, resultado_reglas: RulesResult) -> str:
    """Genera un texto descriptivo del hallazgo a partir de las reglas."""
    
    nivel = resultado_reglas.nivel_riesgo.upper()
    num_incumplimientos = len(resultado_reglas.incumplimientos)
    
    if num_incumplimientos == 0:
        return f"Inspección completada. Estado: CONFORME (Nivel de riesgo: {nivel})"
    
    tipos = ", ".join([inc.tipo for inc in resultado_reglas.incumplimientos[:3]])
    acciones_texto = " • ".join(resultado_reglas.acciones_sugeridas[:2])
    
    return f"""Hallazgo de {categoria.value}
Nivel de riesgo: {nivel}
Incumplimientos detectados: {num_incumplimientos}
Tipos: {tipos}
Acciones recomendadas: {acciones_texto}
Requiere validación de auditor antes de aplicar acciones."""
