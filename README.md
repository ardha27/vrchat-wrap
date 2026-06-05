# VRChat Wrap

Your VRChat history, turned into a slide deck. Drop your VRCX database and get a personal recap of every world, session, and person you crossed paths with — last 30 days, last year, or all time.

Everything runs in your browser. Your data never gets uploaded.

## How to use

1. Open the site.
2. Find your VRCX database (`%AppData%\VRCX\VRCX.sqlite3` on Windows).
3. Drag it onto the page, or click to browse.
4. Pick a time window: last 30 days, last 12 months, or all time.
5. Swipe / arrow-key through the slides.

No account, no upload, no server. The file is read locally with sql.js (SQLite compiled to WebAssembly) and never leaves the tab. Don't have VRCX? Hit **View demo with sample data**.

## What you get

A series of slides pulled from your own logs:

- Hours spent in-world
- Unique worlds visited
- The world you kept coming back to (click to open in VRChat)
- People you crossed paths with
- Your squad: who you spent the most time with (each links to their VRChat profile)
- Friends added
- When you're actually online — peak hour clock, night counted as 9 PM–6 AM
- Your busiest month (all-time mode shows the year too)
- Your VRC16 personality type — a 4-letter result based on your actual play patterns

The personality card shows your name, time range, type code, and the scores behind each axis. Download as JPG or share directly to X.

### VRC16 personality types

At the end you get a 4-letter play personality. Not a quiz — it comes from your data:

- **E / I** — Explorer vs Inhabitant: do you constantly try new worlds, or return to the same ones?
- **S / L** — Social vs Lone: do you fill sessions with people, or prefer quieter worlds?
- **N / D** — Night vs Day: do most of your sessions happen after 9 PM?
- **B / R** — Binge vs Regular: long marathon sessions, or consistent shorter plays?

16 base types, plus 6 special overrides for edge cases (Night Wanderer, World Veteran, Metaverse Explorer, and others). Each axis is scored from several weighted ratios, not a single hard cutoff.

### Languages

English, Indonesian, Japanese, Korean, Chinese, Spanish, and French. Picks your browser language by default and remembers your choice.

### Live world thumbnails (optional)

World thumbnails are disabled by default because the VRChat API doesn't send CORS headers, so a static site can't read world data from the browser. You can fix this with a **Cloudflare Worker** (free):

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/) → Workers & Pages → Create → Worker.
2. Copy the contents of [`worker.js`](worker.js) and paste it in. Deploy.
3. Copy your worker URL (e.g. `https://vrcwrap.<you>.workers.dev`).
4. Open `index.html`, find `const WORLD_PROXY=''`, and paste the URL inside the quotes.

The worker validates the world id, fetches the API server-side (where CORS doesn't apply), and returns only the thumbnail fields. World ids are not logged or stored.

Friend profile pictures still aren't available — the user API requires a VRChat login and returns 401 without one. Squad members without images fall back to gradient avatars.

## Run locally

It's one file, so any static server works:

```bash
python3 -m http.server 8777
# open http://localhost:8777
```

Or just open `index.html` directly.

## Deploy to GitHub Pages

```bash
git add index.html README.md .gitignore
git commit -m "VRChat Wrap"
git push
```

Then enable Pages in repo settings → Source: `main` / root. sql.js loads over HTTPS from a CDN, so it works on `*.github.io` with no extra setup.

> **Heads up:** your `VRCX.sqlite3` holds personal logs — friend names, the worlds you visit, your hours. `.gitignore` already blocks `*.sqlite*`, but double-check it never gets committed to a public repo.

## Where the numbers come from

Reads these VRCX tables, filtered to the selected time window:

| Table | Used for |
|-------|----------|
| `gamelog_location` | worlds, visits, hours, busiest month, active days, hour-of-day |
| `gamelog_join_leave` | people met, encounters, your squad |
| `*_friend_log_history` | friends added |

Each stat is computed defensively — a missing table or odd schema won't crash the rest. Tables are matched by suffix, so the per-user prefix (e.g. `usr<id>_friend_log_history`) doesn't matter.

## Stack

- One `index.html` — no build step
- [sql.js](https://github.com/sql-js/sql.js) for reading SQLite in the browser
- [html2canvas-pro](https://github.com/niklasvh/html2canvas) for card capture (supports `color-mix()` and `oklch`)
- Fonts: Anton, Space Mono, Outfit
- Canvas particles + CSS for the rest

## Privacy

100% client-side. No analytics, no tracking, no network calls beyond fonts and the sql.js runtime. Your VRChat history stays on your machine.
