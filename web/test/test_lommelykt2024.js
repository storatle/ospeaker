#!/usr/bin/env node
/*
 * Test av Poengløp v2.12 mot Lommelyktløpet 2024 (løp 57) i den lokale Brikkesys-databasen.
 *
 * Testen lager en kopi av løpet, «TEST Lommelyktløpet 2024», med klassene, løypa og postene fra løp 57.
 * Løp 57 endres aldri. Bare rader med løps-ID-en til kopien skrives eller slettes.
 *
 *   Scenario 1: ingen deltakere er registrert, bare løyper og poster.
 *   Scenario 2: alle deltakerne er registrert og ute i skogen. Så kommer de i mål og blir registrert
 *               én og én (i samme rekkefølge som i 2024). Resultatene leses og kontrolleres etter hver.
 *
 * Til slutt sammenlignes resultatlista for kopien med resultatlista for det ekte løp 57.
 * Poengene regnes med koden fra Poenglop_v2.12.html og poengoppsettet i poeng-data/race-57.json.
 *
 * Start:  node web/test/test_lommelykt2024.js [--live] [--pause SEK] [--keep]
 *   --live       følg testen i nettleseren: åpner testløpet i Poengløp med automatisk oppdatering hvert 5. sek,
 *                venter på Enter før deltakerne registreres og før testløpet slettes, og har 10 sek pause
 *                mellom hver målgang. Innstillingen for automatisk oppdatering settes tilbake etterpå.
 *   --pause SEK  venter SEK sekunder mellom hver målgang
 *   --keep       lar testløpet stå i databasen etterpå (ellers slettes det)
 *
 * Bruker Poengløp på http://127.0.0.1:8090 hvis den kjører, ellers startes en egen server.
 * Tilkoblingen til MySQL hentes fra poeng-config.json og kan overstyres med POENG_DB_USER/POENG_DB_PASSWORD.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { spawn } = require('child_process');

const APP_DIR = path.join(__dirname, '..', 'Poenglop_v2.12');
const mysql = require(path.join(APP_DIR, 'node_modules', 'mysql2', 'promise'));

const SOURCE_RACE = 57;
const TEST_NAME = 'TEST Lommelyktløpet 2024';
const args = process.argv.slice(2);
const LIVE = args.includes('--live');
const PAUSE = args.includes('--pause') ? Number(args[args.indexOf('--pause') + 1]) * 1000 || 0 : LIVE ? 10000 : 0;
const KEEP = args.includes('--keep');
const LIVE_REFRESH_SEC = 5;

const appConfig = JSON.parse(fs.readFileSync(path.join(APP_DIR, 'poeng-config.json'), 'utf8'));
const PORT = appConfig.server?.port || 8090;
const BASE = `http://127.0.0.1:${PORT}`;
const sleep = ms => new Promise(r => setTimeout(r, ms));

// Venter på Enter i live-modus. Uten terminal (f.eks. i en pipe) ventes det ikke.
function waitEnter(text) {
  if (!LIVE || !process.stdin.isTTY) return Promise.resolve();
  process.stdout.write(`\n  ▶ ${text} – trykk Enter for å fortsette `);
  return new Promise(resolve => process.stdin.once('data', () => { process.stdin.pause(); resolve(); }).resume());
}
function openBrowser(url) {
  const cmd = process.platform === 'win32' ? 'cmd' : process.platform === 'darwin' ? 'open' : 'xdg-open';
  const a = process.platform === 'win32' ? ['/c', 'start', '', url] : [url];
  spawn(cmd, a, { stdio: 'ignore', detached: true }).on('error', () => {}).unref();
}

// ---------------------------------------------------------------------------
// Små hjelpere for kontroller og utskrift
// ---------------------------------------------------------------------------
let passed = 0, failed = 0;
function check(ok, text) {
  if (ok) { passed++; console.log('  ✓ ' + text); }
  else { failed++; console.log('  ✗ ' + text); }
}
function eq(actual, expected, text) {
  const a = JSON.stringify(actual), e = JSON.stringify(expected);
  check(a === e, a === e ? text : `${text} (fikk ${a}, ventet ${e})`);
}

// ---------------------------------------------------------------------------
// Poengberegningen fra appen: skriptet i Poenglop_v2.12.html kjøres i en sandkasse uten nettleser
// ---------------------------------------------------------------------------
function loadAppLogic() {
  const html = fs.readFileSync(path.join(APP_DIR, 'Poenglop_v2.12.html'), 'utf8');
  const start = html.lastIndexOf('<script>'), end = html.lastIndexOf('</script>');
  const code = html.slice(start + '<script>'.length, end).replace(/\binit\(\);\s*$/, '')
    + '\nglobalThis.__app = { S, normalize, recalc, ranked, groups, isOut, isFinished, defaultSettings, fmt };';
  const ctx = { location: { search: '', protocol: 'file:' }, URLSearchParams, document: {}, console };
  vm.createContext(ctx);
  vm.runInContext(code, ctx);
  return ctx.__app;
}
const app = loadAppLogic();

// Samme som loadRace() i appen, uten tegning
function calculate(raceData, settings, race) {
  const { S } = app;
  S.races = [race]; S.raceId = race.race_id; S.sort = 'time';
  S.data = app.normalize(raceData);
  S.settings = Object.assign(app.defaultSettings(), JSON.parse(JSON.stringify(settings)));
  S.settings.overtime = Object.assign(app.defaultSettings().overtime, S.settings.overtime || {});
  app.recalc();
  const list = app.groups('course').flatMap(g => app.ranked(g.rows));
  return {
    results: list,
    finished: S.data.runners.filter(app.isFinished),
    out: S.data.runners.filter(app.isOut),
    classFinish: S.data.classFinish
  };
}
const summary = x => ({ name: x.r.name, cls: x.r.cls, rank: x.rank, rt: x.rt, controls: x.nControls, points: x.totalPts, total: x.totalSec });

function printResults(list) {
  for (const x of list.filter(y => y.counted)) {
    console.log(`      ${String(x.rank).padStart(2)}. ${x.r.name.padEnd(30)} ${x.r.cls.padEnd(9)} ${app.fmt(x.rt).padStart(6)}  ${String(x.nControls).padStart(2)} poster  ${String(x.totalPts).padStart(5)} poeng  totaltid ${app.fmt(x.totalSec)}`);
  }
}

// ---------------------------------------------------------------------------
// Poengløp-serveren
// ---------------------------------------------------------------------------
async function api(p, body) {
  const res = await fetch(BASE + p, body === undefined ? {} : { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Poenglop': '1' }, body: JSON.stringify(body) });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'HTTP ' + res.status);
  return data;
}
async function ensureServer() {
  try { await api('/api/status'); console.log(`Bruker Poengløp som kjører på ${BASE}`); return null; } catch (e) { /* starter egen */ }
  console.log(`Starter Poengløp på ${BASE}`);
  const child = spawn(process.execPath, [path.join(APP_DIR, 'Poenglop_v2.12_server.js'), '--no-browser'], { cwd: APP_DIR, stdio: 'ignore' });
  for (let i = 0; i < 50; i++) {
    await sleep(200);
    try { const s = await api('/api/status'); if (s.connected) return child; } catch (e) { /* venter */ }
  }
  child.kill();
  throw new Error('Poengløp startet ikke');
}

// ---------------------------------------------------------------------------
// Databasen
// ---------------------------------------------------------------------------
async function connect() {
  const c = appConfig.brikkesysDb || {};
  const host = c.host || '127.0.0.1';
  // Testen skriver i databasen. Den skal aldri kjøre mot løps-PC-en.
  if (!['127.0.0.1', 'localhost', '::1'].includes(host)) throw new Error(`Testen kjører bare mot lokal database, ikke ${host}`);
  return mysql.createConnection({
    host, port: c.port || 3306, database: c.database || 'resultatdatabase', charset: c.charset || 'utf8mb4',
    user: process.env.POENG_DB_USER || c.user || 'root', password: process.env.POENG_DB_PASSWORD ?? c.password ?? '',
    dateStrings: true
  });
}

async function deleteTestRaces(db) {
  const [rows] = await db.query('SELECT id FROM races WHERE name = ?', [TEST_NAME]);
  for (const { id } of rows) {
    if (id === SOURCE_RACE) throw new Error('Testløpet har samme ID som løp ' + SOURCE_RACE);
    for (const t of ['controltimes', 'names', 'classcource', 'classes']) await db.query(`DELETE FROM ${t} WHERE raceid = ?`, [id]);
    await db.query('DELETE FROM races WHERE id = ?', [id]);
    const f = path.join(APP_DIR, 'poeng-data', `race-${id}.json`);
    if (fs.existsSync(f)) fs.unlinkSync(f);
  }
}

// Kopierer løpet med klasser, løyper og postkoder, men uten deltakere. Gir kart fra gamle til nye klasse-ID-er.
async function createTestRace(db) {
  const [[src]] = await db.query('SELECT * FROM races WHERE id = ?', [SOURCE_RACE]);
  if (!src) throw new Error('Fant ikke løp ' + SOURCE_RACE);
  const [r] = await db.query('INSERT INTO races (name, racedate, timecalculation, use_as_database) VALUES (?, ?, ?, ?)',
    [TEST_NAME, src.racedate, src.timecalculation, src.use_as_database]);
  const raceId = r.insertId;

  const classMap = new Map();
  const [classes] = await db.query('SELECT * FROM classes WHERE raceid = ? ORDER BY id', [SOURCE_RACE]);
  for (const c of classes) {
    const { id, changed, ...rest } = c;
    rest.raceid = raceId;
    const [ins] = await db.query('INSERT INTO classes SET ?', [rest]);
    classMap.set(id, ins.insertId);
  }
  const [cc] = await db.query('SELECT * FROM classcource WHERE raceid = ?', [SOURCE_RACE]);
  for (const x of cc) {
    const { id, ...rest } = x;
    await db.query('INSERT INTO classcource SET ?', [{ ...rest, raceid: raceId, classid: classMap.get(x.classid) ?? x.classid, courceid: classMap.get(x.courceid) ?? x.courceid }]);
  }
  // Samme poengoppsett som løp 57, så resultatene kan følges i nettleseren
  const settingsFile = path.join(APP_DIR, 'poeng-data', `race-${SOURCE_RACE}.json`);
  fs.copyFileSync(settingsFile, path.join(APP_DIR, 'poeng-data', `race-${raceId}.json`));
  return { raceId, classMap, race: { race_id: String(raceId), race_name: TEST_NAME, race_date: src.racedate } };
}

// Felt som Brikkesys fyller ut når brikka leses ut i mål
const FINISH_FIELDS = ['time', 'milliseconds', 'status', 'codesandtimes', 'intime', 'readtime', 'nulltime', 'codes', 'points', 'dsqreason', 'timecalculation'];

// ---------------------------------------------------------------------------
// Testen
// ---------------------------------------------------------------------------
async function main() {
  const settings = JSON.parse(fs.readFileSync(path.join(APP_DIR, 'poeng-data', `race-${SOURCE_RACE}.json`), 'utf8'));
  const db = await connect();
  const server = await ensureServer();
  let test = null, savedRefresh = null;
  try {
    await deleteTestRaces(db);   // rester fra en avbrutt kjøring
    const [source] = await db.query('SELECT * FROM names WHERE raceid = ? ORDER BY readtime, id', [SOURCE_RACE]);
    const [[course]] = await db.query('SELECT codes FROM classes WHERE raceid = ? AND cource = 1', [SOURCE_RACE]);
    const [srcClasses] = await db.query('SELECT name FROM classes WHERE raceid = ? AND cource = 0', [SOURCE_RACE]);
    const finishCode = course.codes.trim().split(/\s+/).pop();

    // Fasit: det ekte løp 57 lest gjennom Poengløp
    const srcRace = (await api('/api/races')).find(x => String(x.race_id) === String(SOURCE_RACE));
    const fasit = calculate(await api('/api/race?id=' + SOURCE_RACE), settings, srcRace);
    console.log(`\nFasit fra løp ${SOURCE_RACE}: ${source.length} deltakere, ${fasit.finished.length} i mål`);

    // ----- Scenario 1 -----
    console.log('\nScenario 1: løyper og poster, ingen deltakere');
    test = await createTestRace(db);
    const races = await api('/api/races');
    check(races.some(x => String(x.race_id) === test.race.race_id && x.race_name === TEST_NAME), `«${TEST_NAME}» (løp ${test.raceId}) vises i lista over løp`);
    let data = await api('/api/race?id=' + test.raceId);
    eq(data.runners.length, 0, 'ingen deltakere');
    eq(data.punches.length, 0, 'ingen stemplinger');
    eq(data.warnings, [], 'ingen advarsler');
    eq([...data.classNames].sort(), srcClasses.map(c => c.name).sort(), `alle ${srcClasses.length} klassene vises`);
    const courseRow = data.classCodes.find(c => c.is_course);
    eq(courseRow?.codes, course.codes, 'løypa har postene og målposten');
    let calc = calculate(data, settings, test.race);
    eq(calc.results.length, 0, 'resultatlista er tom');
    eq(Object.values(calc.classFinish).every(f => f === finishCode), true, `målpost ${finishCode} for alle klassene`);

    if (LIVE) {
      // Siden leser innstillingen for automatisk oppdatering når den åpnes, så den settes før nettleseren åpnes
      savedRefresh = (await api('/api/apiconfig')).autoRefresh;
      await api('/api/refresh', { enabled: true, seconds: LIVE_REFRESH_SEC });
      const url = `${BASE}/#${test.raceId}`;
      console.log(`\n  Åpner ${url} i nettleseren (automatisk oppdatering hvert ${LIVE_REFRESH_SEC}. sek)`);
      openBrowser(url);
      await waitEnter('Testløpet uten deltakere vises');
    }

    // ----- Scenario 2 -----
    console.log(`\nScenario 2: ${source.length} deltakere registrert og ute`);
    const ids = new Map();
    for (const s of source) {
      const { id, changed, ...rest } = s;
      for (const f of FINISH_FIELDS) rest[f] = null;
      rest.status = 'I';
      rest.raceid = test.raceId;
      rest.classid = test.classMap.get(s.classid) ?? s.classid;
      rest.courceid = s.courceid === null ? null : test.classMap.get(s.courceid) ?? s.courceid;
      const [ins] = await db.query('INSERT INTO names SET ?', [rest]);
      ids.set(id, ins.insertId);
    }
    data = await api('/api/race?id=' + test.raceId);
    calc = calculate(data, settings, test.race);
    eq(data.runners.length, source.length, `${source.length} deltakere registrert`);
    eq(calc.out.length, source.length, 'alle er ute');
    eq(calc.finished.length, 0, 'ingen i mål');
    eq(calc.results.filter(x => x.counted).length, 0, 'ingen i resultatlista');
    eq(data.runners.every(r => r.course_name === 'PoengO-course'), true, 'alle har løypa PoengO-course fra klassen');
    await waitEnter(`Alle ${source.length} er ute. Deretter kommer én i mål hvert ${PAUSE / 1000}. sek`);

    const fasitBy = new Map(fasit.results.map(x => [x.r.name, x]));
    for (const [i, s] of source.entries()) {
      if (PAUSE) await sleep(PAUSE);
      const n = i + 1;
      const update = Object.fromEntries(FINISH_FIELDS.map(f => [f, s[f]]));
      await db.query('UPDATE names SET ? WHERE id = ? AND raceid = ?', [update, ids.get(s.id), test.raceId]);

      data = await api('/api/race?id=' + test.raceId);
      calc = calculate(data, settings, test.race);
      const me = calc.results.find(x => x.r.name === s.name), want = fasitBy.get(s.name);
      console.log(`\n  ${n}/${source.length} i mål: ${s.name} (${calc.results.find(x => x.r.name === s.name)?.r.cls}) kl. ${String(s.intime).slice(11)}, registrert ${String(s.readtime).slice(11)}`);
      eq(calc.finished.length, n, `${n} i mål`);
      eq(calc.out.length, source.length - n, `${source.length - n} ute`);
      eq(calc.results.filter(x => x.counted).length, n, `${n} i resultatlista`);
      check(me?.counted, `${s.name} er med i resultatlista`);
      eq(me?.rt, want.rt, 'løpstid som i løp 57');
      eq(me?.controls.map(c => c.code), want.controls.map(c => c.code), 'postene som i løp 57');
      eq(me?.controlPts, want.controlPts, 'postpoeng som i løp 57');
      eq(me?.params.filter(p => p.name === 'Klassebonus').map(p => p.pts), want.params.filter(p => p.name === 'Klassebonus').map(p => p.pts), 'klassebonus som i løp 57');
      eq(me?.overPts, want.overPts, 'poengtrekk for overtid som i løp 57');
      printResults(calc.results);
    }

    // ----- Sluttkontroll -----
    console.log('\nSluttkontroll: resultatlista for testløpet er lik den for løp ' + SOURCE_RACE);
    eq(calc.results.map(summary), fasit.results.map(summary), 'samme plass, tid, poster, poeng og totaltid for alle');
    eq(data.punches.length, (await api('/api/race?id=' + SOURCE_RACE)).punches.length, 'like mange stemplinger');
    await waitEnter(KEEP ? 'Ferdig' : 'Ferdig. Testløpet slettes');
  } finally {
    if (savedRefresh) await api('/api/refresh', savedRefresh).catch(() => {});
    if (test && !KEEP) await deleteTestRaces(db);
    else if (test) console.log(`\nTestløpet står i databasen som løp ${test.raceId}. Slettes ved neste kjøring.`);
    await db.end();
    if (server) server.kill();
  }
  console.log(`\n${passed} kontroller bestått, ${failed} feilet`);
  process.exitCode = failed ? 1 : 0;
}

main().catch(e => { console.error('\nTesten stoppet: ' + e.message); process.exitCode = 2; });
