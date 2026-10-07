/**
 * PROYECTO COMENTARISTA - CLIENT APPLICATION
 * Lógica interactiva: conexión con Grafana, motor IA, previsualización reactiva de X y portapapeles.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elementos DOM
  const grafanaBadge = document.getElementById("grafana-badge");
  const aiBadge = document.getElementById("ai-badge");
  const rawIdea = document.getElementById("raw-idea");
  const liveEditor = document.getElementById("live-tweet-editor");
  const btnGenerateAi = document.getElementById("btn-generate-ai");
  const variantsList = document.getElementById("variants-list");

  // Grafana
  const grafanaDashboardSelect = document.getElementById("grafana-dashboard");
  const grafanaPanelSelect = document.getElementById("grafana-panel");
  const grafanaRangeSelect = document.getElementById("grafana-range");
  const btnRenderGrafana = document.getElementById("btn-render-grafana");

  // Pestañas Multimedia
  const tabBtnGrafana = document.getElementById("tab-btn-grafana");
  const tabBtnLocal = document.getElementById("tab-btn-local");
  const tabContentGrafana = document.getElementById("tab-content-grafana");
  const tabContentLocal = document.getElementById("tab-content-local");
  const dropzone = document.getElementById("dropzone");
  const localFileInput = document.getElementById("local-file-input");

  // Medios en el Tweet
  const mediaPreviewBox = document.getElementById("media-preview-box");
  const tweetImagePreview = document.getElementById("tweet-image-preview");
  const btnRemoveMedia = document.getElementById("btn-remove-media");

  // Contador de caracteres
  const charCurrent = document.getElementById("char-count-current");
  const charStatusBadge = document.getElementById("char-status-badge");
  const progressCircle = document.getElementById("progress-ring-circle");

  // Acciones en 1 clic
  const btnCopyText = document.getElementById("btn-copy-text");
  const btnCopyImage = document.getElementById("btn-copy-image");
  const btnOpenX = document.getElementById("btn-open-x");
  const toast = document.getElementById("toast");

  // Circunferencia del anillo SVG (radio = 16px)
  const CIRCUMFERENCE = 2 * Math.PI * 16;
  progressCircle.style.strokeDasharray = `${CIRCUMFERENCE}`;
  progressCircle.style.strokeDashoffset = `${CIRCUMFERENCE}`;

  let currentMediaUrl = null;

  // ==========================================
  // 1. INICIALIZACIÓN Y ESTADO DEL SISTEMA
  // ==========================================
  async function initSystem() {
    try {
      const res = await fetch("/api/status");
      const data = await res.json();

      // Estado de Grafana
      if (data.grafana && data.grafana.status === "ok") {
        grafanaBadge.className = "status-pill status-online";
        grafanaBadge.querySelector(".status-text").textContent = `Grafana: Online (v${data.grafana.version})`;
      } else {
        grafanaBadge.className = "status-pill status-offline";
        grafanaBadge.querySelector(".status-text").textContent = "Grafana: Offline";
      }

      // Estado de IA
      if (data.ai_engine && data.ai_engine.provider) {
        aiBadge.querySelector(".status-text").textContent = `IA: ${data.ai_engine.provider}`;
      }

      // Perfil de usuario
      if (data.user_profile) {
        document.getElementById("preview-display-name").textContent = data.user_profile.name;
        document.getElementById("preview-handle").textContent = `@${data.user_profile.handle}`;
        const initials = data.user_profile.name.split(" ").map(n => n[0]).join("").toUpperCase();
        document.getElementById("avatar-preview").textContent = initials || "GV";
      }

      // Cargar lista de Dashboards
      await loadDashboards();
    } catch (err) {
      console.error("Error al obtener estado:", err);
      grafanaBadge.className = "status-pill status-offline";
      grafanaBadge.querySelector(".status-text").textContent = "Servidor Offline";
    }
  }

  // ==========================================
  // 2. GESTIÓN DE GRAFANA
  // ==========================================
  async function loadDashboards() {
    try {
      const res = await fetch("/api/grafana/dashboards");
      const data = await res.json();

      grafanaDashboardSelect.innerHTML = '<option value="">-- Elige un Cuadro de Mando --</option>';
      if (data.dashboards && data.dashboards.length > 0) {
        data.dashboards.forEach(d => {
          const opt = document.createElement("option");
          opt.value = d.uid;
          opt.textContent = `${d.title} (${d.folderTitle || 'General'})`;
          grafanaDashboardSelect.appendChild(opt);
        });
      } else {
        grafanaDashboardSelect.innerHTML = '<option value="">Sin dashboards disponibles</option>';
      }
    } catch (err) {
      console.error("Error al cargar dashboards:", err);
      grafanaDashboardSelect.innerHTML = '<option value="">Error de conexión</option>';
    }
  }

  grafanaDashboardSelect.addEventListener("change", async (e) => {
    const uid = e.target.value;
    if (!uid) {
      grafanaPanelSelect.innerHTML = '<option value="">Selecciona un dashboard primero</option>';
      grafanaPanelSelect.disabled = true;
      return;
    }

    grafanaPanelSelect.innerHTML = '<option value="">Cargando paneles...</option>';
    grafanaPanelSelect.disabled = true;

    try {
      const res = await fetch(`/api/grafana/panels?uid=${encodeURIComponent(uid)}`);
      const data = await res.json();

      grafanaPanelSelect.innerHTML = '<option value="">-- Elige un Panel --</option>';
      if (data.panels && data.panels.length > 0) {
        data.panels.forEach(p => {
          const opt = document.createElement("option");
          opt.value = p.id;
          opt.textContent = `[ID ${p.id}] ${p.title}`;
          grafanaPanelSelect.appendChild(opt);
        });
        grafanaPanelSelect.disabled = false;
      } else {
        grafanaPanelSelect.innerHTML = '<option value="">Sin paneles encontrados</option>';
      }
    } catch (err) {
      console.error("Error al cargar paneles:", err);
      grafanaPanelSelect.innerHTML = '<option value="">Error al cargar paneles</option>';
    }
  });

  btnRenderGrafana.addEventListener("click", async () => {
    const dashboardUid = grafanaDashboardSelect.value;
    const panelId = grafanaPanelSelect.value;
    const timeRange = grafanaRangeSelect.value;

    if (!dashboardUid || !panelId) {
      showToast("⚠️ Selecciona un dashboard y un panel de Grafana");
      return;
    }

    const originalBtnText = btnRenderGrafana.innerHTML;
    btnRenderGrafana.innerHTML = '<span class="btn-icon">⏳</span> Renderizando...';
    btnRenderGrafana.disabled = true;

    try {
      const res = await fetch("/api/grafana/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dashboard_uid: dashboardUid,
          panel_id: parseInt(panelId, 10),
          from_time: timeRange,
          to_time: "now",
          width: 1200,
          height: 675
        })
      });

      if (!res.ok) throw new Error("Error en renderizado");
      const data = await res.json();

      if (data.image_url) {
        setMedia(data.image_url);
        showToast("✅ ¡Gráfico de Grafana cargado con éxito!");
      }
    } catch (err) {
      console.error("Error al renderizar panel:", err);
      showToast("❌ Error al renderizar el gráfico desde Grafana");
    } finally {
      btnRenderGrafana.innerHTML = originalBtnText;
      btnRenderGrafana.disabled = false;
    }
  });

  // ==========================================
  // 3. PESTAÑAS MULTIMEDIA Y ARCHIVOS LOCALES
  // ==========================================
  tabBtnGrafana.addEventListener("click", () => {
    tabBtnGrafana.classList.add("active");
    tabBtnLocal.classList.remove("active");
    tabContentGrafana.classList.add("active");
    tabContentLocal.classList.remove("active");
  });

  tabBtnLocal.addEventListener("click", () => {
    tabBtnLocal.classList.add("active");
    tabBtnGrafana.classList.remove("active");
    tabContentLocal.classList.add("active");
    tabContentGrafana.classList.remove("active");
  });

  dropzone.addEventListener("click", () => localFileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("drag-over");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("drag-over");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag-over");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  });

  localFileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  });

  async function uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    try {
      showToast("⏳ Subiendo archivo...");
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData
      });
      if (!res.ok) throw new Error("Error en la subida");
      const data = await res.json();
      if (data.image_url) {
        setMedia(data.image_url);
        showToast("✅ Archivo adjuntado al tweet");
      }
    } catch (err) {
      console.error(err);
      showToast("❌ Error al subir el archivo");
    }
  }

  function setMedia(url) {
    currentMediaUrl = url;
    tweetImagePreview.src = url;
    mediaPreviewBox.style.display = "block";
    btnCopyImage.disabled = false;
  }

  btnRemoveMedia.addEventListener("click", () => {
    currentMediaUrl = null;
    tweetImagePreview.src = "";
    mediaPreviewBox.style.display = "none";
    btnCopyImage.disabled = true;
    showToast("Imagen eliminada del tweet");
  });

  // ==========================================
  // 4. EDITOR EN VIVO Y CONTADOR DE CARACTERES
  // ==========================================
  function updateCharCounter() {
    const text = liveEditor.value;
    const count = text.length;
    charCurrent.textContent = count;

    // Actualizar anillo de progreso (máximo 280)
    const ratio = Math.min(count / 280, 1);
    const offset = CIRCUMFERENCE - (ratio * CIRCUMFERENCE);
    progressCircle.style.strokeDashoffset = `${offset}`;

    // Estado y colores
    if (count <= 240) {
      progressCircle.style.stroke = "#1d9bf0";
      charStatusBadge.className = "badge-status-ok";
      charStatusBadge.textContent = "En Rango";
      charCurrent.style.color = "#e7e9ea";
    } else if (count <= 280) {
      progressCircle.style.stroke = "#ffd400";
      charStatusBadge.className = "badge-status-warning";
      charStatusBadge.textContent = "Cerca del Límite";
      charCurrent.style.color = "#ffd400";
    } else {
      progressCircle.style.stroke = "#f4212e";
      charStatusBadge.className = "badge-status-danger";
      charStatusBadge.textContent = `+${count - 280} caract. extra`;
      charCurrent.style.color = "#f4212e";
    }
  }

  liveEditor.addEventListener("input", updateCharCounter);

  // Sincronizar idea inicial si el editor de tweet está vacío
  rawIdea.addEventListener("input", () => {
    if (!liveEditor.dataset.userEdited) {
      liveEditor.value = rawIdea.value;
      updateCharCounter();
    }
  });

  liveEditor.addEventListener("keydown", () => {
    liveEditor.dataset.userEdited = "true";
  });

  const btnFactCheckAi = document.getElementById("btn-factcheck-ai");
  const factCheckContainer = document.getElementById("factcheck-container");
  const factCheckVerdictBadge = document.getElementById("factcheck-verdict-badge");
  const factCheckExplanation = document.getElementById("factcheck-explanation");
  const factCheckNewsTitle = document.getElementById("factcheck-news-title");
  const factCheckNewsSource = document.getElementById("factcheck-news-source");
  const factCheckNewsSummary = document.getElementById("factcheck-news-summary");

  // ==========================================
  // 5. INVESTIGAR, FACT-CHECK & GENERAR INFOGRAFÍA
  // ==========================================
  if (btnFactCheckAi) {
    btnFactCheckAi.addEventListener("click", async () => {
      const text = rawIdea.value.trim() || liveEditor.value.trim();
      if (!text) {
        showToast("⚠️ Escribe una idea o apunte primero");
        return;
      }

      const selectedTone = document.querySelector('input[name="tone"]:checked')?.value || "Divulgativo";
      const originalBtnText = btnFactCheckAi.innerHTML;
      btnFactCheckAi.innerHTML = '<span class="btn-icon">⏳</span> Investigando datos y generando infografía...';
      btnFactCheckAi.disabled = true;

      try {
        const res = await fetch("/api/factcheck-and-generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            idea: text,
            tone: selectedTone
          })
        });

        if (!res.ok) throw new Error("Error en fact-checking");
        const data = await res.json();

        // 1. Mostrar Fact-Checking y Explicación
        if (data.fact_check) {
          factCheckContainer.style.display = "flex";
          factCheckVerdictBadge.textContent = data.fact_check.verdict || "Verificación Realizada";
          factCheckExplanation.textContent = data.fact_check.explanation || "";

          if (data.fact_check.is_accurate) {
            factCheckVerdictBadge.className = "badge-verdict badge-status-ok";
          } else {
            factCheckVerdictBadge.className = "badge-verdict badge-status-warning";
          }
        }

        // 2. Mostrar Noticia Relacionada
        if (data.news && data.news.length > 0) {
          const mainNews = data.news[0];
          factCheckNewsTitle.textContent = mainNews.title;
          factCheckNewsTitle.href = mainNews.url || "#";
          factCheckNewsSource.textContent = `${mainNews.source} · ${mainNews.date}`;
          factCheckNewsSummary.textContent = mainNews.summary || "";
          document.getElementById("factcheck-news-box").style.display = "flex";
        }

        // 3. Adjuntar Infografía generada al Tweet Card
        if (data.infographic_url) {
          setMedia(data.infographic_url);
        }

        // 4. Renderizar Variantes de Tweets
        if (data.variants && data.variants.length > 0) {
          renderVariants(data.variants);
          // Cargar por defecto la primera variante en el simulador
          liveEditor.value = data.variants[0].text;
          liveEditor.dataset.userEdited = "true";
          updateCharCounter();
        }

        showToast("✨ ¡Fact-checking completado e infografía generada!");
      } catch (err) {
        console.error("Error en factcheck:", err);
        showToast("❌ Error al verificar o generar infografía");
      } finally {
        btnFactCheckAi.innerHTML = originalBtnText;
        btnFactCheckAi.disabled = false;
      }
    });
  }

  function renderVariants(variants) {
    if (!variants || variants.length === 0) {
      variantsList.innerHTML = '<div class="variant-empty-state">No se pudieron generar propuestas.</div>';
      return;
    }

    variantsList.innerHTML = "";
    variants.forEach((v) => {
      const card = document.createElement("div");
      card.className = "variant-card";
      card.innerHTML = `
        <div class="variant-card-header">
          <span class="variant-tone-badge">${v.tone || 'Propuesta'}</span>
          <span class="variant-char-count">${v.char_count || v.text.length} / 280 caract.</span>
        </div>
        <div class="variant-text">${escapeHtml(v.text)}</div>
      `;

      card.addEventListener("click", () => {
        liveEditor.value = v.text;
        liveEditor.dataset.userEdited = "true";
        updateCharCounter();
        showToast(`Variante "${v.tone}" cargada en el simulador`);
      });

      variantsList.appendChild(card);
    });
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  // ==========================================
  // 6. ACCIONES RÁPIDAS (ONE-CLICK)
  // ==========================================
  btnCopyText.addEventListener("click", async () => {
    const text = liveEditor.value;
    if (!text) {
      showToast("⚠️ El tweet está vacío");
      return;
    }

    try {
      await navigator.clipboard.writeText(text);
      showToast("📋 ¡Texto del tweet copiado al portapapeles!");
    } catch (err) {
      console.error("Error al copiar texto:", err);
      showToast("❌ No se pudo acceder al portapapeles");
    }
  });

  btnCopyImage.addEventListener("click", async () => {
    if (!currentMediaUrl) {
      showToast("⚠️ No hay imagen adjunta");
      return;
    }

    try {
      const response = await fetch(currentMediaUrl);
      const blob = await response.blob();

      // Intentar copiar al portapapeles como ClipboardItem (formato PNG)
      if (navigator.clipboard && navigator.clipboard.write) {
        try {
          const item = new ClipboardItem({ [blob.type]: blob });
          await navigator.clipboard.write([item]);
          showToast("🖼️ ¡Imagen copiada al portapapeles! Lista para pegar (Ctrl+V)");
          return;
        } catch (clipErr) {
          console.warn("Fallo en navigator.clipboard.write, recurriendo a descarga:", clipErr);
        }
      }

      // Si el navegador bloquea escritura directa de imagen, descargarla
      const a = document.createElement("a");
      a.href = currentMediaUrl;
      a.download = "grafico_comentarista.png";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      showToast("📥 Imagen descargada lista para arrastrar a X");
    } catch (err) {
      console.error("Error al copiar/descargar imagen:", err);
      showToast("❌ Error al procesar la imagen");
    }
  });

  btnOpenX.addEventListener("click", () => {
    const text = liveEditor.value;
    const url = `https://x.com/intent/tweet?text=${encodeURIComponent(text)}`;
    window.open(url, "_blank");
  });

  // Notificación Toast
  let toastTimer = null;
  function showToast(message) {
    if (toastTimer) clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add("show");
    toastTimer = setTimeout(() => {
      toast.classList.remove("show");
    }, 3200);
  }

  // Inicializar
  initSystem();
  updateCharCounter();
});
