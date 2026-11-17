// Frame-accurate render: scene.html -> PNG frames -> ffmpeg (H.264 1080x1920 30fps) + mix.wav
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const FPS = 30, DUR = 30, FROM = +(process.env.FROM || 0), TO = +(process.env.TO || DUR);
const OUT = process.env.OUT || 'build/video_silent.mp4';
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.addInitScript(() => { window.__RENDER__ = true; });
  await page.goto('file://' + path.resolve('scene.html'));
  await page.evaluate(() => document.fonts.ready);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', OUT], { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.round((TO - FROM) * FPS);
  for (let i = 0; i < total; i++) {
    const f = Math.round(FROM * FPS) + i;
    await page.evaluate(([t, f]) => renderAt(t, f), [f / FPS, f]);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log(`frame ${i}/${total}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
})();
