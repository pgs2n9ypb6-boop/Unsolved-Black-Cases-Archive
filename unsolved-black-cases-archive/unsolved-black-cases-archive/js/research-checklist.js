// Research Checklist — a simple, per-case progress tracker so a visitor
// digging into a specific case has a concrete sense of what they've
// actually done versus what's left. Entirely client-side: check-state is
// stored only in this browser's localStorage, same privacy model as the
// rest of the Researcher's Dashboard. The item list is fixed (not
// user-editable) — a well-designed default is more useful here than
// asking someone to build their own checklist from a blank page.
(function () {
  "use strict";

  var STATE_KEY = "ubca_checklist_state"; // { [caseId]: { [itemId]: true } }

  var BASE_ITEMS = [
    { id: "read-file", label: "Read the full case file (Summary, Known, Unknown, Unanswered Questions)" },
    { id: "reviewed-sources", label: "Reviewed every source cited on this page directly, not just the excerpt here" },
    { id: "local-news-search", label: "Searched for local news coverage beyond what's cited here" },
    { id: "records-request", label: "Sent a public records request for this case" },
    { id: "court-records", label: "Checked court records or case dockets for related civil or criminal proceedings" },
    { id: "unanswered-check", label: "Checked whether any of this case's \u201cUnanswered Questions\u201d have been addressed publicly since this was written" },
    { id: "social-search", label: "Searched social media or local forums for community discussion or leads" },
    { id: "logged-notes", label: "Logged your findings in this case's Research Notes" },
  ];
  var TYPE_ITEMS = {
    homicide: { id: "officer-pattern", label: "Checked whether the officer(s) or agency involved appear in other documented incidents" },
    missing_persons: { id: "namus-check", label: "Checked (or filed) this case's entry in NamUs, the National Missing and Unidentified Persons System" },
  };

  function itemsFor(caseType) {
    var extra = TYPE_ITEMS[caseType];
    return extra ? BASE_ITEMS.concat([extra]) : BASE_ITEMS;
  }

  function readState() {
    try {
      var raw = localStorage.getItem(STATE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) { return {}; }
  }
  function writeState(state) {
    try { localStorage.setItem(STATE_KEY, JSON.stringify(state)); } catch (e) { /* ignore */ }
  }

  // Exposed so other scripts (the Researcher's Dashboard's saved-case
  // cards) can show progress without duplicating this logic.
  function progressFor(caseId, caseType) {
    var items = itemsFor(caseType);
    var checked = readState()[caseId] || {};
    var done = items.filter(function (it) { return checked[it.id]; }).length;
    return { done: done, total: items.length };
  }
  window.UBCA_CHECKLIST_PROGRESS = progressFor;
  // Also expose the item list itself (with human-readable labels) and the
  // raw per-case checked-state, so other tools — specifically the Case
  // Research Packet export — can build a readable checklist without
  // duplicating this item list and risking it drifting out of sync.
  window.UBCA_CHECKLIST_ITEMS_FOR = itemsFor;
  window.UBCA_CHECKLIST_STATE_FOR = function (caseId) { return readState()[caseId] || {}; };

  function initCaseChecklist() {
    var lists = document.querySelectorAll("[data-checklist]");
    if (!lists.length) return;
    lists.forEach(function (list) {
      var caseId = list.getAttribute("data-checklist");
      var caseType = list.getAttribute("data-checklist-type");
      var progressEl = document.querySelector('[data-checklist-progress="' + caseId + '"]');
      var items = itemsFor(caseType);
      var state = readState();
      var checked = state[caseId] || {};

      function renderProgress() {
        var done = items.filter(function (it) { return checked[it.id]; }).length;
        if (progressEl) {
          progressEl.innerHTML =
            '<span class="checklist-progress-text">' + done + " of " + items.length + " complete</span>" +
            '<span class="checklist-progress-bar"><span style="width:' + Math.round((done / items.length) * 100) + '%"></span></span>';
        }
      }

      list.innerHTML = items.map(function (it) {
        return (
          '<li class="checklist-item">' +
          '<label><input type="checkbox" data-checklist-item="' + it.id + '"' + (checked[it.id] ? " checked" : "") + ">" +
          "<span>" + it.label + "</span></label></li>"
        );
      }).join("");

      list.querySelectorAll("[data-checklist-item]").forEach(function (box) {
        box.addEventListener("change", function () {
          var itemId = box.getAttribute("data-checklist-item");
          checked[itemId] = box.checked;
          if (!box.checked) delete checked[itemId];
          state[caseId] = checked;
          writeState(state);
          renderProgress();
        });
      });

      renderProgress();
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initCaseChecklist);
  else initCaseChecklist();
})();
