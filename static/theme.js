(function () {
    var PRIORITY_MATRIX = {
        "High|High": { label: "Critical", cls: "badge-critical" },
        "High|Medium": { label: "High", cls: "badge-high" },
        "High|Low": { label: "Medium", cls: "badge-medium" },
        "Medium|High": { label: "High", cls: "badge-high" },
        "Medium|Medium": { label: "Medium", cls: "badge-medium" },
        "Medium|Low": { label: "Low", cls: "badge-low" },
        "Low|High": { label: "Medium", cls: "badge-medium" },
        "Low|Medium": { label: "Low", cls: "badge-low" },
        "Low|Low": { label: "Low", cls: "badge-low" }
    };

    function syncThemeButton(theme) {
        var btn = document.getElementById("themeBtn");
        if (!btn) return;
        var isDark = theme === "dark";
        btn.setAttribute("aria-pressed", isDark ? "true" : "false");
        btn.setAttribute(
            "aria-label",
            isDark ? "Switch to light mode" : "Switch to dark mode"
        );
        btn.setAttribute(
            "title",
            isDark ? "Light mode" : "Dark mode"
        );
    }

    function applyTheme(theme) {
        var normalized = theme === "dark" ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", normalized);
        localStorage.setItem("theme", normalized);
        syncThemeButton(normalized);
    }

    function initPriorityPreview() {
        var urgencyEl = document.querySelector('select[name="urgency"]');
        var impactEl = document.querySelector('select[name="impact"]');
        var previewEl = document.getElementById("priorityPreview");
        if (!urgencyEl || !impactEl || !previewEl) return;

        function update() {
            var u = urgencyEl.value;
            var imp = impactEl.value;
            var match = PRIORITY_MATRIX[u + "|" + imp];
            if (!match) {
                previewEl.className = "matrix-preview-badge matrix-idle";
                previewEl.textContent = "Select Urgency & Impact";
                return;
            }
            previewEl.className = "badge " + match.cls;
            previewEl.textContent = match.label;
        }

        urgencyEl.addEventListener("change", update);
        impactEl.addEventListener("change", update);
        update();
    }

    document.addEventListener("DOMContentLoaded", function () {
        var current = document.documentElement.getAttribute("data-theme") || "light";
        syncThemeButton(current);

        var btn = document.getElementById("themeBtn");
        if (btn) {
            btn.addEventListener("click", function () {
                var active = document.documentElement.getAttribute("data-theme");
                applyTheme(active === "dark" ? "light" : "dark");
            });
        }

        document.querySelectorAll("[data-confirm]").forEach(function (el) {
            el.addEventListener("click", function (event) {
                var msg = el.getAttribute("data-confirm");
                if (msg && !window.confirm(msg)) {
                    event.preventDefault();
                }
            });
        });

        initPriorityPreview();
    });
})();
