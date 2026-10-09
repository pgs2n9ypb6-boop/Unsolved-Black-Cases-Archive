// Case Research Packet — bundles everything about one case, official and
// personal, into a single downloadable document: the case file itself,
// your saved sources for that case, your research notes, and your
// checklist progress. This is the natural next step past the plain
// citation export — something you could actually hand to someone else or
// paste into a document you're writing. Reads the same localStorage keys
// saved-cases.js and research-checklist.js already use (documented below)
// rather than duplicating their write logic — this module only reads.
(function () {
  "use strict";

  var NOTES_KEY = "ubca_research_notes";   // { [caseId]: [{id, text, createdAt}, ...] } — see saved-cases.js
  var SOURCES_KEY = "ubca_saved_sources";  // [{id, caseId, caseName, sourceName, url, savedAt}, ...] — see saved-cases.js

  function readJSON(key, fallback) {
    try {
      var raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : (fallback !== undefined ? fallback : {});
    } catch (e) { return fallback !== undefined ? fallback : {}; }
  }

  function notesFor(caseId) { return readJSON(NOTES_KEY)[caseId] || []; }
  function sourcesFor(caseId) {
    return readJSON(SOURCES_KEY, []).filter(function (s) { return s.caseId === caseId; });
  }
  function formatDate(ts) {
    try { return new Date(ts).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }); }
    catch (e) { return ""; }
  }
  function rule() { return "\u2500".repeat(60); }
  function bulleted(items) {
    if (!items || !items.length) return "  (none recorded)";
    return items.map(function (i) { return "  \u2022 " + i; }).join("\n");
  }

  function buildPacketText(c) {
    var loc = [c.city, c.state].filter(Boolean).join(", ");
    var lines = [];

    lines.push("UNSOLVED BLACK CASES ARCHIVE");
    lines.push("Research Packet \u2014 " + c.name);
    lines.push("Exported " + formatDate(Date.now()));
    lines.push("");
    lines.push(rule());
    lines.push("CASE FILE");
    lines.push(rule());
    lines.push("Case #" + (c.caseNumber || "\u2014") + " \u00b7 " + (c.status || "unsolved").toUpperCase() +
      " \u00b7 " + (c.year || "year unknown") + (loc ? " \u00b7 " + loc : ""));
    lines.push("");
    lines.push("SUMMARY");
    lines.push(c.summary || "(none recorded)");
    lines.push("");
    lines.push("KNOWN");
    lines.push(bulleted(c.known));
    lines.push("");
    lines.push("UNKNOWN");
    lines.push(bulleted(c.unknown));
    lines.push("");
    lines.push("UNANSWERED QUESTIONS");
    lines.push(bulleted(c.unanswered));
    lines.push("");

    lines.push(rule());
    lines.push("OFFICIAL SOURCES CITED ON THIS CASE PAGE");
    lines.push(rule());
    if (c.sources && c.sources.length) {
      c.sources.forEach(function (s) {
        lines.push("  " + s.name);
        if (s.url) lines.push("  " + s.url);
      });
    } else {
      lines.push("  (none recorded)");
    }
    lines.push("");

    lines.push(rule());
    lines.push("YOUR RESEARCH NOTES");
    lines.push(rule());
    var notes = notesFor(c.id);
    if (notes.length) {
      notes.forEach(function (n, i) {
        if (i > 0) lines.push("");
        lines.push("  [" + formatDate(n.createdAt) + "]");
        lines.push("  " + (n.text || "(empty note)"));
      });
    } else {
      lines.push("  (no notes saved for this case yet)");
    }
    lines.push("");

    lines.push(rule());
    lines.push("YOUR SAVED SOURCES FOR THIS CASE");
    lines.push(rule());
    var sources = sourcesFor(c.id);
    if (sources.length) {
      sources.forEach(function (s) {
        lines.push("  " + s.sourceName);
        lines.push("  " + s.url);
      });
    } else {
      lines.push("  (no sources individually saved for this case yet)");
    }
    lines.push("");

    lines.push(rule());
    lines.push("YOUR RESEARCH CHECKLIST");
    lines.push(rule());
    if (typeof window.UBCA_CHECKLIST_ITEMS_FOR === "function") {
      var items = window.UBCA_CHECKLIST_ITEMS_FOR(c.caseType);
      var state = window.UBCA_CHECKLIST_STATE_FOR(c.id);
      var done = 0;
      items.forEach(function (it) {
        var checked = !!state[it.id];
        if (checked) done++;
        lines.push("  [" + (checked ? "x" : " ") + "] " + it.label);
      });
      lines.push("");
      lines.push("  " + done + " of " + items.length + " complete");
    } else {
      lines.push("  (checklist data unavailable)");
    }
    lines.push("");

    lines.push(rule());
    lines.push("Full case file: " + window.location.origin + "/cases/" + c.id + ".html");
    lines.push("Exported from the Unsolved Black Cases Archive Researcher's Dashboard.");
    lines.push("Nothing in this export was sent anywhere \u2014 it was generated entirely in your own browser.");

    return lines.join("\n");
  }

  function slugForFile(c) { return "ubca-research-packet-" + c.id + ".txt"; }

  function init() {
    var buttons = document.querySelectorAll("[data-packet-export-btn]");
    if (!buttons.length) return;
    var cases = window.__UBCA_CASES__ || [];
    var byId = {};
    cases.forEach(function (c) { byId[c.id] = c; });

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var c = byId[btn.getAttribute("data-packet-export-btn")];
        if (!c) return;
        var text = buildPacketText(c);
        var blob = new Blob([text], { type: "text/plain" });
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = slugForFile(c);
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
