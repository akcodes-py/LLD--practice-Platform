# Website quality & pre-launch checklist — verification

Checked against the running app on 2026-09-25. “Verified” means inspected in code and/or the live UI.

## Website quality (20)

1. **Remove horizontal scrolling** — Verified: layouts are `max-w-*` centred with wrapping grids/flex; no full-bleed
   fixed-width elements. Resize to 360px shows no x-scroll.
2. **Find and fix broken links** — Verified: header/footer/problem/history/review links all point at real routes;
   unknown paths render the custom 404 (no dead buttons).
3. **Add a working mobile menu** — Verified: hamburger toggles `#mobile-menu` with `aria-expanded`; links close it.
4. **Add a favicon** — Verified: `public/favicon.svg` + `<link rel="icon">`.
5. **Fix page titles** — Verified: every route sets `document.title` via `usePageMeta`.
6. **Add meta descriptions** — Verified: base tag in `index.html`, updated per route.
7. **Fix footer links** — Verified: Problems / My attempts / Privacy / Terms all resolve.
8. **Add a custom 404 page** — Verified: `*` route renders `NotFound` with paths home.
9. **Keep the copyright year current** — Verified: `new Date().getFullYear()` in footer and legal pages.
10. **Compress and optimise images** — Verified: only two tiny SVGs (favicon ~0.5KB, OG preview); no raster images to compress.
11. **Fix broken buttons** — Verified: every button acts (start/save/submit/retry/re-evaluate/navigate); disabled states while pending; no dead CTAs.
12. **Add success messages** — Verified: draft-saved, submitted, retry-created, re-evaluated confirmations (`role="status"`).
13. **Add error messages** — Verified: API failures, per-field validation, evaluator-failure panel (`role="alert"`).
14. **Remove placeholder text** — Verified: no lorem ipsum; editor placeholders are instructional; copy is product-specific.
15. **Remove unused navigation** — Verified: nav contains only Problems / My attempts / CTA; no LMS/store/community links copied from the audit.
16. **Fix mobile overflow** — Verified with #1: grids collapse to one column; score bars and badges wrap at 360px.
17. **Make the logo clickable** — Verified: logo links to `/` with an accessible name.
18. **Make phone numbers clickable if present** — N/A: no phone numbers exist anywhere in the product (correct for a prototype; nothing to link).
19. **Make email addresses clickable if present** — N/A: no email addresses exist in the product.
20. **Optimise every page for mobile** — Verified: responsive grids, 16px+ type, tap targets ≥40px, sticky header + hamburger, tested widths 360/768/1280.

## Pre-launch (20)

1. **Privacy policy page** — Verified: `/privacy` describes local storage, no tracking, LLM opt-in data flow, deletion.
2. **Terms and conditions** — Verified: `/terms` covers prototype status, ownership, no secrets, heuristic feedback.
3. **Keep secrets off the frontend** — Verified: frontend only knows `VITE_API_URL`; `LLM_API_KEY` is backend-only (`config/settings.py`); `.env.example` files ship without values.
4. **Enforce HTTPS in production** — Implemented in config (`SECURE_SSL_REDIRECT` + HSTS + secure cookies when `DEBUG=0`); deployment note: terminate TLS at the proxy/ingress in front of the Compose stack. Not runtime-verified here (no TLS env on this machine) — limitation recorded.
5. **Cookie consent** — Intentionally omitted with justification: the app sets no non-essential cookies and runs no analytics; adding a banner would be misleading. Documented in `/privacy`.
6. **Page-specific titles and descriptions** — Verified (see quality #5–6).
7. **Social preview image** — Verified: `public/og-preview.svg` + `og:`/`twitter:` meta tags.
8. **Favicon** — Verified (see quality #4).
9. **Sitemap and robots.txt** — Verified: `public/sitemap.xml` (public routes only; `/attempts`, `/history` disallowed) + `public/robots.txt`.
10. **Meaningful alt text** — Verified: logo and decorative/OG images labelled; no informative raster images exist.
11. **Optimise images** — Verified (see quality #10).
12. **Check performance** — Partially verified: production bundle is ~200KB JS / 17KB CSS (gz 63KB/4KB); no image/font payloads; no analytics. No lab profiling tool was available on this machine — limitation recorded.
13. **Verify colour contrast** — Verified by token choice: ink `#0F172A` on white/slate-50, white on brand-600 `#E07D18` for primary actions, red-700/green-800 text on tinted panels; visible 3px focus ring. No automated audit tool run — limitation recorded.
14. **Verify mobile usability** — Verified (see quality #20).
15. **Custom 404** — Verified (see quality #8).
16. **Fix broken links** — Verified (see quality #2).
17. **Frontend and backend validation** — Verified: frontend required/min-length + honeypot; backend `validate_content` minimums + 400 envelope; both exercised by tests.
18. **Spam/bot protection** — Implemented proportionately: editor honeypot + auto-save throttling + no public anonymous write except attempt creation (low abuse value); no CAPTCHA, justified for a local prototype. Documented.
19. **Analytics** — Intentionally omitted: no tracking code ships and no personal data is collected. Would only be added if explicitly configured. Documented in `/privacy`.
20. **One clear primary CTA** — Verified: “Start practicing” in header (desktop + mobile), home hero, and problem pages.

## Exceptions / limitations

- CI workflow (`.github/workflows/ci.yml`) and Docker Compose were written carefully but **not executed** on this machine (no Docker daemon; GitHub Actions needs a push). This is stated in the README and final report — not claimed as passing.
- HTTPS redirect and performance/contrast tooling were configured by construction but not lab-verified here (noted above).
