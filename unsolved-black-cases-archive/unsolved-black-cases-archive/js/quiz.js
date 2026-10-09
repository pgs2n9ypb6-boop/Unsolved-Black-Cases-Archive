// Civil Rights Cold Case Quiz — a short, self-scoring quiz about the LEGAL
// SYSTEM around these cases (the Emmett Till Act, statutes of limitations,
// what "closed" actually means) rather than about any individual victim.
// Every answer here is grounded in facts gathered while researching this
// archive's own cases; nothing here is invented for the quiz.
(function () {
  "use strict";

  var QUESTIONS = [
    {
      q: "What does the Emmett Till Unsolved Civil Rights Crime Act (signed 2008) actually do?",
      options: [
        "Makes lynching a standalone federal hate crime",
        "Directs the DOJ and FBI to formally review unsolved, racially motivated killings from before 1980",
        "Provides financial reparations to victims' families",
        "Automatically reopens every closed civil rights case every decade"
      ],
      correct: 1,
      explanation: "The Till Act created a formal review process for pre-1980 civil rights-era cold cases \u2014 it's the reason most of the DOJ case files cited throughout this archive exist at all. (A separate federal anti-lynching law wasn't passed until 2022.)"
    },
    {
      q: "Why can't most 1950s\u201360s civil rights-era killings be federally prosecuted today, even when new evidence surfaces?",
      options: [
        "They were already solved at the time",
        "Federal civil rights statutes of limitations have expired and most identifiable suspects are now deceased",
        "Only state governments were ever allowed to prosecute these cases",
        "No federal law has ever covered racially motivated killings"
      ],
      correct: 1,
      explanation: "This is the single most common reason DOJ closing files (cited throughout this archive) give for ending a review \u2014 not that the case wasn't real, but that legal and practical avenues have run out."
    },
    {
      q: "According to the DOJ's own reporting on Till Act closures, which reason is cited more often for closing a case?",
      options: [
        "Insufficient evidence to prove a violation occurred",
        "All identifiable subjects are deceased",
        "The victim's family asked DOJ to stop",
        "A court ordered the file sealed"
      ],
      correct: 1,
      explanation: "DOJ reporting has found more cases closed specifically because every identifiable subject had died than for lack of evidence \u2014 a reflection of just how much time has passed since most of these killings."
    },
    {
      q: "When the DOJ \u201ccloses\u201d a case under the Till Act, what does that actually mean?",
      options: [
        "The crime has been officially solved",
        "Someone has been convicted",
        "DOJ's review has ended \u2014 usually without prosecution, which is not the same as the case being solved",
        "The case file is permanently destroyed"
      ],
      correct: 2,
      explanation: "This is a distinction this whole archive is built around: every case here is \u201cclosed\u201d only in the sense that formal review ended, not in the sense that anyone was ever held accountable."
    },
    {
      q: "Roughly how many successful prosecutions has the Emmett Till Act itself directly produced since 2008?",
      options: [
        "Zero",
        "Just one",
        "About a dozen",
        "Over fifty"
      ],
      correct: 1,
      explanation: "Reporting on the Till Act's first decade found only one successful prosecution traceable to it \u2014 a stark number given how many hundreds of cases have been reviewed."
    },
    {
      q: "When a jury acquits someone in one of these cases, what does that legally establish?",
      options: [
        "That the person is factually proven innocent",
        "That prosecutors didn't prove guilt beyond a reasonable doubt in that trial \u2014 not the same as innocence",
        "That the case must be automatically retried",
        "That every piece of evidence presented was false"
      ],
      correct: 1,
      explanation: "Several cases in this archive ended in acquittal, sometimes after very short jury deliberation. Acquittal is a legal outcome about the burden of proof at trial, not a factual finding of innocence."
    },
    {
      q: "When did the United States finally pass a federal law making lynching itself a specific hate crime \u2014 something civil rights advocates had tried and failed to pass for over a century?",
      options: [
        "1955, the year Emmett Till was killed",
        "2008, the same year as the Emmett Till Unsolved Civil Rights Crime Act",
        "2022",
        "It still hasn't happened"
      ],
      correct: 2,
      explanation: "The Emmett Till Antilynching Act was signed into law on March 29, 2022 \u2014 the first federal anti-lynching law in American history, after more than 200 earlier attempts in Congress had failed over the preceding century. It's a separate, later law from the 2008 Till Act referenced above, which only created a review process for old cases."
    },
    {
      q: "The federal Civil Rights Cold Case Records Review Board's own released case files are concentrated almost entirely in how many states?",
      options: [
        "All 50 states, roughly evenly",
        "Roughly a dozen states, almost entirely in the Deep South",
        "Only Mississippi",
        "Every state except the Northeast"
      ],
      correct: 1,
      explanation: "This isn't a gap in this archive's research \u2014 it's the government's own registry. Checking its own state filters directly shows its cases cluster in a small handful of Southern states, reflecting where this violence was most concentrated and documented."
    },
    {
      q: "In several cases in this archive where a suspect actually stood trial, all-white juries sometimes returned a not-guilty verdict after deliberating for as little as:",
      options: [
        "A full week",
        "Under two hours",
        "Several months",
        "Juries in these cases always deliberated for days"
      ],
      correct: 1,
      explanation: "Real examples from this archive: a jury acquitted James T. Scott's accused killer after 11 minutes; another acquitted Samuel Younge Jr.'s killer after 71 minutes. Fast acquittals like these are a recurring pattern, not an exception."
    },
    {
      q: "Which best describes the overall pattern across most cases in this archive?",
      options: [
        "The perpetrator's identity was rarely known to anyone",
        "A suspect's identity was often known, sometimes even admitted by the person themselves, but no conviction ever followed",
        "Nearly every case ended in a full criminal trial",
        "Federal prosecution was the most common outcome"
      ],
      correct: 1,
      explanation: "Across this archive, the recurring story isn't mystery \u2014 it's impunity. Grand juries declining to indict, confessions that went nowhere, and acquittals in minutes are far more common than genuine uncertainty about who was responsible."
    }
  ];

  function init() {
    var form = document.getElementById("quiz-form");
    if (!form) return;

    var html = QUESTIONS.map(function (item, qi) {
      var opts = item.options.map(function (opt, oi) {
        return '<label class="quiz-option"><input type="radio" name="q' + qi + '" value="' + oi + '"><span>' + opt + "</span></label>";
      }).join("");
      return (
        '<fieldset class="quiz-question" data-qindex="' + qi + '">' +
        '<legend>' + (qi + 1) + ". " + item.q + "</legend>" +
        '<div class="quiz-options">' + opts + "</div>" +
        '<div class="quiz-explanation" hidden></div>' +
        "</fieldset>"
      );
    }).join("");
    form.innerHTML = html + '<button type="submit" class="quiz-submit">Check My Answers</button>';

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var score = 0;
      var unanswered = 0;
      QUESTIONS.forEach(function (item, qi) {
        var fieldset = form.querySelector('[data-qindex="' + qi + '"]');
        var selected = fieldset.querySelector('input[name="q' + qi + '"]:checked');
        var explanationEl = fieldset.querySelector(".quiz-explanation");
        var optionLabels = fieldset.querySelectorAll(".quiz-option");
        optionLabels.forEach(function (label, oi) {
          label.classList.remove("is-correct", "is-incorrect");
          if (oi === item.correct) label.classList.add("is-correct");
          else if (selected && parseInt(selected.value, 10) === oi) label.classList.add("is-incorrect");
        });
        if (!selected) { unanswered++; }
        else if (parseInt(selected.value, 10) === item.correct) { score++; }
        explanationEl.textContent = item.explanation;
        explanationEl.hidden = false;
      });

      var resultEl = document.getElementById("quiz-result");
      var total = QUESTIONS.length;
      var msg = "You got " + score + " of " + total + " correct.";
      if (unanswered > 0) msg += " (" + unanswered + " left unanswered, counted as incorrect.)";
      resultEl.textContent = msg;
      resultEl.hidden = false;
      resultEl.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
