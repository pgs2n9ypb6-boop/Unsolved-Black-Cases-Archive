// Public Records Request Generator — turns "this was never released publicly"
// (a line that recurs across dozens of case files) into an actual letter a
// visitor can send. Runs entirely client-side: the letter is assembled from
// data already in cases-data.js, and the sender's own name/email/address are
// stored only in this browser's localStorage — never transmitted anywhere —
// exactly the same privacy model as Saved Cases and the rest of the
// Researcher's Dashboard.
(function () {
  "use strict";

  var SENDER_KEY = "ubca_records_sender"; // { name, email, address } — remembered across cases/visits

  // Official public records law name per state, used to cite the correct
  // statute in the generated letter. Every state actually used anywhere in
  // the case archive is covered; STATE_LAW_FALLBACK covers anything new
  // added later before this list is updated to match.
  var STATE_LAW = {
    AK: "the Alaska Public Records Act",
    AL: "the Alabama Open Records Act",
    AR: "the Arkansas Freedom of Information Act",
    AZ: "Arizona's Public Records Law",
    CA: "the California Public Records Act",
    CO: "the Colorado Open Records Act",
    CT: "the Connecticut Freedom of Information Act",
    DC: "the District of Columbia Freedom of Information Act",
    DE: "the Delaware Freedom of Information Act",
    FL: "the Florida Public Records Act (Chapter 119, Florida Statutes)",
    GA: "the Georgia Open Records Act",
    IA: "Iowa's public records law (Iowa Code Chapter 22)",
    IL: "the Illinois Freedom of Information Act",
    IN: "the Indiana Access to Public Records Act",
    KS: "the Kansas Open Records Act",
    KY: "the Kentucky Open Records Act",
    LA: "the Louisiana Public Records Act",
    MA: "the Massachusetts Public Records Law",
    MD: "the Maryland Public Information Act",
    MI: "the Michigan Freedom of Information Act",
    MN: "the Minnesota Government Data Practices Act",
    MO: "Missouri's Sunshine Law",
    MS: "the Mississippi Public Records Act",
    NC: "North Carolina's Public Records Law",
    ND: "North Dakota's open records law (N.D. Century Code Chapter 44-04)",
    NE: "Nebraska's public records law",
    NJ: "the New Jersey Open Public Records Act (OPRA)",
    NM: "the New Mexico Inspection of Public Records Act (IPRA)",
    NV: "the Nevada Public Records Act",
    NY: "the New York Freedom of Information Law (FOIL)",
    OH: "the Ohio Public Records Act",
    OK: "the Oklahoma Open Records Act",
    OR: "Oregon's Public Records Law",
    PA: "the Pennsylvania Right-to-Know Law",
    SC: "the South Carolina Freedom of Information Act",
    TN: "the Tennessee Public Records Act",
    TX: "the Texas Public Information Act",
    UT: "the Utah Government Records Access and Management Act (GRAMA)",
    VA: "the Virginia Freedom of Information Act",
    WA: "the Washington Public Records Act",
    WI: "Wisconsin's public records law",
    WV: "the West Virginia Freedom of Information Act",
    WY: "Wyoming's public records law",
  };
  var STATE_LAW_FALLBACK = "your state's public records / open records law";

  function pad(n) { return n < 10 ? "0" + n : "" + n; }
  function todayFormatted() {
    var d = new Date();
    var months = ["January","February","March","April","May","June","July","August","September","October","November","December"];
    return months[d.getMonth()] + " " + d.getDate() + ", " + d.getFullYear();
  }

  // "Who to contact" — deliberately generates search links rather than a
  // static directory of phone numbers or emails. County and city agency
  // contacts change (staff turnover, new phone systems, new portals) far
  // more often than this file would ever get updated, and a stale or wrong
  // number handed to someone trying to do real civic follow-through is
  // worse than no number at all. A search link is never wrong — it just
  // returns whatever is current.
  function buildContactLinks(caseObj) {
    var countyPart = caseObj.county ? caseObj.county + " County, " : "";
    var loc = countyPart + [caseObj.city, caseObj.state].filter(Boolean).join(", ");
    function searchUrl(q) { return "https://www.google.com/search?q=" + encodeURIComponent(q); }
    var links = [
      { label: "District Attorney / prosecutor's office", url: searchUrl(loc + " district attorney public records request") },
      { label: "Sheriff's Office (county-level cases)", url: searchUrl(loc + " sheriff's office public records custodian") },
      { label: "Police Department (city-level cases)", url: searchUrl((caseObj.city || loc) + ", " + caseObj.state + " police department public records officer") },
      { label: "Medical examiner / coroner", url: searchUrl(loc + " medical examiner coroner contact") },
      { label: "Clerk of Court (for case dockets)", url: searchUrl(loc + " clerk of court case records") },
    ];
    if (caseObj.state) {
      links.push({ label: caseObj.state + " Attorney General \u2014 public records office", url: searchUrl(caseObj.state + " attorney general public records open records office") });
    }
    return links;
  }

  function baseRecordsList(caseObj) {
    if (caseObj.caseType === "missing_persons") {
      return [
        "The original missing person report and any supplemental reports filed",
        "Records of tips or leads received and how each was investigated or resolved",
        "Any search, canvass, or search-and-rescue records connected to the case",
        "Any updates or additional records connected to the case's entry in NamUs (the National Missing and Unidentified Persons System), if applicable",
      ];
    }
    return [
      "The incident or offense report and any supplemental reports filed",
      "Body-worn camera and/or dashcam footage from the incident, if any officers were present",
      "911 call recordings and computer-aided dispatch (CAD) logs from the date of the incident",
      "Any internal affairs review, use-of-force review, or administrative investigation connected to the case",
      "The medical examiner's or coroner's report",
      "Any grand jury, inquest, or prosecutorial review summary that is not otherwise sealed by law",
    ];
  }

  function buildLetterText(caseObj, sender) {
    var loc = [caseObj.city, caseObj.state].filter(Boolean).join(", ");
    var lawName = STATE_LAW[caseObj.state] || STATE_LAW_FALLBACK;
    var senderName = sender.name || "[Your Name]";
    var senderEmail = sender.email || "[your email]";
    var senderAddress = sender.address ? sender.address + "\n" : "";
    var records = baseRecordsList(caseObj);
    var unanswered = (caseObj.unanswered || []).slice(0, 3);

    var lines = [];
    lines.push(todayFormatted());
    lines.push("");
    lines.push("Records Custodian");
    lines.push((caseObj.county ? caseObj.county + " County, " : "") + loc);
    lines.push("");
    lines.push("Re: Public Records Request \u2014 " + caseObj.name + (caseObj.year ? " (" + caseObj.year + ")" : ""));
    lines.push("");
    lines.push("To the Records Custodian:");
    lines.push("");
    lines.push("Under " + lawName + ", I am requesting copies of public records related to the " +
      (caseObj.caseType === "missing_persons" ? "disappearance" : "death") + " of " + caseObj.name +
      " in " + loc + (caseObj.year ? " in " + caseObj.year : "") + ".");
    lines.push("");
    lines.push("Specifically, I am requesting:");
    records.forEach(function (r) { lines.push("  \u2022 " + r); });
    if (unanswered.length) {
      lines.push("");
      lines.push("I am also specifically interested in any records that would help clarify:");
      unanswered.forEach(function (q) { lines.push("  \u2022 " + q); });
    }
    lines.push("");
    lines.push("If any portion of this request is denied, please cite the specific statutory exemption relied " +
      "upon for each withheld record, and release all reasonably segregable non-exempt portions. If fees are " +
      "expected to exceed $25, please notify me before proceeding.");
    lines.push("");
    lines.push("Please respond within the timeframe required under " + lawName + ". If it would help process " +
      "this request, I'm glad to be contacted by email.");
    lines.push("");
    lines.push("Thank you for your time and attention to this request.");
    lines.push("");
    lines.push("Sincerely,");
    lines.push(senderName);
    lines.push(senderAddress + senderEmail);
    return lines.join("\n");
  }

  function readSender() {
    try {
      var raw = localStorage.getItem(SENDER_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) { return {}; }
  }
  function writeSender(sender) {
    try { localStorage.setItem(SENDER_KEY, JSON.stringify(sender)); } catch (e) { /* ignore */ }
  }

  function init() {
    var overlay = document.querySelector(".records-overlay");
    if (!overlay) return;
    var caseSelect = document.getElementById("records-case-select");
    var caseField = document.querySelector("[data-records-case-field]");
    var nameInput = document.getElementById("records-your-name");
    var emailInput = document.getElementById("records-your-email");
    var addressInput = document.getElementById("records-your-address");
    var letterBox = document.getElementById("records-letter-text");
    var copiedMsg = document.querySelector("[data-records-copied]");
    var contactList = document.querySelector("[data-records-contact-list]");
    var cases = window.__UBCA_CASES__ || [];
    var byId = {};
    cases.forEach(function (c) { byId[c.id] = c; });

    // Restore remembered sender info.
    var sender = readSender();
    if (sender.name) nameInput.value = sender.name;
    if (sender.email) emailInput.value = sender.email;
    if (sender.address) addressInput.value = sender.address;

    // Populate the case picker once, sorted by name, for standalone-page use.
    // On a case page, the picker is hidden entirely since the case is fixed.
    var sortedCases = cases.slice().sort(function (a, b) { return a.name.localeCompare(b.name); });
    sortedCases.forEach(function (c) {
      var opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = c.name + (c.year ? " (" + c.year + ")" : "");
      caseSelect.appendChild(opt);
    });

    function currentSender() {
      return { name: nameInput.value.trim(), email: emailInput.value.trim(), address: addressInput.value.trim() };
    }

    function regenerate() {
      var caseObj = byId[caseSelect.value];
      if (!caseObj) return;
      letterBox.value = buildLetterText(caseObj, currentSender());
      if (contactList) {
        contactList.innerHTML = buildContactLinks(caseObj).map(function (link) {
          return '<li><a href="' + link.url + '" target="_blank" rel="noopener noreferrer">' + link.label + " \u2192</a></li>";
        }).join("");
      }
    }

    [nameInput, emailInput, addressInput].forEach(function (el) {
      el.addEventListener("input", function () {
        writeSender(currentSender());
        regenerate();
      });
    });
    caseSelect.addEventListener("change", regenerate);
    var releaseRecordsFocusTrap = null;

    function openFor(caseId, lockCase, triggerEl) {
      if (caseId && byId[caseId]) caseSelect.value = caseId;
      caseField.hidden = !!lockCase;
      regenerate();
      overlay.classList.add("open");
      if (!nameInput.value) nameInput.focus();
      if (window.UBCA_TRAP_FOCUS) releaseRecordsFocusTrap = window.UBCA_TRAP_FOCUS(overlay.querySelector(".records-modal") || overlay, triggerEl || document.activeElement);
    }
    function close() {
      overlay.classList.remove("open");
      if (releaseRecordsFocusTrap) { releaseRecordsFocusTrap(); releaseRecordsFocusTrap = null; }
    }

    document.querySelectorAll("[data-records-request-btn]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        openFor(btn.getAttribute("data-records-request-btn"), true, btn);
      });
    });
    document.querySelectorAll("[data-records-open-standalone]").forEach(function (btn) {
      btn.addEventListener("click", function () { openFor(caseSelect.value || (sortedCases[0] && sortedCases[0].id), false, btn); });
    });
    overlay.addEventListener("click", function (e) { if (e.target === overlay) close(); });
    document.querySelectorAll("[data-records-close]").forEach(function (btn) { btn.addEventListener("click", close); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });

    var copyBtn = document.querySelector("[data-records-copy]");
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        letterBox.select();
        try {
          navigator.clipboard.writeText(letterBox.value).then(showCopied, function () {
            document.execCommand("copy");
            showCopied();
          });
        } catch (e) {
          document.execCommand("copy");
          showCopied();
        }
      });
    }
    function showCopied() {
      if (!copiedMsg) return;
      copiedMsg.hidden = false;
      setTimeout(function () { copiedMsg.hidden = true; }, 2000);
    }

    var downloadBtn = document.querySelector("[data-records-download]");
    if (downloadBtn) {
      downloadBtn.addEventListener("click", function () {
        var caseObj = byId[caseSelect.value];
        var filename = "records-request-" + (caseObj ? caseObj.id : "ubca") + ".txt";
        var blob = new Blob([letterBox.value], { type: "text/plain" });
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      });
    }

    // If this page was opened directly on the standalone records-request
    // page (rather than triggered from a case page's button), open the
    // modal immediately with the picker visible.
    if (document.body.hasAttribute("data-records-standalone-page")) {
      openFor(null, false);
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
