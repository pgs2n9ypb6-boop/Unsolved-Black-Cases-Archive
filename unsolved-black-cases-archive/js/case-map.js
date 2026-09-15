// Your Case Map — a private version of the site's own documented Case
// Connections graph, scoped to the cases you've personally saved, where
// YOU draw the connections instead of reading ones the archive already
// verified. This is explicitly framed as personal theory-building, not
// fact: the visual style (dashed, cyan) is deliberately different from
// the site-wide graph's documented connections (solid, crimson/amber),
// and nothing drawn here is ever asserted as verified or shown to anyone
// else — it's stored only in this browser's localStorage.
(function () {
  "use strict";

  var CONN_KEY = "ubca_user_connections"; // [{id, a, b, note, createdAt}, ...]

  function readJSON(key, fallback) {
    try {
      var raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : (fallback !== undefined ? fallback : {});
    } catch (e) { return fallback !== undefined ? fallback : {}; }
  }
  function writeJSON(key, obj) {
    try { localStorage.setItem(key, JSON.stringify(obj)); } catch (e) { /* ignore */ }
  }
  function genId() { return "c" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }
  function escapeHtml(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function getConnections() { return readJSON(CONN_KEY, []); }
  function addConnection(a, b, note) {
    var list = getConnections();
    // Refuse an exact duplicate (either direction) rather than stacking
    // two identical lines on top of each other.
    var exists = list.some(function (c) { return (c.a === a && c.b === b) || (c.a === b && c.b === a); });
    if (exists) return null;
    var entry = { id: genId(), a: a, b: b, note: note || "", createdAt: Date.now() };
    list.push(entry);
    writeJSON(CONN_KEY, list);
    return entry;
  }
  function removeConnection(id) {
    writeJSON(CONN_KEY, getConnections().filter(function (c) { return c.id !== id; }));
  }

  function init() {
    var host = document.getElementById("case-map-widget");
    if (!host) return; // not on the dashboard page

    var allCases = window.__UBCA_CASES__ || [];
    var byId = {};
    allCases.forEach(function (c) { byId[c.id] = c; });

    var connectMode = false;
    var pendingNodeId = null;

    render();

    function savedCaseList() {
      var savedIds = [];
      try { savedIds = Object.keys(JSON.parse(localStorage.getItem("ubca_saved_cases") || "{}")); } catch (e) { /* ignore */ }
      return savedIds.map(function (id) { return byId[id]; }).filter(Boolean);
    }

    function render() {
      var cases = savedCaseList();
      if (cases.length < 2) {
        host.innerHTML = '<p class="quiz-result" style="display:block;">Save at least two cases to start ' +
          'mapping connections between them.</p>';
        return;
      }

      var connections = getConnections().filter(function (c) { return byId[c.a] && byId[c.b] && cases.some(function (x) { return x.id === c.a; }) && cases.some(function (x) { return x.id === c.b; }); });

      var size = 520, cx = size / 2, cy = size / 2, r = size / 2 - 80;
      var nodeIndex = {};
      cases.forEach(function (c, i) {
        var angle = (i / cases.length) * Math.PI * 2 - Math.PI / 2;
        c._x = cx + r * Math.cos(angle);
        c._y = cy + r * Math.sin(angle);
        nodeIndex[c.id] = c;
      });

      function truncate(s, n) { return s && s.length > n ? s.slice(0, n - 1) + "\u2026" : s; }

      var edgeSvg = connections.map(function (conn) {
        var a = nodeIndex[conn.a], b = nodeIndex[conn.b];
        if (!a || !b) return "";
        return '<line class="case-map-edge" x1="' + a._x + '" y1="' + a._y + '" x2="' + b._x + '" y2="' + b._y +
          '" data-conn-id="' + conn.id + '"></line>';
      }).join("");

      var nodeSvg = cases.map(function (c) {
        return '<g class="case-map-node" data-node-id="' + c.id + '">' +
          '<circle cx="' + c._x + '" cy="' + c._y + '" r="7"></circle>' +
          '<text x="' + c._x + '" y="' + (c._y + (c._y > cy ? 18 : -12)) + '" text-anchor="middle">' +
          escapeHtml(truncate(c.name, 16)) + "</text></g>";
      }).join("");

      var connListHtml = connections.length
        ? connections.map(function (conn) {
            var a = nodeIndex[conn.a], b = nodeIndex[conn.b];
            return '<div class="case-map-conn-item">' +
              '<span>' + escapeHtml(a ? a.name : conn.a) + " \u2194 " + escapeHtml(b ? b.name : conn.b) + "</span>" +
              (conn.note ? '<p class="case-map-conn-note">' + escapeHtml(conn.note) + "</p>" : "") +
              '<button type="button" class="saved-remove" data-remove-conn="' + conn.id + '">Remove</button>' +
              "</div>";
          }).join("")
        : '<p class="case-map-empty">No connections drawn yet.</p>';

      host.innerHTML =
        '<button type="button" class="records-btn' + (connectMode ? " primary" : "") + '" data-connect-toggle>' +
        (connectMode ? "\u2713 Connect Mode On \u2014 tap two cases" : "\U0001F517 Connect Two Cases") + "</button>" +
        '<div class="case-map-wrap"><svg class="case-map-svg" viewBox="0 0 ' + size + ' ' + size + '" role="img" ' +
        'aria-label="Your private case connections">' + edgeSvg + nodeSvg + "</svg></div>" +
        '<div class="case-map-conn-list">' + connListHtml + "</div>";

      wire();
    }

    function wire() {
      var toggleBtn = host.querySelector("[data-connect-toggle]");
      if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
          connectMode = !connectMode;
          pendingNodeId = null;
          render();
        });
      }

      host.querySelectorAll(".case-map-node").forEach(function (node) {
        node.addEventListener("click", function () {
          var nodeId = node.getAttribute("data-node-id");
          if (!connectMode) {
            window.location.href = "cases/" + nodeId + ".html";
            return;
          }
          if (!pendingNodeId) {
            pendingNodeId = nodeId;
            render(); // re-render is heavy-handed for a selection highlight, but keeps this simple and correct
            var reselected = host.querySelector('.case-map-node[data-node-id="' + nodeId + '"]');
            if (reselected) reselected.classList.add("case-map-node-selected");
            return;
          }
          if (pendingNodeId === nodeId) {
            pendingNodeId = null; // clicked the same node again — cancel
            return;
          }
          var note = window.prompt("Optional: why do you think these two cases are connected? (Leave blank to skip.)", "");
          if (note !== null) addConnection(pendingNodeId, nodeId, note.trim());
          pendingNodeId = null;
          render();
        });
      });

      host.querySelectorAll("[data-remove-conn]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          removeConnection(btn.getAttribute("data-remove-conn"));
          render();
        });
      });
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
