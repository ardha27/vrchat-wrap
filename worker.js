// VRChat Wrap — world thumbnail proxy (Cloudflare Worker)
//
// VRChat's world API is public but sends no CORS header, so a static site
// can't read it directly. This worker fetches the world JSON server-side and
// returns just the image fields with CORS enabled. It validates the id, so it
// is not an open proxy. User/avatar data needs a login and is intentionally
// not proxied here.
//
// Deploy (free):
//   1. https://dash.cloudflare.com → Workers & Pages → Create → Worker
//   2. Paste this file, Deploy.
//   3. Copy the URL (e.g. https://vrcwrap.<you>.workers.dev) and set it as
//      WORLD_PROXY in index.html.
// Or with wrangler:  npx wrangler deploy worker.js

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Cache-Control': 'public, max-age=86400',
};

export default {
  async fetch(req) {
    if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });

    const id = new URL(req.url).searchParams.get('id') || '';
    if (!/^wrld_[0-9a-fA-F-]{36}$/.test(id))
      return json({ error: 'invalid world id' }, 400);

    let r;
    try {
      r = await fetch('https://api.vrchat.cloud/api/1/worlds/' + id, {
        headers: { 'User-Agent': 'vrchat-wrap/1.0 (github.io static site)' },
        cf: { cacheTtl: 86400, cacheEverything: true },
      });
    } catch (e) {
      return json({ error: 'fetch failed' }, 502);
    }
    if (!r.ok) return json({ error: 'upstream', status: r.status }, r.status);

    const w = await r.json();
    return json({
      name: w.name,
      authorName: w.authorName,
      thumbnailImageUrl: w.thumbnailImageUrl,
      imageUrl: w.imageUrl,
    });
  },
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { ...CORS, 'Content-Type': 'application/json' },
  });
}
