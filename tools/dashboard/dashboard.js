(() => {
  "use strict";

  const CONFIG = JSON.parse(document.getElementById("dashboard-config")?.textContent || "{}");
  const REVIEW_KEY = "ad-gen-reviews-v2";
  const LEGACY_KEY = "ad-gen-flagged";
  const SELECTION_KEY = "ad-gen-selected-v2";
  const QA_LABELS = {
    unreviewed: "Nehodnotené",
    pass: "PASS",
    minor: "Drobná oprava",
    fail: "FAIL",
    stale: "Prehodnotiť",
  };
  const cards = [...document.querySelectorAll(".card")];
  const sections = [...document.querySelectorAll(".adset-section")];
  const templateCards = [...document.querySelectorAll(".template-card")];
  const cardById = new Map(cards.map(card => [card.dataset.bannerId, card]));
  let currentView = "creative";
  let toastTimer;
  let activeCard = null;
  let lightboxCards = [];
  let lightboxIndex = 0;
  let lastFocus = null;

  const $ = id => document.getElementById(id);
  const filter = {
    search: $("filter-search"),
    brand: $("filter-brand"),
    product: $("filter-product"),
    adset: $("filter-adset"),
    country: $("filter-country"),
    outputs: $("filter-outputs"),
    qa: $("filter-qa"),
    sort: $("filter-sort"),
  };

  function readStorage(key, fallback = {}) {
    try { return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback)); }
    catch (_) { return fallback; }
  }

  function writeStorage(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function escapeHtml(value) {
    return String(value || "").replace(/[&<>"']/g, char => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;",
    })[char]);
  }

  function showToast(message) {
    const toast = $("toast");
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 2600);
  }

  function initializeReviews() {
    if (localStorage.getItem(REVIEW_KEY)) return;
    const legacy = readStorage(LEGACY_KEY, {});
    const source = Object.keys(legacy).length ? legacy : (CONFIG.seed || {});
    const migrated = {};
    Object.entries(source).forEach(([id, value]) => {
      migrated[id] = {
        ...value,
        status: "minor",
        note: value.note || "",
        updated_at: value.flagged_at || new Date().toISOString(),
        migrated_from_flag: true,
      };
    });
    writeStorage(REVIEW_KEY, migrated);
  }

  function getReviews() { return readStorage(REVIEW_KEY, {}); }

  // Verdikt platí iba pre bajty PNG, ktoré človek videl. Prehodnotiť treba nový render
  // pod rovnakou cestou (iný hash), staré hodnotenie bez hashu aj chýbajúci súbor.
  function staleReason(card, review) {
    if (!review || review.status === "unreviewed") return "";
    if (!card.dataset.sha256) return "súbor chýba";
    if (!review.sha256) return "hodnotenie spred evidencie hashu";
    if (review.sha256 !== card.dataset.sha256) return "súbor sa od hodnotenia zmenil";
    return "";
  }

  function isStale(card, review) {
    return Boolean(staleReason(card, review));
  }

  function reviewFor(card, reviews = getReviews()) {
    const review = reviews[card.dataset.bannerId];
    if (!review) return { status: "unreviewed", note: "" };
    if (isStale(card, review)) {
      return { ...review, status: "stale", previous_status: review.status, stale_reason: staleReason(card, review) };
    }
    return review;
  }
  function getSelection() { return new Set(readStorage(SELECTION_KEY, []).filter(id => cardById.has(id))); }
  function saveSelection(selection) { writeStorage(SELECTION_KEY, [...selection]); }

  function setQaBadge(card, status) {
    const normalized = QA_LABELS[status] ? status : "unreviewed";
    const badge = card.querySelector(".qa-badge");
    card.dataset.qa = normalized;
    badge.textContent = QA_LABELS[normalized];
    badge.className = `qa-badge qa-${normalized}`;
  }

  function renderReviews() {
    const reviews = getReviews();
    cards.forEach(card => setQaBadge(card, reviewFor(card, reviews).status));
  }

  function cardPayload(card) {
    return {
      brand: card.dataset.brand,
      country: card.dataset.country,
      product: card.dataset.product,
      adset: card.dataset.adset,
      outputs: card.dataset.outputs,
      concept_id: card.dataset.conceptId,
      plan_id: card.dataset.planId,
      ad_id: card.dataset.adId,
      template_name: card.dataset.templateName,
      template_num: Number(card.dataset.templateNum) || 0,
      variation: card.dataset.variation,
      aspect: card.dataset.aspect,
      file: card.dataset.file,
      sha256: card.dataset.sha256 || null,
      headline: card.dataset.headline,
    };
  }

  function bannerCountLabel(count) {
    if (count === 1) return "1 banner";
    if (count >= 2 && count <= 4) return `${count} bannery`;
    return `${count} bannerov`;
  }

  function saveReview(card, status, note) {
    const reviews = getReviews();
    const id = card.dataset.bannerId;
    if (status === "unreviewed" && !String(note || "").trim()) {
      delete reviews[id];
    } else {
      reviews[id] = {
        ...cardPayload(card),
        status,
        note: String(note || "").trim(),
        updated_at: new Date().toISOString(),
      };
    }
    writeStorage(REVIEW_KEY, reviews);
    setQaBadge(card, status);
    if (filter.qa.value) applyFilters({ updateOptions: false });
  }

  function renderSelection() {
    const selection = getSelection();
    cards.forEach(card => {
      const selected = selection.has(card.dataset.bannerId);
      card.classList.toggle("selected", selected);
      const button = card.querySelector(".select-btn");
      button.setAttribute("aria-pressed", String(selected));
      button.setAttribute("aria-label", selected ? "Odobrať banner z výberu" : "Vybrať banner");
    });
    const count = selection.size;
    $("selected-count").textContent = count;
    $("selection-bar").hidden = count === 0;
    $("btn-compare").disabled = count < 2 || count > 4;
    $("btn-compare").title = count > 4 ? "Porovnať možno najviac 4 bannery" : count < 2 ? "Vyber aspoň 2 bannery" : "";
    if (activeCard) {
      const selected = selection.has(activeCard.dataset.bannerId);
      $("lb-select").setAttribute("aria-pressed", String(selected));
      $("lb-select").textContent = selected ? "Odobrať z výberu" : "Pridať do výberu";
    }
  }

  function toggleSelection(card) {
    const selection = getSelection();
    const id = card.dataset.bannerId;
    selection.has(id) ? selection.delete(id) : selection.add(id);
    saveSelection(selection);
    renderSelection();
  }

  function clearSelection() {
    writeStorage(SELECTION_KEY, []);
    renderSelection();
  }

  function optionValuesFor(selectName) {
    const brand = filter.brand.value;
    const product = filter.product.value;
    const adset = filter.adset.value;
    const country = filter.country.value;
    return new Set(sections.filter(section => {
      if (selectName !== "brand" && brand && section.dataset.brand !== brand) return false;
      if (selectName !== "product" && product && section.dataset.product !== product) return false;
      if (selectName !== "adset" && adset && section.dataset.adset !== adset) return false;
      if (selectName !== "country" && country && section.dataset.country !== country) return false;
      return true;
    }).map(section => section.dataset[selectName]));
  }

  function updateDependentOptions() {
    ["product", "adset", "country", "outputs"].forEach(name => {
      const select = filter[name];
      const available = optionValuesFor(name);
      [...select.options].forEach((option, index) => {
        if (index === 0) return;
        const enabled = available.has(option.value);
        option.hidden = !enabled;
        option.disabled = !enabled;
      });
      if (select.value && !available.has(select.value)) select.value = "";
    });
  }

  function currentQuery() {
    return filter.search.value.trim().toLocaleLowerCase("sk");
  }

  function cardMatches(card) {
    if (filter.brand.value && card.dataset.brand !== filter.brand.value) return false;
    if (filter.product.value && card.dataset.product !== filter.product.value) return false;
    if (filter.adset.value && card.dataset.adset !== filter.adset.value) return false;
    if (filter.country.value && card.dataset.country !== filter.country.value) return false;
    if (filter.outputs.value && card.dataset.outputs !== filter.outputs.value) return false;
    if (filter.qa.value && card.dataset.qa !== filter.qa.value) return false;
    const query = currentQuery();
    if (!query) return true;
    const haystack = [
      card.dataset.brand, card.dataset.product, card.dataset.adset, card.dataset.adId,
      card.dataset.templateName, card.dataset.conceptId, card.dataset.headline,
      card.dataset.aspect, card.dataset.variation,
    ].join(" ").toLocaleLowerCase("sk");
    return haystack.includes(query);
  }

  function syncUrl() {
    const params = new URLSearchParams();
    Object.entries(filter).forEach(([name, element]) => {
      if (element.value && name !== "sort") params.set(name, element.value);
    });
    if (filter.sort.value !== "newest") params.set("sort", filter.sort.value);
    try {
      const suffix = params.toString() ? `?${params}` : location.pathname;
      history.replaceState(null, "", suffix);
    } catch (_) { /* file:// browsers may restrict history writes */ }
  }

  function applySort() {
    const mode = filter.sort.value;
    const parent = $("creative-view");
    [...sections].sort((a, b) => {
      if (mode === "name") return `${a.dataset.brand} ${a.dataset.adset}`.localeCompare(`${b.dataset.brand} ${b.dataset.adset}`, "sk");
      const delta = (Number(a.dataset.mtime) || 0) - (Number(b.dataset.mtime) || 0);
      return mode === "oldest" ? delta : -delta;
    }).forEach(section => parent.insertBefore(section, $("filter-empty")));
  }

  function applyFilters({ updateOptions = true } = {}) {
    if (updateOptions) updateDependentOptions();
    let visibleCards = 0;
    let visibleSections = 0;
    cards.forEach(card => {
      const visible = cardMatches(card);
      card.hidden = !visible;
      if (visible) visibleCards++;
    });
    sections.forEach(section => {
      const count = [...section.querySelectorAll(".card")].filter(card => !card.hidden).length;
      section.hidden = count === 0;
      if (count) visibleSections++;
      const countEl = section.querySelector(".section-count");
      if (countEl) countEl.textContent = bannerCountLabel(count);
    });
    $("visible-count").textContent = visibleCards;
    $("filter-empty").hidden = visibleCards !== 0 || cards.length === 0;
    const active = [filter.brand, filter.product, filter.adset, filter.country, filter.outputs, filter.qa].filter(el => el.value).length + (currentQuery() ? 1 : 0);
    const activeLabel = active === 1 ? "1 aktívny filter" : `${active} aktívne filtre`;
    $("active-filter-summary").textContent = active ? `· ${activeLabel} · ${visibleSections} ad setov` : "";
    applySort();
    syncUrl();
  }

  function resetFilters() {
    Object.values(filter).forEach(element => {
      element.value = element === filter.sort ? "newest" : "";
    });
    applyFilters();
    filter.search.focus();
  }

  function loadFiltersFromUrl() {
    const params = new URLSearchParams(location.search);
    Object.entries(filter).forEach(([name, element]) => {
      const value = params.get(name);
      if (value && [...element.options || []].some(option => option.value === value)) element.value = value;
      else if (value && name === "search") element.value = value;
    });
  }

  function visibleCards() {
    return cards.filter(card => !card.hidden && !card.closest(".adset-section")?.hidden);
  }

  function setOverlayState(open) {
    document.body.classList.toggle("overlay-open", open);
  }

  function qaStateFor(card) {
    return reviewFor(card);
  }

  function renderLightbox() {
    activeCard = lightboxCards[lightboxIndex];
    if (!activeCard) return;
    const image = $("lb-img");
    image.src = activeCard.dataset.imageUrl || activeCard.dataset.file;
    image.alt = activeCard.querySelector("img")?.alt || "Detail banneru";
    $("lb-context").textContent = `${activeCard.dataset.brand} · ${activeCard.dataset.country} · ${lightboxIndex + 1}/${lightboxCards.length}`;
    $("lb-title").textContent = activeCard.dataset.adId || "Banner";
    $("lb-headline").textContent = activeCard.dataset.headline || "Headline nie je v prompte.";
    const details = [
      ["Koncept", activeCard.dataset.conceptId || "—"], ["Test plán", activeCard.dataset.planId || "legacy / bez väzby"],
      ["Template", `T${String(activeCard.dataset.templateNum || "0").padStart(2, "0")} · ${activeCard.dataset.templateName || "—"}`],
      ["Formát", `${activeCard.dataset.aspect || "—"} · ${activeCard.dataset.variation || "—"}`],
      ["Produkt", activeCard.dataset.product || "—"], ["Ad set", activeCard.dataset.adset || "—"],
      ["Súbor", activeCard.dataset.exists === "true" ? activeCard.dataset.file : "CHÝBA"],
    ];
    const history = qaStateFor(activeCard);
    if (history.status === "stale") {
      details.push(["QA", `Prehodnotiť — ${history.stale_reason}; pôvodne ${QA_LABELS[history.previous_status] || history.previous_status}`]);
    }
    $("lb-details").innerHTML = details.map(([term, value]) => `<dt>${escapeHtml(term)}</dt><dd>${escapeHtml(value)}</dd>`).join("");
    const review = qaStateFor(activeCard);
    $("lb-note").value = review.note || "";
    document.querySelectorAll(".qa-controls button").forEach(button => button.classList.toggle("active", button.dataset.qa === review.status));
    renderSelection();
  }

  function openLightbox(card) {
    lastFocus = document.activeElement;
    lightboxCards = visibleCards();
    lightboxIndex = Math.max(0, lightboxCards.indexOf(card));
    $("lightbox").hidden = false;
    setOverlayState(true);
    renderLightbox();
    $("lb-close").focus();
  }

  function closeLightbox() {
    $("lightbox").hidden = true;
    activeCard = null;
    setOverlayState(false);
    lastFocus?.focus();
  }

  function moveLightbox(delta) {
    if (!lightboxCards.length) return;
    lightboxIndex = (lightboxIndex + delta + lightboxCards.length) % lightboxCards.length;
    renderLightbox();
  }

  function setActiveQa(status) {
    if (!activeCard) return;
    saveReview(activeCard, status, $("lb-note").value);
    renderLightbox();
    showToast(`QA: ${QA_LABELS[status]}`);
  }

  function selectedCards() {
    const selection = getSelection();
    return [...selection].map(id => cardById.get(id)).filter(Boolean);
  }

  function openCompare() {
    const selected = selectedCards();
    if (selected.length < 2 || selected.length > 4) {
      showToast("Na porovnanie vyber 2 až 4 bannery");
      return;
    }
    const grid = $("compare-grid");
    grid.style.setProperty("--compare-columns", String(selected.length));
    grid.innerHTML = selected.map(card => `
      <article class="compare-item">
        <div class="compare-image"><img src="${escapeHtml(card.dataset.imageUrl || card.dataset.file)}" alt="${escapeHtml(card.querySelector("img")?.alt)}"></div>
        <div class="compare-caption"><h3>${escapeHtml(card.dataset.adId)}</h3><p>${escapeHtml(card.dataset.conceptId || "bez concept_id")} · T${escapeHtml(card.dataset.templateNum)} · ${escapeHtml(card.dataset.aspect)} · ${escapeHtml(QA_LABELS[card.dataset.qa])}</p></div>
      </article>`).join("");
    $("compare-overlay").hidden = false;
    setOverlayState(true);
    $("compare-close").focus();
  }

  function closeCompare() {
    $("compare-overlay").hidden = true;
    setOverlayState(false);
    $("btn-compare").focus();
  }

  function safeName(card) {
    return `${card.dataset.country}_${card.dataset.brand}_${card.dataset.conceptId || `t${card.dataset.templateNum}`}_${card.dataset.adId}_${card.dataset.aspect}.png`
      .normalize("NFKD").replace(/[^\w.\-]+/g, "-");
  }

  async function downloadSelected() {
    const selected = selectedCards();
    if (!selected.length) return showToast("Najprv vyber bannery");
    if (window.showDirectoryPicker) {
      let directory;
      try { directory = await window.showDirectoryPicker(); } catch (_) { return; }
      let saved = 0;
      for (const card of selected) {
        if (card.dataset.exists !== "true") continue;
        try {
          const response = await fetch(card.dataset.file);
          const handle = await directory.getFileHandle(safeName(card), { create: true });
          const writable = await handle.createWritable();
          await writable.write(await response.blob());
          await writable.close();
          saved++;
        } catch (_) { /* summarized below */ }
      }
      showToast(`Uložené: ${saved} z ${selected.length}`);
      return;
    }
    selected.filter(card => card.dataset.exists === "true").forEach((card, index) => {
      setTimeout(() => {
        const link = document.createElement("a");
        link.href = card.dataset.file;
        link.download = safeName(card);
        link.click();
      }, index * 160);
    });
    showToast(`Spustené sťahovanie ${selected.length} bannerov`);
  }

  function exportQa() {
    const reviews = getReviews();
    const items = Object.entries(reviews).filter(([, review]) => review.status !== "unreviewed" || review.note).map(([id, review]) => {
      const card = cardById.get(id);
      return { id, ...review, current_sha256: card?.dataset.sha256 || null, stale: card ? isStale(card, review) : false };
    });
    if (!items.length) return showToast("Zatiaľ nie je uložené žiadne QA hodnotenie");
    const payload = { schema_version: 2, exported_at: new Date().toISOString(), count: items.length, items };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.download = "creative-qa.json";
    link.click();
    URL.revokeObjectURL(url);
    showToast("creative-qa.json bol stiahnutý");
  }

  function printSelected() {
    const selected = selectedCards();
    if (!selected.length) return showToast("Najprv vyber bannery");
    const brands = [...new Set(selected.map(card => card.dataset.brand))];
    const title = brands.length === 1 ? `${brands[0]} · ukážka reklám` : `Výber reklám · ${brands.length} značky`;
    const reviews = getReviews();
    let html = `<section class="print-cover"><h1>${escapeHtml(title)}</h1><p>${selected.length} bannerov · ${new Date().toLocaleDateString("sk-SK")}</p></section>`;
    for (let index = 0; index < selected.length; index += 4) {
      html += '<section class="print-page">';
      selected.slice(index, index + 4).forEach(card => {
        const review = reviewFor(card, reviews);
        html += `<article class="print-item"><img src="${escapeHtml(card.dataset.imageUrl || card.dataset.file)}"><h3>${escapeHtml(card.dataset.adId)}</h3><p>${escapeHtml(card.dataset.conceptId)} · ${escapeHtml(card.dataset.aspect)} · ${escapeHtml(QA_LABELS[review.status])}</p>${review.note ? `<p>${escapeHtml(review.note)}</p>` : ""}</article>`;
      });
      html += "</section>";
    }
    $("print-area").innerHTML = html;
    setTimeout(() => window.print(), 120);
  }

  function switchView(view) {
    currentView = view === "templates" ? "templates" : "creative";
    $("creative-view").hidden = currentView !== "creative";
    $("templates-view").hidden = currentView !== "templates";
    document.querySelector(".creative-controls").hidden = currentView !== "creative";
    document.querySelector(".template-controls").hidden = currentView !== "templates";
    document.querySelectorAll(".view-tab").forEach(button => {
      const active = button.dataset.view === currentView;
      button.classList.toggle("active", active);
      button.setAttribute("aria-selected", String(active));
    });
    if (currentView === "templates") $("selection-bar").hidden = true;
    else renderSelection();
  }

  function applyTemplateFilters() {
    const query = $("template-search").value.trim().toLocaleLowerCase("sk");
    const scope = $("template-scope").value;
    const brand = $("template-brand").value;
    const status = $("template-status").value;
    let visible = 0;
    templateCards.forEach(card => {
      const haystack = [card.dataset.title, card.dataset.brand, card.dataset.layout, card.dataset.description, card.dataset.styles, card.dataset.slots].join(" ").toLocaleLowerCase("sk");
      const matches = (!query || haystack.includes(query)) && (!scope || card.dataset.scope === scope) && (!brand || card.dataset.brand === brand) && (!status || card.dataset.status === status);
      card.hidden = !matches;
      if (matches) visible++;
    });
    $("visible-template-count").textContent = visible;
    $("template-filter-empty").hidden = visible !== 0 || templateCards.length === 0;
  }

  function openTemplateDetail(card) {
    lastFocus = document.activeElement;
    $("template-detail-context").textContent = `${card.dataset.scope === "brand" ? card.dataset.brand : "Globálna knižnica"} · ${card.dataset.aspect} · ${card.dataset.status}`;
    $("template-detail-title").textContent = card.dataset.title;
    $("template-detail-description").textContent = card.dataset.description || "Štrukturálny náhľad šablóny.";
    const image = $("template-detail-image");
    image.src = card.dataset.image || card.dataset.wireframe || "";
    image.alt = `Náhľad šablóny ${card.dataset.title}`;
    const details = [
      ["Layout", card.dataset.layout], ["Formát", card.dataset.aspect],
      ["Štýly", card.dataset.styles || "A: Default"], ["Copy sloty", card.dataset.slots || "—"],
      ["Template", card.dataset.templatePath],
      ["Wireframe", card.dataset.wireframeCurrent === "true" ? "aktuálny" : "chýba / neaktuálny"],
      ["Gemini", card.dataset.renderedCurrent === "true" ? "aktuálny" : card.dataset.rendered ? "neaktuálny" : "nevytvorený"],
    ];
    $("template-detail-list").innerHTML = details.map(([term, value]) => `<dt>${escapeHtml(term)}</dt><dd>${escapeHtml(value)}</dd>`).join("");
    $("template-command").value = card.dataset.command;
    $("template-paid-command").value = card.dataset.paidCommand;
    $("template-overlay").hidden = false;
    setOverlayState(true);
    $("template-close").focus();
  }

  function closeTemplateDetail() {
    $("template-overlay").hidden = true;
    setOverlayState(false);
    lastFocus?.focus();
  }

  async function copyCommand(targetId) {
    const field = $(targetId);
    try {
      await navigator.clipboard.writeText(field.value);
    } catch (_) {
      field.select();
      document.execCommand("copy");
    }
    showToast("Príkaz bol skopírovaný");
  }

  function wireEvents() {
    cards.forEach(card => {
      card.querySelector(".select-btn").addEventListener("click", event => { event.stopPropagation(); toggleSelection(card); });
      card.querySelector(".card-img-link").addEventListener("click", event => { event.preventDefault(); openLightbox(card); });
      card.querySelector(".qa-badge").addEventListener("click", () => openLightbox(card));
    });
    sections.forEach(section => section.querySelector(".collapse-btn").addEventListener("click", event => {
      const collapsed = section.classList.toggle("collapsed");
      event.currentTarget.setAttribute("aria-expanded", String(!collapsed));
      event.currentTarget.setAttribute("aria-label", collapsed ? "Rozbaliť ad set" : "Zbaliť ad set");
    }));
    Object.entries(filter).forEach(([name, element]) => {
      element.addEventListener(name === "search" ? "input" : "change", () => applyFilters());
    });
    $("btn-reset-filters").addEventListener("click", resetFilters);
    $("btn-toggle-filters").addEventListener("click", event => {
      const open = $("filters-panel").classList.toggle("open");
      event.currentTarget.setAttribute("aria-expanded", String(open));
    });
    $("btn-export-qa").addEventListener("click", exportQa);
    $("btn-clear-selection").addEventListener("click", clearSelection);
    $("btn-compare").addEventListener("click", openCompare);
    $("btn-download").addEventListener("click", downloadSelected);
    $("btn-pdf").addEventListener("click", printSelected);
    $("lb-close").addEventListener("click", closeLightbox);
    $("lb-prev").addEventListener("click", () => moveLightbox(-1));
    $("lb-next").addEventListener("click", () => moveLightbox(1));
    $("lb-select").addEventListener("click", () => activeCard && toggleSelection(activeCard));
    $("lb-note").addEventListener("input", () => {
      if (!activeCard) return;
      const status = qaStateFor(activeCard).status;
      saveReview(activeCard, status === "stale" ? "unreviewed" : status, $("lb-note").value);
    });
    document.querySelectorAll(".qa-controls button").forEach(button => button.addEventListener("click", () => setActiveQa(button.dataset.qa)));
    $("compare-close").addEventListener("click", closeCompare);
    document.querySelectorAll(".view-tab").forEach(button => button.addEventListener("click", () => switchView(button.dataset.view)));
    [$("template-search"), $("template-scope"), $("template-brand"), $("template-status")].forEach(element => element.addEventListener(element.tagName === "INPUT" ? "input" : "change", applyTemplateFilters));
    $("btn-reset-template-filters").addEventListener("click", () => {
      $("template-search").value = ""; $("template-scope").value = ""; $("template-brand").value = ""; $("template-status").value = "";
      applyTemplateFilters(); $("template-search").focus();
    });
    templateCards.forEach(card => card.querySelector(".template-preview").addEventListener("click", () => openTemplateDetail(card)));
    $("template-close").addEventListener("click", closeTemplateDetail);
    document.querySelectorAll(".copy-template-command").forEach(button => button.addEventListener("click", () => copyCommand(button.dataset.copyTarget)));
    window.addEventListener("afterprint", () => { $("print-area").innerHTML = ""; });
    document.addEventListener("keydown", event => {
      if (!$("template-overlay").hidden && event.key === "Escape") return closeTemplateDetail();
      if (!$("compare-overlay").hidden && event.key === "Escape") return closeCompare();
      if ($("lightbox").hidden) return;
      if (event.key === "Escape") closeLightbox();
      else if (event.key === "ArrowLeft") moveLightbox(-1);
      else if (event.key === "ArrowRight") moveLightbox(1);
      else if ((event.key === "f" || event.key === "F") && activeCard) toggleSelection(activeCard);
      else if (event.key === "Tab") {
        const focusable = [...$("lightbox").querySelectorAll("button, textarea")].filter(element => !element.disabled);
        const first = focusable[0], last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      }
    });
  }

  initializeReviews();
  loadFiltersFromUrl();
  renderReviews();
  renderSelection();
  wireEvents();
  applyFilters();
  applyTemplateFilters();
  switchView("creative");
})();
