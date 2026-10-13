/* Verify the actual hosted origin, storage, MP3 playback and offline cache. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');
const root = path.resolve(__dirname, '..');
const version = fs.readFileSync(path.join(root, 'VERSION'), 'utf8').trim();
const url = process.env.PAROLA_URL || 'https://florame-ai.github.io/parola-mahjong/';
const checks = [], errors = [];
function passed(check, details = {}) { checks.push({check, passed: true, ...details}); console.log('PASS', check, JSON.stringify(details)); }
(async () => {
 const browser = await chromium.launch({headless: true, args: ['--autoplay-policy=no-user-gesture-required']});
 try {
  const context = await browser.newContext({viewport: {width: 1360, height: 950}, acceptDownloads: true, reducedMotion: 'reduce'});
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => {if (m.type() === 'error') errors.push(m.text());});
  const response = await page.goto(url);
  assert.equal(response.status(), 200);
  await page.waitForFunction(() => !!window.Parola);
  assert.equal(await page.locator('meta[name="application-version"]').getAttribute('content'), version);
  assert.equal(await page.locator('.unitcard').count(), 24);
  assert.equal(await page.locator('a[href="./changelog.html"]').count(), 1);
  await page.evaluate(() => Parola.intro('identity', 'write'));
  assert.equal(await page.locator('.mode-card').count(), 5);
  passed('hosted boot, release version, 24 units and five modes');
  for (const lang of ['it', 'en', 'ru']) {
   assert.equal(await page.evaluate(async lang => {
    const item = Parola.data.items.find(i => i.id === 'greetings_0');
    return Parola.player.speak(lang, item.text[lang], {context: item.id});
   }, lang), true);
   passed('actual MP3 playback', {language: lang});
  }
  await page.evaluate(() => {
   Parola.player.speak = async () => false;
   Parola.setRoute('en', 'it', 'it'); Parola.intro('identity', 'write'); Parola.start();
  });
  const saved = await page.evaluate(() => Parola.state.game);
  await page.reload(); await page.waitForFunction(() => !!window.Parola);
  await page.locator('[data-action="resume"]').click();
  assert.equal(await page.evaluate(() => Parola.state.game.id), saved.id);
  passed('real localStorage keeps the active game after reload');
  await page.evaluate(() => localStorage.setItem('parola-mahjong-v6', '{corrupt'));
  await page.reload(); await page.waitForFunction(() => !!window.Parola);
  await page.locator('[data-action="resume"]').click();
  assert.equal(await page.evaluate(() => Parola.state.game.id), saved.id);
  passed('real browser storage recovers a corrupt primary from backup');
  await page.evaluate(() => {
   Parola.player.speak = async () => false;
   Parola.nav('settings');
   const cb = document.querySelector('[data-setting="effects"]');
   cb.checked = false; cb.dispatchEvent(new Event('change', {bubbles: true}));
  });
  for (const target of ['it', 'en', 'ar', 'ru']) for (const support of ['it', 'en', 'ar', 'ru']) {
   if (support === target) continue;
   const pairs = await page.evaluate(({target, support}) => {
    Parola.setRoute(support, target, support); Parola.intro('identity', 'write'); Parola.start();
    let moves = 0;
    while (Parola.state.view === 'game' && moves++ < 40) {
     const g = Parola.state.game;
     const free = g.board.filter(t => !t.gone && document.querySelector(`.tile[data-id="${t.id}"]`).dataset.free === 'true');
     let pair;
     for (const x of free) for (const y of free) if (x.type === 'target' && y.type === 'support' && x.pairKey === y.pairKey) pair = [x, y];
     if (!pair) throw Error('No free pair');
     const [x, y] = pair;
     if (!g.revealed.includes(x.itemId)) {
      Parola.pick(x.id);
      document.querySelector('#write-answer').value = [...Parola.data.items, ...Parola.data.vocab].find(i => i.id === x.itemId).text[target];
      Parola.checkWrite();
     }
     Parola.pick(x.id); Parola.pick(y.id);
    }
    if (Parola.state.view !== 'summary' || Parola.state.lastSummary.errors) throw Error('Writing game incomplete or incorrect');
    return Parola.state.lastSummary.completed.length;
   }, {target, support});
   assert.equal(pairs, 6); passed('complete writing game', {target, support, pairs});
  }
  await page.setViewportSize({width: 390, height: 844});
  for (const ui of ['it', 'en', 'ar', 'ru']) {
   const layout = await page.evaluate(ui => {
    Parola.setRoute('en', 'it', ui); Parola.intro('identity', 'write'); Parola.start();
    return {lang: document.documentElement.lang, dir: document.documentElement.dir, width: document.body.scrollWidth, viewport: innerWidth};
   }, ui);
   assert.equal(layout.lang, ui); assert.equal(layout.dir, ui === 'ar' ? 'rtl' : 'ltr');
   assert.ok(layout.width <= layout.viewport + 1); passed('mobile layout and language', {ui});
  }
  await page.evaluate(() => {document.querySelectorAll('.toast').forEach(e => e.remove());});
  await page.screenshot({path: path.join(root, `docs/pages-mobile-${version}.png`), fullPage: true});
  await page.setViewportSize({width: 1360, height: 950});
  await page.evaluate(() => {Parola.setRoute('en', 'it', 'it'); Parola.nav('home');});
  await page.screenshot({path: path.join(root, `docs/pages-desktop-${version}.png`), fullPage: true});
  await page.evaluate(() => navigator.serviceWorker.ready);
  await page.waitForFunction(() => navigator.serviceWorker.controller !== null);
  assert.ok((await page.evaluate(() => caches.keys())).some(k => k.endsWith(version)));
  await context.setOffline(true);
  await page.reload(); await page.waitForFunction(() => !!window.Parola);
  assert.equal(await page.evaluate(() => Parola.state.store.version), 6);
  assert.equal(await page.evaluate(() => Parola.player.speak('it', 'Ciao!', {context: 'greetings_0'})), true);
  passed('offline reload and actual embedded MP3 playback');
  await page.locator('a[href="./changelog.html"]').click();
  assert.ok((await page.locator('h2').first().textContent()).includes(version));
  passed('public changelog accessible offline');
  assert.deepEqual(errors, []);
  passed('no JavaScript errors or missing translations');
  const report = {version, url, checks: checks.length, storage: 'real browser localStorage', offline: true, audioTested: ['it', 'en', 'ru'], arabicAudioIncluded: false, errors, results: checks};
  fs.writeFileSync(path.join(root, `docs/pages-verification-${version}.json`), JSON.stringify(report, null, 2) + '\n');
  console.log('TOTAL', checks.length);
 } finally {await browser.close();}
})().catch(e => {console.error(e); process.exitCode = 1;});
