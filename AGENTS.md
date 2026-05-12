# NexGenWebLab — Frontend

## Stack
- Static HTML/CSS/JS site deployed on **Vercel**
- Tailwind CSS via CDN, Font Awesome, AOS animations
- Supabase JS client for auth (signup/login/upgrade)

## Key URLs
- Production: https://nexgenweblab.com
- Tools (backend): https://tools.nexgenweblab.com

## Pages (all at root level, no /pages/ folder)
- `/` — index.html (home)
- `/about` — about.html
- `/pricing` — pricing.html
- `/contact` — contact.html
- `/auth` — auth.html (signup)
- `/upgrade` — upgrade.html
- `/sitemap` — sitemap.html (visual sitemap)

## Key files
- `assets/js/site.js` — injects global header/footer, active nav detection, AOS init
- `assets/js/auth.js` — Supabase auth: email/password + Google OAuth, plan metadata
- `vercel.json` — cleanUrls, no trailing slash, `/sitemap` rewrite

## Supabase (auth)
- URL: https://ubnvjmvobwzsystdktpk.supabase.co
- Anon key: sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v

## Formspree (contact form)
- Endpoint: https://formspree.io/f/xgoddlky

## Git
- Remote: https://github.com/Malikaman9t9/nexgen-frontend.git
- Branch: main

## Recent work
- Fixed vercel.json Content-Type bug (was serving all assets as text/html)
- Moved pages from /pages/ folder to root
- Removed text logo from header (image only)
- Created visual sitemap page at /sitemap
- Wired contact form to Formspree with AJAX
- Created site.js for universal header/footer injection
