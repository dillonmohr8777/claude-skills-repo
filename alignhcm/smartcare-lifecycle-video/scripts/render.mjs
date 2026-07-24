#!/usr/bin/env node
/* Deterministic frame capture for the SmartCare sizzle.
 * Drives window.seek(t) in Chromium (Playwright) and pipes PNG frames
 * straight into ffmpeg (image2pipe) -> H.264 mp4 (video only, no disk frame dump).
 *
 *   node render.mjs                     full render -> output/video_raw.mp4
 *   node render.mjs --fps 15            faster proof render
 *   node render.mjs --range 16:26       render only t=16..26s
 *   node render.mjs --stills 0.6,8,20,30,44,58   save PNG stills for inspection
 */
import { spawn, execSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import { mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
// resolve the globally-installed Playwright (ESM doesn't honour NODE_PATH)
const require = createRequire(import.meta.url);
const GLOBAL_ROOT = (process.env.NODE_PATH || execSync('npm root -g').toString().trim());
const { chromium } = require(resolve(GLOBAL_ROOT, 'playwright'));

const __dir = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dir, '..');
const HTML = 'file://' + resolve(ROOT, 'src/video.html');
const OUT = resolve(ROOT, 'output');
const W = 1920, H = 1080;

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const FPS = parseInt(opt('--fps', '30'), 10);
const JPEG = opt('--jpeg', null);            // e.g. --jpeg 96  -> capture jpeg q96 (faster)
const OUTFILE = resolve(OUT, opt('--out', 'video_raw.mp4'));
const stills = opt('--stills', null);
const range = opt('--range', null);
const FFMPEG = execSync('python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"').toString().trim();

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function main() {
  mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--disable-lcd-text', '--hide-scrollbars'] });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.goto(HTML, { waitUntil: 'load' });
  await page.waitForFunction('window.__ready === true', { timeout: 30000 });
  const DUR = await page.evaluate('window.DURATION');

  if (stills) {
    const dir = resolve(OUT, 'stills'); mkdirSync(dir, { recursive: true });
    for (const s of stills.split(',').map(Number)) {
      await page.evaluate(t => window.seek(t), s);
      await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
      const name = `t_${s.toFixed(2).replace('.', '_')}.png`;
      await page.screenshot({ path: resolve(dir, name) });
      console.log('still', name);
    }
    await browser.close(); return;
  }

  let t0 = 0, t1 = DUR;
  if (range) { const [a, b] = range.split(':').map(Number); t0 = a; t1 = b; }
  const nFrames = Math.round((t1 - t0) * FPS);
  console.log(`rendering ${nFrames} frames @ ${FPS}fps  (${t0}..${t1}s)  ffmpeg=${FFMPEG}`);

  const ff = spawn(FFMPEG, [
    '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', 'pipe:0',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '16',
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUTFILE,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });

  let ffErr = null;
  ff.stdin.on('error', e => { ffErr = e; });
  const write = buf => new Promise((res, rej) => {
    if (ffErr) return rej(ffErr);
    if (ff.stdin.write(buf)) res(); else ff.stdin.once('drain', res);
  });

  const start = Date.now();
  for (let i = 0; i < nFrames; i++) {
    const t = t0 + i / FPS;
    // seek + one rAF flush in a single round-trip
    await page.evaluate(tt => { window.seek(tt); return new Promise(r => requestAnimationFrame(r)); }, t);
    const buf = JPEG
      ? await page.screenshot({ type: 'jpeg', quality: parseInt(JPEG, 10) })
      : await page.screenshot({ type: 'png' });
    await write(buf);
    if (i % 60 === 0) {
      const pct = ((i / nFrames) * 100).toFixed(1);
      const fps = (i / ((Date.now() - start) / 1000) || 0).toFixed(1);
      console.log(`  ${pct}%  frame ${i}/${nFrames}  (${fps} cap-fps)`);
    }
  }
  ff.stdin.end();
  await new Promise((res, rej) => { ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg exit ' + c))); });
  await browser.close();
  console.log('done ->', OUTFILE, `(${((Date.now() - start) / 1000).toFixed(0)}s)`);
}
main().catch(e => { console.error(e); process.exit(1); });
