import base64
import json
import os
from anthropic import Anthropic
from app.models.schemas import Categoria, VisionResult

PROMPTS = {
    Categoria.extintores: """Analiza esta foto de un extintor. Responde SOLO en JSON válido, sin texto adicional:
{
  "existe": true/false,
  "tipo_extintor": "solkaflam|co2|pqs|agua|espuma|desconocido",
  "estado_fisico": ["bueno|corrosion|fuga|en_el_piso|obstruido|sin_soporte"],
  "senalizacion": "presente|ausente",
  "manometro": "verde|rojo|no_visible|no_aplica",
  "pasador_seguridad": "presente|ausente|no_visible",
  "sello_inviolabilidad": "presente|ausente|no_visible",
  "fecha_vencimiento_visible": true/false,
  "confianza_general": 0.0
}""",
    Categoria.epp: """Analiza esta foto de EPP (equipo de protección personal). Responde SOLO en JSON válido:
{
  "personas_detectadas": 0,
  "elementos": [],
  "riesgo_visible": "bajo|medio|alto|critico|no_determinable",
  "confianza_general": 0.0
}"""
}

async def analizar_foto(foto_bytes: bytes, categoria: Categoria) -> VisionResult:
    """Envía la foto a Claude y devuelve el análisis estructurado."""
    
    if categoria not in PROMPTS:
        raise ValueError(f"Categoría no soportada: {categoria}")
    
    prompt = PROMPTS[categoria]
    foto_b64 = base64.b64encode(foto_bytes).decode()
    
    try:
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": foto_b64}},
                    {"type": "text", "text": prompt},
                ],
            }],
        )

        texto_respuesta = "".join(block.text for block in response.content if block.type == "text")

        # Limpiar markdown code blocks si Claude los incluyó
        if texto_respuesta.startswith("```"):
            texto_respuesta = texto_respuesta.split("```")[1]  # quita primer ```
            if texto_respuesta.startswith("json"):
                texto_respuesta = texto_respuesta[4:]  # quita "json"
            texto_respuesta = texto_respuesta.strip()

        print(f"RESPUESTA LIMPIA: '{texto_respuesta}'")
        
        if not texto_respuesta:
            raise ValueError("Claude devolvió una respuesta vacía")
        
        datos = json.loads(texto_respuesta)
        confianza = datos.pop("confianza_general", 0.5)
        return VisionResult(categoria=categoria, datos=datos, confianza_general=confianza)
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude no devolvió JSON válido: {e}")
    except Exception as e:
        raise ValueError(f"Error al llamar a Claude: {str(e)}")