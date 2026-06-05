#!/usr/bin/env node
// Generates XOR-obfuscated key arrays for index.html
// Usage:  node keygen.js [your-secret-string]
// If no argument given, a random 32-char hex string is used.
//
// Output:
//   SUBMIT_SECRET — paste into: npx wrangler secret put SUBMIT_SECRET
//   _KA / _KB     — paste into index.html where marked

const secret = process.argv[2] || require('crypto').randomBytes(16).toString('hex');
const mask   = Array.from({length: 16}, () => Math.floor(Math.random() * 256));
const encoded = [...Buffer.from(secret, 'utf8')].map((b, i) => b ^ mask[i % mask.length]);

console.log('\n── SUBMIT_SECRET (set this in Cloudflare) ──────────────────');
console.log(secret);

console.log('\n── Paste these into index.html ─────────────────────────────');
console.log('const _KA=' + JSON.stringify(encoded) + ';');
console.log('const _KB=' + JSON.stringify(mask) + ';');
console.log('\nVerify round-trip:', Buffer.from(encoded.map((b,i)=>b^mask[i%mask.length])).toString('utf8') === secret ? 'OK' : 'FAIL');
