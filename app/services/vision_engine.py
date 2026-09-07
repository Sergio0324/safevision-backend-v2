import base64
import json
import os

from anthropic import Anthropic
from app.models.schemas import Categoria, VisionResult


PROMPTS = {

    # ============================================================
    # 1. EXTINTORES
    # ============================================================
    Categoria.extintores: """ANALIZA CUIDADOSAMENTE esta foto de un extintor.

Responde SOLO en JSON válido, sin texto adicional.

INSTRUCCIONES CRÍTICAS:

1. SOLO determina "manometro_cargado" si VES CLARAMENTE el manómetro.
2. Si el manómetro NO está visible:
   - "manometro": "no_visible"
   - "manometro_cargado": null
3. Si ves claramente el manómetro EN VERDE:
   - "manometro": "verde"
   - "manometro_cargado": true
4. Si ves claramente el manómetro EN ROJO:
   - "manometro": "rojo"
   - "manometro_cargado": false
5. Si ves claramente el manómetro EN AMARILLO:
   - "manometro": "amarillo"
   - "manometro_cargado": false
6. Si NO ESTÁS SEGURO del color o estado del manómetro:
   - "manometro_cargado": null
7. NO inventes información que no pueda observarse.

PARA FECHAS:

8. Si VES claramente una fecha de vencimiento, escríbela como YYYY-MM o YYYY-MM-DD.
9. Si NO ves claramente la fecha → "fecha_vencimiento": "no_visible".
10. "vencido": true SOLO si la fecha visible está claramente en el pasado.
11. "vencido": false SOLO si la fecha visible está claramente en el futuro.
12. "vencido": null si no existe una fecha visible o no puede determinarse.

PARA EL ESTADO FÍSICO:

13. Solo reporta daños que sean VISIBLES.
14. No determines mantenimiento interno mediante la fotografía.
15. Si no puedes determinar una condición → no la inventes.

Responde SOLO este JSON:

{
  "existe": true,
  "tipo_extintor": "solkaflam|co2|pqs|agua|espuma|desconocido",
  "estado_fisico": ["bueno|corrosion|fuga|en_el_piso|obstruido|sin_soporte"],
  "senalizacion": "presente|ausente|no_visible",
  "manometro": "verde|rojo|amarillo|no_visible|no_aplica",
  "manometro_cargado": true,
  "pasador_seguridad": "presente|ausente|no_visible",
  "sello_inviolabilidad": "presente|ausente|no_visible",
  "fecha_vencimiento": "no_visible|YYYY-MM-DD|YYYY-MM",
  "vencido": true,
  "observaciones": "descripción breve de lo que ves",
  "confianza_general": 0.0
}""",


    # ============================================================
    # 2. SEÑALIZACIÓN DE SEGURIDAD
    # ============================================================
    Categoria.senalizacion_seguridad: """ANALIZA CUIDADOSAMENTE esta foto de señalización de seguridad.

Responde SOLO en JSON válido, sin texto adicional.

INSTRUCCIONES CRÍTICAS:

1. Determina "existe": true SOLO si ves claramente una señalización de seguridad.
2. Si no existe una señal visible → "existe": false.
3. NO confundas publicidad, decoración o avisos generales con señalización de seguridad.
4. Identifica el tipo de señal SOLO cuando pueda determinarse visualmente.
5. Si el símbolo o texto no es claramente visible → usa "no_visible".
6. Evalúa el estado físico únicamente por daños visibles.
7. NO determines cumplimiento de una norma solamente por la fotografía.
8. NO inventes texto, colores, símbolos o dimensiones.
9. Si NO ESTÁS SEGURO → usa "no_visible" o null.

Responde SOLO este JSON:

{
  "existe": true,
  "tipo_senal": "prohibicion|obligacion|advertencia|emergencia|incendio|evacuacion|informativa|no_visible",
  "estado_fisico": ["bueno|deteriorada|rota|desgastada|obstruida|sucia"],
  "visibilidad": "visible|parcialmente_visible|obstruida|no_visible",
  "ubicacion_aparente": "adecuada|inadecuada|no_visible",
  "simbolo_visible": true,
  "texto_visible": true,
  "colores_identificables": true,
  "observaciones": "descripción breve de lo que ves",
  "confianza_general": 0.0
}""",


    # ============================================================
    # 3. EQUIPOS DE EMERGENCIA
    # ============================================================
    Categoria.equipos_emergencia: """ANALIZA CUIDADOSAMENTE esta foto de un equipo o elemento para atención de emergencias.

Responde SOLO en JSON válido, sin texto adicional.

INSTRUCCIONES CRÍTICAS:

1. "existe": true SOLO si identificas claramente un equipo o elemento de emergencia.
2. Si no puedes identificar ningún equipo → "existe": false.
3. Si no puedes determinar el tipo → "desconocido".
4. Evalúa únicamente condiciones VISIBLES.
5. No afirmes que un equipo funciona correctamente solo por su apariencia.
6. Si el contenido no puede verse → "no_visible".
7. Si una fecha no puede leerse claramente → "no_visible".
8. No inventes cantidades, fechas, certificaciones ni funcionamiento.
9. Si NO ESTÁS SEGURO → usa null o "no_visible".

Responde SOLO este JSON:

{
  "existe": true,
  "tipo_equipo": "botiquin|camilla|ducha_emergencia|lavaojos|alarma|kit_derrame|radio_comunicacion|linterna|otro|desconocido",
  "estado_fisico": ["bueno|deteriorado|roto|sucio|corrosion|obstruido"],
  "accesibilidad": "accesible|obstruido|no_visible",
  "senalizacion": "presente|ausente|no_visible",
  "contenido_visible": "completo|incompleto|vacio|no_visible|no_aplica",
  "fecha_visible": "presente|ausente|no_visible|no_aplica",
  "observaciones": "descripción breve de lo que ves",
  "confianza_general": 0.0
}""",


    # ============================================================
    # 4. EPP
    # ============================================================
    Categoria.epp: """ANALIZA CUIDADOSAMENTE esta foto de elementos de protección personal (EPP).

Responde SOLO en JSON válido, sin texto adicional.

INSTRUCCIONES CRÍTICAS:

1. "existe": true SOLO si ves claramente uno o más elementos de protección personal.
2. Identifica únicamente EPP que puedan reconocerse visualmente.
3. Si no puedes identificar el elemento → "desconocido".
4. Evalúa el estado únicamente mediante daños visibles.
5. NO determines certificación, talla, resistencia o capacidad de protección mediante una fotografía.
6. Si una característica no puede verse → "no_visible" o null.
7. Si aparece una persona, diferencia entre EPP presente y uso correcto.
8. Solo indica uso incorrecto cuando exista evidencia visual clara.
9. No inventes elementos que estén fuera del campo visual.
10. Si NO ESTÁS SEGURO → utiliza null o "no_visible".

Responde SOLO este JSON:

{
  "existe": true,
  "personas_detectadas": 0,
  "elementos": [
    "casco|gafas_seguridad|proteccion_auditiva|respirador|guantes|botas_seguridad|chaleco_reflectivo|ropa_protectora|careta|proteccion_facial|otro"
  ],
  "estado_fisico": ["bueno|deteriorado|roto|sucio|desgastado|no_visible"],
  "uso_visible": "correcto_aparente|incorrecto_aparente|no_aplica|no_visible",
  "elementos_danados": true,
  "elementos_ausentes_aparentes": true,
  "certificacion_visible": true,
  "observaciones": "descripción breve de lo que ves",
  "confianza_general": 0.0
}""",


    # ============================================================
    # 5. EPCC
    # ============================================================
    Categoria.epcc: """ANALIZA CUIDADOSAMENTE esta foto de equipos de protección contra caídas (EPCC).

Responde SOLO en JSON válido, sin texto adicional.

INSTRUCCIONES CRÍTICAS:

1. "existe": true SOLO si identificas claramente un elemento de protección contra caídas.
2. Identifica únicamente elementos que puedan reconocerse visualmente.
3. Si no puedes determinar el tipo → "desconocido".
4. Evalúa únicamente daños visibles.
5. Busca visualmente cortes, desgaste, corrosión, deformaciones, roturas o deterioro.
6. NO determines resistencia, capacidad de carga o funcionamiento mediante una fotografía.
7. NO inventes certificaciones.
8. Si una etiqueta o fecha no es claramente legible → "no_visible".
9. Si NO ESTÁS SEGURO → utiliza null o "no_visible".

Responde SOLO este JSON:

{
  "existe": true,
  "tipo_equipo": "arnes|eslinga|linea_de_vida|absorbedor_energia|conector|mosqueton|punto_anclaje|dispositivo_retractil|otro|desconocido",
  "estado_fisico": ["bueno|deteriorado|roto|cortado|desgastado|corrosion|deformado|no_visible"],
  "costuras_visibles": "buen_estado|danadas|no_visible|no_aplica",
  "conectores_visibles": "buen_estado|danados|deformados|no_visible|no_aplica",
  "etiqueta_identificacion": "visible|no_visible|no_aplica",
  "fecha_inspeccion_visible": "visible|no_visible|no_aplica",
  "danos_visibles": true,
  "observaciones": "descripción breve de lo que ves",
  "confianza_general": 0.0
}""",


    # ============================================================
    # 6. TRABAJO EN CALIENTE
    # ============================================================
    Categoria.trabajo_caliente: """ANALIZA CUIDADOSAMENTE esta foto relacionada con trabajo en caliente.

Responde SOLO en JSON válido, sin texto adicional.

INSTRUCCIONES CRÍTICAS:

1. "existe": true SOLO si observas evidencia visual clara de una actividad o equipo relacionado con trabajo en caliente.
2. Considera actividades como soldadura, corte, esmerilado con chispas o llama abierta.
3. No determines un permiso de trabajo si el documento no es claramente visible.
4. No afirmes que el área es segura únicamente por su apariencia.
5. Identifica EPP y equipos de control de incendios únicamente si son visibles.
6. No inventes controles que no aparezcan en la imagen.
7. Si NO ESTÁS SEGURO → utiliza null o "no_visible".

Responde SOLO este JSON:

{
  "existe": true,
  "actividad": "soldadura|corte|esmerilado|llama_abierta|otra|no_visible",
  "chispas_o_llama_visible": true,
  "persona_con_epp": true,
  "proteccion_visual": "presente|ausente|no_visible|no_aplica",
  "guantes_proteccion": "presentes|ausentes|no_visible|no_aplica",
  "proteccion_corporal": "presente|ausente|no_visible|no_aplica",
  "extintor_visible": true,
  "materiales_combustibles_cercanos": true,
  "permiso_trabajo_visible": true,
  "observaciones": "descripción breve de lo que ves",
  "confianza_general": 0.0
}""",


    # ============================================================
    # 7. IZAJE DE CARGAS
    # ============================================================
    Categoria.izaje_cargas: """ANALIZA CUIDADOSAMENTE esta foto relacionada con izaje de cargas.

Responde SOLO en JSON válido, sin texto adicional.

INSTRUCCIONES CRÍTICAS:

1. "existe": true SOLO si observas claramente una actividad o equipo de izaje.
2. Identifica únicamente equipos reconocibles visualmente.
3. NO determines capacidad de carga, resistencia o certificación mediante una fotografía.
4. Si una etiqueta de capacidad no es claramente legible → "no_visible".
5. Evalúa únicamente daños o condiciones VISIBLES.
6. No afirmes que una carga está correctamente asegurada si no puede determinarse visualmente.
7. No inventes pesos, capacidades, fechas ni certificaciones.
8. Si NO ESTÁS SEGURO → utiliza null o "no_visible".

Responde SOLO este JSON:

{
  "existe": true,
  "equipo_principal": "grua|polipasto|montacargas|puente_grua|eslinga|cadena|cable_acero|gancho|grillete|otro|desconocido",
  "carga_visible": true,
  "carga_aparentemente_asegurada": true,
  "eslinga_visible": true,
  "gancho_visible": true,
  "pestillo_seguridad_visible": true,
  "danos_visibles": true,
  "capacidad_carga_visible": true,
  "area_delimitada": "si|no|no_visible|no_aplica",
  "personas_bajo_carga": true,
  "observaciones": "descripción breve de lo que ves",
  "confianza_general": 0.0
}""",


    # ============================================================
    # 8. ESPACIOS CONFINADOS
    # ============================================================
    Categoria.espacios_confinados: """ANALIZA CUIDADOSAMENTE esta foto relacionada con espacios confinados.

Responde SOLO en JSON válido, sin texto adicional.

INSTRUCCIONES CRÍTICAS:

1. "existe": true SOLO si observas claramente una entrada, estructura o actividad que pueda identificarse visualmente como relacionada con un espacio confinado.
2. NO determines cumplimiento legal únicamente mediante una fotografía.
3. Identifica señales, barreras, trípodes, líneas de vida y equipos de rescate únicamente si son visibles.
4. NO afirmes que existe monitoreo atmosférico si el equipo no es claramente visible.
5. Si una característica no puede observarse → "no_visible".
6. Si NO ESTÁS SEGURO → utiliza null.
7. No inventes permisos, mediciones atmosféricas, vigencias ni procedimientos.

Responde SOLO este JSON:

{
  "existe": true,
  "tipo_espacio": "tanque|pozo|silo|camara|alcantarilla|excavacion|otro|no_visible",
  "entrada_visible": true,
  "persona_en_espacio": true,
  "senalizacion": "presente|ausente|no_visible",
  "barrera_delimitacion": "presente|ausente|no_visible|no_aplica",
  "tripode_rescate": "presente|ausente|no_visible|no_aplica",
  "linea_de_vida": "presente|ausente|no_visible|no_aplica",
  "detector_gases": "presente|ausente|no_visible|no_aplica",
  "equipo_rescate": "presente|ausente|no_visible|no_aplica",
  "permiso_visible": true,
  "observaciones": "descripción breve de lo que ves",
  "confianza_general": 0.0
}""",


    # ============================================================
    # 9. TRABAJO ELÉCTRICO
    # ============================================================
    Categoria.trabajo_electrico: """ANALIZA CUIDADOSAMENTE esta foto relacionada con trabajo eléctrico.

Responde SOLO en JSON válido, sin texto adicional.

INSTRUCCIONES CRÍTICAS:

1. "existe": true SOLO si observas claramente una instalación, equipo o actividad eléctrica.
2. Identifica únicamente elementos eléctricos visualmente reconocibles.
3. NO determines que una instalación está energizada si no existe evidencia visual suficiente.
4. NO determines cumplimiento de normas eléctricas mediante una fotografía.
5. NO afirmes ausencia de tensión, puesta a tierra o aislamiento si no pueden observarse.
6. Evalúa únicamente daños o condiciones visibles.
7. Si una etiqueta, señal o elemento no es claramente visible → "no_visible".
8. No inventes voltajes, capacidades, mediciones ni certificaciones.
9. Si NO ESTÁS SEGURO → utiliza null o "no_visible".

Responde SOLO este JSON:

{
  "existe": true,
  "tipo_elemento": "tablero_electrico|cableado|tomacorriente|interruptor|motor|equipo_electrico|instalacion|otro|desconocido",
  "trabajador_visible": true,
  "epp_electrico_visible": true,
  "guantes_aislantes_visibles": true,
  "proteccion_facial_visible": true,
  "senalizacion_riesgo_electrico": "presente|ausente|no_visible",
  "tablero_cerrado": true,
  "cableado_danado": true,
  "partes_expuestas_visibles": true,
  "puesta_tierra_visible": true,
  "permiso_o_procedimiento_visible": true,
  "observaciones": "descripción breve de lo que ves",
  "confianza_general": 0.0
}""",


    # ============================================================
    # 10. SUSTANCIAS QUÍMICAS
    # ============================================================
    Categoria.sustancias_quimicas: """ANALIZA CUIDADOSAMENTE esta foto relacionada con sustancias químicas.

Responde SOLO en JSON válido, sin texto adicional.

INSTRUCCIONES CRÍTICAS:

1. "existe": true SOLO si observas claramente un recipiente, producto, sustancia o área relacionada con sustancias químicas.
2. Identifica el producto SOLO si la etiqueta o características visuales permiten hacerlo con suficiente certeza.
3. NO inventes el nombre de una sustancia.
4. Si una etiqueta contiene información que no puede leerse claramente → "no_visible".
5. Identifica pictogramas de peligro únicamente cuando sean claramente visibles.
6. NO determines propiedades químicas únicamente por color o apariencia.
7. Evalúa únicamente daños, fugas, derrames o condiciones visibles.
8. No inventes concentraciones, peligros, fichas de seguridad o condiciones de almacenamiento.
9. Si NO ESTÁS SEGURO → utiliza null o "no_visible".

Responde SOLO este JSON:

{
  "existe": true,
  "tipo_recipiente": "envase|caneca|tambor|cilindro|tanque|contenedor|otro|desconocido",
  "nombre_producto_visible": "texto_visible|no_visible",
  "etiqueta": "presente|ausente|no_visible",
  "pictogramas_sga_visibles": true,
  "pictogramas_identificables": [
    "inflamable|corrosivo|toxico|comburente|gas_presurizado|peligro_salud|irritante|peligro_ambiental|explosivo|desconocido"
  ],
  "envase_danado": true,
  "fuga_visible": true,
  "derrame_visible": true,
  "tapa_cierre": "presente|ausente|no_visible|no_aplica",
  "senalizacion": "presente|ausente|no_visible",
  "observaciones": "descripción breve de lo que ves",
  "confianza_general": 0.0
}"""
}


# ============================================================
# ANÁLISIS DE FOTOGRAFÍA
# ============================================================

async def analizar_foto(
    foto_bytes: bytes,
    categoria: Categoria
) -> VisionResult:
    """Envía la foto a Claude y devuelve el análisis estructurado."""

    if categoria not in PROMPTS:
        raise ValueError(f"Categoría no soportada: {categoria}")

    prompt = PROMPTS[categoria]

    foto_b64 = base64.b64encode(foto_bytes).decode()

    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY no está configurada en las variables de entorno"
            )

        client = Anthropic(api_key=api_key)

        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": foto_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        texto_respuesta = "".join(
            block.text
            for block in response.content
            if block.type == "text"
        )

        # --------------------------------------------------------
        # Limpiar markdown si Claude devuelve ```json ... ```
        # --------------------------------------------------------

        texto_respuesta = texto_respuesta.strip()

        if texto_respuesta.startswith("```"):
            partes = texto_respuesta.split("```")

            if len(partes) >= 2:
                texto_respuesta = partes[1]

            if texto_respuesta.startswith("json"):
                texto_respuesta = texto_respuesta[4:]

            texto_respuesta = texto_respuesta.strip()

        print(f"RESPUESTA LIMPIA: '{texto_respuesta}'")

        if not texto_respuesta:
            raise ValueError("Claude devolvió una respuesta vacía")

        # --------------------------------------------------------
        # Convertir respuesta a JSON
        # --------------------------------------------------------

        datos = json.loads(texto_respuesta)

        confianza_original = datos.pop(
            "confianza_general",
            0.5
        )

        # Asegurar que confianza sea numérica
        try:
            confianza_original = float(confianza_original)
        except (TypeError, ValueError):
            confianza_original = 0.5

        confianza_original = max(
            0.0,
            min(1.0, confianza_original)
        )

        # --------------------------------------------------------
        # Ajustar confianza
        # --------------------------------------------------------

        confianza_ajustada = _ajustar_confianza(
            categoria,
            datos,
            confianza_original
        )

        print(
            f"Categoría: {categoria.value}"
        )

        print(
            f"Confianza original: {confianza_original}, "
            f"Ajustada: {confianza_ajustada}"
        )

        if categoria.value == "extintores":
            print(
                f"Fecha vencimiento: "
                f"{datos.get('fecha_vencimiento')}, "
                f"Vencido: {datos.get('vencido')}"
            )

        return VisionResult(
            categoria=categoria,
            datos=datos,
            confianza_general=confianza_ajustada
        )

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Claude no devolvió JSON válido: {e}"
        )

    except Exception as e:
        raise ValueError(
            f"Error al llamar a Claude: {str(e)}"
        )


# ============================================================
# AJUSTE DE CONFIANZA
# ============================================================

def _ajustar_confianza(
    categoria: Categoria,
    datos: dict,
    confianza_base: float
) -> float:
    """
    Ajusta la confianza según evidencia visible
    y problemas detectados.
    """

    confianza = confianza_base

    # ============================================================
    # EXTINTORES
    # ============================================================

    if categoria.value == "extintores":

        if datos.get("manometro_cargado") is False:
            confianza *= 0.5

        if datos.get("vencido") is True:
            confianza *= 0.5

        if datos.get("manometro") == "rojo":
            confianza *= 0.6

        if datos.get("manometro_cargado") is None:
            confianza *= 0.7

        if datos.get("manometro") == "no_visible":
            confianza *= 0.7

        if datos.get("fecha_vencimiento") == "no_visible":
            confianza *= 0.8

        if "fuga" in datos.get("estado_fisico", []):
            confianza *= 0.65

        if "corrosion" in datos.get("estado_fisico", []):
            confianza *= 0.8

        if datos.get("pasador_seguridad") == "ausente":
            confianza *= 0.85

        if datos.get("sello_inviolabilidad") == "ausente":
            confianza *= 0.85

        if datos.get("senalizacion") == "ausente":
            confianza *= 0.9

    # ============================================================
    # SEÑALIZACIÓN
    # ============================================================

    elif categoria.value == "senalizacion_seguridad":

        if datos.get("visibilidad") == "no_visible":
            confianza *= 0.7

        if datos.get("visibilidad") == "parcialmente_visible":
            confianza *= 0.85

        if datos.get("tipo_senal") == "no_visible":
            confianza *= 0.8

    # ============================================================
    # EQUIPOS DE EMERGENCIA
    # ============================================================

    elif categoria.value == "equipos_emergencia":

        if datos.get("tipo_equipo") == "desconocido":
            confianza *= 0.7

        if datos.get("accesibilidad") == "obstruido":
            confianza *= 0.85

        if datos.get("contenido_visible") == "no_visible":
            confianza *= 0.9

    # ============================================================
    # EPP
    # ============================================================

    elif categoria.value == "epp":

        if datos.get("uso_visible") == "no_visible":
            confianza *= 0.9

        if datos.get("elementos_danados") is True:
            confianza *= 0.75

        if datos.get("certificacion_visible") is None:
            confianza *= 0.95

    # ============================================================
    # EPCC
    # ============================================================

    elif categoria.value == "epcc":

        if datos.get("tipo_equipo") == "desconocido":
            confianza *= 0.7

        if datos.get("danos_visibles") is True:
            confianza *= 0.75

        if datos.get("fecha_inspeccion_visible") == "no_visible":
            confianza *= 0.9

    # ============================================================
    # TRABAJO EN CALIENTE
    # ============================================================

    elif categoria.value == "trabajo_caliente":

        if datos.get("actividad") == "no_visible":
            confianza *= 0.7

        if datos.get("permiso_trabajo_visible") is None:
            confianza *= 0.9

    # ============================================================
    # IZAJE
    # ============================================================

    elif categoria.value == "izaje_cargas":

        if datos.get("equipo_principal") == "desconocido":
            confianza *= 0.7

        if datos.get("danos_visibles") is True:
            confianza *= 0.75

        if datos.get("capacidad_carga_visible") is None:
            confianza *= 0.9

    # ============================================================
    # ESPACIOS CONFINADOS
    # ============================================================

    elif categoria.value == "espacios_confinados":

        if datos.get("tipo_espacio") == "no_visible":
            confianza *= 0.75

        if datos.get("detector_gases") == "no_visible":
            confianza *= 0.9

        if datos.get("permiso_visible") is None:
            confianza *= 0.9

    # ============================================================
    # TRABAJO ELÉCTRICO
    # ============================================================

    elif categoria.value == "trabajo_electrico":

        if datos.get("tipo_elemento") == "desconocido":
            confianza *= 0.7

        if datos.get("cableado_danado") is True:
            confianza *= 0.75

        if datos.get("partes_expuestas_visibles") is True:
            confianza *= 0.7

    # ============================================================
    # SUSTANCIAS QUÍMICAS
    # ============================================================

    elif categoria.value == "sustancias_quimicas":

        if datos.get("tipo_recipiente") == "desconocido":
            confianza *= 0.75

        if datos.get("nombre_producto_visible") == "no_visible":
            confianza *= 0.9

        if datos.get("etiqueta") == "ausente":
            confianza *= 0.85

        if datos.get("fuga_visible") is True:
            confianza *= 0.75

        if datos.get("derrame_visible") is True:
            confianza *= 0.75

    # ============================================================
    # LIMITAR ENTRE 0 Y 1
    # ============================================================

    return max(
        0.0,
        min(1.0, confianza)
    )