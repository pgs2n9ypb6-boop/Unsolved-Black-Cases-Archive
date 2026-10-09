// Submit a Tip — posts the form to Formspree (a free hosted form backend;
// see https://formspree.io) via fetch, so the visitor gets an inline
// confirmation instead of leaving the site. No custom server required.
//
// SETUP: this only works once you replace YOUR_FORM_ID in the form's
// `action` attribute (in build.py, build_submit()) with your own Formspree
// form ID. Sign up free at formspree.io, create a form, and copy the ID
// from the endpoint it gives you (https://formspree.io/f/xxxxxxxx). Until
// then, submissions will fail with a 404 and the visitor will see the
// error message below.
(function () {
  "use strict";

  function init() {
    var form = document.querySelector("[data-tip-form]");
    if (!form) return;
    var btn = form.querySelector("[data-tip-submit-btn]");
    var status = form.querySelector("[data-tip-form-status]");

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (form.action.indexOf("YOUR_FORM_ID") !== -1) {
        if (status) {
          status.textContent = "This form isn't connected yet \u2014 the site owner needs to add a Formspree form ID.";
          status.classList.add("is-error");
        }
        return;
      }

      btn.disabled = true;
      btn.textContent = "Sending\u2026";
      if (status) { status.textContent = ""; status.classList.remove("is-error"); }

      fetch(form.action, {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" },
      })
        .then(function (res) {
          if (res.ok) {
            form.reset();
            form.hidden = true;
            var confirmation = document.createElement("p");
            confirmation.className = "quiz-result";
            confirmation.setAttribute("role", "status");
            confirmation.textContent = "Thank you \u2014 your submission was received and will be reviewed before anything is published.";
            form.insertAdjacentElement("afterend", confirmation);
          } else {
            throw new Error("Submission failed");
          }
        })
        .catch(function () {
          if (status) {
            status.textContent = "Something went wrong sending this. Please try again, or reach us via the Contact page.";
            status.classList.add("is-error");
          }
          btn.disabled = false;
          btn.textContent = "Submit";
        });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
