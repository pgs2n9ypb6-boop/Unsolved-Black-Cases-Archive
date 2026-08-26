// Saved Cases — a fully private, no-account "save for later" feature.
// Everything here lives ONLY in the visitor's own browser via localStorage:
// nothing is sent to a server, nothing is visible to the site owner or
// anyone else, and it disappears if the visitor clears their browser data
// or opens the site on a different device. This is a convenience feature,
// not an account system — the site has no backend to build one on.
(function () {
  "use strict";

  var SAVED_KEY = "ubca_saved_cases";     // { [caseId]: true }
  var NOTES_KEY = "ubca_case_notes";      // { [caseId]: "note text" }

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
  function getNote(caseId) { return readJSON(NOTES_KEY)[caseId] || ""; }
  function setNote(caseId, text) {
    var notes = readJSON(NOTES_KEY);
    if (text && text.trim()) notes[caseId] = text;
    else delete notes[caseId];
    writeJSON(NOTES_KEY, notes);
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

    var noteArea = document.querySelector("[data-case-note]");
    if (noteArea) {
      noteArea.value = getNote(caseId);
      var status = document.querySelector("[data-case-note-status]");
      var timer = null;
      noteArea.addEventListener("input", function () {
        if (timer) clearTimeout(timer);
        if (status) status.textContent = "Saving\u2026";
        timer = setTimeout(function () {
          setNote(caseId, noteArea.value);
          if (status) status.textContent = "Saved privately in this browser.";
        }, 500);
      });
    }
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

    var notes = readJSON(NOTES_KEY);
    host.innerHTML = found.map(function (c) {
      var note = notes[c.id];
      var noteHtml = note ? '<div class="saved-note">' + escapeHtml(note) + "</div>" : "";
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

  function init() { initCaseToggle(); initSavedList(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
