// Compare Cases — up to four cases side by side, so the patterns that
// repeat across the archive (the same kind of grand jury language, the
// same gap between a coroner's finding and a prosecutor's conclusion) are
// something a visitor can actually see laid out, not just sense while
// clicking between pages one at a time. The list of which cases are being
// compared lives only in this browser's localStorage (same privacy model
// as the rest of the dashboard) and is also mirrored into the compare
// page's own URL, so a specific comparison can be bookmarked or shared.
(function () {
  "use strict";

  var LIST_KEY = "ubca_compare_list"; // array of case ids, most-recently-added last
  var MAX_COMPARE = 4;

  function readList() {
    try {
      var raw = localStorage.getItem(LIST_KEY);
      var list = raw ? JSON.parse(raw) : [];
      return Array.isArray(list) ? list : [];
    } catch (e) { return []; }
  }
  function writeList(list) {
    try { localStorage.setItem(LIST_KEY, JSON.stringify(list)); } catch (e) { /* ignore */ }
  }
  function escapeHtml(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // ---- Case-page "+ Add to Compare" button -----------------------------

  function initCompareButtons() {
    var buttons = document.querySelectorAll("[data-compare-btn]");
    if (!buttons.length) return;
    buttons.forEach(function (btn) {
      var caseId = btn.getAttribute("data-compare-btn");
      function render() {
        var list = readList();
        var inList = list.indexOf(caseId) !== -1;
        btn.classList.toggle("in-compare", inList);
        btn.textContent = inList
          ? "\u2696 In Compare (" + list.length + "/" + MAX_COMPARE + ") \u2014 Remove"
          : "\u2696 Add to Compare";
      }
      render();
      btn.addEventListener("click", function () {
        var list = readList();
        var idx = list.indexOf(caseId);
        if (idx !== -1) {
          list.splice(idx, 1);
        } else {
          if (list.length >= MAX_COMPARE) {
            var original = btn.textContent;
            btn.textContent = "Compare list full (" + MAX_COMPARE + " max) \u2014 remove one first";
            setTimeout(function () { btn.textContent = original; }, 2200);
            return;
          }
          list.push(caseId);
        }
        writeList(list);
        render();
      });
    });
  }

  // ---- Standalone compare page ------------------------------------------

  function initComparePage() {
    var grid = document.getElementById("compare-grid");
    if (!grid) return;
    var addSelect = document.getElementById("compare-add-select");
    var cases = window.__UBCA_CASES__ || [];
    var byId = {};
    cases.forEach(function (c) { byId[c.id] = c; });

    // A URL like compare.html?ids=a,b,c takes priority on first load (so a
    // shared/bookmarked link reproduces the same comparison), and from then
    // on the URL is kept in sync with whatever's actually being compared.
    function idsFromUrl() {
      var params = new URLSearchParams(window.location.search);
      var raw = params.get("ids");
      if (!raw) return null;
      return raw.split(",").map(function (s) { return s.trim(); }).filter(function (id) { return byId[id]; });
    }
    var fromUrl = idsFromUrl();
    if (fromUrl && fromUrl.length) writeList(fromUrl.slice(0, MAX_COMPARE));

    function syncUrl(list) {
      var url = new URL(window.location.href);
      if (list.length) url.searchParams.set("ids", list.join(","));
      else url.searchParams.delete("ids");
      window.history.replaceState({}, "", url);
    }

    var sortedCases = cases.slice().sort(function (a, b) { return a.name.localeCompare(b.name); });
    sortedCases.forEach(function (c) {
      var opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = c.name + (c.year ? " (" + c.year + ")" : "");
      addSelect.appendChild(opt);
    });

    function locYear(c) {
      var loc = [c.city, c.state].filter(Boolean).join(", ");
      return [loc, c.year].filter(Boolean).join(" \u2014 ");
    }
    function bulletList(items) {
      if (!items || !items.length) return '<p class="compare-empty">Nothing recorded.</p>';
      return "<ul>" + items.map(function (i) { return "<li>" + escapeHtml(i) + "</li>"; }).join("") + "</ul>";
    }

    function render() {
      var list = readList();
      syncUrl(list);
      addSelect.value = "";
      var found = list.map(function (id) { return byId[id]; }).filter(Boolean);
      if (!found.length) {
        grid.innerHTML = '<p class="compare-empty-state">No cases selected yet. Add up to four above, or use ' +
          '\u201c\u2696 Add to Compare\u201d on any case page.</p>';
        return;
      }
      grid.innerHTML = found.map(function (c) {
        return (
          '<div class="compare-col">' +
          '<div class="compare-col-head">' +
          '<a href="cases/' + c.id + '.html"><h3>' + escapeHtml(c.name) + "</h3></a>" +
          '<span class="compare-meta">' + escapeHtml(locYear(c)) + "</span>" +
          (c.age ? '<span class="compare-meta">Age ' + c.age + "</span>" : "") +
          '<button type="button" class="saved-remove" data-compare-remove="' + c.id + '">Remove</button>' +
          "</div>" +
          '<div class="compare-section"><h4>Summary</h4><p>' + escapeHtml(c.summary || "") + "</p></div>" +
          '<div class="compare-section"><h4>Known</h4>' + bulletList(c.known) + "</div>" +
          '<div class="compare-section"><h4>Unknown</h4>' + bulletList(c.unknown) + "</div>" +
          '<div class="compare-section"><h4>Unanswered Questions</h4>' + bulletList(c.unanswered) + "</div>" +
          "</div>"
        );
      }).join("");
      grid.querySelectorAll("[data-compare-remove]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var id = btn.getAttribute("data-compare-remove");
          writeList(readList().filter(function (existing) { return existing !== id; }));
          render();
        });
      });
    }

    addSelect.addEventListener("change", function () {
      var id = addSelect.value;
      if (!id) return;
      var list = readList();
      if (list.indexOf(id) === -1) {
        if (list.length >= MAX_COMPARE) list.shift(); // make room, oldest first
        list.push(id);
        writeList(list);
      }
      render();
    });

    render();
  }

  function init() { initCompareButtons(); initComparePage(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
