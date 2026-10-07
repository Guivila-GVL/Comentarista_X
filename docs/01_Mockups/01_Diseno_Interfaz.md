# 01. Diseño de Interfaz y Prototipos Visuales 🎨📱

Este documento detalla la estructura visual y la experiencia de usuario (UI/UX) de la aplicación **Comentarista**.

---

## 1. Disposición de Pantalla (Layout Side-by-Side)

La aplicación utiliza un diseño de dos paneles dividido al 50%/50% (o 45%/55% en pantallas panorámicas), pensado para maximizar la productividad y permitir comparar la idea de partida con el resultado final en tiempo real.

```
+-----------------------------------------------------------------------------------+
|  🎙️ COMENTARISTA  |  Asistente Editorial para X               [⚙️ Config] [🌙]     |
+-----------------------------------------+-----------------------------------------+
| PANEL IZQUIERDO: REDACCIÓN & IA         | PANEL DERECHO: SIMULADOR DE X (EN VIVO)  |
|                                         |                                         |
| 💡 Idea Inicial / Apunte:               | ┌─────────────────────────────────────┐ |
| [ Hoy el precio del pool eléctrico ha  ]| │ 👤 Guillermo Vila @guivila · Ahora  │ |
| [ caído a 0 €/MWh durante 6 horas por  ]| │                                     │ |
| [ el viento. Baterías cargando a tope. ]| │ Desplome histórico en el pool       │ |
|                                         | │ eléctrico 🇪🇸:                        │ |
| Tono deseado:                           | │ 6 horas consecutivas a 0,00 €/MWh.  │ |
| ( ) Analítico  (*) Divulgativo  ( ) X   | │ Las baterías aprovechan el exceso.  │ |
|                                         | │                                     │ |
| 📊 Fuente Multimedia:                  | │ ┌─────────────────────────────────┐ │ |
| [*] Grafana Local   ( ) Archivo Local   | │ │                                 │ │ |
| Dashboard: [⚡ Precios ESIOS Hoy   ▼]   | │ │  [ Render Grafana Panel 1200x675]│ │ |
| Panel:     [Curva Horaria PVPC    ▼]   | │ │                                 │ │ |
| Rango:     [Últimas 24 horas      ▼]   | │ └─────────────────────────────────┘ │ |
| [ 🔄 Renderizar Panel ]                 | │ 💬 0    🔁 0    ❤️ 0    📊 1        │ |
|                                         | └─────────────────────────────────────┘ |
| [ ✨ Generar Variantes con IA ]         |                                         |
|                                         | 📏 184 / 280 caracteres [🟢 En rango]   |
| [1] Corto e impactante                  |                                         |
| [2] Didáctico y detallado               | ACCIONES RÁPIDAS:                       |
| [3] Formato pregunta/debate             | [ 📋 Copiar Texto ] [ 🖼️ Copiar Imagen] |
|                                         | [ 🚀 Abrir Directo en X.com ]          |
+-----------------------------------------+-----------------------------------------+
```

---

## 2. Elementos Clave de la Interfaz

### 2.1. Panel de Control y Asistencia (Izquierda)
1. **Área de Texto "Idea en Bruto"**:
   - Espacio amplio para escribir sin preocuparse por la gramática, longitud ni formato.
2. **Selector de Intención / Tono**:
   - Píldoras interactivas con estados activos: *Analítico*, *Divulgativo*, *Crítico*, *Pregunta para Comunidad*.
3. **Selector Rápido de Multimedia**:
   - Permite arrastrar una imagen o vídeo.
   - Botón directo para explorar carpetas del ordenador (con acceso preconfigurado a proyectos de gráficos de energía).
4. **Selector de Variantes IA**:
   - Muestra 3 tarjetas con propuestas redactadas. Al hacer clic en una variante, se traslada de inmediato al editor y a la vista previa.

### 2.2. Tarjeta Simulador de X (Derecha)
1. **Fidelidad Visual Total**:
   - Mismo fondo (#000000 o #0f1419), tipografía Chirp/Inter, avatar redondeado, formato de enlaces y hashtags resaltados en azul `#1d9bf0`.
2. **Contador de Caracteres Reactivo**:
   - Círculo de progreso SVG dinámico idéntico a X:
     - 🟢 Verde: 0 a 240 caracteres.
     - 🟡 Ámbar: 241 a 280 caracteres.
     - 🔴 Rojo con número negativo: Si supera los 280 caracteres (con advertencia de formato largo).
3. **Barra de Acciones en 1 Clic**:
   - **Copiar Texto**: Con animación de feedback visual *"¡Copiado al portapapeles!"*.
   - **Copiar Imagen**: Coloca el blob de imagen en el portapapeles para pegar directo con Ctrl+V.
   - **Abrir en X**: Lanza `https://x.com/intent/tweet?text=...` en el navegador.
