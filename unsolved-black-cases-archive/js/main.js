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
      var matchesQuery = query === "" || text.indexOf(query) !== -1;
      var matchesStatus =
        activeStatus === "all" ||
        (activeStatus === "series" ? series :
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
  function initBoard() {
    var viewport = document.querySelector(".board-viewport");
    var canvas = document.querySelector(".board-canvas");
    if (!viewport || !canvas) return;
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
    function layoutCards() {
      canvas.style.display = "grid";
      canvas.style.gridTemplateColumns = "repeat(auto-fill, 250px)";
      canvas.style.gap = "20px";
      canvas.style.paddingBottom = "32px";
      cards.forEach(function (card) {
        card.style.position = "static";
        card.style.left = "";
        card.style.top = "";
      });
      requestAnimationFrame(function () {
        var canvasRect = canvas.getBoundingClientRect();
        cards.forEach(function (card) {
          var r = card.getBoundingClientRect();
          card.style.left = (r.left - canvasRect.left) + "px";
          card.style.top = (r.top - canvasRect.top) + "px";
        });
        canvas.style.display = "block";
        cards.forEach(function (card) { card.style.position = "absolute"; });
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
        svg.appendChild(line);
      });
    }

    // Drag individual cards
    cards.forEach(function (card) {
      var dragging = false, startX, startY, origLeft, origTop;
      card.addEventListener("pointerdown", function (e) {
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
      function endDrag() { dragging = false; }
      card.addEventListener("pointerup", endDrag);
      card.addEventListener("pointercancel", endDrag);
    });

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
      });
    });
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
  // Interactive US state grid map. A "tile grid" layout (each state a
  // clickable square, positioned to approximate its real geography) rather
  // than a traced geographic SVG — this needs no external map data or API,
  // stays perfectly crisp at any size, and every state (including small
  // ones like DC and RI) gets an equally easy-to-click target.
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
  // [row, column] on a 12-col grid, approximating true position.
  var STATE_GRID = {
    ME: [1, 12], WA: [3, 1], MT: [3, 3], ND: [3, 4], MN: [3, 5], WI: [3, 7],
    VT: [2, 10], NH: [2, 11], NY: [3, 10], MA: [3, 11],
    ID: [4, 2], WY: [4, 3], SD: [4, 4], IA: [4, 5], IL: [4, 6], MI: [4, 7], PA: [4, 9], NJ: [4, 10], CT: [4, 11], RI: [4, 12],
    OR: [5, 1], NV: [5, 2], UT: [5, 3], CO: [5, 4], NE: [5, 5], MO: [5, 6], IN: [5, 7], OH: [5, 8], WV: [5, 9], VA: [5, 10], MD: [5, 11], DE: [5, 12],
    CA: [6, 2], AZ: [6, 3], NM: [6, 4], KS: [6, 5], AR: [6, 6], KY: [6, 7], TN: [6, 8], NC: [6, 9], SC: [6, 10], DC: [6, 11],
    OK: [7, 5], LA: [7, 6], MS: [7, 7], AL: [7, 8], GA: [7, 9],
    AK: [8, 1], HI: [8, 2], TX: [8, 5], FL: [8, 10]
  };

  function stateCode(name) {
    if (!name) return null;
    var trimmed = name.trim();
    if (STATE_NAMES[trimmed.toUpperCase()]) return trimmed.toUpperCase();
    var upper = trimmed.toUpperCase();
    for (var code in STATE_NAMES) { if (STATE_NAMES[code].toUpperCase() === upper) return code; }
    return trimmed.toUpperCase();
  }

  function renderMap() {
    var host = document.getElementById("view-map");
    if (!host || host.getAttribute("data-built") === "true") return;
    loadCases().then(function (cases) {
      var byState = {};
      cases.forEach(function (c) {
        var code = stateCode(c.state);
        if (!code) return;
        (byState[code] = byState[code] || []).push(c);
      });

      var tiles = Object.keys(STATE_GRID).map(function (code) {
        var pos = STATE_GRID[code];
        var count = (byState[code] || []).length;
        var cls = "state-tile" + (count ? " has-cases" : " empty");
        return '<button type="button" class="' + cls + '" data-state-code="' + code + '" ' +
          'style="grid-row:' + pos[0] + '; grid-column:' + pos[1] + ';" ' +
          'aria-pressed="false"' + (count ? "" : " disabled") + '>' +
          '<span class="st-code">' + code + '</span>' +
          (count ? '<span class="st-count">' + count + '</span>' : '') +
          '</button>';
      }).join("");

      host.innerHTML =
        '<div class="map-note">Click a highlighted state to see its cases. Grid position approximates real ' +
        'geography; every state \u2014 including small ones like D.C. \u2014 gets an equally easy target to tap.</div>' +
        '<div class="state-grid-wrap">' +
        '<div class="state-grid-scroll"><div class="state-grid">' + tiles + '</div></div>' +
        '<div class="state-detail" id="state-detail" aria-live="polite"></div>' +
        '</div>';
      host.setAttribute("data-built", "true");

      var detail = document.getElementById("state-detail");
      var tileEls = host.querySelectorAll(".state-tile[data-state-code]");

      function showState(code) {
        tileEls.forEach(function (t) {
          t.setAttribute("aria-pressed", t.getAttribute("data-state-code") === code ? "true" : "false");
        });
        var list = byState[code] || [];
        if (!list.length) { detail.classList.remove("open"); return; }
        detail.innerHTML =
          '<div class="sd-head">' +
          '<span>' + escapeHtml(STATE_NAMES[code] || code) + ' \u2014 ' + list.length + (list.length === 1 ? ' case' : ' cases') + '</span>' +
          '<button type="button" class="sd-close" aria-label="Close">\u00d7</button>' +
          '</div>' +
          '<div class="related-grid">' + list.map(caseCardHtml).join("") + '</div>';
        // Two-step class toggle (off, then on next frame) so CSS transitions
        // actually animate in, rather than jumping straight to the open state.
        detail.classList.remove("open");
        requestAnimationFrame(function () { detail.classList.add("open"); });
        detail.querySelector(".sd-close").addEventListener("click", function () {
          detail.classList.remove("open");
          tileEls.forEach(function (t) { t.setAttribute("aria-pressed", "false"); });
        });
      }

      tileEls.forEach(function (tile) {
        tile.addEventListener("click", function () {
          var code = tile.getAttribute("data-state-code");
          var alreadyOpen = tile.getAttribute("aria-pressed") === "true";
          if (alreadyOpen) {
            detail.classList.remove("open");
            tileEls.forEach(function (t) { t.setAttribute("aria-pressed", "false"); });
          } else {
            showState(code);
          }
        });
      });
    });
  }

  function caseCardHtml(c) {
    var meta = [c.year, [c.city, c.state].filter(Boolean).join(", ")].filter(Boolean).join(" \u00b7 ");
    return '<a class="related-card" href="' + rootPrefix + 'cases/' + c.id + '.html">' +
      '<span class="rc-name">' + escapeHtml(c.name) + '</span>' +
      '<span class="rc-meta">' + escapeHtml(meta.toUpperCase()) + '</span></a>';
  }

  // ---------------------------------------------------------------------
  document.addEventListener("DOMContentLoaded", function () {
    initBoard();
    initArchiveViews();
  });
})();
