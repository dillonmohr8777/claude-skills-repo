#!/usr/bin/env node
/**
 * Build a BigOrange deck from a recipe and a brief.
 *
 *   node build_deck.js <brief.json> <out.pptx> [--recipe path] [--no-validate]
 *
 * brief.json:
 *   { "recipe": "industry-pitch",          // or a path to a recipe json
 *     "title": "...", "date": "September 2026", "presenter": "Dillon Mohr",
 *     "client": { "name": "Acme Builders", "line": "Custom homes, Cincinnati" },
 *     "logo": { "path": "acme.png", "source": "https://...", "verified": true },
 *     "industry": "home-builders", "sampleData": true,
 *     "vars": { "any": "value used by {{vars.any}} in recipe strings" },
 *     "slides": { "<slide id>": { ...block data merged over the recipe defaults... } },
 *     "skip": ["<slide id>"] }
 *
 * Recipe slides declare { id, block, mode, eyebrow, title, data, notes, required }.
 * Every string in the recipe may use {{path.to.brief.value}} interpolation.
 * Missing required values render as [[slot]] so validate_deck.py fails closed.
 */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const kit = require('../lib/deck-kit');

const SKILL = path.resolve(__dirname, '..');
const RECIPES = path.resolve(SKILL, '..', 'bigorange-client-decks', 'recipes');

function get(obj, p) { return p.split('.').reduce((o, k) => (o == null ? undefined : o[k]), obj); }
function tpl(v, ctx) {
  if (typeof v === 'string') {
    const whole = v.match(/^\{\{\s*([\w.\-]+)\s*\}\}$/);
    if (whole) { const r = get(ctx, whole[1]); return r == null ? `[[${whole[1]}]]` : (typeof r === 'string' ? r : tpl(r, ctx)); }
    return v.replace(/\{\{\s*([\w.\-]+)\s*\}\}/g, (m, p) => { const r = get(ctx, p); return r == null ? `[[${p}]]` : String(r); });
  }
  if (Array.isArray(v)) return v.map(x => tpl(x, ctx));
  if (v && typeof v === 'object') { const o = {}; for (const k of Object.keys(v)) o[k] = tpl(v[k], ctx); return o; }
  return v;
}
function merge(a, b) {
  if (Array.isArray(a) && Array.isArray(b)) return b;
  if (a && b && typeof a === 'object' && typeof b === 'object') { const o = Object.assign({}, a); for (const k of Object.keys(b)) o[k] = merge(a[k], b[k]); return o; }
  return b === undefined ? a : b;
}

async function build(briefPath, outPath, opts = {}) {
  const brief = JSON.parse(fs.readFileSync(briefPath, 'utf8'));
  const recipePath = opts.recipe || (brief.recipe && brief.recipe.endsWith('.json') ? brief.recipe : path.join(RECIPES, `${brief.recipe}.json`));
  const recipe = JSON.parse(fs.readFileSync(recipePath, 'utf8'));
  const ctx = Object.assign({ today: new Date().toISOString().slice(0, 10) }, brief, { client: brief.client || {}, vars: brief.vars || {}, logo: brief.logo || {} });
  const draft = brief.sampleData !== false && recipe.defaultDraft !== false;
  const d = kit.create({ title: tpl(recipe.title || brief.title || 'BigOrange deck', ctx), footer: tpl(recipe.footer || 'BigOrange.Marketing · {{date}}', ctx), draft });
  const skip = new Set(brief.skip || []);
  let n = 0;
  for (const sl of recipe.slides) {
    if (skip.has(sl.id)) continue;
    const over = (brief.slides && brief.slides[sl.id]) || {};
    const data = tpl(merge(sl.data || {}, over), ctx);
    const eyebrow = tpl(over.eyebrow || sl.eyebrow || '', ctx);
    const title = tpl(over.title || sl.title || '', ctx);
    const s = d.slide(sl.mode || 'white'); n += 1;
    if (sl.block === 'coverDark') { d.coverDark(s, Object.assign({ eyebrow, title }, data)); if (draft) d.draftBanner(s); }
    else if (sl.block === 'coverClient') { d.coverClient(s, Object.assign({ eyebrow, title, clientName: ctx.client.name, clientLine: ctx.client.line, clientLogo: ctx.logo }, data)); if (draft) d.draftBanner(s); }
    else {
      d.chrome(s, n); d.head(s, eyebrow, title);
      const fn = d[sl.block];
      if (typeof fn !== 'function') throw new Error(`unknown block '${sl.block}' on slide ${sl.id}`);
      await fn(s, data);
    }
    d.notes(s, tpl(over.notes || sl.notes || '', ctx));
  }
  await d.write(outPath);
  const result = { out: outPath, slides: n, draft };
  if (!opts.noValidate) {
    const args = [path.join(SKILL, 'scripts', 'validate_deck.py'), outPath];
    if (draft) args.push('--draft');
    if (ctx.client.name) args.push('--client-name', ctx.client.name);
    if (ctx.logo.path && ctx.logo.verified) args.push('--client-logo', ctx.logo.path);
    try { result.validation = execFileSync('python3', args, { encoding: 'utf8' }); result.passed = true; }
    catch (e) { result.validation = (e.stdout || '') + (e.stderr || ''); result.passed = false; }
  }
  return result;
}

if (require.main === module) {
  const argv = process.argv.slice(2);
  const [briefPath, outPath] = argv;
  const ri = argv.indexOf('--recipe');
  if (!briefPath || !outPath) { console.error('usage: build_deck.js <brief.json> <out.pptx> [--recipe path] [--no-validate]'); process.exit(2); }
  build(briefPath, outPath, { recipe: ri > -1 ? argv[ri + 1] : undefined, noValidate: argv.includes('--no-validate') })
    .then(r => { console.log(`wrote ${r.out} (${r.slides} slides, draft=${r.draft})`); if (r.validation) process.stdout.write(r.validation); process.exit(r.passed === false ? 1 : 0); })
    .catch(e => { console.error(e); process.exit(1); });
}
module.exports = { build };
