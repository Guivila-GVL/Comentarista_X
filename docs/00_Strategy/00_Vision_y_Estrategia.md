# 00. Visión y Estrategia de Producto: Proyecto Comentarista 🎙️✨

## 1. Declaración de Propósito
**Proyecto Comentarista** es una herramienta de asistencia y composición editorial personal para escritorio/local. Su objetivo es transformar ideas breves, reflexiones o datos analíticos (por ejemplo, observaciones sobre el mercado eléctrico o transición energética) en publicaciones de alto impacto optimizadas para **X (Twitter)** y otras redes sociales, listas para copiar y pegar con un solo clic.

---

## 2. El Problema Actual
- **Fricción al publicar**: Pasar de una idea mental o un análisis técnico a un post estructurado y con gancho en X requiere tiempo y esfuerzo de redacción.
- **Riesgo de errores**: Falta de revisión ortográfica instantánea, tono inadecuado o superación involuntaria del límite de caracteres (280 para usuarios estándar o formato hilo/artículo).
- **Desconexión con recursos multimedia**: Dificultad para asociar de inmediato capturas, infografías o gráficos analíticos generados en otros proyectos locales (como los gráficos de ESIOS en `2026_Proyecto_Energia_Graficos`).
- **Pérdida de inmediatez**: La necesidad de abrir varias herramientas para pulir el texto antes de pegarlo en la red social.

---

## 3. Propuesta de Valor y Funcionalidades Clave

### A. "De Idea a Tweet Perfecto" (Motor Asistido)
- **Entrada natural**: El usuario introduce una idea en lenguaje coloquial (ej.: *"Quiero comentar que hoy el precio de la luz se ha desplomado por el viento y que las baterías han cargado a coste cero"*).
- **Asistente de Redacción y Pulido**:
  - Corrección ortográfica y gramatical automática.
  - Ajuste de tono seleccionable: *Divulgativo/Pedagógico*, *Analítico/Técnico*, *Impactante/Periodístico*, *Irónico/Casual*.
  - Generación de 3 variantes alternativas para elegir la mejor.
  - Formateo inteligente con emojis medidos, saltos de línea legibles y sugerencia de hashtags relevantes.

### B. Vinculación Multimedia Fluida
- Selección o arrastre de imágenes y vídeos.
- Acceso directo a carpetas de recursos gráficos locales (galería de gráficos de energía, capturas o renders).
- Visualización previa en tamaño real del recurso multimedia integrado con el texto.

### C. Simulador Fiel de X (Previsualización WYSWYG)
- Interfaz espejo idéntica al diseño de X (Dark Mode / Light Mode).
- Tarjeta de tweet con avatar del usuario, handle `@`, contador dinámico de caracteres con advertencia visual (anillo de progreso circular).
- Comprobación de corte de texto y adaptación de imagen en la proporción real de X (16:9, 1:1, etc.).

### D. Flujo de Salida Instantáneo (One-Click Copy & Go)
- **Botón "Copiar Tweet"**: Copia el texto perfectamente formateado al portapapeles.
- **Botón "Copiar/Descargar Multimedia"**: Deja el archivo listo para pegar (Ctrl+V) en el compositor de X.
- **Botón "Abrir en X"**: Enlace directo (`intent/tweet`) que abre el navegador con el texto ya insertado.
- **Historial local**: Registro de borradores y tweets generados para reutilización o consulta.

---

## 4. Métricas de Éxito del Proyecto
1. **Tiempo de creación < 60 segundos**: Desde la idea inicial hasta el tweet copiado y listo en X.
2. **Cero fricción de despliegue**: Ejecutable en local con un script de inicio (`iniciar_comentarista.bat`).
3. **Control total del usuario**: Nada se publica automáticamente sin la supervisión y clic final del usuario ("Human-in-the-Loop").
