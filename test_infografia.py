import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import textwrap

def generate_infographic(
    badge: str = "⚡ SISTEMA ELÉCTRICO ESPAÑOL | VERIFICACIÓN TÉCNICA",
    title: str = "Protección de la Red: El SRAD de Red Eléctrica",
    subtitle: str = "Verificación de datos: Activación de mecanismos de contingencia ante caídas en el sistema",
    cards = None,
    source: str = "Fuente: Red Eléctrica de España (REE) / ESIOS | Análisis @guivila",
    output_path: str = "app/static/media/infografia_sample.png"
):
    if cards is None:
        cards = [
            {
                "tag": "1. CONCEPTO CORRECTO",
                "val": "SRAD (No \"RESA\")",
                "desc": "El Servicio de Respuesta Activa de la Demanda permite a REE ordenar paradas a grandes industrias para estabilizar la red.",
                "color": "#00ba7c"
            },
            {
                "tag": "2. TIEMPO DE RESPUESTA",
                "val": "< 15 minutos",
                "desc": "Mecanismo ultrarrápido para corregir desviaciones de frecuencia (50 Hz) y evitar desconexiones masivas en cascada.",
                "color": "#1d9bf0"
            },
            {
                "tag": "3. MARCO REGULATORIO",
                "val": "P.O. 11.1 (REE)",
                "desc": "Criterios Generales de Protección actualizados en 2026 para gestionar la masiva penetración de renovables no síncronas.",
                "color": "#ffd400"
            }
        ]

    fig = plt.figure(figsize=(12, 6.75), dpi=100) # 1200 x 675 px exact 16:9
    fig.patch.set_facecolor('#080a0f')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('#080a0f')
    ax.axis('off')

    # Accent top glowing bar
    ax.plot([0.05, 0.95], [0.985, 0.985], color='#1d9bf0', lw=3, solid_capstyle='round')

    # Header badge & title
    ax.text(0.06, 0.91, badge.upper(), color='#1d9bf0', fontsize=11, weight='bold', fontfamily='sans-serif')
    ax.text(0.06, 0.83, title, color='#ffffff', fontsize=22, weight='bold', fontfamily='sans-serif')
    ax.text(0.06, 0.77, subtitle, color='#8b949e', fontsize=12, fontfamily='sans-serif')

    # Subtle divider
    ax.plot([0.06, 0.94], [0.73, 0.73], color='#21262d', lw=1.2)

    # 3 Cards Layout
    card_width = 0.275
    gap = 0.027
    start_x = 0.06

    for i, c in enumerate(cards[:3]):
        x = start_x + i * (card_width + gap)
        # Background card
        rect = patches.FancyBboxPatch(
            (x, 0.15), card_width, 0.53,
            boxstyle='round,pad=0.015,rounding_size=0.025',
            facecolor='#12151c', edgecolor='#252a36', linewidth=1.5
        )
        ax.add_patch(rect)

        # Color accent strip inside card
        ax.plot([x + 0.02, x + 0.08], [0.655, 0.655], color=c.get('color', '#1d9bf0'), lw=3.5, solid_capstyle='round')

        # Tag
        ax.text(x + 0.02, 0.615, c.get('tag', '').upper(), color=c.get('color', '#1d9bf0'), fontsize=9.5, weight='bold', fontfamily='sans-serif')

        # Value / Title
        val_text = c.get('val', '')
        ax.text(x + 0.02, 0.54, val_text, color='#ffffff', fontsize=15, weight='bold', fontfamily='sans-serif')

        # Description wrapped
        desc = c.get('desc', '')
        wrapped = textwrap.fill(desc, width=33)
        ax.text(x + 0.02, 0.44, wrapped, color='#c9d1d9', fontsize=10.5, va='top', linespacing=1.45, fontfamily='sans-serif')

    # Footer
    ax.plot([0.06, 0.94], [0.10, 0.10], color='#1c2128', lw=1)
    ax.text(0.06, 0.05, source, color='#6e7681', fontsize=10, fontfamily='sans-serif')
    ax.text(0.94, 0.05, 'COMUNICACIÓN DIGITAL & FACT-CHECKING', color='#1d9bf0', fontsize=9.5, weight='bold', ha='right', fontfamily='sans-serif')

    plt.savefig(output_path, dpi=100, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    return output_path

if __name__ == '__main__':
    generate_infographic()
    print("Infografía actualizada!")
