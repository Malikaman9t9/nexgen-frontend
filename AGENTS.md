# NexGenWebLab — Backend (SEO Auditor Tool)

## Stack
- **Streamlit** Python app deployed on **Render**
- Supabase for auth (optional — app falls back to demo mode without it)
- Google PageSpeed API (speed metrics)
- Google Gemini API (AI recommendations)
- RapidAPI / SimilarWeb (traffic analytics)
- python-docx + matplotlib (white label DOCX report export)

## Key URL
- Production: https://tools.nexgenweblab.com

## Modules (backend/modules/)
- `onpage_scraper.py` — scrapes HTML for meta tags, H1, images, schema etc.
- `speed_checker.py` — Google PageSpeed API v5, falls back to HTTP estimation
- `ai_analyzer.py` — Gemini 2.0 Flash for SEO recommendations
- `report_export.py` — generates DOCX with matplotlib gauge charts
- `traffic_checker.py` — SimilarWeb via RapidAPI

## Key files
- `app.py` — main streamlit app (auth gate, audit UI, tabs, bulk analysis)
- `.env.example` — template for required env vars
- `requirements.txt` — pip deps (pinned to minimum versions with >=)

## Required environment variables (set on Render dashboard)
- `SUPABASE_URL` — Supabase project URL
- `SUPABASE_KEY` — Supabase anon key
- `SPEED_API_KEY` — Google PageSpeed API key
- `GEMINI_API_KEY` — Google Gemini API key
- `RAPIDAPI_KEY` — RapidAPI key for SimilarWeb

## Supabase (auth)
- URL: https://ubnvjmvobwzsystdktpk.supabase.co
- Anon key: sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v

## Git
- Remote: https://github.com/Malikaman9t9/Nex-Gen-Web-Lab.git
- Branch: main

## Recent work
- Fixed pro detection: now uses Supabase `user_metadata.plan` instead of email hack
- Bulk analysis now actually works (was a fake progress bar)
- Removed `verify=False` from all HTTP requests
- Cleaned up code comments to all English
- Fixed Gemini model to `gemini-2.0-flash`
- Pinned requirements to minimum versions with `>=`
- Made Supabase optional — app runs in demo mode without it
- Fixed `st.image(use_container_width)` version compatibility
- Redesigned URL input bar to match frontend hero section
