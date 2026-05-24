/**
 * banner_image_hints.js
 * Updates the image help-text dynamically when the ad_type field changes,
 * and shows a live dimension badge next to each image file input.
 */
(function () {
  "use strict";

  const SPECS = {
    banner:       { desktop: [728,  90],  mobile: [320, 50],  mobileRequired: true  },
    sidebar:      { desktop: [300, 250],  mobile: null,        mobileRequired: false },
    popup:        { desktop: [300, 250],  mobile: null,        mobileRequired: false },
    featured_box: { desktop: [970, 250],  mobile: null,        mobileRequired: false },
  };

  function renderHint(spec) {
    const dw = spec.desktop[0], dh = spec.desktop[1];
    let html = `<strong>📐 صورة الإعلان:</strong> ${dw}×${dh} بكسل`;
    if (spec.mobile) {
      const mw = spec.mobile[0], mh = spec.mobile[1];
      html += ` &nbsp;|&nbsp; <strong>📱 صورة الموبايل:</strong> ${mw}×${mh} بكسل`;
      if (spec.mobileRequired) html += ' <span style="color:red">*إجبارية</span>';
    }
    return html;
  }

  /** Attach a real-time dimension checker to a file input. */
  function attachDimChecker(input, getExpected) {
    const badge = document.createElement("span");
    badge.style.cssText = "margin-right:8px;font-size:12px;";
    input.parentNode.insertBefore(badge, input.nextSibling);

    input.addEventListener("change", function () {
      const file = this.files && this.files[0];
      if (!file || !file.type.startsWith("image/")) { badge.textContent = ""; return; }
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = function () {
        URL.revokeObjectURL(url);
        const [ew, eh] = getExpected();
        if (!ew) { badge.textContent = ""; return; }
        if (img.width === ew && img.height === eh) {
          badge.innerHTML = `<span style="color:green">✅ ${img.width}×${img.height}</span>`;
        } else {
          badge.innerHTML =
            `<span style="color:red">❌ ${img.width}×${img.height} — المطلوب ${ew}×${eh}</span>`;
        }
      };
      img.src = url;
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const adTypeSelect   = document.getElementById("id_ad_type");
    const hintBox        = document.getElementById("banner-dim-hint");
    const imageInput     = document.getElementById("id_image");
    const mobileInput    = document.getElementById("id_mobile_image");
    const mobileRow      = mobileInput && mobileInput.closest(".form-row, .field-mobile_image");

    // Create hint box if not present
    let hint = hintBox;
    if (!hint && adTypeSelect) {
      hint = document.createElement("p");
      hint.id = "banner-dim-hint";
      hint.className = "help";
      hint.style.cssText = "background:#fff3cd;border:1px solid #ffc107;padding:6px 10px;border-radius:4px;margin-top:4px;";
      adTypeSelect.parentNode.appendChild(hint);
    }

    function updateHint() {
      const spec = SPECS[adTypeSelect ? adTypeSelect.value : "banner"];
      if (!spec) return;
      if (hint) hint.innerHTML = renderHint(spec);
      // Show/hide mobile image row
      if (mobileRow) {
        mobileRow.style.display = spec.mobile ? "" : "none";
      }
    }

    if (adTypeSelect) {
      adTypeSelect.addEventListener("change", updateHint);
      updateHint();
    }

    // Real-time dimension checkers
    if (imageInput) {
      attachDimChecker(imageInput, function () {
        const spec = SPECS[adTypeSelect ? adTypeSelect.value : "banner"];
        return spec ? spec.desktop : [null, null];
      });
    }
    if (mobileInput) {
      attachDimChecker(mobileInput, function () {
        const spec = SPECS[adTypeSelect ? adTypeSelect.value : "banner"];
        return spec && spec.mobile ? spec.mobile : [null, null];
      });
    }
  });
})();
