# 01. Historias de Usuario y Casos de Uso 👤📋

Este documento define las historias de usuario que guían el desarrollo de **Proyecto Comentarista**.

---

## 🎯 Caso de Uso Principal (Happy Path)

Guillermo está analizando los precios del mercado eléctrico del día. Observa un comportamiento inusual (precios cero o alta penetración eólica).
1. Abre la aplicación **Comentarista** desde su escritorio mediante un archivo `.bat`.
2. Escribe una frase rápida con su idea: *"El viento ha hundido hoy los precios a cero en las horas centrales. Adjunto gráfico con el desglose horario"*.
3. Hace clic en un botón para adjuntar el gráfico recién generado en su carpeta de gráficos de energía.
4. Pulsa **"Generar Variantes"**. La aplicación le ofrece 3 textos redactados, sin faltas ortográficas, con la métrica destacada y emojis adecuados.
5. Elige la variante que más le gusta y ajusta una palabra en el editor. Ve en tiempo real cómo queda exactamente en la tarjeta de X.
6. Pulsa **"Copiar Texto"** y **"Copiar Imagen"**, entra a X y hace Ctrl+V. El tweet queda publicado en menos de un minuto.

---

## 📑 Historias de Usuario Detalladas

### US-01: Redacción Asistida a partir de Ideas
- **Como** usuario analista o divulgador,
- **Quiero** escribir notas rápidas o ideas sin preocuparme por la estructura final,
- **Para que** el sistema me genere textos estructurados con ganchos (*hooks*) y llamadas a la acción efectivos.
- **Criterios de Aceptación**:
  - Debe aceptar cualquier longitud de texto inicial.
  - Ofrecer al menos 3 propuestas de tweet: sintético, explicativo y conversacional.

### US-02: Control Estricto de Longitud y Ortografía
- **Como** usuario que publica en X,
- **Quiero** ver un contador de caracteres en tiempo real y una corrección ortográfica impecable,
- **Para que** nunca me corte el texto ni publique errores tipográficos o gramaticales.
- **Criterios de Aceptación**:
  - Contador reactivo hasta 280 caracteres con indicador de colores.
  - Opción de dividir en hilo (1/N, 2/N) si el texto excede voluntariamente la longitud.

### US-03: Asociación de Multimedia Local
- **Como** creador de contenido con gráficos generados en el ordenador,
- **Quiero** arrastrar o seleccionar imágenes directamente desde mis carpetas locales de proyectos,
- **Para que** se muestren integradas en la previsualización del tweet.
- **Criterios de Aceptación**:
  - Soporte para `.png`, `.jpg`, `.webp` y `.mp4`.
  - Acceso directo rápido a la carpeta de gráficos del proyecto de energía.

### US-04: Simulación Visual Idéntica a X
- **Como** usuario perfeccionista con el diseño,
- **Quiero** previsualizar el tweet exactamente como se verá en el feed de X (Dark Mode),
- **Para que** pueda validar cómo se leen las líneas y cómo encaja la imagen antes de subirlo.
- **Criterios de Aceptación**:
  - Muestra foto de perfil, nombre, handle, saltos de línea e imagen en proporción 16:9 / nativa.

### US-05: Copiado Rápido al Portapapeles (One-Click)
- **Como** usuario que publica manualmente en X,
- **Quiero** copiar el texto y la imagen con un solo clic,
- **Para que** el paso a la plataforma sea inmediato y sin fricciones.
- **Criterios de Aceptación**:
  - Botón de copia con confirmación visual.
  - Opción de abrir la ventana de tweet de X directamente en el navegador con el texto pre-cargado.
