// ============================================================
// NexGenWebLab — Universal Site Components
// ============================================================

const SITE = {
  page: '',

  headerHTML() {
    const p = this.page;
    const a = (href, label, cls = '') =>
      `<a href="${href}" class="${cls}${p === href || (href !== '/' && p.startsWith(href)) ? ' text-primary' : ' text-slate-500 hover:text-primary'} transition-colors font-bold text-sm">${label}</a>`;

    return `
    <header class="sticky top-0 z-[100] backdrop-blur-xl border-b border-slate-100 bg-white/80">
      <div class="max-w-7xl mx-auto flex items-center justify-between h-20 px-4 sm:px-6 lg:px-8 relative">
        <a href="/" class="flex items-center hover:opacity-90 transition-opacity">
          <img src="/assets/images/logo.png" alt="NexGenWebLab - SEO Audit Tool" class="h-8 md:h-10 w-auto object-contain">
        </a>
        <nav class="hidden lg:flex items-center gap-10" itemscope itemtype="https://schema.org/SiteNavigationElement">
          ${a('/', 'Home')}
          ${a('/about', 'About Solution')}
          ${a('/pricing', 'Pricing Plans')}
          ${a('/contact', 'Contact Support')}
        </nav>
        <div class="hidden lg:flex items-center gap-5">
          <a href="https://tools.nexgenweblab.com" class="text-sm font-extrabold text-slate-600 hover:text-primary transition-colors">Client Login</a>
          <a href="/auth" class="text-sm font-black bg-slate-900 text-white px-7 py-3.5 rounded-2xl hover:bg-slate-800 transition-all shadow-xl hover:shadow-primary/20 flex items-center gap-2">
            Get Started Free
          </a>
        </div>
        <button id="mobile-menu-btn" class="lg:hidden text-slate-600 hover:text-primary focus:outline-none text-2xl">
          <i class="fa-solid fa-bars"></i>
        </button>
      </div>
      <div id="mobile-menu" class="hidden lg:hidden bg-white border-t border-slate-100 absolute top-20 left-0 w-full shadow-2xl">
        <div class="flex flex-col px-6 py-6 space-y-4">
          ${a('/', 'Home', 'text-lg')}
          ${a('/about', 'About Solution', 'text-lg')}
          ${a('/pricing', 'Pricing Plans', 'text-lg')}
          ${a('/contact', 'Contact Support', 'text-lg')}
          <hr class="border-slate-100">
          <a href="https://tools.nexgenweblab.com" class="text-lg font-bold text-slate-600 hover:text-primary transition-colors">Client Login</a>
          <a href="/auth" class="text-center font-black bg-slate-900 text-white px-6 py-4 rounded-xl hover:bg-slate-800 transition-all shadow-md mt-2">Get Started Free</a>
        </div>
      </div>
    </header>`;
  },

  footerHTML() {
    return `
    <footer class="bg-slate-950 text-slate-400 border-t border-white/5">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-20">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12 lg:gap-20">
          <div>
            <img src="/assets/images/logo.png" alt="NexGenWebLab" class="h-8 lg:h-10 w-auto mb-6 lg:mb-8 brightness-0 invert">
            <p class="text-xs lg:text-sm font-medium leading-relaxed max-w-xs">NexGenWebLab provides professional SEO auditing tools and AI-driven growth strategies for modern digital brands.</p>
          </div>
          <div>
            <h4 class="text-white font-black uppercase tracking-widest text-[10px] lg:text-xs mb-6 lg:mb-8">Quick Navigation</h4>
            <ul class="space-y-3 lg:space-y-4 text-xs lg:text-sm font-bold">
              <li><a href="/" class="hover:text-primary transition-colors">Home Page</a></li>
              <li><a href="/about" class="hover:text-primary transition-colors">Our Mission</a></li>
              <li><a href="/pricing" class="hover:text-primary transition-colors">Pricing & Plans</a></li>
              <li><a href="/contact" class="hover:text-primary transition-colors">Technical Support</a></li>
            </ul>
          </div>
          <div>
            <h4 class="text-white font-black uppercase tracking-widest text-[10px] lg:text-xs mb-6 lg:mb-8">Technical Tools</h4>
            <ul class="space-y-3 lg:space-y-4 text-xs lg:text-sm font-bold">
              <li><a href="https://tools.nexgenweblab.com" class="hover:text-secondary transition-colors">SEO Site Auditor</a></li>
              <li><a href="https://tools.nexgenweblab.com" class="hover:text-secondary transition-colors">Bulk Checker</a></li>
              <li><a href="https://tools.nexgenweblab.com" class="hover:text-secondary transition-colors">Traffic API</a></li>
            </ul>
          </div>
        </div>
        <div class="mt-16 lg:mt-20 pt-6 lg:pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4 lg:gap-6 text-[10px] lg:text-xs font-black uppercase tracking-[0.2em] lg:tracking-[0.3em] text-center md:text-left">
          <p>&copy; 2026 NexGenWebLab. High-Performance SEO Suite.</p>
          <div class="flex gap-6 lg:gap-10">
            <a href="#" class="hover:text-white transition-colors">Twitter</a>
            <a href="#" class="hover:text-white transition-colors">LinkedIn</a>
            <a href="#" class="hover:text-white transition-colors">GitHub</a>
          </div>
        </div>
      </div>
    </footer>`;
  },

  inject() {
    const h = document.getElementById('site-header');
    const f = document.getElementById('site-footer');
    if (h) h.innerHTML = this.headerHTML();
    if (f) f.innerHTML = this.footerHTML();
  },

  mobileMenu() {
    const btn = document.getElementById('mobile-menu-btn');
    const menu = document.getElementById('mobile-menu');
    if (btn && menu) {
      btn.addEventListener('click', () => {
        menu.classList.toggle('hidden');
        const icon = btn.querySelector('i');
        if (icon) {
          icon.classList.toggle('fa-bars');
          icon.classList.toggle('fa-xmark');
        }
      });
    }
  },

  init() {
    this.page = window.location.pathname.replace(/\/+$/, '') || '/';
    this.inject();
    this.mobileMenu();
    if (typeof AOS !== 'undefined') {
      AOS.init({ once: true, offset: 50, duration: 800 });
    }
  }
};

document.addEventListener('DOMContentLoaded', () => SITE.init());
