/**
 * BigOrange.Marketing deck kit (pptxgenjs house library)
 *
 * One brand, one canvas (LAYOUT_WIDE 13.333 x 7.5 in), one set of blocks.
 * Every block takes a pptxgenjs slide and a plain object and draws with the
 * BigOrange tokens below. Nothing here invents copy: blocks render what the
 * brief supplies and leave labelled placeholders when a required slot is empty
 * so the validator can fail closed.
 *
 * Usage:
 *   const kit = require('../lib/deck-kit');
 *   const d = kit.create({ title: 'Deck title', draft: true });
 *   const s = d.slide('white');           // 'white' | 'dark'
 *   d.chrome(s, 2); d.head(s, 'Eyebrow', 'Title');
 *   d.statsRow(s, [{ v: '370', l: 'published URLs', hot: true }]);
 *   await d.write('out.pptx');
 */
const path = require('path');
const pptxgen = require('pptxgenjs');

let sharp = null, React = null, RD = null, Icons = null;
try { sharp = require('sharp'); React = require('react'); RD = require('react-dom/server'); Icons = require('react-icons/fi'); } catch (e) { /* icons optional */ }

const TOKENS = Object.freeze({
  orange: 'FF7C00', orangeDeep: 'D96400', ink: '121212', ink2: '2B2B2B', mute: '6E6A66',
  pith: 'F6F1EA', peel: 'FFF3E8', line: 'E4DDD4', white: 'FFFFFF', soft: 'CFC8C0', reverse: 'EDE7E0', leaf: '1E6B3C',
  fontDisplay: 'Montserrat', fontBody: 'Arial',
});
const ASSETS = path.join(__dirname, '..', 'assets');
const LOGO = { orange: path.join(ASSETS, 'logos', 'bigorange-logo-orange.png'), white: path.join(ASSETS, 'logos', 'bigorange-logo-white.png') };
const W = 13.333, H = 7.5, M = 0.6, CW = W - 2 * M; // content width 12.133

function create(opts = {}) {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';
  pres.author = 'BigOrange.Marketing';
  pres.company = 'BigOrange.Marketing';
  pres.title = opts.title || 'BigOrange deck';
  const O = TOKENS.orange, INK = TOKENS.ink, INK2 = TOKENS.ink2, MUTE = TOKENS.mute, PITH = TOKENS.pith, PEEL = TOKENS.peel, WH = TOKENS.white, SOFT = TOKENS.soft, REV = TOKENS.reverse;
  const Hf = TOKENS.fontDisplay, Bf = TOKENS.fontBody;
  const footer = (opts.footer || 'BigOrange.Marketing').toUpperCase();
  const draft = !!opts.draft;
  let n = 0;
  const slides = [];

  const T = (s, txt, o) => s.addText(txt == null ? '' : String(txt), Object.assign({ isTextBox: true, margin: 0, fontFace: Bf, color: INK, valign: 'top' }, o));
  const rect = (s, x, y, w, h, color) => s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color }, line: { color, width: 0 } });
  const sq = (s, x, y, size = 0.12) => rect(s, x, y, size, size, O);
  const slot = (v, name) => (v == null || v === '' ? `[[${name}]]` : v);

  async function icon(name, color = O, size = 256) {
    if (!sharp || !Icons || !Icons[name]) return null;
    const svg = RD.renderToStaticMarkup(React.createElement(Icons[name], { color: '#' + color, size, strokeWidth: 1.6 }));
    const buf = await sharp(Buffer.from(svg)).png().toBuffer();
    return 'image/png;base64,' + buf.toString('base64');
  }

  function slide(mode = 'white') {
    const s = pres.addSlide();
    s.background = { color: mode === 'dark' ? INK : WH };
    s.__dark = mode === 'dark';
    n += 1; s.__n = n; slides.push(s);
    return s;
  }

  function chrome(s, num = s.__n) {
    const dark = s.__dark;
    s.addImage({ path: dark ? LOGO.white : LOGO.orange, x: M, y: 0.42, h: 0.42, w: 1.24, altText: 'BigOrange.Marketing' });
    T(s, footer, { x: M, y: 6.95, w: 8, h: 0.25, fontFace: Hf, fontSize: 7, bold: true, charSpacing: 2, color: dark ? SOFT : MUTE });
    sq(s, 12.02, 7.0, 0.11);
    T(s, String(num).padStart(2, '0'), { x: 12.2, y: 6.92, w: 0.55, h: 0.3, fontFace: Hf, fontSize: 10, bold: true, color: dark ? WH : INK, align: 'right' });
    if (draft) draftBanner(s);
  }

  function draftBanner(s) {
    rect(s, 9.55, 0.42, 3.18, 0.34, O);
    T(s, 'DRAFT · FIGURES PENDING VALIDATION', { x: 9.55, y: 0.42, w: 3.18, h: 0.34, fontFace: Hf, fontSize: 7.5, bold: true, charSpacing: 2, color: WH, align: 'center', valign: 'middle' });
  }

  function head(s, eyebrow, title, titleW = 11.8) {
    T(s, slot(eyebrow, 'eyebrow').toUpperCase(), { x: M, y: 1.12, w: 9, h: 0.26, fontFace: Hf, fontSize: 9, bold: true, charSpacing: 3, color: O });
    T(s, slot(title, 'title'), { x: M, y: 1.4, w: titleW, h: 0.95, fontFace: Hf, fontSize: 30, bold: true, color: s.__dark ? WH : INK });
  }

  function notes(s, text) { if (text) s.addNotes(String(text)); }

  // ---------- blocks ----------
  function coverDark(s, b) {
    rect(s, 9.6, 0, 3.733, 3.6, O); rect(s, 8.95, 3.6, 0.65, 0.65, O);
    s.addImage({ path: LOGO.white, x: M, y: 0.55, h: 0.6, w: 1.775, altText: 'BigOrange.Marketing' });
    T(s, slot(b.eyebrow, 'eyebrow').toUpperCase(), { x: M, y: 2.05, w: 8, h: 0.3, fontFace: Hf, fontSize: 10, bold: true, charSpacing: 4, color: O });
    T(s, slot(b.title, 'title'), { x: M, y: 2.4, w: 8.4, h: 1.9, fontFace: Hf, fontSize: b.titleSize || 46, bold: true, color: WH, charSpacing: -2 });
    T(s, slot(b.sub, 'sub'), { x: M, y: 4.45, w: 7.6, h: 1.0, fontFace: Bf, fontSize: 15, color: REV });
    T(s, slot(b.date, 'date'), { x: M, y: 6.35, w: 5, h: 0.35, fontFace: Hf, fontSize: 11, bold: true, color: WH, charSpacing: 1 });
    T(s, (b.badge || (draft ? 'DRAFT' : 'PRIVATE REVIEW DRAFT')).toUpperCase(), { x: 8.6, y: 6.35, w: 4.13, h: 0.35, fontFace: Hf, fontSize: 8, bold: true, charSpacing: 3, color: SOFT, align: 'right' });
  }

  // Cover with a named client logo zone (CLIENT_LOGO). Fails visibly when logo is not verified.
  function coverClient(s, b) {
    rect(s, 8.55, 0, 4.783, 7.5, PITH);
    s.addImage({ path: LOGO.orange, x: M, y: 0.55, h: 0.6, w: 1.775, altText: 'BigOrange.Marketing' });
    T(s, slot(b.eyebrow, 'eyebrow').toUpperCase(), { x: M, y: 2.05, w: 7.5, h: 0.3, fontFace: Hf, fontSize: 10, bold: true, charSpacing: 4, color: O });
    T(s, slot(b.title, 'title'), { x: M, y: 2.4, w: 7.6, h: 1.9, fontFace: Hf, fontSize: b.titleSize || 40, bold: true, color: INK, charSpacing: -2 });
    T(s, slot(b.sub, 'sub'), { x: M, y: 4.45, w: 7.2, h: 1.0, fontFace: Bf, fontSize: 14, color: INK2 });
    T(s, slot(b.date, 'date'), { x: M, y: 6.35, w: 5, h: 0.35, fontFace: Hf, fontSize: 11, bold: true, color: INK, charSpacing: 1 });
    T(s, 'PREPARED FOR', { x: 9.1, y: 2.6, w: 3.7, h: 0.3, fontFace: Hf, fontSize: 8, bold: true, charSpacing: 3, color: O, align: 'center' });
    const zone = { x: 9.2, y: 3.0, w: 3.5, h: 1.3 };
    const logo = b.clientLogo || {};
    if (logo.path && logo.verified) {
      s.addImage({ path: logo.path, x: zone.x, y: zone.y, w: zone.w, h: zone.h, sizing: { type: 'contain', w: zone.w, h: zone.h }, altText: 'CLIENT_LOGO' });
    } else {
      s.addShape(pres.shapes.RECTANGLE, { x: zone.x, y: zone.y, w: zone.w, h: zone.h, fill: { color: WH }, line: { color: O, width: 1.5, dashType: 'dash' } });
      T(s, '[[CLIENT_LOGO]]\nverified logo required', { x: zone.x, y: zone.y, w: zone.w, h: zone.h, fontFace: Hf, fontSize: 9, bold: true, color: O, align: 'center', valign: 'middle' });
    }
    T(s, slot(b.clientName, 'clientName'), { x: 9.1, y: 4.45, w: 3.7, h: 0.5, fontFace: Hf, fontSize: 16, bold: true, color: INK, align: 'center' });
    T(s, b.clientLine || '', { x: 9.1, y: 4.95, w: 3.7, h: 0.6, fontFace: Bf, fontSize: 11, color: MUTE, align: 'center' });
    sq(s, 12.4, 6.95, 0.33);
  }

  function stat(s, x, y, w, h, v, l, hot = false) {
    const val = slot(v, 'stat'); const size = String(val).length > 4 ? 26 : String(val).length > 3 ? 30 : 40;
    rect(s, x, y, w, h, hot ? O : PITH);
    T(s, val, { x: x + 0.25, y: y + 0.22, w: w - 0.4, h: 0.9, fontFace: Hf, fontSize: size, bold: true, color: hot ? WH : INK, charSpacing: -2 });
    T(s, slot(l, 'label'), { x: x + 0.25, y: y + h - 0.7, w: w - 0.4, h: 0.55, fontFace: Bf, fontSize: 10.5, color: hot ? WH : INK2, valign: 'bottom' });
  }

  function statsRow(s, stats, y = 2.75, h = 2.0, x0 = M, totalW = 6.7) {
    const gap = 0.12; const w = (totalW - gap * (stats.length - 1)) / stats.length;
    stats.forEach((st, i) => stat(s, x0 + i * (w + gap), y, w, h, st.v, st.l, !!st.hot));
  }

  function card(s, x, y, w, h, b, o = {}) {
    const dark = !!o.dark; rect(s, x, y, w, h, dark ? INK : PITH);
    T(s, slot(b.kicker, 'kicker').toUpperCase(), { x: x + 0.3, y: y + 0.28, w: w - 0.6, h: 0.24, fontFace: Hf, fontSize: 8, bold: true, charSpacing: 2.5, color: O });
    T(s, slot(b.title, 'title'), { x: x + 0.3, y: y + 0.55, w: w - 0.6, h: 0.5, fontFace: Hf, fontSize: o.titleSize || 16, bold: true, color: dark ? WH : INK });
    T(s, slot(b.body, 'body'), { x: x + 0.3, y: y + 1.1, w: w - 0.6, h: h - 1.3, fontFace: Bf, fontSize: o.bodySize || 11.5, color: dark ? REV : INK2, paraSpaceAfter: 6 });
  }

  // stats left (up to 4) + card right, optional takeaway line under stats
  function twoUp(s, b) {
    statsRow(s, (b.stats || []).slice(0, 4), 2.75, 2.0, M, 6.7);
    card(s, 7.6, 2.75, 5.13, 3.85, b.card || {}, { dark: b.cardDark !== false, bodySize: 12 });
    if (b.takeaway) T(s, b.takeaway, { x: M, y: 5.0, w: 6.6, h: 1.2, fontFace: Hf, fontSize: 17, bold: true, color: s.__dark ? WH : INK });
  }

  // three column cards, last one dark by default (agreement / offer style)
  function columns(s, b) {
    const items = b.items || []; const gap = 0.2; const w = (CW - gap * (items.length - 1)) / items.length; const y = 2.75, h = 3.7;
    items.forEach((c, i) => { const x = M + i * (w + gap); const hot = c.hot != null ? c.hot : i === items.length - 1;
      rect(s, x, y, w, h, hot ? INK : PITH);
      T(s, slot(c.kicker, 'kicker').toUpperCase(), { x: x + 0.35, y: y + 0.35, w: w - 0.7, h: 0.25, fontFace: Hf, fontSize: 8.5, bold: true, charSpacing: 2.5, color: O });
      T(s, slot(c.big, 'big'), { x: x + 0.35, y: y + 0.7, w: w - 0.7, h: 0.9, fontFace: Hf, fontSize: 30, bold: true, color: hot ? WH : INK, charSpacing: -1 });
      T(s, slot(c.body, 'body'), { x: x + 0.35, y: y + 1.75, w: w - 0.7, h: 1.7, fontFace: Bf, fontSize: 12.5, color: hot ? REV : INK2 });
    });
  }

  // numbered grid of small cards (page contract style)
  function grid(s, b) {
    const items = b.items || []; const cols = b.cols || 5; const rows = Math.ceil(items.length / cols); const gap = 0.15;
    const w = (CW - gap * (cols - 1)) / cols; const h = rows > 2 ? 1.25 : 1.75; const y0 = 2.7;
    items.forEach((it, i) => { const c = i % cols, r = Math.floor(i / cols); const x = M + c * (w + gap), y = y0 + r * (h + 0.2); const hot = !!it.hot;
      rect(s, x, y, w, h, hot ? O : PITH);
      T(s, it.n != null ? it.n : String(i + 1).padStart(2, '0'), { x: x + 0.22, y: y + 0.16, w: 1.2, h: 0.5, fontFace: Hf, fontSize: 20, bold: true, color: hot ? WH : O, charSpacing: -1 });
      T(s, slot(it.title, 'title'), { x: x + 0.22, y: y + 0.66, w: w - 0.4, h: 0.35, fontFace: Hf, fontSize: 12, bold: true, color: hot ? WH : INK });
      T(s, it.body || '', { x: x + 0.22, y: y + 1.0, w: w - 0.4, h: h - 1.08, fontFace: Bf, fontSize: 10, color: hot ? WH : INK2 });
    });
  }

  // horizontal flow of dark steps with orange connectors (process)
  function flow(s, b) {
    const items = b.items || []; const gap = 0.14; const w = (CW - gap * (items.length - 1)) / items.length; const y = 2.75, h = 2.7;
    items.forEach((f, i) => { const x = M + i * (w + gap); const hot = f.hot != null ? f.hot : i === (b.hotIndex != null ? b.hotIndex : -1);
      rect(s, x, y, w, h, hot ? O : (b.light ? PITH : INK));
      const num = hot ? WH : O, ttl = b.light && !hot ? INK : WH, bod = hot ? WH : (b.light ? INK2 : REV);
      T(s, String(i + 1), { x: x + 0.22, y: y + 0.2, w: 1, h: 0.7, fontFace: Hf, fontSize: 30, bold: true, color: num });
      T(s, slot(f.title, 'title').toUpperCase(), { x: x + 0.22, y: y + 1.05, w: w - 0.4, h: 0.3, fontFace: Hf, fontSize: 10, bold: true, charSpacing: 2, color: ttl });
      T(s, f.body || '', { x: x + 0.22, y: y + 1.4, w: w - 0.4, h: 1.1, fontFace: Bf, fontSize: 10.5, color: bod });
      if (i < items.length - 1) sq(s, x + w + 0.02, y + 1.28, 0.1);
    });
    if (b.bar) { rect(s, M, 5.65, CW, 0.75, INK); T(s, b.bar, { x: M + 0.3, y: 5.65, w: CW - 0.6, h: 0.75, fontFace: Hf, fontSize: 13, bold: true, color: WH, valign: 'middle' }); }
    else if (b.takeaway) T(s, b.takeaway, { x: M, y: 5.78, w: CW, h: 0.65, fontFace: Hf, fontSize: 15, bold: true, color: s.__dark ? WH : INK, valign: 'middle' });
  }

  // four phase timeline (first hot)
  function timeline(s, b) {
    const items = b.items || []; const gap = 0.2; const w = (CW - gap * (items.length - 1)) / items.length; const y = 2.75, h = 2.75;
    items.forEach((r, i) => { const x = M + i * (w + gap); const hot = i === 0;
      rect(s, x, y, w, h, hot ? O : PITH);
      T(s, String(i + 1).padStart(2, '0'), { x: x + 0.25, y: y + 0.2, w: 1.5, h: 0.9, fontFace: Hf, fontSize: 40, bold: true, color: hot ? WH : INK, charSpacing: -2 });
      T(s, slot(r.label, 'label').toUpperCase(), { x: x + 0.25, y: y + 1.2, w: w - 0.5, h: 0.3, fontFace: Hf, fontSize: 10, bold: true, charSpacing: 2, color: hot ? WH : O });
      T(s, r.body || '', { x: x + 0.25, y: y + 1.55, w: w - 0.5, h: 1.1, fontFace: Bf, fontSize: 12, color: hot ? WH : INK2 });
    });
    if (b.takeaway) T(s, b.takeaway, { x: M, y: 5.8, w: CW, h: 0.7, fontFace: Hf, fontSize: 14, bold: true, color: s.__dark ? WH : INK, valign: 'middle' });
  }

  // two big numbers + explanation (technical priority style)
  function bigNumbers(s, b) {
    const a = b.items || []; const w = 3.6, gap = 0.25, y = 2.75, h = 3.3;
    a.slice(0, 2).forEach((it, i) => { const x = M + i * (w + gap); const hot = i === 0;
      rect(s, x, y, w, h, hot ? O : INK2);
      T(s, slot(it.v, 'value'), { x: x + 0.25, y: y + 0.2, w: w - 0.4, h: 1.7, fontFace: Hf, fontSize: String(it.v || '').length > 3 ? 64 : 88, bold: true, color: WH, charSpacing: -4 });
      T(s, slot(it.l, 'label'), { x: x + 0.25, y: y + 2.45, w: w - 0.4, h: 0.6, fontFace: Bf, fontSize: 12, color: hot ? WH : SOFT });
    });
    T(s, b.body || '', { x: 8.55, y: 3.0, w: 4.2, h: 3.0, fontFace: Bf, fontSize: 14, color: s.__dark ? REV : INK2 });
  }

  // 2x2 feature grid with icons
  async function features(s, b) {
    const items = (b.items || []).slice(0, 4);
    for (let i = 0; i < items.length; i++) { const c = i % 2, r = Math.floor(i / 2); const x = M + c * 6.15, y = 2.7 + r * 1.98, w = 5.98, h = 1.82;
      rect(s, x, y, w, h, PITH); s.addShape(pres.shapes.OVAL, { x: x + 0.28, y: y + 0.3, w: 0.7, h: 0.7, fill: { color: O }, line: { color: O, width: 0 } });
      const ic = await icon(items[i].icon || 'FiCheck', WH); if (ic) s.addImage({ data: ic, x: x + 0.45, y: y + 0.47, w: 0.36, h: 0.36 });
      T(s, slot(items[i].kicker, 'kicker').toUpperCase(), { x: x + 1.2, y: y + 0.28, w: w - 1.45, h: 0.24, fontFace: Hf, fontSize: 8, bold: true, charSpacing: 2.5, color: O });
      T(s, slot(items[i].title, 'title'), { x: x + 1.2, y: y + 0.52, w: w - 1.45, h: 0.4, fontFace: Hf, fontSize: 15, bold: true, color: INK });
      T(s, items[i].body || '', { x: x + 1.2, y: y + 0.95, w: w - 1.45, h: 0.8, fontFace: Bf, fontSize: 11, color: INK2 });
    }
  }

  // decisions grid (4 per row, last hot) + closing line
  function decisions(s, b) {
    const items = b.items || []; const cols = 4; const gap = 0.2; const w = (CW - gap * (cols - 1)) / cols; const h = 1.4;
    items.forEach((d, i) => { const c = i % cols, r = Math.floor(i / cols); const x = M + c * (w + gap), y = 2.65 + r * (h + 0.15); const hot = i === items.length - 1;
      rect(s, x, y, w, h, hot ? O : (s.__dark ? INK2 : PITH));
      T(s, String(i + 1).padStart(2, '0'), { x: x + 0.22, y: y + 0.15, w: 1, h: 0.5, fontFace: Hf, fontSize: 20, bold: true, color: hot ? WH : O });
      T(s, typeof d === 'string' ? d : slot(d.title, 'title'), { x: x + 0.22, y: y + 0.6, w: w - 0.44, h: 0.75, fontFace: Hf, fontSize: 11.5, bold: true, color: hot || s.__dark ? WH : INK });
    });
    if (b.takeaway) T(s, b.takeaway, { x: M, y: 5.85, w: CW, h: 0.7, fontFace: Bf, fontSize: 14, color: s.__dark ? REV : INK2, valign: 'middle' });
  }

  // title + intro paragraph + bullet list (left) + optional side card
  function textBullets(s, b) {
    const hasCard = !!b.card; const w = hasCard ? 7.0 : CW;
    if (b.intro) T(s, b.intro, { x: M, y: 2.7, w, h: 1.0, fontFace: Bf, fontSize: 14, color: s.__dark ? REV : INK2 });
    const items = (b.bullets || []).map((t, i) => ({ text: String(t), options: { bullet: { code: '25A0' }, breakLine: i < (b.bullets.length - 1), paraSpaceAfter: 8, color: s.__dark ? WH : INK } }));
    if (items.length) s.addText(items, { isTextBox: true, x: M, y: b.intro ? 3.75 : 2.7, w, h: 2.9, fontFace: Bf, fontSize: 13, valign: 'top', margin: 0.05 });
    if (hasCard) card(s, 7.9, 2.7, 4.83, 3.9, b.card, { dark: true, bodySize: 12 });
  }

  // native table
  function table(s, b) {
    const rows = [];
    if (b.header) rows.push(b.header.map(h => ({ text: String(h).toUpperCase(), options: { bold: true, color: O, fontFace: Hf, fontSize: 8, fill: { color: WH }, charSpacing: 2, border: [{ type: 'none' }, { type: 'none' }, { pt: 1.5, color: INK }, { type: 'none' }] } })));
    (b.rows || []).forEach(r => rows.push(r.map((c, ci) => ({ text: String(c), options: { fontFace: Bf, fontSize: 11, bold: ci === 0, color: INK, fill: { color: WH }, border: [{ type: 'none' }, { type: 'none' }, { pt: 0.75, color: TOKENS.line }, { type: 'none' }] } }))));
    s.addTable(rows, { x: M, y: 2.7, w: CW, colW: b.colW, rowH: 0.42, margin: 0.08, autoPage: false });
    if (b.takeaway) T(s, b.takeaway, { x: M, y: 6.0, w: CW, h: 0.6, fontFace: Hf, fontSize: 13, bold: true, color: INK, valign: 'middle' });
  }

  // native chart (line/bar) with tokens
  function chart(s, b) {
    const type = b.type === 'line' ? pres.charts.LINE : pres.charts.BAR;
    const data = (b.series || []).map(se => ({ name: se.name, labels: b.labels || [], values: se.values || [] }));
    s.addChart(type, data, { x: M, y: 2.7, w: 7.6, h: 3.8, chartColors: [O, INK, TOKENS.mute, TOKENS.leaf], showTitle: !!b.chartTitle, title: b.chartTitle, titleFontFace: Hf, titleFontSize: 12,
      showValue: true, dataLabelPosition: b.type === 'line' ? 't' : 'outEnd', dataLabelFontSize: 9, catAxisLabelColor: MUTE, valAxisLabelColor: MUTE, valGridLine: { color: TOKENS.line, size: 0.5 }, catGridLine: { style: 'none' }, showLegend: data.length > 1, legendPos: 'b', barGapWidthPct: 60 });
    if (b.card) card(s, 8.5, 2.7, 4.23, 3.8, b.card, { dark: true, bodySize: 11.5 });
  }

  function closeDark(s, b) {
    rect(s, M, 2.7, CW, 3.55, INK2);
    T(s, slot(b.title, 'title'), { x: M + 0.4, y: 3.0, w: 7.8, h: 1.2, fontFace: Hf, fontSize: 28, bold: true, color: WH, charSpacing: -1 });
    T(s, b.body || '', { x: M + 0.4, y: 4.2, w: 7.8, h: 1.3, fontFace: Bf, fontSize: 14, color: REV });
    T(s, slot(b.cta, 'cta'), { x: M + 0.4, y: 5.45, w: 7.8, h: 0.5, fontFace: Hf, fontSize: 13, bold: true, color: O });
    T(s, b.contact || '', { x: 9.2, y: 3.0, w: 3.2, h: 2.6, fontFace: Bf, fontSize: 12, color: REV, align: 'right' });
    sq(s, 12.05, 5.7, 0.33);
  }

  async function write(file) { await pres.writeFile({ fileName: file }); return file; }

  return { pres, TOKENS, LOGO, T, rect, sq, icon, slide, chrome, draftBanner, head, notes, coverDark, coverClient, stat, statsRow, card, twoUp, columns, grid, flow, timeline, bigNumbers, features, decisions, textBullets, table, chart, closeDark, write, get count() { return n; } };
}

module.exports = { create, TOKENS, LOGO, W, H, M, CW };
