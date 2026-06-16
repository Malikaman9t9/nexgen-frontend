(function () {
    "use strict";

    var SITE_NAME = "NexGenWebLab";
    var BASE_URL = window.location.origin;
    var TOOLS_URL = "https://tools.nexgenweblab.com";

    var isActive = function (path) {
        var p = window.location.pathname.replace(/\/$/, "");
        if (path === "/" && (p === "" || p === "/index.html")) return true;
        if (path !== "/" && p.startsWith(path)) return true;
        return false;
    };

    var navLink = function (href, label, className) {
        className = className || "text-slate-600 hover:text-slate-900 font-semibold text-sm transition-colors";
        var a = document.createElement("a");
        a.href = href;
        a.className = className;
        if (isActive(href)) a.classList.add("text-primary", "font-bold");
        a.textContent = label;
        return a;
    };

    var SOLUTIONS = [
        { label: "WordPress", href: "/solutions/wordpress" },
        { label: "Shopify", href: "/solutions/shopify" },
        { label: "Digital Agencies", href: "/solutions/digital-agencies" },
        { label: "Freelancers", href: "/solutions/freelancers" },
        { label: "E-commerce Stores", href: "/solutions/e-commerce-stores" },
        { label: "Real Estate Agents", href: "/solutions/real-estate-agents" },
        { label: "Local Businesses", href: "/solutions/local-businesses" },
        { label: "SaaS Companies", href: "/solutions/saas-companies" }
    ];

    var solutionsDropdownHtml = function () {
        var items = SOLUTIONS.map(function (s) {
            return '<a href="' + s.href + '" class="block px-4 py-2.5 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 hover:text-primary transition-colors">' + s.label + '</a>';
        }).join('');
        return '<div class="relative group">' +
            '<button class="flex items-center gap-1.5 text-slate-600 hover:text-slate-900 font-semibold text-sm transition-colors cursor-pointer">' +
            'Solutions' +
            '<i class="fa-solid fa-chevron-down text-[10px] transition-transform duration-200 group-hover:rotate-180"></i>' +
            '</button>' +
            '<div class="absolute top-full left-1/2 -translate-x-1/2 pt-3 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 translate-y-1 group-hover:translate-y-0">' +
            '<div class="bg-white rounded-xl shadow-xl border border-slate-100 p-2 min-w-[220px]">' +
            items +
            '</div>' +
            '</div>' +
            '</div>';
    };

    function injectHeader() {
        if (document.getElementById("global-header")) return;

        var isHome = window.location.pathname === "/" || window.location.pathname === "/index.html";

        var header = document.createElement("header");
        header.id = "global-header";
        header.className = "bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50";

        header.innerHTML =
            '<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">' +
            '  <div class="flex justify-between items-center h-16 lg:h-20">' +
            '    <a href="' + BASE_URL + '/" class="flex items-center gap-2 shrink-0" aria-label="' + SITE_NAME + ' home">' +
            '      <img src="' + BASE_URL + '/assets/images/logo.png" alt="' + SITE_NAME + '" class="h-7 w-auto">' +
            '    </a>' +
            '    <nav class="hidden md:flex items-center gap-8" aria-label="Main navigation">' +
            navLink(BASE_URL + "/", "Home").outerHTML +
            navLink(BASE_URL + "/about", "About").outerHTML +
            navLink(BASE_URL + "/blog", "Blog").outerHTML +
            solutionsDropdownHtml() +
            navLink(BASE_URL + "/pricing", "Pricing").outerHTML +
            navLink(BASE_URL + "/contact", "Contact").outerHTML +
            '      <a href="' + TOOLS_URL + '" class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm bg-slate-900 text-white hover:bg-slate-800 transition-colors shadow-md">' +
            '        <i class="fa-solid fa-gauge-high"></i> Dashboard' +
            '      </a>' +
            '    </nav>' +
            '    <button id="mobile-menu-btn" class="md:hidden p-2 rounded-lg hover:bg-slate-100 transition-colors" aria-label="Toggle menu" aria-expanded="false">' +
            '      <i class="fa-solid fa-bars text-xl text-slate-700"></i>' +
            '    </button>' +
            '  </div>' +
            '  <div id="mobile-menu" class="md:hidden hidden pb-6 border-t border-slate-100 pt-4 space-y-3" role="menu">' +
'    <a href="' + BASE_URL + '/" class="block px-4 py-3 rounded-xl text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors" role="menuitem">Home</a>' +
'    <a href="' + BASE_URL + '/about" class="block px-4 py-3 rounded-xl text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors" role="menuitem">About</a>' +
'    <a href="' + BASE_URL + '/blog" class="block px-4 py-3 rounded-xl text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors" role="menuitem">Blog</a>' +
'    <div class="px-2">' +
'      <div class="text-xs font-black uppercase tracking-widest text-slate-400 px-4 pt-2 pb-1">Solutions</div>' +
      SOLUTIONS.map(function(s) {
        return '<a href="' + s.href + '" class="block px-4 py-2.5 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-50 hover:text-primary transition-colors" role="menuitem">' + s.label + '</a>';
      }).join('') +
'    </div>' +
'    <a href="' + BASE_URL + '/pricing" class="block px-4 py-3 rounded-xl text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors" role="menuitem">Pricing</a>' +
'    <a href="' + BASE_URL + '/contact" class="block px-4 py-3 rounded-xl text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors" role="menuitem">Contact</a>' +
            '    <a href="' + TOOLS_URL + '" class="block px-4 py-3 rounded-xl text-sm font-bold text-white bg-slate-900 hover:bg-slate-800 transition-colors text-center" role="menuitem">Dashboard</a>' +
            '  </div>' +
            '</div>';

        document.body.prepend(header);

        var btn = document.getElementById("mobile-menu-btn");
        var menu = document.getElementById("mobile-menu");
        if (btn && menu) {
            btn.addEventListener("click", function () {
                var expanded = btn.getAttribute("aria-expanded") === "true";
                btn.setAttribute("aria-expanded", !expanded);
                menu.classList.toggle("hidden");
                var icon = btn.querySelector("i");
                if (icon) {
                    icon.className = expanded
                        ? "fa-solid fa-bars text-xl text-slate-700"
                        : "fa-solid fa-xmark text-xl text-slate-700";
                }
            });
            
            // Close menu when clicking on a link
            var menuLinks = menu.querySelectorAll("a");
            menuLinks.forEach(function(link) {
                link.addEventListener("click", function() {
                    btn.setAttribute("aria-expanded", "false");
                    menu.classList.add("hidden");
                    var icon = btn.querySelector("i");
                    if (icon) {
                        icon.className = "fa-solid fa-bars text-xl text-slate-700";
                    }
                });
            });
        }
    }

    function injectFooter() {
        if (document.getElementById("global-footer")) return;
        var footer = document.createElement("footer");
        footer.id = "global-footer";
        footer.className = "bg-slate-900 text-slate-300 border-t border-slate-800 mt-auto";
        footer.innerHTML =
            '<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">' +
            '  <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">' +
            '    <div>' +
            '      <img src="' + BASE_URL + '/assets/images/logo.png" alt="' + SITE_NAME + '" class="h-7 mb-3 brightness-0 invert">' +
            '      <p class="text-xs text-slate-500 font-medium leading-relaxed">' +
            '        ' + SITE_NAME + ' provides free technical SEO audits with AI-powered insights,<br>' +
            '        traffic analytics, and white-label reporting for modern web teams.' +
            '      </p>' +
            '    </div>' +
            '    <div>' +
            '      <h4 class="text-sm font-bold text-white mb-3">Quick Links</h4>' +
            '      <ul class="space-y-1.5 text-xs font-medium text-slate-500">' +
            '        <li><a href="' + BASE_URL + '/about" class="hover:text-white transition-colors">About</a></li>' +
            '        <li><a href="' + BASE_URL + '/pricing" class="hover:text-white transition-colors">Pricing</a></li>' +
            '        <li><a href="' + BASE_URL + '/contact" class="hover:text-white transition-colors">Contact</a></li>' +
            '        <li><a href="' + TOOLS_URL + '" class="hover:text-white transition-colors">Dashboard</a></li>' +
            '      </ul>' +
            '    </div>' +
            '    <div>' +
            '      <h4 class="text-sm font-bold text-white mb-3">Legal</h4>' +
            '      <ul class="space-y-1.5 text-xs font-medium text-slate-500">' +
            '        <li><a href="' + BASE_URL + '/privacy" class="hover:text-white transition-colors">Privacy Policy</a></li>' +
            '        <li><a href="' + BASE_URL + '/terms" class="hover:text-white transition-colors">Terms of Service</a></li>' +
            '      </ul>' +
            '    </div>' +
            '  </div>' +
            '  <div class="border-t border-slate-800 pt-6 flex flex-col md:flex-row justify-between items-center gap-3 text-xs text-slate-500 font-medium">' +
            '    <p>&copy; ' + new Date().getFullYear() + ' ' + SITE_NAME + '. All rights reserved.</p>' +
            '    <p class="flex items-center gap-4">Made with <i class="fa-solid fa-heart text-secondary"></i> for the open web</p>' +
            '  </div>' +
            '</div>';
        document.body.appendChild(footer);
    }

    function detectPlanFromUrl() {
        var params = new URLSearchParams(window.location.search);
        var plan = params.get("plan");
        if (plan === "pro" || plan === "free") {
            var radio = document.getElementById("plan-" + plan);
            if (radio) radio.checked = true;
            try { sessionStorage.setItem("selectedPlan", plan); } catch (e) {}
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        injectHeader();
        injectFooter();
        detectPlanFromUrl();

        if (typeof AOS !== "undefined") {
            AOS.init({
                duration: 800,
                easing: "ease-out-cubic",
                once: true,
                offset: 80,
            });
        }
    });
})();
