import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

def search_live_news(query: str, max_items: int = 4) -> List[Dict[str, str]]:
    """
    Busca noticias reales en vivo mediante Google News RSS (región España).
    Totalmente dinámico, sin datos predefinidos ni hardcodeados.
    """
    clean_query = query.strip()
    # Si la consulta es muy larga (frase completa), extraer términos clave
    words = [w for w in clean_query.split() if len(w) > 3 and w.lower() not in ["para", "como", "sobre", "nuestra", "nuestro", "otra", "este", "esta", "otra", "otra vez"]]
    search_term = " ".join(words[:6]) if len(words) > 6 else clean_query

    url = f"https://news.google.com/rss/search?q={requests.utils.quote(search_term)}&hl=es&gl=ES&ceid=ES:es"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code != 200:
            return []
        
        root = ET.fromstring(r.content)
        items = []
        for item in root.findall(".//item")[:max_items]:
            title = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            source = item.find("source").text if item.find("source") is not None else "Medio de Comunicación"
            
            clean_title = title.rsplit(" - ", 1)[0] if " - " in title else title
            formatted_date = pub_date[:16] if pub_date else "Reciente"

            items.append({
                "title": clean_title,
                "source": source,
                "url": link,
                "date": formatted_date,
                "summary": f"Publicado por {source} ({formatted_date}). Noticia relacionada con {search_term}."
            })
        return items
    except Exception as e:
        print(f"[NewsSearch] Error buscando noticias para '{query}': {e}")
        return []

def search_technical_facts(query: str) -> Dict[str, Any]:
    """
    Busca contexto o definiciones de referencia mediante DuckDuckGo Instant Answers.
    """
    try:
        url = f"https://api.duckduckgo.com/?q={requests.utils.quote(query)}&format=json&kl=es-es"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            abstract = data.get("AbstractText", "")
            heading = data.get("Heading", "")
            if abstract:
                return {
                    "heading": heading or query,
                    "summary": abstract,
                    "source": data.get("AbstractSource", "Enciclopedia / Web")
                }
    except Exception as e:
        print(f"[NewsSearch] Error en DDG para '{query}': {e}")
    return {}
