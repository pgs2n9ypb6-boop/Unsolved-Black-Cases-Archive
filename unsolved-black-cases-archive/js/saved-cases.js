// Saved Cases & Research Notes — a fully private, no-account feature.
// Everything here lives ONLY in the visitor's own browser via localStorage:
// nothing is sent to a server, nothing is visible to the site owner or
// anyone else, and it disappears if the visitor clears their browser data
// or opens the site on a different device. This is a convenience feature,
// not an account system — the site has no backend to build one on.
(function () {
  "use strict";

  var SAVED_KEY = "ubca_saved_cases";         // { [caseId]: true }
  var LEGACY_NOTES_KEY = "ubca_case_notes";    // { [caseId]: "note text" } — old single-note format
  var RESEARCH_KEY = "ubca_research_notes";    // { [caseId]: [{id, text, createdAt}, ...] }

  function readJSON(key) {
    try {
      var raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }
  function writeJSON(key, obj) {
    try { localStorage.setItem(key, JSON.stringify(obj)); } catch (e) { /* storage unavailable — fail silently */ }
  }

  function isSaved(caseId) { return !!readJSON(SAVED_KEY)[caseId]; }
  function toggleSaved(caseId) {
    var saved = readJSON(SAVED_KEY);
    if (saved[caseId]) delete saved[caseId];
    else saved[caseId] = true;
    writeJSON(SAVED_KEY, saved);
    return !!saved[caseId];
  }

  // ---- Research notes (multiple boxes per case) --------------------------

  function genId() {
    return "n" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

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

  function formatDate(ts) {
    try {
      return new Date(ts).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
    } catch (e) {
      return "";
    }
  }

  function initCaseToggle() {
    var btn = document.querySelector("[data-save-case-btn]");
    if (!btn) return;
    var caseId = btn.getAttribute("data-save-case-btn");

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

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function initSavedList() {
    var host = document.getElementById("saved-cases-list");
    if (!host) return;
    var savedIds = Object.keys(readJSON(SAVED_KEY));
    var allCases = window.__UBCA_CASES__ || [];
    var byId = {};
    allCases.forEach(function (c) { byId[c.id] = c; });

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
      return (
        '<div class="related-card saved-case-card">' +
        '<a href="cases/' + c.id + '.html"><span class="rc-name">' + escapeHtml(c.name) + "</span>" +
        '<span class="rc-meta">' + c.year + " \u00b7 " + escapeHtml(c.city || "") + (c.state ? ", " + c.state : "") + "</span></a>" +
        noteHtml +
        '<button type="button" class="saved-remove" data-remove-id="' + c.id + '">Remove</button>' +
        "</div>"
      );
    }).join("");

    host.querySelectorAll("[data-remove-id]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        toggleSaved(btn.getAttribute("data-remove-id"));
        initSavedList();
      });
    });
  }

  function init() { initCaseToggle(); initResearchNotes(); initSavedList(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
