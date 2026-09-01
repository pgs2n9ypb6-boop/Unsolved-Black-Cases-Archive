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
    if (saved[caseId]) delete saved[caseId];
    else saved[caseId] = true;
    writeJSON(SAVED_KEY, saved);
    return !!saved[caseId];
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
    var btn = document.querySelector("[data-save-case-btn]");
    if (!btn) return;
    var caseId = btn.getAttribute("data-save-case-btn");
    trackRecentlyViewed(caseId); // this element only exists on a real case page, so this is a reliable "case page viewed" signal

    function render() {
      var saved = isSaved(caseId);
      btn.textContent = saved ? "\u2605 Saved to My Cases" : "\u2606 Save This Case";
      btn.classList.toggle("is-saved", saved);
    }
    render();
    btn.addEventListener("click", function () { toggleSaved(caseId); render(); });
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
    renderSavedSources();
    renderTopics();
    renderRecentlyViewed();

    function renderStats() {
      var el;
      el = document.getElementById("stat-saved-cases"); if (el) el.textContent = Object.keys(readJSON(SAVED_KEY)).length;
      el = document.getElementById("stat-notes"); if (el) el.textContent = totalNotesCount();
      el = document.getElementById("stat-sources"); if (el) el.textContent = getSavedSources().length;
      el = document.getElementById("stat-topics"); if (el) el.textContent = getTopics().length;
      el = document.getElementById("stat-recent"); if (el) el.textContent = getRecentlyViewed().length;
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

    function renderSavedCases() {
      var host = document.getElementById("saved-cases-list");
      if (!host) return;
      var savedIds = Object.keys(readJSON(SAVED_KEY));
      var found = savedIds.map(function (id) { return byId[id]; }).filter(Boolean);
      if (found.length === 0) {
        host.innerHTML = '<p class="quiz-result" style="display:block;">You haven\u2019t saved any cases yet. ' +
          'Open any case file and click \u201c\u2606 Save This Case\u201d \u2014 it\u2019ll show up here, in this browser only.</p>';
        return;
      }
      host.innerHTML = found.map(function (c) {
        var notes = getResearchNotes(c.id);
        var noteHtml = notes.length
          ? '<div class="saved-note">' + notes.length + (notes.length === 1 ? " research note" : " research notes") + "</div>"
          : "";
        return caseCardHtml(c, noteHtml, true);
      }).join("");
      host.querySelectorAll("[data-remove-id]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          toggleSaved(btn.getAttribute("data-remove-id"));
          renderSavedCases();
          renderStats();
        });
      });
    }

    function renderSavedSources() {
      var host = document.getElementById("saved-sources-list");
      if (!host) return;
      var list = getSavedSources();
      if (!list.length) {
        host.innerHTML = '<p class="quiz-result" style="display:block;">No saved sources yet. Open any ' +
          'case\u2019s Sources tab and tap \u2606 next to a citation to save it here.</p>';
        return;
      }
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

  function init() { initCaseToggle(); initResearchNotes(); initSourceSaveButtons(); initDashboard(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
