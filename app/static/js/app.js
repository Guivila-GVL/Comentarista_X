/**
 * PROYECTO COMENTARISTA - CLIENT APPLICATION
 * Flujo: 1. Idea -> 2. Búsqueda Noticias/Datos -> 3. Tweet directo en Simulador -> 4. Refinamiento -> 5. Gestión Infografía
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elementos DOM Principales
  const grafanaBadge = document.getElementById("grafana-badge");
  const aiBadge = document.getElementById("ai-badge");
  const rawIdea = document.getElementById("raw-idea");
  const btnSearchDraft = document.getElementById("btn-search-draft");

  // Resultados de Búsqueda
  const researchCard = document.getElementById("research-results-card");
  const verdictBadge = document.getElementById("factcheck-verdict-badge");
  const researchExplanation = document.getElementById("research-explanation");
  const newsItemsList = document.getElementById("news-items-list");

  // Gestión de Infografía
  const infographicCard = document.getElementById("infographic-management-card");
  const infographicCardsSummary = document.getElementById("infographic-cards-summary");
  const formUpdateInfographic = document.getElementById("form-update-infographic");
  const infographicOrderInput = document.getElementById("infographic-order-input");
  const btnToggleAttachInfo = document.getElementById("btn-toggle-attach-info");
  const btnDownloadInfographic = document.getElementById("btn-download-infographic");

  // Simulador de X
  const liveEditor = document.getElementById("live-tweet-editor");
  const mediaPreviewBox = document.getElementById("media-preview-box");
  const tweetImagePreview = document.getElementById("tweet-image-preview");
  const btnRemoveMedia = document.getElementById("btn-remove-media");

  // Contador de caracteres
  const charCurrent = document.getElementById("char-count-current");
  const charStatusBadge = document.getElementById("char-status-badge");
  const progressCircle = document.getElementById("progress-ring-circle");

  // Refinamiento Iterativo
  const tweetVersionBadge = document.getElementById("tweet-version-badge");
  const btnUndoVersion = document.getElementById("btn-undo-version");
  const btnRedoVersion = document.getElementById("btn-redo-version");
  const formRefine = document.getElementById("form-refine");
  const feedbackInput = document.getElementById("feedback-input");
  const feedbackLog = document.getElementById("feedback-log");
  const feedbackLogText = document.getElementById("feedback-log-text");
  const quickChips = document.querySelectorAll(".quick-chip");

  // Acciones en 1 clic
  const btnCopyText = document.getElementById("btn-copy-text");
  const btnCopyImage = document.getElementById("btn-copy-image");
  const btnOpenX = document.getElementById("btn-open-x");
  const toast = document.getElementById("toast");

  // Modal Ajustes
  const btnOpenSettings = document.getElementById("btn-open-settings");
  const settingsModal = document.getElementById("settings-modal");
  const btnCloseSettings = document.getElementById("btn-close-settings");
  const btnSaveSettings = document.getElementById("btn-save-settings");
  const cfgGeminiKey = document.getElementById("cfg-gemini-key");
  const cfgUserName = document.getElementById("cfg-user-name");
  const cfgUserHandle = document.getElementById("cfg-user-handle");

  // Grafana (Opciones secundarias)
  const grafanaDashboardSelect = document.getElementById("grafana-dashboard");
  const grafanaPanelSelect = document.getElementById("grafana-panel");
  const grafanaRangeSelect = document.getElementById("grafana-range");
  const btnRenderGrafana = document.getElementById("btn-render-grafana");
  const tabBtnGrafana = document.getElementById("tab-btn-grafana");
  const tabBtnLocal = document.getElementById("tab-btn-local");
  const tabContentGrafana = document.getElementById("tab-content-grafana");
  const tabContentLocal = document.getElementById("tab-content-local");
  const dropzone = document.getElementById("dropzone");
  const localFileInput = document.getElementById("local-file-input");

  // Estado en memoria
  let currentMediaUrl = null;
  let isInfographicAttached = true;
  let currentInfographicData = { title: "", subtitle: "", cards: [] };
  const tweetHistory = [];
  let historyIndex = -1;

  // Circunferencia anillo SVG
  const CIRCUMFERENCE = 2 * Math.PI * 16;
  progressCircle.style.strokeDasharray = `${CIRCUMFERENCE}`;
  progressCircle.style.strokeDashoffset = `${CIRCUMFERENCE}`;

  // ==========================================
  // 1. INICIALIZACIÓN
  // ==========================================
  async function initSystem() {
    try {
      const res = await fetch("/api/status");
      const data = await res.json();

      if (data.grafana && data.grafana.status === "ok") {
        grafanaBadge.className = "status-pill status-online";
        grafanaBadge.querySelector(".status-text").textContent = `Grafana: Online (v${data.grafana.version})`;
      } else {
        grafanaBadge.className = "status-pill status-offline";
        grafanaBadge.querySelector(".status-text").textContent = "Grafana: Offline";
      }

      if (data.ai_engine) {
        aiBadge.querySelector(".status-text").textContent = `Motor: ${data.ai_engine.provider}`;
      }

      if (data.user_profile) {
        document.getElementById("preview-display-name").textContent = data.user_profile.name;
        document.getElementById("preview-handle").textContent = `@${data.user_profile.handle}`;
        const initials = data.user_profile.name.split(" ").map(n => n[0]).join("").toUpperCase();
        document.getElementById("avatar-preview").textContent = initials || "GV";
        if (cfgUserName) cfgUserName.value = data.user_profile.name;
        if (cfgUserHandle) cfgUserHandle.value = data.user_profile.handle;
      }

      loadDashboards();
    } catch (err) {
      console.error("Error al iniciar:", err);
    }
  }

  // ==========================================
  // 2. PASO 1 Y 2: BUSCAR NOTICIAS Y PREPARAR TWEET DIRECTO
  // ==========================================
  btnSearchDraft.addEventListener("click", async () => {
    const text = rawIdea.value.trim();
    if (!text) {
      showToast("⚠️ Escribe tu idea o comentario primero");
      return;
    }

    const selectedTone = document.querySelector('input[name="tone"]:checked')?.value || "Divulgativo";
    const originalBtn = btnSearchDraft.innerHTML;
    btnSearchDraft.innerHTML = '<span class="btn-icon">⏳</span> Buscando noticias y preparando tweet...';
    btnSearchDraft.disabled = true;

    try {
      const res = await fetch("/api/search-and-draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ idea: text, tone: selectedTone })
      });

      if (!res.ok) throw new Error("Error procesando solicitud");
      const data = await res.json();

      // 1. Mostrar Noticias y Verificación
      researchCard.style.display = "flex";
      verdictBadge.textContent = data.fact_check?.verdict || "Datos contrastados";
      researchExplanation.textContent = data.fact_check?.explanation || "";

      renderNewsList(data.news || []);

      // 2. Colocar el Tweet preparado DIRECTAMENTE en el simulador
      if (data.tweet_text) {
        liveEditor.value = data.tweet_text;
        liveEditor.dataset.userEdited = "true";
        pushVersion(data.tweet_text, "Borrador contrastado inicial");
        updateCharCounter();
      }

      // 3. Preparar la Infografía
      if (data.infographic_data) {
        currentInfographicData = data.infographic_data;
        renderInfographicSummary(data.infographic_data);
        infographicCard.style.display = "flex";
      }

      if (data.infographic_url) {
        currentMediaUrl = data.infographic_url;
        setMedia(data.infographic_url);
        isInfographicAttached = true;
        updateAttachButtonState();
        if (btnDownloadInfographic) btnDownloadInfographic.href = data.infographic_url;
      }

      showToast("✨ ¡Noticias encontradas y tweet preparado en el simulador!");
    } catch (err) {
      console.error(err);
      showToast("❌ Error al buscar noticias o preparar el tweet");
    } finally {
      btnSearchDraft.innerHTML = originalBtn;
      btnSearchDraft.disabled = false;
    }
  });

  function renderNewsList(news) {
    newsItemsList.innerHTML = "";
    if (!news || news.length === 0) {
      newsItemsList.innerHTML = '<div class="news-item-card"><span class="news-item-meta">Sin noticias inmediatas para este término.</span></div>';
      return;
    }

    news.forEach(item => {
      const card = document.createElement("div");
      card.className = "news-item-card";
      card.innerHTML = `
        <a href="${item.url || '#'}" target="_blank" class="news-item-title">${escapeHtml(item.title)}</a>
        <div class="news-item-meta">${escapeHtml(item.source)} · ${escapeHtml(item.date)}</div>
      `;
      newsItemsList.appendChild(card);
    });
  }

  function renderInfographicSummary(infoData) {
    infographicCardsSummary.innerHTML = "";
    const cards = infoData.cards || [];
    cards.forEach((c, idx) => {
      const mini = document.createElement("div");
      mini.className = "info-card-mini";
      mini.innerHTML = `
        <span class="info-card-mini-tag" style="color: ${c.color || '#1d9bf0'}">${escapeHtml(c.tag || `T${idx+1}`)}</span>
        <strong class="info-card-mini-val">${escapeHtml(c.val || '')}</strong>
        <p class="info-card-mini-desc">${escapeHtml(c.desc || '')}</p>
      `;
      infographicCardsSummary.appendChild(mini);
    });
  }

  // ==========================================
  // 3. PASO 4: GESTIONAR Y MODIFICAR LA INFOGRAFÍA
  // ==========================================
  formUpdateInfographic.addEventListener("submit", async (e) => {
    e.preventDefault();
    const orderText = infographicOrderInput.value.trim();
    if (!orderText) {
      showToast("⚠️ Escribe qué orden o cambio deseas en la infografía");
      return;
    }

    const btnSubmit = document.getElementById("btn-submit-info-order");
    const originalBtn = btnSubmit.innerHTML;
    btnSubmit.innerHTML = '<span>⏳ Actualizando...</span>';
    btnSubmit.disabled = true;

    try {
      const res = await fetch("/api/update-infographic", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: currentInfographicData.title,
          subtitle: currentInfographicData.subtitle,
          cards: currentInfographicData.cards,
          instruction: orderText
        })
      });

      if (!res.ok) throw new Error("Error actualizando infografía");
      const data = await res.json();

      if (data.infographic_url) {
        currentMediaUrl = data.infographic_url;
        if (isInfographicAttached) {
          setMedia(data.infographic_url);
        }
        if (btnDownloadInfographic) btnDownloadInfographic.href = data.infographic_url;
        if (data.infographic_data) {
          currentInfographicData = data.infographic_data;
          renderInfographicSummary(data.infographic_data);
        }
        infographicOrderInput.value = "";
        showToast("🎨 ¡Infografía actualizada con tus órdenes!");
      }
    } catch (err) {
      console.error(err);
      showToast("❌ Error al modificar la infografía");
    } finally {
      btnSubmit.innerHTML = originalBtn;
      btnSubmit.disabled = false;
    }
  });

  btnToggleAttachInfo.addEventListener("click", () => {
    isInfographicAttached = !isInfographicAttached;
    updateAttachButtonState();
    if (isInfographicAttached && currentMediaUrl) {
      setMedia(currentMediaUrl);
      showToast("📎 Infografía adjuntada al tweet");
    } else {
      mediaPreviewBox.style.display = "none";
      btnCopyImage.disabled = true;
      showToast("Infografía desvinculada del tweet");
    }
  });

  function updateAttachButtonState() {
    if (isInfographicAttached) {
      btnToggleAttachInfo.className = "btn btn-toggle-attached";
      btnToggleAttachInfo.innerHTML = "<span>📎 Adjunta al Tweet (Activa)</span>";
    } else {
      btnToggleAttachInfo.className = "btn btn-toggle-attached detached";
      btnToggleAttachInfo.innerHTML = "<span>➕ Adjuntar Infografía al Tweet</span>";
    }
  }

  // ==========================================
  // 4. PASO 3: REFINAR TWEET CON COMENTARIOS
  // ==========================================
  function pushVersion(text, explanation = "") {
    if (historyIndex >= 0 && tweetHistory[historyIndex]?.text === text) return;
    if (historyIndex < tweetHistory.length - 1) {
      tweetHistory.splice(historyIndex + 1);
    }
    tweetHistory.push({ text, explanation });
    historyIndex = tweetHistory.length - 1;
    updateVersionControls();
  }

  function updateVersionControls() {
    if (tweetVersionBadge) tweetVersionBadge.textContent = `v${historyIndex + 1}`;
    if (btnUndoVersion) btnUndoVersion.disabled = historyIndex <= 0;
    if (btnRedoVersion) btnRedoVersion.disabled = historyIndex >= tweetHistory.length - 1;
  }

  btnUndoVersion.addEventListener("click", () => {
    if (historyIndex > 0) {
      historyIndex--;
      const v = tweetHistory[historyIndex];
      liveEditor.value = v.text;
      updateCharCounter();
      updateVersionControls();
      if (feedbackLog && feedbackLogText) {
        feedbackLog.style.display = "flex";
        feedbackLogText.textContent = `Vuelto a v${historyIndex + 1}: ${v.explanation}`;
      }
      showToast(`↩️ Vuelto a versión v${historyIndex + 1}`);
    }
  });

  btnRedoVersion.addEventListener("click", () => {
    if (historyIndex < tweetHistory.length - 1) {
      historyIndex++;
      const v = tweetHistory[historyIndex];
      liveEditor.value = v.text;
      updateCharCounter();
      updateVersionControls();
      if (feedbackLog && feedbackLogText) {
        feedbackLog.style.display = "flex";
        feedbackLogText.textContent = `Avanzado a v${historyIndex + 1}: ${v.explanation}`;
      }
      showToast(`↪️ Avanzado a versión v${historyIndex + 1}`);
    }
  });

  async function executeRefinement(instruction) {
    const currentText = liveEditor.value.trim();
    if (!currentText) {
      showToast("⚠️ El tweet en el simulador está vacío");
      return;
    }
    if (!instruction) {
      showToast("⚠️ Escribe tu comentario o instrucción de cambio");
      return;
    }

    const btnSubmit = document.querySelector("#form-refine button[type='submit']");
    const originalBtn = btnSubmit ? btnSubmit.innerHTML : "";
    if (btnSubmit) {
      btnSubmit.innerHTML = '<span>⏳ Aplicando...</span>';
      btnSubmit.disabled = true;
    }

    try {
      const res = await fetch("/api/refine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          current_text: currentText,
          feedback: instruction,
          fact_context: researchExplanation ? researchExplanation.textContent : "",
          tone: document.querySelector('input[name="tone"]:checked')?.value || "Divulgativo"
        })
      });

      if (!res.ok) throw new Error("Error modificando tweet");
      const data = await res.json();

      if (data.updated_text) {
        liveEditor.value = data.updated_text;
        liveEditor.dataset.userEdited = "true";
        pushVersion(data.updated_text, data.explanation || instruction);
        updateCharCounter();

        if (feedbackLog && feedbackLogText) {
          feedbackLog.style.display = "flex";
          feedbackLogText.textContent = data.explanation || "Cambio aplicado.";
        }
        if (feedbackInput) feedbackInput.value = "";
        showToast("⚡ ¡Tweet modificado con tu comentario!");
      }
    } catch (err) {
      console.error(err);
      showToast("❌ Error al aplicar el cambio al tweet");
    } finally {
      if (btnSubmit) {
        btnSubmit.innerHTML = originalBtn;
        btnSubmit.disabled = false;
      }
    }
  }

  formRefine.addEventListener("submit", (e) => {
    e.preventDefault();
    executeRefinement(feedbackInput.value.trim());
  });

  quickChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const inst = chip.dataset.instruction;
      if (feedbackInput) feedbackInput.value = inst;
      executeRefinement(inst);
    });
  });

  // ==========================================
  // 5. EDITOR Y CONTADOR EN VIVO
  // ==========================================
  function updateCharCounter() {
    const text = liveEditor.value;
    const count = text.length;
    charCurrent.textContent = count;

    const ratio = Math.min(count / 280, 1);
    const offset = CIRCUMFERENCE - (ratio * CIRCUMFERENCE);
    progressCircle.style.strokeDashoffset = `${offset}`;

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

  liveEditor.addEventListener("input", () => {
    updateCharCounter();
  });

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
    isInfographicAttached = false;
    updateAttachButtonState();
    showToast("Imagen quitada del tweet");
  });

  // ==========================================
  // 6. ACCIONES ONE-CLICK
  // ==========================================
  btnCopyText.addEventListener("click", async () => {
    const text = liveEditor.value;
    if (!text) {
      showToast("⚠️ El tweet está vacío");
      return;
    }
    try {
      await navigator.clipboard.writeText(text);
      showToast("📋 ¡Texto del tweet copiado!");
    } catch (err) {
      console.error(err);
      showToast("❌ Error al copiar texto");
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
      if (navigator.clipboard && navigator.clipboard.write) {
        try {
          const item = new ClipboardItem({ [blob.type]: blob });
          await navigator.clipboard.write([item]);
          showToast("🖼️ ¡Imagen copiada! Pégala con Ctrl+V en X");
          return;
        } catch (clipErr) {
          console.warn(clipErr);
        }
      }
      const a = document.createElement("a");
      a.href = currentMediaUrl;
      a.download = "infografia_comentarista.png";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      showToast("📥 Imagen descargada");
    } catch (err) {
      console.error(err);
      showToast("❌ Error con la imagen");
    }
  });

  btnOpenX.addEventListener("click", () => {
    const text = liveEditor.value;
    window.open(`https://x.com/intent/tweet?text=${encodeURIComponent(text)}`, "_blank");
  });

  // ==========================================
  // 7. MODAL DE AJUSTES
  // ==========================================
  btnOpenSettings.addEventListener("click", () => {
    settingsModal.style.display = "flex";
  });

  btnCloseSettings.addEventListener("click", () => {
    settingsModal.style.display = "none";
  });

  btnSaveSettings.addEventListener("click", async () => {
    const apiKey = cfgGeminiKey.value.trim();
    const name = cfgUserName.value.trim();
    const handle = cfgUserHandle.value.trim().replace("@", "");

    try {
      const res = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          gemini_api_key: apiKey || null,
          user_name: name || "Guillermo Vila",
          user_handle: handle || "guivila"
        })
      });
      if (!res.ok) throw new Error("Error guardando ajustes");
      document.getElementById("preview-display-name").textContent = name;
      document.getElementById("preview-handle").textContent = `@${handle}`;
      settingsModal.style.display = "none";
      showToast("💾 Ajustes guardados correctamente");
    } catch (err) {
      showToast("❌ Error al guardar ajustes");
    }
  });

  // ==========================================
  // 8. GRAFANA Y ARCHIVOS (OPCIONAL)
  // ==========================================
  async function loadDashboards() {
    try {
      const res = await fetch("/api/grafana/dashboards");
      const data = await res.json();
      grafanaDashboardSelect.innerHTML = '<option value="">-- Elige un Cuadro de Mando --</option>';
      (data.dashboards || []).forEach(d => {
        const opt = document.createElement("option");
        opt.value = d.uid;
        opt.textContent = `${d.title} (${d.folderTitle || 'General'})`;
        grafanaDashboardSelect.appendChild(opt);
      });
    } catch (e) {
      console.error(e);
    }
  }

  grafanaDashboardSelect?.addEventListener("change", async (e) => {
    const uid = e.target.value;
    if (!uid) return;
    try {
      const res = await fetch(`/api/grafana/panels?uid=${encodeURIComponent(uid)}`);
      const data = await res.json();
      grafanaPanelSelect.innerHTML = '<option value="">-- Elige un Panel --</option>';
      (data.panels || []).forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.id;
        opt.textContent = `[ID ${p.id}] ${p.title}`;
        grafanaPanelSelect.appendChild(opt);
      });
      grafanaPanelSelect.disabled = false;
    } catch (e) {
      console.error(e);
    }
  });

  btnRenderGrafana?.addEventListener("click", async () => {
    const dashboardUid = grafanaDashboardSelect.value;
    const panelId = grafanaPanelSelect.value;
    if (!dashboardUid || !panelId) {
      showToast("⚠️ Selecciona un dashboard y un panel");
      return;
    }
    try {
      showToast("⏳ Renderizando panel...");
      const res = await fetch("/api/grafana/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dashboard_uid: dashboardUid,
          panel_id: parseInt(panelId, 10),
          from_time: grafanaRangeSelect.value,
          to_time: "now"
        })
      });
      const data = await res.json();
      if (data.image_url) {
        setMedia(data.image_url);
        showToast("✅ Gráfico de Grafana cargado");
      }
    } catch (e) {
      showToast("❌ Error al renderizar de Grafana");
    }
  });

  tabBtnGrafana?.addEventListener("click", () => {
    tabBtnGrafana.classList.add("active");
    tabBtnLocal.classList.remove("active");
    tabContentGrafana.classList.add("active");
    tabContentLocal.classList.remove("active");
  });

  tabBtnLocal?.addEventListener("click", () => {
    tabBtnLocal.classList.add("active");
    tabBtnGrafana.classList.remove("active");
    tabContentLocal.classList.add("active");
    tabContentGrafana.classList.remove("active");
  });

  dropzone?.addEventListener("click", () => localFileInput?.click());

  localFileInput?.addEventListener("change", async (e) => {
    if (e.target.files && e.target.files[0]) {
      const formData = new FormData();
      formData.append("file", e.target.files[0]);
      const res = await fetch("/api/upload", { method: "POST", body: formData });
      const data = await res.json();
      if (data.image_url) setMedia(data.image_url);
    }
  });

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  let toastTimer = null;
  function showToast(message) {
    if (toastTimer) clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.add("show");
    toastTimer = setTimeout(() => toast.classList.remove("show"), 3200);
  }

  initSystem();
  updateCharCounter();
});
