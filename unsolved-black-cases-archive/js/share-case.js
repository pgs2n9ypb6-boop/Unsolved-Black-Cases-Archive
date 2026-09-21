// Share This Case — one click to the native OS share sheet where it's
// available (every modern mobile browser, and a growing number of desktop
// ones), with a small fallback menu everywhere else. The pre-written text
// is deliberately plain and accurate rather than sensational: it states
// what's actually true of the case (no charges were ever filed, or
// charges were filed but no conviction resulted) using the same
// distinction the rest of the site draws, not a dramatized version of it.
(function () {
  "use strict";

  function escapeHtml(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function pronounSubject(gender) {
    if (gender === "male") return "he";
    if (gender === "female") return "she";
    return "they";
  }
  function pronounPossessive(gender) {
    if (gender === "male") return "his";
    if (gender === "female") return "her";
    return "their";
  }
  function pronounVerb(gender, singularVerb, pluralVerb) {
    return gender === "male" || gender === "female" ? singularVerb : pluralVerb;
  }
  // The gender field alone isn't a reliable signal for "one person or
  // several" — several joint-victim cases have a uniform gender (e.g.
  // three men, two women) set on a case that still represents multiple
  // named people, where a singular "his"/"her" would be wrong regardless
  // of whether the gender itself is accurate. Every such case in this
  // archive is named either as an explicit "&" pairing or as a named
  // collective/event, so checking the name itself is the more reliable
  // signal here.
  function isCollectiveCase(c) {
    return /&/.test(c.name) || /\b(massacre|riot|five|twins|group)\b/i.test(c.name);
  }

  function buildShareText(c) {
    var loc = [c.city, c.state].filter(Boolean).join(", ");
    var who = c.name + (c.age ? ", " + c.age : "") + (c.year ? ", " + c.year : "") + (loc ? " \u2014 " + loc : "");
    var collective = isCollectiveCase(c);
    var poss = collective ? "their" : pronounPossessive(c.gender);

    if (c.caseType === "missing_persons") {
      var verb = collective ? "have" : pronounVerb(c.gender, "has", "have");
      return who + ". " + (collective ? "They have" : c.name.split(" ")[0] + " " + verb) + " never been found.";
    }
    if (c.status === "unresolved") {
      return who + ". Charges were filed, but no one has ever been convicted in " + poss + " death.";
    }
    return who + ". No charges have ever been filed in " + poss + " death.";
  }

  function init() {
    var buttons = document.querySelectorAll("[data-share-btn]");
    if (!buttons.length) return;
    var cases = window.__UBCA_CASES__ || [];
    var byId = {};
    cases.forEach(function (c) { byId[c.id] = c; });
    var menu = document.getElementById("share-fallback-menu");

    function caseUrl(c) {
      return window.location.origin + "/cases/" + c.id + ".html";
    }

    function openFallback(c) {
      if (!menu) return;
      var text = buildShareText(c);
      var url = caseUrl(c);
      var xUrl = "https://twitter.com/intent/tweet?text=" + encodeURIComponent(text) + "&url=" + encodeURIComponent(url);
      var fbUrl = "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(url);
      menu.innerHTML =
        '<a class="stat-popup-row" href="' + xUrl + '" target="_blank" rel="noopener noreferrer">Share on X</a>' +
        '<a class="stat-popup-row" href="' + fbUrl + '" target="_blank" rel="noopener noreferrer">Share on Facebook</a>' +
        '<button type="button" class="stat-popup-row" data-copy-share-link style="width:100%; text-align:left; background:none; border:none; cursor:pointer; font:inherit;">Copy Link</button>';
      menu.hidden = false;
      var copyBtn = menu.querySelector("[data-copy-share-link]");
      if (copyBtn) {
        copyBtn.addEventListener("click", function () {
          var fullText = text + "\n" + url;
          function done() { copyBtn.textContent = "Copied \u2713"; setTimeout(function () { menu.hidden = true; }, 900); }
          try {
            navigator.clipboard.writeText(fullText).then(done, function () {
              var ta = document.createElement("textarea");
              ta.value = fullText; document.body.appendChild(ta); ta.select();
              document.execCommand("copy"); document.body.removeChild(ta); done();
            });
          } catch (e) { done(); }
        });
      }
    }

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var c = byId[btn.getAttribute("data-share-btn")];
        if (!c) return;
        var text = buildShareText(c);
        var url = caseUrl(c);
        if (navigator.share) {
          navigator.share({ title: c.name + " \u2014 Unsolved Black Cases Archive", text: text, url: url }).catch(function () { /* user cancelled — no error needed */ });
        } else {
          openFallback(c);
        }
      });
    });

    document.addEventListener("click", function (e) {
      if (menu && !menu.hidden && !menu.contains(e.target) && !e.target.closest("[data-share-btn]")) {
        menu.hidden = true;
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu && !menu.hidden) menu.hidden = true;
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
