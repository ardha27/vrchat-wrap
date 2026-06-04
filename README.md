# VRChat Wrap

Your year in VR, replayed. Drop your VRCX database and get a personal year-in-review of every world, friend, and late-night session, styled after Discord's Checkpoint.

Everything runs in your browser. Your data never gets uploaded.

## How to use

1. Open the site.
2. Find your VRCX database (`%AppData%\VRCX\VRCX.sqlite3` on Windows).
3. Drag it onto the page, or click to browse.
4. Swipe / arrow-key through your year.

No account, no upload, no server. The file is read locally with sql.js (SQLite compiled to WebAssembly) and never leaves the tab. Don't have VRCX? Hit **View demo with sample data**.

## What you get

Pick a window first — last 30 days, last 12 months, or all time — then walk ten slides pulled straight from your own logs:

- Hours spent in-world
- Unique worlds visited
- The world you kept coming back to (click it to open in VRChat)
- People you crossed paths with
- Your squad: who you spent the most time with (each links to their VRChat profile)
- Friends added
- When you're actually online (night-owl clock)
- Your busiest month
- A holographic trading card you can download and share to X

The final card has a name field, an auto-filled caption with the site link and hashtags, a download button, and Share on X (plus native share on mobile).

### Languages

English, Indonesian, Japanese, Korean, Chinese, Spanish, and French. It picks your browser language by default and remembers your choice.

### A note on world and friend images

VRChat thumbnails and profile pictures aren't shown. The VRChat API needs a login and blocks browser requests (CORS), and VRCX's offline image cache is usually empty and stores nothing for friends. Instead, worlds and friends get generated color avatars so the lists still read well, and both link out to VRChat where you can see the real thing.

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

Reads these VRCX tables, filtered to the detected year:

| Table | Used for |
|-------|----------|
| `gamelog_location` | worlds, visits, hours, busiest month, active days, hour-of-day |
| `gamelog_join_leave` | people met, encounters, your squad |
| `*_friend_log_history` | friends added |

Each stat is computed defensively — a missing table or odd schema won't crash the rest. Tables are matched by suffix, so the per-user prefix (e.g. `usr<id>_friend_log_history`) doesn't matter.

## Stack

- One `index.html` — no build step
- [sql.js](https://github.com/sql-js/sql.js) for reading SQLite in the browser
- Fonts: Anton, Space Mono, Outfit
- Canvas particles + CSS for the rest

## Privacy

100% client-side. No analytics, no tracking, no network calls beyond fonts and the sql.js runtime. Your VRChat history stays on your machine.
