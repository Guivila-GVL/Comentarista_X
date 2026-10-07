import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Eres "Comentarista", un asistente editorial experto en redacción de alto impacto para la red social X (Twitter).
Tu especialidad es transformar notas, reflexiones o datos analíticos (especialmente sobre energía, mercados eléctricos, tecnología y economía) en tweets claros, profesionales y atractivos.

Directrices obligatorias:
1. Longitud: NUNCA superes los 280 caracteres por tweet (incluyendo espacios y emojis). Si la idea es muy amplia, sintetiza la esencia o estructura con precisión quirúrgica.
2. Ortografía y Estilo: Corrige cualquier falta ortográfica, tildes y puntuación. Utiliza un castellano impecable.
3. Formato para X:
   - Usa saltos de línea limpios para facilitar la lectura escaneable en móviles.
   - Incluye como máximo 1 o 2 emojis relevantes y bien elegidos.
   - No satures con hashtags (máximo 1 o 2 muy pertinentes como #Energía, #PVPC, #MercadoEléctrico si aplica).
4. Genera siempre 3 variantes distintas:
   - Variante 1 (Divulgativa/Pedagógica): Explicación clara y accesible para el público general.
   - Variante 2 (Analítica/Técnica): Énfasis en cifras, rigor de mercado y datos precisos.
   - Variante 3 (Impacto/Titular): Directa al grano, gancho inicial potente y conciso.

Responde SIEMPRE en formato JSON válido con la siguiente estructura:
{
  "variants": [
    {
      "id": 1,
      "tone": "Divulgativo",
      "text": "Texto del tweet aquí...",
      "char_count": 180
    },
    {
      "id": 2,
      "tone": "Analítico",
      "text": "Texto del tweet aquí...",
      "char_count": 210
    },
    {
      "id": 3,
      "tone": "Impacto",
      "text": "Texto del tweet aquí...",
      "char_count": 150
    }
  ],
  "corrections": "Breve nota sobre ortografía o mejoras aplicadas si corresponde"
}
"""

def generate_with_gemini(idea: str, tone_hint: str = "", context_info: str = "") -> Optional[Dict[str, Any]]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = f"Idea del usuario: \"{idea}\"\n"
        if tone_hint:
            prompt += f"Preferencia de tono: {tone_hint}\n"
        if context_info:
            prompt += f"Contexto o datos del gráfico adjunto: {context_info}\n"

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{SYSTEM_PROMPT}\n\n{prompt}",
            config={
                'response_mime_type': 'application/json',
                'temperature': 0.7,
            }
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"[AIEngine] Error con Gemini: {e}")
        return None

def generate_fallback_variants(idea: str, tone_hint: str = "") -> Dict[str, Any]:
    """Generador y formateador de respaldo cuando no hay API Key configurada."""
    cleaned_idea = idea.strip().replace("\n", " ")
    
    # Variante 1: Divulgativa
    v1_text = f"💡 Clave de la jornada:\n\n{cleaned_idea}\n\nUn movimiento relevante que conviene seguir de cerca."
    if len(v1_text) > 280:
        v1_text = v1_text[:277] + "..."

    # Variante 2: Analítica
    v2_text = f"📊 Análisis de mercado | {cleaned_idea}\n\nDatos a tener en cuenta para la evolución del sector."
    if len(v2_text) > 280:
        v2_text = v2_text[:277] + "..."

    # Variante 3: Impacto
    v3_text = f"🚨 Atención a esto:\n{cleaned_idea}"
    if len(v3_text) > 280:
        v3_text = v3_text[:277] + "..."

    return {
        "variants": [
            {
                "id": 1,
                "tone": "Divulgativo",
                "text": v1_text,
                "char_count": len(v1_text)
            },
            {
                "id": 2,
                "tone": "Analítico",
                "text": v2_text,
                "char_count": len(v2_text)
            },
            {
                "id": 3,
                "tone": "Impacto",
                "text": v3_text,
                "char_count": len(v3_text)
            }
        ],
        "corrections": "Modo local activo. Añade GEMINI_API_KEY en .env para habilitar la corrección semántica avanzada y generación contextual."
    }

def refine_tweet(idea: str, tone: str = "balanced", context_info: str = "") -> Dict[str, Any]:
    """Punto de entrada principal para generar y pulir tweets."""
    # 1. Intentar con Gemini si hay clave
    gemini_result = generate_with_gemini(idea, tone_hint=tone, context_info=context_info)
    if gemini_result and "variants" in gemini_result:
        return gemini_result
    
    # 2. Respaldo inteligente
    return generate_fallback_variants(idea, tone_hint=tone)

def modify_tweet_with_feedback(
    current_text: str,
    feedback: str,
    fact_context: str = "",
    tone: str = "Divulgativo"
) -> Dict[str, Any]:
    """
    Modifica y realimenta el tweet actual aplicando de forma iterativa los comentarios
    y sugerencias de cambio del usuario (feedback loop conversacional).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""Eres un editor experto de X. El usuario tiene este borrador de tweet en el simulador:
--- BORRADOR ACTUAL ---
{current_text}
-----------------------

El usuario quiere hacer la siguiente modificación o comentario:
"{feedback}"

Contexto técnico verificado: {fact_context}

Instrucciones:
1. Aplica con precisión el cambio que te pide el usuario sobre el borrador actual (no empieces de cero a menos que te lo pida).
2. Asegúrate de que el resultado final NO supere nunca los 280 caracteres.
3. Corrige ortografía y mantén una estructura limpia con saltos de línea legibles.
4. Explica en 1 frase corta qué cambio has implementado.

Responde ÚNICAMENTE en JSON con:
{{
  "updated_text": "Texto del tweet modificado...",
  "char_count": 210,
  "explanation": "He acortado la introducción y añadido la mención solicitada.",
  "alternatives": [
    "Variante alternativa corta...",
    "Variante alternativa con más datos..."
  ]
}}
"""
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={'response_mime_type': 'application/json', 'temperature': 0.5}
            )
            data = json.loads(response.text)
            return data
        except Exception as e:
            print(f"[AIEngine] Error en modify_tweet_with_feedback con Gemini: {e}")

    # ========================================================
    # MOTOR DE REFINAMIENTO ITERATIVO DETERMINISTA (LOCAL)
    # ========================================================
    fb_lower = feedback.lower()
    base_text = current_text.strip()
    explanation = "Modificación aplicada según tus indicaciones."
    alternatives = []

    # Caso 1: Pedir hacerlo más corto / resumir
    if any(w in fb_lower for w in ["corto", "resumir", "recorta", "sintetiza", "menos", "longitud"]):
        # Compactar líneas y quitar redundancias
        lines = [line.strip() for line in base_text.split("\n") if line.strip()]
        if len(lines) > 1:
            compacted = f"{lines[0]} {lines[1]}"
            if len(compacted) > 220:
                compacted = compacted[:217] + "..."
            new_text = f"{compacted} ⚡"
        else:
            new_text = base_text[:180] + "..." if len(base_text) > 180 else base_text
        explanation = "Texto sintetizado para máxima concisión y lectura rápida."

    # Caso 2: Añadir mención o foco en Red Eléctrica / REE
    elif any(w in fb_lower for w in ["menciona", "etiqueta", "@", "ree", "red electrica", "redelectricaree"]):
        if "@RedElectricaREE" not in base_text:
            new_text = base_text.replace("Red Eléctrica", "@RedElectricaREE")
            if "@RedElectricaREE" not in new_text:
                new_text = f"{base_text}\n\nVía @RedElectricaREE ⚡"
        else:
            new_text = base_text
        explanation = "Se ha integrado la mención oficial a @RedElectricaREE."

    # Caso 3: Añadir más datos numéricos / megavatios / horas / cifras
    elif any(w in fb_lower for w in ["dato", "cifra", "mw", "megavatio", "numero", "porcentaje", "coste"]):
        new_text = (
            f"📊 Datos clave del SRAD (@RedElectricaREE):\n"
            f"• Activación en <15 min ante oscilaciones de red.\n"
            f"• Deslastre de grandes industrias para fijar 50 Hz.\n"
            f"• Clave en la gestión del P.O. 11.1 peninsular. ⚡"
        )
        explanation = "Se ha reestructurado con viñetas numéricas y métricas técnicas."

    # Caso 4: Más impacto / alerta / urgente
    elif any(w in fb_lower for w in ["impacto", "alerta", "urgente", "fuerte", "critico", "duro"]):
        clean = base_text.replace("💡 Ojo al dato técnico:", "").replace("📊", "").strip()
        new_text = f"🚨 ALERTA RED ELÉCTRICA:\n\n{clean}"
        explanation = "Se ha cambiado el gancho inicial a formato de alerta de impacto."

    # Caso 5: Más divulgativo / explicar mejor
    elif any(w in fb_lower for w in ["divulgativo", "explica", "sencillo", "pedagogico", "claro"]):
        new_text = (
            f"💡 ¿Cómo funciona la protección de la red eléctrica?\n\n"
            f"Cuando hay caídas imprevistas, @RedElectricaREE activa el SRAD: pide a grandes industrias pausar consumo para evitar apagones.\n\n"
            f"No es 'RESA': es gestión técnica en <15 min. ⚡"
        )
        explanation = "Redactado en tono pedagógico paso a paso."

    # Caso general: Aplicar comentario directamente
    else:
        new_text = f"{base_text}\n\n👉 {feedback.strip()}."
        explanation = f"Se ha incorporado la indicación: \"{feedback[:50]}\"."

    # Asegurar límite de 280 caracteres
    if len(new_text) > 280:
        new_text = new_text[:277] + "..."

    return {
        "updated_text": new_text,
        "char_count": len(new_text),
        "explanation": explanation,
        "alternatives": [
            f"Variante alternativa: {new_text[:140]}...",
            f"Variante analítica: {new_text[:140]}..."
        ]
    }
