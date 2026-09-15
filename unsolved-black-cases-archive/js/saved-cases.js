// Researcher's Dashboard — Saved Cases, Notes, Sources, Research Topics,
// and Recently Viewed — a fully private, no-account feature. Everything
// here lives ONLY in the visitor's own browser via localStorage: nothing
// is sent to a server, nothing is visible to the site owner or anyone
// else, and it disappears if the visitor clears their browser data or
// opens the site on a different device. This is a convenience feature,
// not an account system — the site has no backend to build one on.
(function () {
  "use strict";

  var SAVED_KEY = "ubca_saved_cases";          // { [caseId]: true }
  var STATUS_KEY = "ubca_case_status";          // { [caseId]: "to-review" | "researching" | "reviewed" }
  var STATUS_LABELS = { "to-review": "To Review", "researching": "Actively Researching", "reviewed": "Reviewed" };
  var STATUS_ORDER = ["to-review", "researching", "reviewed"];
  var LEGACY_NOTES_KEY = "ubca_case_notes";     // { [caseId]: "note text" } — old single-note format
  var RESEARCH_KEY = "ubca_research_notes";     // { [caseId]: [{id, text, createdAt}, ...] }
  var BOARD_NOTES_KEY = "ubca_board_user_cards"; // { [caseId]: [{id, text, x, y}, ...] } — set by main.js's board feature
  var SOURCES_KEY = "ubca_saved_sources";       // [{id, caseId, caseName, sourceName, url, savedAt}, ...]
  var TOPICS_KEY = "ubca_research_topics";      // [{id, text, createdAt}, ...]
  var RECENT_KEY = "ubca_recently_viewed";      // [caseId, ...] most-recent-first, capped
  var RECENT_CAP = 20;

  function readJSON(key, fallback) {
    try {
      var raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : (fallback !== undefined ? fallback : {});
    } catch (e) {
      return fallback !== undefined ? fallback : {};
    }
  }
  function writeJSON(key, obj) {
    try { localStorage.setItem(key, JSON.stringify(obj)); } catch (e) { /* storage unavailable — fail silently */ }
  }
  function genId() {
    return "n" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  // ---- Saved cases ---------------------------------------------------

  function isSaved(caseId) { return !!readJSON(SAVED_KEY)[caseId]; }
  function toggleSaved(caseId) {
    var saved = readJSON(SAVED_KEY);
    if (saved[caseId]) {
      delete saved[caseId];
    } else {
      saved[caseId] = Date.now(); // when saved, not just whether — powers "updated since you saved it"
      var statuses = readJSON(STATUS_KEY);
      if (!statuses[caseId]) { statuses[caseId] = "to-review"; writeJSON(STATUS_KEY, statuses); }
    }
    writeJSON(SAVED_KEY, saved);
    return !!saved[caseId];
  }
  function getCaseStatus(caseId) { return readJSON(STATUS_KEY)[caseId] || "to-review"; }
  function setCaseStatus(caseId, status) {
    var statuses = readJSON(STATUS_KEY);
    statuses[caseId] = status;
    writeJSON(STATUS_KEY, statuses);
  }
  // A case saved before this feature existed has a legacy `true` value
  // instead of a timestamp. Treating that as 0 (earliest possible time)
  // means any correction on record will correctly show as "since you
  // saved it" for those cases too, rather than silently missing updates
  // that happened well before this feature could have tracked them.
  function getSavedAt(caseId) {
    var v = readJSON(SAVED_KEY)[caseId];
    return typeof v === "number" ? v : (v ? 0 : null);
  }

  // ---- "Updated since you saved it" ------------------------------------

  function getLatestCorrection(caseId) {
    var corrections = window.__UBCA_CORRECTIONS__ || [];
    var latest = null;
    corrections.forEach(function (c) {
      if (c.caseId === caseId && (!latest || c.date > latest.date)) latest = c;
    });
    return latest; // { date: "YYYY-MM-DD", caseId, text } or null
  }
  function findUpdatedSavedCases() {
    var savedIds = Object.keys(readJSON(SAVED_KEY));
    var updated = [];
    savedIds.forEach(function (id) {
      var savedAt = getSavedAt(id);
      var correction = getLatestCorrection(id);
      if (savedAt == null || !correction) return;
      // savedAt is a millisecond timestamp; correction dates are "YYYY-MM-DD".
      // Comparing a formatted date string against a Date built from savedAt
      // keeps this simple without a date-parsing library.
      var savedDateStr = new Date(savedAt).toISOString().slice(0, 10);
      if (correction.date > savedDateStr) updated.push(correction);
    });
    return updated;
  }

  // ---- Research notes (multiple boxes per case) -----------------------

  function getResearchNotes(caseId) {
    var all = readJSON(RESEARCH_KEY);
    var list = all[caseId];
    if (list) return list;
    // One-time migration: an older visit may have left a single free-text
    // note under the legacy key. Fold it into the new multi-box format so
    // nothing the visitor already wrote gets lost.
    var legacy = readJSON(LEGACY_NOTES_KEY)[caseId];
    if (legacy && legacy.trim()) {
      return [{ id: genId(), text: legacy, createdAt: Date.now() }];
    }
    return [];
  }

  function setResearchNotes(caseId, list) {
    var all = readJSON(RESEARCH_KEY);
    if (list.length) all[caseId] = list;
    else delete all[caseId];
    writeJSON(RESEARCH_KEY, all);
  }

  function addResearchNote(caseId) {
    var list = getResearchNotes(caseId);
    var note = { id: genId(), text: "", createdAt: Date.now() };
    list.push(note);
    setResearchNotes(caseId, list);
    return note.id;
  }

  function updateResearchNote(caseId, noteId, text) {
    var list = getResearchNotes(caseId);
    var note = list.filter(function (n) { return n.id === noteId; })[0];
    if (note) note.text = text;
    setResearchNotes(caseId, list);
  }

  function deleteResearchNote(caseId, noteId) {
    var list = getResearchNotes(caseId).filter(function (n) { return n.id !== noteId; });
    setResearchNotes(caseId, list);
  }

  // Total note count across every case, combining the sidebar research
  // notes with the visual board's "your own note" cards — both are notes
  // from the researcher's point of view, just stored under two different
  // keys because they render in two different places on a case page.
  function totalNotesCount() {
    var all = readJSON(RESEARCH_KEY);
    var boardAll = readJSON(BOARD_NOTES_KEY);
    var total = 0;
    Object.keys(all).forEach(function (id) { total += (all[id] || []).length; });
    Object.keys(boardAll).forEach(function (id) { total += (boardAll[id] || []).length; });
    return total;
  }

  // ---- Saved sources ---------------------------------------------------

  function getSavedSources() { return readJSON(SOURCES_KEY, []); }
  function isSourceSaved(caseId, sourceName) {
    return getSavedSources().some(function (s) { return s.caseId === caseId && s.sourceName === sourceName; });
  }
  function toggleSavedSource(entry) {
    var list = getSavedSources();
    var idx = -1;
    for (var i = 0; i < list.length; i++) {
      if (list[i].caseId === entry.caseId && list[i].sourceName === entry.sourceName) { idx = i; break; }
    }
    if (idx !== -1) {
      list.splice(idx, 1);
      writeJSON(SOURCES_KEY, list);
      return false;
    }
    entry.id = genId();
    entry.savedAt = Date.now();
    list.push(entry);
    writeJSON(SOURCES_KEY, list);
    return true;
  }
  function removeSavedSource(id) {
    writeJSON(SOURCES_KEY, getSavedSources().filter(function (s) { return s.id !== id; }));
  }

  // ---- Research topics (general, not tied to a case) --------------------

  function getTopics() { return readJSON(TOPICS_KEY, []); }
  function addTopic(text) {
    text = (text || "").trim();
    if (!text) return null;
    var list = getTopics();
    var topic = { id: genId(), text: text, createdAt: Date.now() };
    list.unshift(topic);
    writeJSON(TOPICS_KEY, list);
    return topic;
  }
  function removeTopic(id) {
    writeJSON(TOPICS_KEY, getTopics().filter(function (t) { return t.id !== id; }));
  }

  // ---- Recently viewed --------------------------------------------------

  function trackRecentlyViewed(caseId) {
    var list = readJSON(RECENT_KEY, []).filter(function (id) { return id !== caseId; });
    list.unshift(caseId);
    if (list.length > RECENT_CAP) list = list.slice(0, RECENT_CAP);
    writeJSON(RECENT_KEY, list);
  }
  function getRecentlyViewed() { return readJSON(RECENT_KEY, []); }

  function formatDate(ts) {
    try {
      return new Date(ts).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
    } catch (e) {
      return "";
    }
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // ---- Case-page wiring ---------------------------------------------

  function initCaseToggle() {
    var buttons = document.querySelectorAll("[data-save-case-btn]");
    if (!buttons.length) return;
    var caseId = buttons[0].getAttribute("data-save-case-btn");
    trackRecentlyViewed(caseId); // this element only exists on a real case page, so this is a reliable "case page viewed" signal

    function render() {
      var saved = isSaved(caseId);
      buttons.forEach(function (btn) {
        btn.textContent = saved ? "\u2605 Saved to My Cases" : "\u2606 Save This Case";
        btn.classList.toggle("is-saved", saved);
      });
    }
    render();
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () { toggleSaved(caseId); render(); });
    });
  }

  function initResearchNotes() {
    var list = document.querySelector("[data-research-notes-list]");
    var addBtn = document.querySelector("[data-add-research-note]");
    if (!list || !addBtn) return;
    var caseId = list.getAttribute("data-research-notes-list");

    function renderBox(note) {
      var box = document.createElement("div");
      box.className = "research-note-box";
      box.setAttribute("data-note-id", note.id);
      box.innerHTML =
        '<textarea rows="3" placeholder="What did you find\u2026"></textarea>' +
        '<div class="research-note-footer">' +
        '<span class="research-note-date"></span>' +
        '<button type="button" class="research-note-remove">Remove</button>' +
        "</div>";
      var textarea = box.querySelector("textarea");
      var dateEl = box.querySelector(".research-note-date");
      var removeBtn = box.querySelector(".research-note-remove");
      textarea.value = note.text;
      dateEl.textContent = note.text ? "Added " + formatDate(note.createdAt) : "New note";

      var timer = null;
      textarea.addEventListener("input", function () {
        if (timer) clearTimeout(timer);
        dateEl.textContent = "Saving\u2026";
        timer = setTimeout(function () {
          updateResearchNote(caseId, note.id, textarea.value);
          dateEl.textContent = "Saved \u00b7 " + formatDate(note.createdAt);
        }, 500);
      });
      removeBtn.addEventListener("click", function () {
        deleteResearchNote(caseId, note.id);
        box.remove();
      });
      return box;
    }

    function renderAll() {
      list.innerHTML = "";
      getResearchNotes(caseId).forEach(function (note) { list.appendChild(renderBox(note)); });
    }

    renderAll();
    addBtn.addEventListener("click", function () {
      var id = addResearchNote(caseId);
      var note = getResearchNotes(caseId).filter(function (n) { return n.id === id; })[0];
      var box = renderBox(note);
      list.appendChild(box);
      box.querySelector("textarea").focus();
    });
  }

  function initSourceSaveButtons() {
    var buttons = document.querySelectorAll("[data-save-source-btn]");
    if (!buttons.length) return;
    buttons.forEach(function (btn) {
      var entry = {
        caseId: btn.getAttribute("data-case-id"),
        caseName: btn.getAttribute("data-case-name"),
        sourceName: btn.getAttribute("data-source-name"),
        url: btn.getAttribute("data-source-url"),
      };
      function render() {
        var saved = isSourceSaved(entry.caseId, entry.sourceName);
        btn.textContent = saved ? "\u2605" : "\u2606";
        btn.classList.toggle("is-saved", saved);
        btn.setAttribute("aria-pressed", saved ? "true" : "false");
      }
      render();
      btn.addEventListener("click", function () { toggleSavedSource(entry); render(); });
    });
  }

  // ---- Dashboard page (saved.html) -----------------------------------

  function initDashboard() {
    var statsHost = document.getElementById("dashboard-stats");
    if (!statsHost) return; // not on the dashboard page

    var allCases = window.__UBCA_CASES__ || [];
    var byId = {};
    allCases.forEach(function (c) { byId[c.id] = c; });

    renderStats();
    renderSavedCases();
    renderAllNotes();
    renderSavedSources();
    renderTopics();
    renderRecentlyViewed();
    renderUpdatedBanner();
    initCitationExport();
    initStatPopups();

    function flattenAllNotes() {
      var allNotesRaw = readJSON(RESEARCH_KEY); // { [caseId]: [{id, text, createdAt}, ...] }
      var flat = [];
      Object.keys(allNotesRaw).forEach(function (caseId) {
        (allNotesRaw[caseId] || []).forEach(function (n) {
          if (n.text && n.text.trim()) flat.push({ caseId: caseId, text: n.text, createdAt: n.createdAt });
        });
      });
      flat.sort(function (a, b) { return (b.createdAt || 0) - (a.createdAt || 0); });
      return flat;
    }

    function renderAllNotes() {
      var host = document.getElementById("all-notes-list");
      if (!host) return;
      var flat = flattenAllNotes();
      if (!flat.length) {
        host.innerHTML = '<p class="quiz-result" style="display:block;">No notes yet. Open any saved case ' +
          'and click \u201c+ Add a note\u201d \u2014 it\u2019ll show up here too, across every case.</p>';
        return;
      }
      host.innerHTML = flat.map(function (n) {
        var c = byId[n.caseId];
        var caseName = c ? c.name : n.caseId;
        return (
          '<div class="all-notes-item">' +
          '<div class="all-notes-item-head">' +
          '<a href="cases/' + n.caseId + '.html">' + escapeHtml(caseName) + "</a>" +
          '<span class="all-notes-date">' + formatDate(n.createdAt) + "</span>" +
          "</div>" +
          '<p class="all-notes-text">' + escapeHtml(n.text) + "</p>" +
          "</div>"
        );
      }).join("");
    }

    // Clicking a stat opens an immediate inline list right there in the
    // stats row, rather than requiring a scroll to a section further down
    // the page — clicking the same stat again closes it; clicking a
    // different one swaps the content in place.
    function initStatPopups() {
      var popup = document.getElementById("stat-popup");
      if (!popup) return;
      var openKind = null;

      function emptyRow(text) { return '<p class="stat-popup-empty">' + text + "</p>"; }
      function caseLinkRow(c, meta) {
        return '<a class="stat-popup-row" href="cases/' + c.id + '.html"><span>' + escapeHtml(c.name) + "</span>" +
          (meta ? '<span class="stat-popup-meta">' + escapeHtml(meta) + "</span>" : "") + "</a>";
      }

      function buildContent(kind) {
        if (kind === "saved-cases") {
          var savedIds = Object.keys(readJSON(SAVED_KEY));
          var found = savedIds.map(function (id) { return byId[id]; }).filter(Boolean);
          if (!found.length) return emptyRow("No saved cases yet.");
          return found.map(function (c) { return caseLinkRow(c, STATUS_LABELS[getCaseStatus(c.id)]); }).join("");
        }
        if (kind === "notes") {
          var flat = flattenAllNotes();
          if (!flat.length) return emptyRow("No notes yet.");
          return flat.map(function (n) {
            var c = byId[n.caseId];
            var excerpt = n.text.length > 80 ? n.text.slice(0, 77) + "\u2026" : n.text;
            return '<a class="stat-popup-row stat-popup-row-note" href="cases/' + n.caseId + '.html">' +
              '<span class="stat-popup-note-case">' + escapeHtml(c ? c.name : n.caseId) + "</span>" +
              '<span class="stat-popup-note-text">' + escapeHtml(excerpt) + "</span></a>";
          }).join("");
        }
        if (kind === "sources") {
          var sources = getSavedSources();
          if (!sources.length) return emptyRow("No sources saved yet.");
          return sources.map(function (s) {
            return '<a class="stat-popup-row" href="' + s.url + '" target="_blank" rel="noopener noreferrer">' +
              '<span>' + escapeHtml(s.sourceName) + "</span>" +
              '<span class="stat-popup-meta">' + escapeHtml(s.caseName) + "</span></a>";
          }).join("");
        }
        if (kind === "topics") {
          var topics = getTopics();
          if (!topics.length) return emptyRow("No research topics yet.");
          return topics.map(function (t) { return '<div class="stat-popup-row stat-popup-row-static"><span>' + escapeHtml(t.text) + "</span></div>"; }).join("");
        }
        if (kind === "recently-viewed") {
          var recent = getRecentlyViewed().map(function (id) { return byId[id]; }).filter(Boolean);
          if (!recent.length) return emptyRow("No cases viewed yet this browser.");
          return recent.map(function (c) { return caseLinkRow(c, c.year + " \u00b7 " + (c.city || "")); }).join("");
        }
        if (kind === "updated") {
          var updates = findUpdatedSavedCases();
          if (!updates.length) return emptyRow("Nothing updated since you saved it \u2014 yet.");
          return updates.map(function (u) {
            var c = byId[u.caseId];
            if (!c) return "";
            return '<a class="stat-popup-row stat-popup-row-note" href="cases/' + c.id + '.html">' +
              '<span class="stat-popup-note-case">' + escapeHtml(c.name) + "</span>" +
              '<span class="stat-popup-note-text">' + escapeHtml(u.text) + "</span></a>";
          }).join("");
        }
        return emptyRow("Nothing here yet.");
      }

      document.querySelectorAll(".dash-stat-link").forEach(function (link) {
        link.addEventListener("click", function (e) {
          e.preventDefault();
          var kind = link.getAttribute("data-stat-kind");
          document.querySelectorAll(".dash-stat-link").forEach(function (l) { l.classList.remove("dash-stat-open"); });
          if (openKind === kind) {
            // same stat clicked again — close it
            popup.hidden = true;
            popup.innerHTML = "";
            openKind = null;
            return;
          }
          openKind = kind;
          link.classList.add("dash-stat-open");
          popup.innerHTML = buildContent(kind);
          popup.hidden = false;
        });
      });
    }

    function renderStats() {
      var el;
      el = document.getElementById("stat-saved-cases"); if (el) el.textContent = Object.keys(readJSON(SAVED_KEY)).length;
      el = document.getElementById("stat-notes"); if (el) el.textContent = totalNotesCount();
      el = document.getElementById("stat-sources"); if (el) el.textContent = getSavedSources().length;
      el = document.getElementById("stat-topics"); if (el) el.textContent = getTopics().length;
      el = document.getElementById("stat-recent"); if (el) el.textContent = getRecentlyViewed().length;
      el = document.getElementById("stat-updated"); if (el) el.textContent = findUpdatedSavedCases().length;
    }

    function renderUpdatedBanner() {
      var host = document.getElementById("updated-cases-banner");
      if (!host) return;
      var updates = findUpdatedSavedCases();
      if (!updates.length) { host.hidden = true; host.innerHTML = ""; return; }
      host.hidden = false;
      var heading = updates.length === 1
        ? "1 saved case has been updated since you saved it"
        : updates.length + " saved cases have been updated since you saved them";
      host.innerHTML =
        '<div class="updated-cases-head">' + heading + "</div>" +
        updates.map(function (u) {
          var c = byId[u.caseId];
          if (!c) return "";
          return (
            '<div class="updated-case-item">' +
            '<a href="cases/' + c.id + '.html">' + escapeHtml(c.name) + "</a>" +
            '<span class="updated-case-date">' + formatDate(new Date(u.date).getTime()) + "</span>" +
            '<p class="updated-case-text">' + escapeHtml(u.text) + "</p>" +
            "</div>"
          );
        }).join("");
    }

    function caseCardHtml(c, extraHtml, removeAttr) {
      return (
        '<div class="related-card saved-case-card">' +
        '<a href="cases/' + c.id + '.html"><span class="rc-name">' + escapeHtml(c.name) + "</span>" +
        '<span class="rc-meta">' + (c.year || "") + " \u00b7 " + escapeHtml(c.city || "") + (c.state ? ", " + c.state : "") + "</span></a>" +
        (extraHtml || "") +
        (removeAttr ? '<button type="button" class="saved-remove" data-remove-id="' + c.id + '">Remove</button>' : "") +
        "</div>"
      );
    }

    var savedFilter = "all"; // ephemeral — resets on reload, which is fine for a filter control
    var savedSearchQuery = "";

    function renderSavedCases() {
      var host = document.getElementById("saved-cases-list");
      var filterHost = document.getElementById("saved-cases-filter");
      var searchInput = document.getElementById("saved-cases-search");
      if (!host) return;
      var savedIds = Object.keys(readJSON(SAVED_KEY));
      var found = savedIds.map(function (id) { return byId[id]; }).filter(Boolean);

      if (searchInput && !searchInput.dataset.wired) {
        searchInput.dataset.wired = "true";
        searchInput.hidden = found.length === 0;
        searchInput.addEventListener("input", function () {
          savedSearchQuery = searchInput.value;
          renderSavedCases();
        });
      } else if (searchInput) {
        searchInput.hidden = found.length === 0;
      }

      if (filterHost) {
        if (!found.length) {
          filterHost.hidden = true;
        } else {
          filterHost.hidden = false;
          var counts = { all: found.length };
          STATUS_ORDER.forEach(function (s) { counts[s] = 0; });
          found.forEach(function (c) { var s = getCaseStatus(c.id); counts[s] = (counts[s] || 0) + 1; });
          var chipDefs = [["all", "All"]].concat(STATUS_ORDER.map(function (s) { return [s, STATUS_LABELS[s]]; }));
          filterHost.innerHTML = chipDefs.map(function (pair) {
            var key = pair[0], label = pair[1];
            return '<button type="button" class="status-filter-chip" data-status-filter="' + key + '" ' +
              'aria-pressed="' + (savedFilter === key ? "true" : "false") + '">' + label + " (" + (counts[key] || 0) + ")</button>";
          }).join("");
          filterHost.querySelectorAll("[data-status-filter]").forEach(function (chip) {
            chip.addEventListener("click", function () {
              savedFilter = chip.getAttribute("data-status-filter");
              renderSavedCases();
            });
          });
        }
      }

      var visible = savedFilter === "all" ? found : found.filter(function (c) { return getCaseStatus(c.id) === savedFilter; });
      var trimmedQuery = savedSearchQuery.trim();
      if (trimmedQuery) {
        var normalizedQuery = typeof window.UBCA_NORMALIZE === "function" ? window.UBCA_NORMALIZE(trimmedQuery) : trimmedQuery.toLowerCase();
        visible = visible.filter(function (c) {
          var text = typeof window.UBCA_CASE_FULL_TEXT === "function" ? window.UBCA_CASE_FULL_TEXT(c) : (c.name || "").toLowerCase();
          return text.indexOf(normalizedQuery) !== -1;
        });
      }

      if (found.length === 0) {
        host.innerHTML = '<p class="quiz-result" style="display:block;">You haven\u2019t saved any cases yet. ' +
          'Open any case file and click \u201c\u2606 Save This Case\u201d \u2014 it\u2019ll show up here, in this browser only.</p>';
        return;
      }
      if (visible.length === 0) {
        host.innerHTML = '<p class="quiz-result" style="display:block;">No saved cases match ' +
          (trimmedQuery ? "\u201c" + escapeHtml(trimmedQuery) + "\u201d" : "that status") + " yet.</p>";
        return;
      }
      host.innerHTML = visible.map(function (c) {
        var notes = getResearchNotes(c.id);
        var noteHtml = notes.length
          ? '<div class="saved-note">' + notes.length + (notes.length === 1 ? " research note" : " research notes") + "</div>"
          : "";
        var progressHtml = "";
        if (typeof window.UBCA_CHECKLIST_PROGRESS === "function") {
          var p = window.UBCA_CHECKLIST_PROGRESS(c.id, c.caseType);
          if (p && p.total) {
            progressHtml = '<div class="saved-note saved-checklist-note">Checklist: ' + p.done + "/" + p.total + " complete</div>";
          }
        }
        var currentStatus = getCaseStatus(c.id);
        var statusHtml = '<select class="status-select status-select-' + currentStatus + '" data-status-select="' + c.id + '">' +
          STATUS_ORDER.map(function (s) {
            return '<option value="' + s + '"' + (s === currentStatus ? " selected" : "") + ">" + STATUS_LABELS[s] + "</option>";
          }).join("") + "</select>";
        return caseCardHtml(c, statusHtml + noteHtml + progressHtml, true);
      }).join("");
      host.querySelectorAll("[data-status-select]").forEach(function (select) {
        select.addEventListener("change", function () {
          setCaseStatus(select.getAttribute("data-status-select"), select.value);
          select.className = "status-select status-select-" + select.value;
          renderSavedCases(); // re-render so the filter counts and current filter view stay accurate
        });
      });
      host.querySelectorAll("[data-remove-id]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          toggleSaved(btn.getAttribute("data-remove-id"));
          renderSavedCases();
          renderStats();
          renderUpdatedBanner();
        });
      });
    }

    function renderSavedSources() {
      var host = document.getElementById("saved-sources-list");
      var exportRow = document.getElementById("sources-export-row");
      if (!host) return;
      var list = getSavedSources();
      if (!list.length) {
        host.innerHTML = '<p class="quiz-result" style="display:block;">No saved sources yet. Open any ' +
          'case\u2019s Sources tab and tap \u2606 next to a citation to save it here.</p>';
        if (exportRow) exportRow.hidden = true;
        return;
      }
      if (exportRow) exportRow.hidden = false;
      list.sort(function (a, b) { return b.savedAt - a.savedAt; });
      host.innerHTML = list.map(function (s) {
        return (
          '<div class="saved-source-item">' +
          '<div class="ssi-main">' +
          '<a href="' + s.url + '" target="_blank" rel="noopener noreferrer">' + escapeHtml(s.sourceName) + "</a>" +
          '<span class="ssi-case">from <a href="cases/' + s.caseId + '.html">' + escapeHtml(s.caseName) + "</a></span>" +
          "</div>" +
          '<button type="button" class="saved-remove" data-remove-source-id="' + s.id + '">Remove</button>' +
          "</div>"
        );
      }).join("");
      host.querySelectorAll("[data-remove-source-id]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          removeSavedSource(btn.getAttribute("data-remove-source-id"));
          renderSavedSources();
          renderStats();
        });
      });
    }

    // Citation export — groups saved sources by the case they came from,
    // since that's the structure the data actually has (no author or
    // publish-date fields are captured per source, so this is a clean
    // reference list rather than a formal academic citation style that
    // would need data we don't collect).
    function buildCitationText() {
      var list = getSavedSources();
      var byCaseId = {};
      var order = [];
      list.forEach(function (s) {
        if (!byCaseId[s.caseId]) { byCaseId[s.caseId] = { name: s.caseName, sources: [] }; order.push(s.caseId); }
        byCaseId[s.caseId].sources.push(s);
      });
      var lines = ["Unsolved Black Cases Archive \u2014 Saved Sources", "Exported " + formatDate(Date.now()), ""];
      order.forEach(function (caseId) {
        var group = byCaseId[caseId];
        lines.push(group.name);
        group.sources.forEach(function (s) {
          lines.push("  " + s.sourceName);
          lines.push("  " + s.url);
        });
        lines.push("");
      });
      return lines.join("\n");
    }

    function initCitationExport() {
      var copyBtn = document.querySelector("[data-export-citations-copy]");
      var downloadBtn = document.querySelector("[data-export-citations-download]");
      var copiedMsg = document.querySelector("[data-export-copied]");
      if (copyBtn) {
        copyBtn.addEventListener("click", function () {
          var text = buildCitationText();
          function done() {
            if (copiedMsg) { copiedMsg.hidden = false; setTimeout(function () { copiedMsg.hidden = true; }, 2000); }
          }
          try {
            navigator.clipboard.writeText(text).then(done, function () {
              var ta = document.createElement("textarea");
              ta.value = text; document.body.appendChild(ta); ta.select();
              document.execCommand("copy"); document.body.removeChild(ta); done();
            });
          } catch (e) { done(); }
        });
      }
      if (downloadBtn) {
        downloadBtn.addEventListener("click", function () {
          var blob = new Blob([buildCitationText()], { type: "text/plain" });
          var url = URL.createObjectURL(blob);
          var a = document.createElement("a");
          a.href = url; a.download = "ubca-saved-sources.txt";
          document.body.appendChild(a); a.click(); document.body.removeChild(a);
          URL.revokeObjectURL(url);
        });
      }
    }

    function renderTopics() {
      var host = document.getElementById("research-topics-list");
      var input = document.getElementById("topic-input");
      var addBtn = document.getElementById("topic-add-btn");
      if (!host) return;
      var list = getTopics();
      host.innerHTML = list.length
        ? list.map(function (t) {
            return (
              '<li class="topic-item"><span>' + escapeHtml(t.text) + "</span>" +
              '<button type="button" class="saved-remove" data-remove-topic-id="' + t.id + '">Remove</button></li>'
            );
          }).join("")
        : '<li class="quiz-result" style="display:block;">No research topics yet \u2014 add a lead or pattern you want to come back to.</li>';
      host.querySelectorAll("[data-remove-topic-id]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          removeTopic(btn.getAttribute("data-remove-topic-id"));
          renderTopics();
          renderStats();
        });
      });
      if (addBtn && input && !addBtn.dataset.wired) {
        addBtn.dataset.wired = "true";
        function submit() {
          if (addTopic(input.value)) { input.value = ""; renderTopics(); renderStats(); }
        }
        addBtn.addEventListener("click", submit);
        input.addEventListener("keydown", function (e) { if (e.key === "Enter") submit(); });
      }
    }

    function renderRecentlyViewed() {
      var host = document.getElementById("recently-viewed-list");
      if (!host) return;
      var found = getRecentlyViewed().map(function (id) { return byId[id]; }).filter(Boolean);
      if (!found.length) {
        host.innerHTML = '<p class="quiz-result" style="display:block;">No cases viewed yet this browser \u2014 ' +
          'open any case file and it\u2019ll show up here next time you visit.</p>';
        return;
      }
      host.innerHTML = found.map(function (c) { return caseCardHtml(c, "", false); }).join("");
    }
  }

  // ---- Homepage "Your Research" widget --------------------------------

  function initHomepageWidget() {
    var host = document.getElementById("homepage-research-widget");
    if (!host) return;
    var allCases = window.__UBCA_CASES__ || [];
    var byId = {};
    allCases.forEach(function (c) { byId[c.id] = c; });

    var savedIds = Object.keys(readJSON(SAVED_KEY));
    var found = savedIds.map(function (id) { return byId[id]; }).filter(Boolean);

    if (!found.length) {
      host.innerHTML =
        '<p class="homepage-research-empty">Save cases, take notes, request public records, and track your ' +
        'own progress \u2014 everything stays private to this browser, nothing is sent anywhere. Open any case ' +
        'file and click \u201c\u2606 Save This Case\u201d to get started.</p>' +
        '<a class="homepage-research-cta" href="saved.html">Open Your Researcher\u2019s Dashboard \u2192</a>';
      return;
    }

    var noteCount = totalNotesCount();
    var researchingCount = found.filter(function (c) { return getCaseStatus(c.id) === "researching"; }).length;
    var recent = found.slice().sort(function (a, b) {
      return getSavedAt(b.id) - getSavedAt(a.id);
    }).slice(0, 5);

    host.innerHTML =
      '<div class="homepage-research-stats">' +
      '<span><strong>' + found.length + '</strong> saved</span>' +
      '<span><strong>' + noteCount + '</strong> notes</span>' +
      '<span><strong>' + researchingCount + '</strong> actively researching</span>' +
      '</div>' +
      '<ul class="homepage-research-list">' +
      recent.map(function (c) {
        return '<li><a href="cases/' + c.id + '.html">' + escapeHtml(c.name) + '</a>' +
          '<span class="homepage-research-status">' + escapeHtml(STATUS_LABELS[getCaseStatus(c.id)]) + '</span></li>';
      }).join("") +
      '</ul>' +
      '<a class="homepage-research-cta" href="saved.html">View Full Dashboard \u2192</a>';
  }

  function init() { initCaseToggle(); initResearchNotes(); initSourceSaveButtons(); initDashboard(); initHomepageWidget(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
