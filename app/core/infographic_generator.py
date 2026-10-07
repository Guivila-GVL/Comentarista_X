import os
import time
import textwrap
from typing import List, Dict, Any, Optional
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_infographic(
    badge: str,
    title: str,
    subtitle: str,
    cards: List[Dict[str, Any]],
    source: str = "Fuente: Red Eléctrica de España (REE) / ESIOS | @guivila",
    output_dir: Optional[str] = None
) -> str:
    """
    Genera una infografía profesional de 1200x675 px (proporción 16:9 ideal para X)
    con diseño dark mode, tarjetas destacadas y métricas clave.
    """
    if not output_dir:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "static", "media")
    os.makedirs(output_dir, exist_ok=True)

    filename = f"infografia_{int(time.time())}.png"
    output_path = os.path.join(output_dir, filename)

    fig = plt.figure(figsize=(12, 6.75), dpi=100)
    fig.patch.set_facecolor('#080a0f')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('#080a0f')
    ax.axis('off')

    # Barra superior con brillo acento X Blue
    ax.plot([0.05, 0.95], [0.985, 0.985], color='#1d9bf0', lw=3, solid_capstyle='round')

    # Cabecera
    ax.text(0.06, 0.91, badge.upper(), color='#1d9bf0', fontsize=11, weight='bold', fontfamily='sans-serif')
    ax.text(0.06, 0.83, title, color='#ffffff', fontsize=22, weight='bold', fontfamily='sans-serif')
    ax.text(0.06, 0.77, subtitle, color='#8b949e', fontsize=12, fontfamily='sans-serif')

    # Divisor sutil
    ax.plot([0.06, 0.94], [0.73, 0.73], color='#21262d', lw=1.2)

    # 3 Tarjetas informativas
    card_width = 0.275
    gap = 0.027
    start_x = 0.06

    for i, c in enumerate(cards[:3]):
        x = start_x + i * (card_width + gap)
        # Fondo de la tarjeta con bordes redondeados
        rect = patches.FancyBboxPatch(
            (x, 0.15), card_width, 0.53,
            boxstyle='round,pad=0.015,rounding_size=0.025',
            facecolor='#12151c', edgecolor='#252a36', linewidth=1.5
        )
        ax.add_patch(rect)

        # Franja de color distintivo
        color = c.get('color', '#1d9bf0')
        ax.plot([x + 0.02, x + 0.08], [0.655, 0.655], color=color, lw=3.5, solid_capstyle='round')

        # Etiqueta / Tag
        ax.text(x + 0.02, 0.615, c.get('tag', '').upper(), color=color, fontsize=9.5, weight='bold', fontfamily='sans-serif')

        # Valor o concepto central
        val_text = c.get('val', '')
        ax.text(x + 0.02, 0.54, val_text, color='#ffffff', fontsize=15, weight='bold', fontfamily='sans-serif')

        # Descripción justificada / ajustada
        desc = c.get('desc', '')
        wrapped = textwrap.fill(desc, width=33)
        ax.text(x + 0.02, 0.44, wrapped, color='#c9d1d9', fontsize=10.5, va='top', linespacing=1.45, fontfamily='sans-serif')

    # Pie de infografía
    ax.plot([0.06, 0.94], [0.10, 0.10], color='#1c2128', lw=1)
    ax.text(0.06, 0.05, source, color='#6e7681', fontsize=10, fontfamily='sans-serif')
    ax.text(0.94, 0.05, 'COMUNICACIÓN DIGITAL & FACT-CHECKING', color='#1d9bf0', fontsize=9.5, weight='bold', ha='right', fontfamily='sans-serif')

    plt.savefig(output_path, dpi=100, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()

    return f"/static/media/{filename}"
