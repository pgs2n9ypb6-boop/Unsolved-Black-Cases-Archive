// ============================================================================
// UNSOLVED BLACK CASES ARCHIVE — dashboard interactions
// Vanilla JS only. No frameworks, no external dependencies, no tracking.
// Loads /data/cases.json for search, timeline, and map views. Individual
// case pages are pre-rendered server-side, so JS is progressive enhancement.
// ============================================================================

(function () {
  "use strict";

  var DATA_URL = (document.body.getAttribute("data-root") || "") + "data/cases.json";
  var casesCache = null;

  function loadCases() {
    if (casesCache) return Promise.resolve(casesCache);
    // Case data is embedded inline in every page (see build.py) so search,
    // timeline, and map work even when the site is opened directly from
    // disk, where fetch() of a local file is blocked by the browser.
    if (window.__UBCA_CASES__) {
      casesCache = window.__UBCA_CASES__;
      return Promise.resolve(casesCache);
    }
    return fetch(DATA_URL)
      .then(function (r) { return r.json(); })
      .then(function (json) { casesCache = json; return json; })
      .catch(function () { return []; });
  }

  // ---------------------------------------------------------------------
  // Mobile drawer (left "Case Files" panel)
  // ---------------------------------------------------------------------
  var menuBtn = document.querySelector("[data-menu-toggle]");
  var leftPanel = document.querySelector(".panel-left");
  var scrim = document.querySelector(".panel-scrim");

  function openDrawer() {
    if (!leftPanel) return;
    leftPanel.classList.add("open");
    if (scrim) scrim.classList.add("open");
    if (menuBtn) menuBtn.setAttribute("aria-expanded", "true");
  }
  function closeDrawer() {
    if (!leftPanel) return;
    leftPanel.classList.remove("open");
    if (scrim) scrim.classList.remove("open");
    if (menuBtn) menuBtn.setAttribute("aria-expanded", "false");
  }
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      leftPanel.classList.contains("open") ? closeDrawer() : openDrawer();
    });
  }
  if (scrim) scrim.addEventListener("click", closeDrawer);
  var drawerCloseBtn = document.querySelector("[data-drawer-close]");
  if (drawerCloseBtn) drawerCloseBtn.addEventListener("click", closeDrawer);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { closeDrawer(); closeSearch(); }
  });

  // ---------------------------------------------------------------------
  // Ad-consent banner (Google AdSense). Shown once per browser until the
  // person accepts or declines; the choice is remembered via localStorage.
  // This is a baseline consent notice, not a certified Consent Management
  // Platform — Google's EU User Consent Policy requires a Google-certified
  // CMP for personalized ads to actually serve to EEA/UK visitors. Swap
  // this banner for a certified CMP (via AdSense > Privacy & messaging)
  // before relying on it for that.
  // ---------------------------------------------------------------------
  (function initConsentBanner() {
    var banner = document.getElementById("consent-banner");
    if (!banner) return;
    var CONSENT_KEY = "ubca-ad-consent";
    var existing = null;
    try { existing = window.localStorage.getItem(CONSENT_KEY); } catch (e) { /* storage disabled */ }
    if (!existing) banner.classList.add("open");

    function setConsent(value) {
      try { window.localStorage.setItem(CONSENT_KEY, value); } catch (e) { /* ignore */ }
      banner.classList.remove("open");
    }
    var acceptBtn = banner.querySelector("[data-consent-accept]");
    var declineBtn = banner.querySelector("[data-consent-decline]");
    if (acceptBtn) acceptBtn.addEventListener("click", function () { setConsent("accepted"); });
    if (declineBtn) declineBtn.addEventListener("click", function () { setConsent("declined"); });
  })();

  // ---------------------------------------------------------------------
  // Left panel: case list search + status filter chips (server-rendered list)
  // ---------------------------------------------------------------------
  function normalize(s) { return (s || "").toLowerCase().trim(); }

  // Single definition of "everything searchable about a case" — used by
  // both the left-panel/grid filter below and the global search overlay.
  // Reads from window.__UBCA_CASES__ (already loaded via <script src>
  // before this file runs) so the full case text lives in exactly one
  // place rather than being duplicated into HTML attributes on every page.
  var caseById = {};
  (window.__UBCA_CASES__ || []).forEach(function (c) { caseById[c.id] = c; });

  function caseFullText(c) {
    var parts = [
      c.name, c.city, c.county, c.state, c.year, c.caseType, c.status, c.caseSeries,
      c.summary, (c.known || []).join(" "), (c.unknown || []).join(" "),
      (c.unanswered || []).join(" "), (c.sources || []).map(function (s) { return s.name; }).join(" ")
    ];
    return normalize(parts.filter(Boolean).join(" "));
  }

  function filterLeftList() {
    var input = document.getElementById("pl-search-input");
    var items = document.querySelectorAll("[data-case-item]");
    if (!items.length) return;
    var query = input ? normalize(input.value) : "";
    var activeChip = document.querySelector('.pl-chip[aria-pressed="true"]');
    var activeStatus = activeChip ? activeChip.getAttribute("data-filter") : "all";

    // Track a visible count per parent list/grid so each one (the sidebar
    // list and, on the Case Index, the main board grid too) can show its
    // own "no results" message independently.
    var counts = [];
    items.forEach(function (item) {
      var caseObj = caseById[item.getAttribute("data-case-id")];
      // Full case text when we have it (name, location, and everything
      // written inside the case file); falls back to the lightweight
      // name/city/state/year attribute if the data lookup ever comes up
      // empty, so the list never just goes blank.
      var text = caseObj ? caseFullText(caseObj) : normalize(item.getAttribute("data-search"));
      var status = item.getAttribute("data-status");
      var caseType = item.getAttribute("data-case-type");
      var series = item.getAttribute("data-series-flag") === "true";
      var isNew = item.getAttribute("data-new-case") === "true";
      var matchesQuery = query === "" || text.indexOf(query) !== -1;
      var matchesStatus =
        activeStatus === "all" ||
        (activeStatus === "new" ? isNew :
         activeStatus === "series" ? series :
         activeStatus === "missing_persons" ? caseType === "missing_persons" :
         activeStatus === status);
      var visible = matchesQuery && matchesStatus;
      item.style.display = visible ? "" : "none";
      var group = item.parentElement;
      var entry = counts.filter(function (e) { return e.group === group; })[0];
      if (!entry) { entry = { group: group, count: 0 }; counts.push(entry); }
      if (visible) entry.count++;
    });

    counts.forEach(function (entry) {
      var host = entry.group.parentElement;
      var noResults = host ? host.querySelector(".no-results") : null;
      if (noResults) noResults.style.display = entry.count === 0 ? "block" : "none";
    });
  }
  var plInput = document.getElementById("pl-search-input");
  if (plInput) plInput.addEventListener("input", filterLeftList);
  document.querySelectorAll(".pl-chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
      document.querySelectorAll(".pl-chip").forEach(function (c) { c.setAttribute("aria-pressed", "false"); });
      chip.setAttribute("aria-pressed", "true");
      filterLeftList();
    });
  });

  // ---------------------------------------------------------------------
  // Global search overlay
  // ---------------------------------------------------------------------
  var searchOverlay = document.querySelector(".search-overlay");
  var searchInput = document.getElementById("global-search-input");
  var searchResults = document.querySelector(".search-results");
  var rootPrefix = document.body.getAttribute("data-root") || "";

  function openSearch() {
    if (!searchOverlay) return;
    searchOverlay.classList.add("open");
    if (searchInput) { searchInput.value = ""; searchInput.focus(); }
    renderSearchResults("");
  }
  function closeSearch() {
    if (!searchOverlay) return;
    searchOverlay.classList.remove("open");
  }
  document.querySelectorAll("[data-search-open]").forEach(function (btn) {
    btn.addEventListener("click", openSearch);
  });
  if (searchOverlay) {
    searchOverlay.addEventListener("click", function (e) {
      if (e.target === searchOverlay) closeSearch();
    });
  }
  document.addEventListener("keydown", function (e) {
    if ((e.key === "/" || (e.metaKey && e.key.toLowerCase() === "k")) &&
        document.activeElement.tagName !== "INPUT" && document.activeElement.tagName !== "TEXTAREA") {
      e.preventDefault();
      openSearch();
    }
  });

  function caseSearchFields(c) {
    // Ordered so the snippet shown to the user favors the most useful field
    // when a match isn't in the name/location itself.
    return [
      { label: "", text: c.name },
      { label: "SUMMARY", text: c.summary || "" },
      { label: "INVESTIGATION", text: (c.known || []).join(" ") },
      { label: "WHAT REMAINS UNKNOWN", text: (c.unknown || []).join(" ") },
      { label: "UNANSWERED QUESTIONS", text: (c.unanswered || []).join(" ") },
      { label: "SOURCES", text: (c.sources || []).map(function (s) { return s.name; }).join(" ") },
      { label: "", text: [c.city, c.county, c.state, c.year, c.caseType, c.status, c.caseSeries].filter(Boolean).join(" ") }
    ];
  }

  function snippetAround(text, q, radius) {
    var idx = normalize(text).indexOf(q);
    if (idx === -1) return "";
    var start = Math.max(0, idx - radius);
    var end = Math.min(text.length, idx + q.length + radius);
    var s = (start > 0 ? "\u2026" : "") + text.slice(start, end).trim() + (end < text.length ? "\u2026" : "");
    return s;
  }

  function renderSearchResults(query) {
    if (!searchResults) return;
    loadCases().then(function (cases) {
      var q = normalize(query);
      var matches = [];
      cases.forEach(function (c) {
        if (q === "") { matches.push({ c: c, field: null, snippet: "" }); return; }
        var fields = caseSearchFields(c);
        for (var i = 0; i < fields.length; i++) {
          if (normalize(fields[i].text).indexOf(q) !== -1) {
            matches.push({
              c: c,
              field: fields[i].label,
              snippet: fields[i].label ? snippetAround(fields[i].text, q, 45) : ""
            });
            break; // one result per case, from its best-matching field
          }
        }
      });
      if (!matches.length) {
        searchResults.innerHTML = '<div class="sr-empty">NO MATCHING CASE RECORDS.</div>';
        return;
      }
      searchResults.innerHTML = matches.slice(0, 30).map(function (m) {
        var c = m.c;
        var meta = [c.year, [c.city, c.state].filter(Boolean).join(", "), c.status].filter(Boolean).join(" \u00b7 ");
        var snippetHtml = m.snippet
          ? '<span class="srs">' + escapeHtml(m.field) + ': ' + escapeHtml(m.snippet) + '</span>'
          : "";
        return '<a class="sr-item" href="' + rootPrefix + 'cases/' + c.id + '.html">' +
          '<span class="srn">' + escapeHtml(c.name) + '</span>' +
          '<span class="srm">' + escapeHtml(meta.toUpperCase()) + '</span>' + snippetHtml + '</a>';
      }).join("");
    });
  }
  if (searchInput) {
    searchInput.addEventListener("input", function () { renderSearchResults(searchInput.value); });
  }

  function escapeHtml(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // ---------------------------------------------------------------------
  // Investigation board: drag cards, pan canvas, zoom, reset
  // ---------------------------------------------------------------------
  // Investigation board: drag cards, pan canvas, zoom, reset, and
  // visitor-added "your own note" cards (a distinct color, saved only in
  // this browser via localStorage — same private, no-account model as the
  // Research Notes panel, just rendered directly on the board instead of
  // in a list).
  var BOARD_NOTES_KEY = "ubca_board_user_cards"; // { [caseId]: [{id, text, x, y}] }
  function readBoardNotes(caseId) {
    try {
      var all = JSON.parse(localStorage.getItem(BOARD_NOTES_KEY) || "{}");
      return all[caseId] || [];
    } catch (e) { return []; }
  }
  function writeBoardNotes(caseId, list) {
    try {
      var all = JSON.parse(localStorage.getItem(BOARD_NOTES_KEY) || "{}");
      if (list.length) all[caseId] = list; else delete all[caseId];
      localStorage.setItem(BOARD_NOTES_KEY, JSON.stringify(all));
    } catch (e) { /* storage unavailable — fail silently */ }
  }

  function initBoard() {
    var viewport = document.querySelector(".board-viewport");
    var canvas = document.querySelector(".board-canvas");
    if (!viewport || !canvas) return;
    var caseId = canvas.getAttribute("data-board-canvas");
    var cards = Array.prototype.slice.call(canvas.querySelectorAll(".board-card"));
    var svg = canvas.querySelector("svg.connectors");
    var hub = canvas.querySelector(".board-card.hub");

    var scale = 1;
    var panX = 0, panY = 0;

    function applyTransform() {
      canvas.style.transform = "translate(" + panX + "px," + panY + "px) scale(" + scale + ")";
    }

    // Convert natural CSS-grid-flow positions into fixed absolute coordinates
    // so cards can be dragged freely. We let the browser lay the cards out
    // with real content heights first (grid auto-flow), measure where each
    // one landed, then freeze those exact coordinates — this avoids the
    // uneven gaps/overlaps a fixed row-height guess would produce when card
    // content (e.g. a long Sources list) is taller than its neighbors.
    // User-added note cards already have a saved (x, y) and are excluded
    // from this auto-flow pass so dragging them doesn't get undone by a
    // later relayout (e.g. on window resize).
    function layoutCards() {
      var autoCards = cards.filter(function (c) { return !c.classList.contains("user-card"); });
      canvas.style.display = "grid";
      canvas.style.gridTemplateColumns = "repeat(auto-fill, 250px)";
      canvas.style.gap = "20px";
      canvas.style.paddingBottom = "32px";
      autoCards.forEach(function (card) {
        card.style.position = "static";
        card.style.left = "";
        card.style.top = "";
      });
      requestAnimationFrame(function () {
        var canvasRect = canvas.getBoundingClientRect();
        autoCards.forEach(function (card) {
          var r = card.getBoundingClientRect();
          card.style.left = (r.left - canvasRect.left) + "px";
          card.style.top = (r.top - canvasRect.top) + "px";
        });
        canvas.style.display = "block";
        autoCards.forEach(function (card) { card.style.position = "absolute"; });
        var maxBottom = 0;
        cards.forEach(function (card) {
          maxBottom = Math.max(maxBottom, card.offsetTop + card.offsetHeight);
        });
        canvas.style.minHeight = (maxBottom + 60) + "px";
        drawConnectors();
      });
    }

    function cardCenter(card) {
      return {
        x: card.offsetLeft + card.offsetWidth / 2,
        y: card.offsetTop + card.offsetHeight / 2
      };
    }

    function drawConnectors() {
      if (!svg) return;
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      if (!hub) return;
      var hc = cardCenter(hub);
      cards.forEach(function (card) {
        if (card === hub) return;
        var cc = cardCenter(card);
        var line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", hc.x); line.setAttribute("y1", hc.y);
        line.setAttribute("x2", cc.x); line.setAttribute("y2", cc.y);
        if (card.classList.contains("user-card")) line.setAttribute("class", "user-connector");
        svg.appendChild(line);
      });
    }

    // Drag individual cards
    function attachDrag(card) {
      var dragging = false, startX, startY, origLeft, origTop;
      card.addEventListener("pointerdown", function (e) {
        if (e.target.closest("textarea, button")) return;
        dragging = true;
        card.setPointerCapture(e.pointerId);
        startX = e.clientX; startY = e.clientY;
        origLeft = card.offsetLeft; origTop = card.offsetTop;
        card.style.zIndex = 10;
      });
      card.addEventListener("pointermove", function (e) {
        if (!dragging) return;
        var dx = (e.clientX - startX) / scale;
        var dy = (e.clientY - startY) / scale;
        card.style.left = (origLeft + dx) + "px";
        card.style.top = (origTop + dy) + "px";
        drawConnectors();
      });
      function endDrag() {
        if (!dragging) return;
        dragging = false;
        if (card.classList.contains("user-card")) saveUserCards();
      }
      card.addEventListener("pointerup", endDrag);
      card.addEventListener("pointercancel", endDrag);
    }
    cards.forEach(attachDrag);

    // ---- Visitor-added note cards -----------------------------------
    function saveUserCards() {
      if (!caseId) return;
      var list = cards.filter(function (c) { return c.classList.contains("user-card"); }).map(function (c) {
        return {
          id: c.getAttribute("data-user-card-id"),
          text: c.querySelector("textarea") ? c.querySelector("textarea").value : "",
          x: c.offsetLeft, y: c.offsetTop
        };
      });
      writeBoardNotes(caseId, list);
    }

    function buildUserCard(note) {
      var card = document.createElement("div");
      card.className = "board-card user-card";
      card.setAttribute("data-user-card-id", note.id);
      card.style.position = "absolute";
      card.style.left = note.x + "px";
      card.style.top = note.y + "px";
      card.innerHTML =
        '<span class="bc-label">Your Note</span>' +
        '<button type="button" class="user-card-remove" aria-label="Remove this note">\u00d7</button>' +
        '<textarea placeholder="Add your own observation\u2026"></textarea>';
      var textarea = card.querySelector("textarea");
      textarea.value = note.text || "";
      var timer = null;
      textarea.addEventListener("input", function () {
        if (timer) clearTimeout(timer);
        timer = setTimeout(saveUserCards, 500);
      });
      card.querySelector(".user-card-remove").addEventListener("click", function () {
        cards = cards.filter(function (c) { return c !== card; });
        card.remove();
        saveUserCards();
        drawConnectors();
      });
      attachDrag(card);
      return card;
    }

    function addUserCard(text, x, y) {
      var note = { id: "u" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6), text: text || "", x: x, y: y };
      var card = buildUserCard(note);
      canvas.appendChild(card);
      cards.push(card);
      saveUserCards();
      drawConnectors();
      return card;
    }

    // Restore any previously saved user cards for this case.
    if (caseId) {
      readBoardNotes(caseId).forEach(function (note) {
        var card = buildUserCard(note);
        canvas.appendChild(card);
        cards.push(card);
      });
    }

    var addBtn = document.querySelector("[data-add-board-note]");
    if (addBtn) {
      addBtn.addEventListener("click", function () {
        var vp = viewport.getBoundingClientRect();
        // Drop the new card near the middle of the visible viewport,
        // converted into canvas coordinates (accounting for current pan/zoom).
        var x = (vp.width / 2 - panX) / scale - 110;
        var y = (vp.height / 2 - panY) / scale - 40;
        var card = addUserCard("", Math.max(0, x), Math.max(0, y));
        drawConnectors();
        var ta = card.querySelector("textarea");
        if (ta) ta.focus();
      });
    }

    // Pan canvas when dragging empty viewport space
    var panning = false, panStartX, panStartY, startPanX, startPanY;
    viewport.addEventListener("pointerdown", function (e) {
      if (e.target.closest(".board-card")) return;
      panning = true;
      panStartX = e.clientX; panStartY = e.clientY;
      startPanX = panX; startPanY = panY;
      viewport.style.cursor = "grabbing";
    });
    window.addEventListener("pointermove", function (e) {
      if (!panning) return;
      panX = startPanX + (e.clientX - panStartX);
      panY = startPanY + (e.clientY - panStartY);
      applyTransform();
    });
    window.addEventListener("pointerup", function () { panning = false; viewport.style.cursor = ""; });

    // Two-finger pinch drives our OWN zoom instead of the phone's native
    // page zoom. Without this, a pinch gesture over the board zooms the
    // whole page (including the toolbar) via the browser itself — a
    // separate system from ours — and on some phones that can leave a
    // visitor zoomed in with no way back, since our "− ZOOM" button only
    // resets our canvas scale, not the browser's own zoom level. Handling
    // touch pinch here ourselves means there's only ever one zoom system,
    // and it's always reachable through the toolbar.
    var pinchStartDist = null, pinchStartScale = 1;
    function touchDist(t0, t1) {
      var dx = t0.clientX - t1.clientX, dy = t0.clientY - t1.clientY;
      return Math.sqrt(dx * dx + dy * dy);
    }
    viewport.addEventListener("touchstart", function (e) {
      if (e.touches.length === 2) {
        pinchStartDist = touchDist(e.touches[0], e.touches[1]);
        pinchStartScale = scale;
      }
    }, { passive: true });
    viewport.addEventListener("touchmove", function (e) {
      if (e.touches.length === 2) {
        e.preventDefault(); // block native page pinch-zoom — we're handling it
        if (pinchStartDist) {
          var dist = touchDist(e.touches[0], e.touches[1]);
          setScale(pinchStartScale * (dist / pinchStartDist));
        }
      }
    }, { passive: false });
    viewport.addEventListener("touchend", function (e) {
      if (e.touches.length < 2) pinchStartDist = null;
    }, { passive: true });

    // Zoom controls
    var zoomIn = document.querySelector("[data-board-zoom-in]");
    var zoomOut = document.querySelector("[data-board-zoom-out]");
    var zoomReset = document.querySelector("[data-board-reset]");
    function setScale(s) { scale = Math.min(1.6, Math.max(0.5, s)); applyTransform(); }
    if (zoomIn) zoomIn.addEventListener("click", function () { setScale(scale + 0.1); });
    if (zoomOut) zoomOut.addEventListener("click", function () { setScale(scale - 0.1); });
    if (zoomReset) zoomReset.addEventListener("click", function () {
      scale = 1; panX = 0; panY = 0; applyTransform(); layoutCards();
    });
    viewport.addEventListener("wheel", function (e) {
      if (!e.ctrlKey) return;
      e.preventDefault();
      setScale(scale + (e.deltaY < 0 ? 0.08 : -0.08));
    }, { passive: false });

    layoutCards();
    window.addEventListener("resize", layoutCards);
  }

  // ---------------------------------------------------------------------
  // Archive view tabs (Board grid / Timeline / Map) — cases/index.html
  // ---------------------------------------------------------------------
  function initArchiveViews() {
    var tabs = document.querySelectorAll("[data-view-tab]");
    if (!tabs.length) return;
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        var target = tab.getAttribute("data-view-tab");
        tabs.forEach(function (t) { t.setAttribute("aria-pressed", "false"); });
        tab.setAttribute("aria-pressed", "true");
        document.querySelectorAll(".view-panel").forEach(function (p) { p.classList.remove("active"); });
        var panel = document.getElementById("view-" + target);
        if (panel) panel.classList.add("active");
        if (target === "timeline") renderTimeline();
        if (target === "map") renderMap();
        if (target === "connections") renderConnections();
      });
    });
  }

  // ---------------------------------------------------------------------
  // Case Connections graph — a circular node/edge diagram of documented
  // relationships between specific cases (a witness, a shared location, a
  // shared source citing both) plus formal case series (Freeway Phantom,
  // Silver Dollar Group), drawn from window.__UBCA_CONNECTIONS__. Every
  // edge here corresponds to something already written into the relevant
  // case files — this view doesn't assert any new connection, it just
  // makes the ones already documented visible and clickable. Deliberately
  // a plain deterministic circular layout (no force-directed physics, no
  // graph library) to match the rest of the site's dependency-free JS.
  function renderConnections() {
    var host = document.getElementById("view-connections");
    if (!host || host.getAttribute("data-built") === "true") return;
    var data = window.__UBCA_CONNECTIONS__;
    if (!data) { host.innerHTML = '<p class="no-results">Connections data unavailable.</p>'; return; }

    // Build the node list: one hub per series with 2+ members, plus every
    // case that appears either in a series or a direct link. Series
    // members are ordered right after their hub so the circle groups
    // related nodes together instead of interleaving them randomly.
    var nodes = [];
    var nodeIndex = {};
    function addNode(id, label, kind, href) {
      if (nodeIndex.hasOwnProperty(id)) return;
      nodeIndex[id] = nodes.length;
      nodes.push({ id: id, label: label, kind: kind, href: href });
    }
    var seriesNames = Object.keys(data.series || {}).filter(function (name) {
      return (data.series[name] || []).length >= 2;
    });
    seriesNames.sort();
    var edges = [];
    seriesNames.forEach(function (name) {
      var hubId = "series:" + name;
      var slug = (data.seriesSlugs || {})[name];
      addNode(hubId, name, "series", slug ? slug + ".html" : null);
      (data.series[name] || []).forEach(function (caseId) {
        var c = caseById[caseId];
        addNode(caseId, c ? c.name : caseId, "case", caseId + ".html");
        edges.push({ a: hubId, b: caseId, label: name + " \u2014 documented case series" });
      });
    });
    (data.links || []).forEach(function (link) {
      var ca = caseById[link.a], cb = caseById[link.b];
      addNode(link.a, ca ? ca.name : link.a, "case", link.a + ".html");
      addNode(link.b, cb ? cb.name : link.b, "case", link.b + ".html");
      edges.push({ a: link.a, b: link.b, label: link.label });
    });

    if (!nodes.length) {
      host.innerHTML = '<p class="no-results">No documented connections yet.</p>';
      host.setAttribute("data-built", "true");
      return;
    }

    var size = 640, cx = size / 2, cy = size / 2, r = size / 2 - 90;
    nodes.forEach(function (n, i) {
      var angle = (i / nodes.length) * Math.PI * 2 - Math.PI / 2;
      n.x = cx + r * Math.cos(angle);
      n.y = cy + r * Math.sin(angle);
    });

    function truncate(s, n) { return s && s.length > n ? s.slice(0, n - 1) + "\u2026" : s; }

    var edgeSvg = edges.map(function (e) {
      var a = nodes[nodeIndex[e.a]], b = nodes[nodeIndex[e.b]];
      if (!a || !b) return "";
      return '<line class="conn-edge" x1="' + a.x + '" y1="' + a.y + '" x2="' + b.x + '" y2="' + b.y +
        '" data-edge-label="' + escAttr(e.label) + '"></line>';
    }).join("");

    var nodeSvg = nodes.map(function (n) {
      var isSeries = n.kind === "series";
      var radius = isSeries ? 9 : 6;
      return '<g class="conn-node conn-node-' + n.kind + '" data-node-id="' + escAttr(n.id) + '" ' +
        'data-href="' + escAttr(n.href || "") + '" tabindex="0" role="link" aria-label="' + escAttr(n.label) + '">' +
        '<circle cx="' + n.x + '" cy="' + n.y + '" r="' + radius + '"></circle>' +
        '<text x="' + n.x + '" y="' + (n.y + (n.y > cy ? 18 : -12)) + '" text-anchor="middle">' +
        escHtml(truncate(n.label, isSeries ? 22 : 16)) + '</text>' +
        '</g>';
    }).join("");

    host.innerHTML =
      '<p class="conn-intro">Documented relationships between cases in this archive \u2014 a shared ' +
      'witness, a shared location, a shared source, or a formal case series. Every connection here is ' +
      'already written into the relevant case files; this is just a way to see them. Tap a node to open ' +
      'that case, or a line to see how the two are connected.</p>' +
      '<div class="conn-wrap"><svg class="conn-svg" viewBox="0 0 ' + size + ' ' + size + '" role="img" ' +
      'aria-label="Graph of connected cases">' + edgeSvg + nodeSvg + '</svg>' +
      '<div class="conn-tooltip" id="conn-tooltip" hidden></div></div>';
    host.setAttribute("data-built", "true");

    var tooltip = document.getElementById("conn-tooltip");
    host.querySelectorAll(".conn-edge").forEach(function (edge) {
      edge.addEventListener("mouseenter", function () { showTooltip(edge.getAttribute("data-edge-label")); });
      edge.addEventListener("mouseleave", hideTooltip);
      edge.addEventListener("click", function () { showTooltip(edge.getAttribute("data-edge-label")); });
    });
    function showTooltip(text) {
      if (!tooltip) return;
      tooltip.textContent = text;
      tooltip.hidden = false;
    }
    function hideTooltip() { if (tooltip) tooltip.hidden = true; }

    host.querySelectorAll(".conn-node").forEach(function (node) {
      var href = node.getAttribute("data-href");
      if (!href) return;
      function go() { window.location.href = href; }
      node.addEventListener("click", go);
      node.addEventListener("keydown", function (e) { if (e.key === "Enter") go(); });
    });
  }

  function escAttr(s) { return String(s || "").replace(/"/g, "&quot;"); }
  function escHtml(s) {
    return String(s || "").replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; });
  }

  function renderTimeline() {
    var host = document.getElementById("view-timeline");
    if (!host || host.getAttribute("data-built") === "true") return;
    loadCases().then(function (cases) {
      var byDecade = {};
      cases.forEach(function (c) {
        if (!c.year) return;
        var decade = Math.floor(c.year / 10) * 10 + "s";
        (byDecade[decade] = byDecade[decade] || []).push(c);
      });
      var decades = Object.keys(byDecade).sort();
      var btnsHtml = decades.map(function (d, i) {
        return '<button class="decade-btn" data-decade="' + d + '" aria-pressed="' + (i === 0 ? "true" : "false") + '">' + d + '</button>';
      }).join("");
      host.innerHTML =
        '<div class="timeline-decades">' + btnsHtml + '</div>' +
        '<div class="related-grid" id="timeline-results"></div>';
      host.setAttribute("data-built", "true");

      function showDecade(d) {
        var results = document.getElementById("timeline-results");
        results.innerHTML = (byDecade[d] || []).map(caseCardHtml).join("");
      }
      host.querySelectorAll(".decade-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
          host.querySelectorAll(".decade-btn").forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
          btn.setAttribute("aria-pressed", "true");
          showDecade(btn.getAttribute("data-decade"));
        });
      });
      if (decades.length) showDecade(decades[0]);
    });
  }

  // ---------------------------------------------------------------------
  // Interactive US map: real state shapes (SVG path data from
  // window.__US_STATE_PATHS__, see js/us-states-paths.js), not an abstract
  // grid. Clicking a highlighted state opens a small popup right at that
  // state showing its case names, rather than a separate panel below.
  // ---------------------------------------------------------------------
  var STATE_NAMES = {
    AL: "Alabama", AK: "Alaska", AZ: "Arizona", AR: "Arkansas", CA: "California",
    CO: "Colorado", CT: "Connecticut", DE: "Delaware", DC: "Washington, D.C.",
    FL: "Florida", GA: "Georgia", HI: "Hawaii", ID: "Idaho", IL: "Illinois",
    IN: "Indiana", IA: "Iowa", KS: "Kansas", KY: "Kentucky", LA: "Louisiana",
    ME: "Maine", MD: "Maryland", MA: "Massachusetts", MI: "Michigan", MN: "Minnesota",
    MS: "Mississippi", MO: "Missouri", MT: "Montana", NE: "Nebraska", NV: "Nevada",
    NH: "New Hampshire", NJ: "New Jersey", NM: "New Mexico", NY: "New York",
    NC: "North Carolina", ND: "North Dakota", OH: "Ohio", OK: "Oklahoma", OR: "Oregon",
    PA: "Pennsylvania", RI: "Rhode Island", SC: "South Carolina", SD: "South Dakota",
    TN: "Tennessee", TX: "Texas", UT: "Utah", VT: "Vermont", VA: "Virginia",
    WA: "Washington", WV: "West Virginia", WI: "Wisconsin", WY: "Wyoming"
  };
  var MAP_VIEWBOX = "0 0 959 593";

  function stateCode(name) {
    if (!name) return null;
    var trimmed = name.trim();
    if (STATE_NAMES[trimmed.toUpperCase()]) return trimmed.toUpperCase();
    var upper = trimmed.toUpperCase();
    for (var code in STATE_NAMES) { if (STATE_NAMES[code].toUpperCase() === upper) return code; }
    return trimmed.toUpperCase();
  }

  function renderMap(containerId) {
    var host = document.getElementById(containerId || "view-map");
    if (!host || host.getAttribute("data-built") === "true") return;
    var paths = window.__US_STATE_PATHS__;
    if (!paths) return;
    loadCases().then(function (cases) {
      var byState = {};
      cases.forEach(function (c) {
        var code = stateCode(c.state);
        if (!code) return;
        (byState[code] = byState[code] || []).push(c);
      });

      var svgPaths = Object.keys(paths).map(function (code) {
        var count = (byState[code] || []).length;
        var cls = count ? "has-cases" : "";
        var name = STATE_NAMES[code] || code;
        return '<path d="' + paths[code] + '" class="' + cls + '" data-state-code="' + code + '" ' +
          (count ? 'tabindex="0" role="button" aria-label="' + escapeHtml(name) + ', ' + count + (count === 1 ? ' case' : ' cases') + '"' : 'aria-hidden="true"') +
          '></path>';
      }).join("");

      host.innerHTML =
        '<div class="map-note">Click a highlighted state to see its cases.</div>' +
        '<div class="us-map-wrap">' +
        '<svg class="us-map-svg" viewBox="' + MAP_VIEWBOX + '" xmlns="http://www.w3.org/2000/svg">' + svgPaths + '</svg>' +
        '<div class="map-popup" id="map-popup-' + (containerId || "view-map") + '" aria-live="polite"></div>' +
        '</div>';
      host.setAttribute("data-built", "true");

      var wrap = host.querySelector(".us-map-wrap");
      var svg = host.querySelector(".us-map-svg");
      var popup = host.querySelector(".map-popup");
      var stateEls = host.querySelectorAll(".us-map-svg path[data-state-code]");
      var activeCode = null;

      function closePopup() {
        popup.classList.remove("open");
        stateEls.forEach(function (p) { p.classList.remove("active"); });
        activeCode = null;
      }

      function openPopupFor(pathEl, code) {
        var list = byState[code] || [];
        if (!list.length) return;
        stateEls.forEach(function (p) { p.classList.remove("active"); });
        pathEl.classList.add("active");
        activeCode = code;

        var items = list.map(function (c) {
          var meta = [c.year, c.status].filter(Boolean).join(" \u00b7 ");
          return '<li><a href="' + rootPrefix + 'cases/' + c.id + '.html">' + escapeHtml(c.name) +
            '<span class="mp-meta">' + escapeHtml(meta.toUpperCase()) + '</span></a></li>';
        }).join("");
        popup.innerHTML =
          '<div class="mp-head"><span>' + escapeHtml(STATE_NAMES[code] || code) + ' \u2014 ' + list.length +
          (list.length === 1 ? ' case' : ' cases') + '</span>' +
          '<button type="button" class="mp-close" aria-label="Close">\u00d7</button></div>' +
          '<ul class="mp-list">' + items + '</ul>';

        // Position the popup at the clicked state's on-screen centroid using
        // getBBox (SVG-space) mapped through the SVG's current CTM, so it
        // lands in the right place at any zoom/viewport size. Then clamp to
        // the map's own bounds so states near an edge (e.g. Washington on a
        // narrow phone screen) never push the popup off-screen — the arrow
        // shifts to compensate so it still points at the actual state.
        var bbox = pathEl.getBBox();
        var cx = bbox.x + bbox.width / 2;
        var cy = bbox.y;
        var pt = svg.createSVGPoint();
        pt.x = cx; pt.y = cy;
        var screenPt = pt.matrixTransform(pathEl.getScreenCTM());
        var wrapRect = wrap.getBoundingClientRect();
        var targetX = screenPt.x - wrapRect.left;
        var targetY = screenPt.y - wrapRect.top;

        popup.style.left = targetX + "px";
        popup.style.top = Math.max(targetY, 24) + "px";
        var popupWidth = popup.getBoundingClientRect().width || 220;
        var margin = 8;
        var halfWidth = popupWidth / 2;
        var minCenter = halfWidth + margin;
        var maxCenter = wrapRect.width - halfWidth - margin;
        var clampedX = Math.min(Math.max(targetX, minCenter), maxCenter);
        var arrowOffset = targetX - clampedX;
        var maxArrowOffset = halfWidth - 14;
        arrowOffset = Math.min(Math.max(arrowOffset, -maxArrowOffset), maxArrowOffset);
        popup.style.left = clampedX + "px";
        popup.style.setProperty("--arrow-offset", arrowOffset + "px");

        popup.classList.remove("open");
        requestAnimationFrame(function () { popup.classList.add("open"); });
        popup.querySelector(".mp-close").addEventListener("click", closePopup);
      }

      stateEls.forEach(function (pathEl) {
        var code = pathEl.getAttribute("data-state-code");
        if (!(byState[code] || []).length) return;
        pathEl.addEventListener("click", function () {
          if (activeCode === code) { closePopup(); } else { openPopupFor(pathEl, code); }
        });
        pathEl.addEventListener("keydown", function (e) {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            if (activeCode === code) { closePopup(); } else { openPopupFor(pathEl, code); }
          }
        });
      });

      document.addEventListener("click", function (e) {
        if (!wrap.contains(e.target)) closePopup();
      });
      window.addEventListener("resize", closePopup);
    });
  }

  function caseCardHtml(c) {
    var meta = [c.year, [c.city, c.state].filter(Boolean).join(", ")].filter(Boolean).join(" \u00b7 ");
    return '<a class="related-card" href="' + rootPrefix + 'cases/' + c.id + '.html">' +
      '<span class="rc-name">' + escapeHtml(c.name) + '</span>' +
      '<span class="rc-meta">' + escapeHtml(meta.toUpperCase()) + '</span></a>';
  }

  // ---------------------------------------------------------------------
  // Footer visit counter. Uses countapi.mileshilliard.com (a maintained,
  // no-signup revival of the original countapi.xyz, which is dead). Every
  // page load increments the same key, so the number reflects total page
  // views across the whole site, not unique visitors.
  function initVisitCounter() {
    var el = document.getElementById("site-visit-count");
    if (!el) return;
    fetch("https://countapi.mileshilliard.com/api/v1/hit/unsolved-black-cases-archive-visits")
      .then(function (res) { return res.json(); })
      .then(function (data) {
        var n = data && (data.value !== undefined ? data.value : data.count);
        if (typeof n === "number") el.textContent = n.toLocaleString();
        else el.parentElement.style.display = "none";
      })
      .catch(function () {
        // Counter service unreachable — hide the line rather than show "…" forever.
        if (el.parentElement) el.parentElement.style.display = "none";
      });
  }

  // "Today" visit counter — same free service, same hit-per-pageview
  // approach, but the key itself is stamped with the current date
  // (e.g. ...-visits-2026-08-27). CountAPI has no built-in daily reset, so
  // this is the standard workaround: a key that's never been hit before
  // starts at 0, and since a new date makes a brand-new key, the count
  // effectively resets itself at midnight with no cron job or backend
  // needed. "Today" is each visitor's own local date, not a single global
  // cutover — a visitor's browser decides what day it is for its own
  // requests, so this is an approximation, not a precise UTC rollover.
  function initDailyVisitCounter() {
    var el = document.getElementById("site-visit-today-count");
    if (!el) return;
    var d = new Date();
    function pad(n) { return n < 10 ? "0" + n : "" + n; }
    var dateKey = d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
    fetch("https://countapi.mileshilliard.com/api/v1/hit/unsolved-black-cases-archive-visits-" + dateKey)
      .then(function (res) { return res.json(); })
      .then(function (data) {
        var n = data && (data.value !== undefined ? data.value : data.count);
        if (typeof n === "number") el.textContent = n.toLocaleString();
        else if (el.parentElement) el.parentElement.style.display = "none";
      })
      .catch(function () {
        if (el.parentElement) el.parentElement.style.display = "none";
      });
  }

  // "Case of the Week" — homepage rotation, computed client-side so it
  // advances every real week with no rebuild or backend needed. The week
  // number is days-since-a-fixed-Monday-epoch divided by 7, modulo the
  // total case count, so every case eventually gets a turn and the whole
  // cycle repeats once every ~N weeks (N = case count). Deliberately not
  // per-visit-random — the goal is the same case all week for everyone,
  // so a visitor has a reason to check back next week for a new one.
  function initCaseOfWeek() {
    var container = document.getElementById("case-of-week");
    if (!container) return;
    var cases = window.__UBCA_CASES__ || [];
    if (!cases.length) return;
    var EPOCH = Date.UTC(2020, 0, 6); // an arbitrary fixed Monday
    var weekIndex = Math.floor((Date.now() - EPOCH) / (7 * 24 * 60 * 60 * 1000));
    var idx = ((weekIndex % cases.length) + cases.length) % cases.length;
    var c = cases[idx];
    var loc = [c.city, c.state].filter(Boolean).join(", ");
    var locYear = [loc, c.year].filter(Boolean).join(" \u2014 ");
    container.innerHTML =
      '<div class="fc-body">' +
      '<span class="fc-eyebrow">Case of the Week</span>' +
      "<h2>" + escHtml(c.name) + "</h2>" +
      '<div class="fc-meta"><span>' + escHtml(locYear) + "</span></div>" +
      '<a class="fc-link" href="cases/' + c.id + '.html">Read the Case \u2192</a>' +
      "</div>";
  }

  // Bottom nav "active page" highlight — plain pathname comparison rather
  // than threading an active-page flag through every page_shell() call
  // site across the whole codebase for one small visual cue.
  function initBottomNavActiveState() {
    var items = document.querySelectorAll("[data-bn-path]");
    if (!items.length) return;
    var here = window.location.pathname;
    var isHome = here === "/" || /\/index\.html$/.test(here) && here.replace(/index\.html$/, "").split("/").filter(Boolean).length === 0;
    items.forEach(function (item) {
      var target = item.getAttribute("data-bn-path").replace(/^(\.\.\/)+/, "");
      var isTargetHome = target === "index.html";
      if ((isTargetHome && isHome) || (!isTargetHome && here.indexOf(target) !== -1)) {
        item.classList.add("bn-active");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initBoard();
    initArchiveViews();
    // Homepage map renders immediately (not behind a tab, unlike the Case
    // Index's Map view) — it's a no-op if #home-map isn't on the page.
    renderMap("home-map");
    initVisitCounter();
    initDailyVisitCounter();
    initCaseOfWeek();
    initBottomNavActiveState();
  });
})();
