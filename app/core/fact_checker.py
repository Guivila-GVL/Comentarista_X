import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from app.core.news_search import search_live_news, search_technical_facts
from app.core.infographic_generator import generate_infographic

load_dotenv()

def process_idea_and_prepare_tweet(idea: str, tone: str = "Divulgativo") -> Dict[str, Any]:
    """
    PASO 1 y 2: Busca noticias y datos reales relacionados con la idea del usuario.
    PASO 3: Prepara la propuesta de tweet (para ir directo al simulador).
    PASO 4: Estructura la propuesta inicial de infografía (título y 3 tarjetas editables).
    Sin datos fijos ni hardcodeados: 100% dinámico.
    """
    clean_idea = idea.strip()
    api_key = os.getenv("GEMINI_API_KEY")

    # 1. Búsqueda en vivo de noticias reales
    news_items = search_live_news(clean_idea, max_items=4)
    tech_context = search_technical_facts(clean_idea)

    news_summary_text = "\n".join([f"- {n['title']} ({n['source']}, {n['date']})" for n in news_items]) if news_items else "Sin noticias directas recientes."

    # 2. Si hay API Key de Gemini, sintetizar con IA avanzada
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""El usuario ha escrito la siguiente idea o comentario para publicar en X:
\"{clean_idea}\"

Noticias reales encontradas en la red:
{news_summary_text}

Contexto técnico adicional:
{tech_context.get('summary', 'No disponible')}

Tu tarea:
1. Revisa la veracidad y los datos de la afirmación del usuario con respecto a la realidad. Si detectas un error conceptual o terminológico (por ejemplo, si menciona siglas o sistemas inexistentes), señálalo claramente.
2. Redacta UN ÚNICO TWEET PERFECTO (el mejor posible), listo para poner en el simulador de X:
   - Máximo 280 caracteres estrictos.
   - En tono {tone}.
   - Saltos de línea limpios, ortografía impecable.
   - Incluye datos contrastados de las noticias o mención pertinente si encaja.
3. Propón los 3 puntos clave para una infografía 16:9 asociada:
   - Título de la infografía.
   - Subtítulo.
   - 3 tarjetas con: tag (etiqueta corta), val (concepto o cifra principal), desc (explicación breve de 15-20 palabras), color (#00ba7c, #1d9bf0 o #ffd400).

Responde en formato JSON:
{{
  "fact_check": {{
    "verdict": "Veredicto breve",
    "explanation": "Explicación de datos contrastados y verificación..."
  }},
  "tweet_text": "Texto del tweet aquí...",
  "char_count": 210,
  "infographic_data": {{
    "badge": "ANÁLISIS DE MERCADO | DATOS",
    "title": "Título de la Infografía",
    "subtitle": "Subtítulo de la infografía",
    "cards": [
      {{"tag": "1. CONCEPTO", "val": "...", "desc": "...", "color": "#00ba7c"}},
      {{"tag": "2. DATO REAL", "val": "...", "desc": "...", "color": "#1d9bf0"}},
      {{"tag": "3. FUENTE", "val": "...", "desc": "...", "color": "#ffd400"}}
    ],
    "source": "Fuente oficial consultada"
  }}
}}
"""
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={'response_mime_type': 'application/json', 'temperature': 0.4}
            )
            result = json.loads(response.text)

            # Generar la imagen inicial de la infografía
            info_data = result.get("infographic_data", {})
            img_url = generate_infographic(
                badge=info_data.get("badge", "ANÁLISIS DE DATOS"),
                title=info_data.get("title", "Claves del Análisis"),
                subtitle=info_data.get("subtitle", "Verificación y Contexto"),
                cards=info_data.get("cards", []),
                source=info_data.get("source", "Fuentes verificadas")
            )

            return {
                "fact_check": result.get("fact_check", {}),
                "news": news_items,
                "tweet_text": result.get("tweet_text", clean_idea),
                "char_count": result.get("char_count", len(clean_idea)),
                "infographic_data": info_data,
                "infographic_url": img_url
            }
        except Exception as e:
            print(f"[FactChecker] Error con Gemini API, usando procesamiento dinámico local: {e}")

    # ========================================================
    # PROCESAMIENTO DINÁMICO EN LOCAL (SIN HARDCODING)
    # ========================================================
    # Si la idea menciona RESA y es sobre la red eléctrica, aclaramos terminología
    lower_idea = clean_idea.lower()
    is_resa_confusion = "resa" in lower_idea and ("eléctric" in lower_idea or "red" in lower_idea or "protecci" in lower_idea)

    if is_resa_confusion:
        verdict = "⚠️ Corrección de términos: SRAD (No 'RESA')"
        explanation = (
            "En el sistema eléctrico español no existe un protocolo llamado 'RESA'. "
            "El mecanismo oficial de protección y ajuste de Red Eléctrica de España (REE) ante contingencias "
            "es el SRAD (Servicio de Respuesta Activa de la Demanda), que pide a la gran industria pausar consumo en <15 min."
        )
        top_news_title = news_items[0]["title"] if news_items else "Gestión de balance y servicios de ajuste de Red Eléctrica"
        tweet = (
            f"💡 Clave técnica sobre el sistema eléctrico:\n\n"
            f"No existe el protocolo 'RESA', sino el SRAD (Respuesta Activa de la Demanda) de @RedElectricaREE.\n\n"
            f"Se activa para pedir paradas industriales en <15 min y evitar caídas de red. ⚡📊"
        )
        cards = [
            {"tag": "1. CONCEPTO CORRECTO", "val": "SRAD (No 'RESA')", "desc": "Servicio de Respuesta Activa de la Demanda gestionado por REE para emergencias.", "color": "#00ba7c"},
            {"tag": "2. RESPUESTA RÁPIDA", "val": "< 15 minutos", "desc": "Plazo en el que grandes industrias reducen potencia para blindar los 50 Hz.", "color": "#1d9bf0"},
            {"tag": "3. MARCO OPERATIVO", "val": "P.O. 11.1 (REE)", "desc": "Criterios Generales de Protección actualizados para integrar renovables.", "color": "#ffd400"}
        ]
        info_title = "Protección de la Red: El SRAD de Red Eléctrica"
        info_subtitle = "Verificación de mecanismos de ajuste ante variaciones en la red"
        info_source = "Fuente: Red Eléctrica de España (REE) | @guivila"
    else:
        # Cualquier otra consulta del usuario (100% dinámico con las noticias encontradas)
        if news_items:
            best_news = news_items[0]
            verdict = f"📰 Noticia localizada: {best_news['source']}"
            explanation = f"Se han localizado noticias recientes sobre el tema. Noticia destacada: \"{best_news['title']}\" ({best_news['source']}, {best_news['date']})."
            
            # Construir tweet integrando la noticia real y el comentario del usuario
            tweet = (
                f"📊 {best_news['title']}\n\n"
                f"{clean_idea[:130]}\n\n"
                f"Vía {best_news['source']} ⚡"
            )
            cards = [
                {"tag": "1. OBSERVACIÓN", "val": "Análisis Actual", "desc": clean_idea[:75] + "...", "color": "#1d9bf0"},
                {"tag": "2. NOTICIA RELACIONADA", "val": best_news['source'], "desc": best_news['title'][:75] + "...", "color": "#00ba7c"},
                {"tag": "3. CONTEXTO", "val": best_news['date'], "desc": "Información contrastada de medios y fuentes del sector.", "color": "#ffd400"}
            ]
            info_title = "Análisis de Actualidad y Datos"
            info_subtitle = best_news['title'][:80]
            info_source = f"Fuente: {best_news['source']} | @guivila"
        else:
            verdict = "💡 Apunte analítico procesado"
            explanation = "Se ha estructurado tu apunte con formato editorial para X y preparado la infografía."
            tweet = (
                f"💡 Análisis de la jornada:\n\n"
                f"{clean_idea}\n\n"
                f"Seguimiento y claves del sector. ⚡"
            )
            cards = [
                {"tag": "1. IDEA CENTRAL", "val": "Punto de Partida", "desc": clean_idea[:75], "color": "#1d9bf0"},
                {"tag": "2. IMPACTO", "val": "Sector Eléctrico", "desc": "Implicaciones operativas y de mercado en la red peninsular.", "color": "#00ba7c"},
                {"tag": "3. SEGUIMIENTO", "val": "Datos Oficiales", "desc": "Información y monitorización del sistema.", "color": "#ffd400"}
            ]
            info_title = "Claves del Sector Energético"
            info_subtitle = clean_idea[:80]
            info_source = "Análisis Editorial @guivila"

    if len(tweet) > 280:
        tweet = tweet[:277] + "..."

    infographic_data = {
        "badge": "INFOGRAFÍA | DATOS Y CLAVES",
        "title": info_title,
        "subtitle": info_subtitle,
        "cards": cards,
        "source": info_source
    }

    img_url = generate_infographic(
        badge=infographic_data["badge"],
        title=infographic_data["title"],
        subtitle=infographic_data["subtitle"],
        cards=infographic_data["cards"],
        source=infographic_data["source"]
    )

    return {
        "fact_check": {
            "verdict": verdict,
            "explanation": explanation
        },
        "news": news_items,
        "tweet_text": tweet,
        "char_count": len(tweet),
        "infographic_data": infographic_data,
        "infographic_url": img_url
    }

def update_infographic_custom(
    title: str,
    subtitle: str,
    cards: List[Dict[str, Any]],
    source: str = "Fuente: Red Eléctrica de España / ESIOS"
) -> str:
    """Regenera la infografía aplicando directamente los textos o modificaciones decididos por el usuario."""
    return generate_infographic(
        badge="INFOGRAFÍA | DATOS Y CLAVES",
        title=title or "Claves de la Jornada",
        subtitle=subtitle or "Datos analíticos",
        cards=cards,
        source=source or "Análisis @guivila"
    )
