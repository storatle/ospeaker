#!/usr/bin/env node
/*
 * Poengløp v2.12 – lokal server for Poengløp-appen
 *
 * Henter data fra Brikkesys (MySQL) på en av to måter, valgt med brikkesysDb.mode i poeng-config.json:
 *   direct – Poengløp leser MySQL direkte med mysql2 (kun SELECT)
 *   api    – gjennom Poengløp Brikkesys-API (standard lesegrensesnitt)
 *   auto   – direkte hvis mysql2 og brukernavn finnes, ellers API (standard)
 * mysql2 hentes fra node_modules i Poengløp-mappen eller i API-mappen ved siden av.
 * Mangler brukernavn i poeng-config.json, brukes tilkoblingen fra API-mappens poeng-brikkesys-config.json.
 * I API-modus startes API-et automatisk fra mappen ved siden av Poeng
 * (f.eks. C:\Poenglop\Poenglop_BrikkesysAPI_v1.4) eller fra mappen angitt i poeng-config.json.
 *
 * Start:   node Poenglop_v2.12_server.js          (Brikkesys direkte eller via API)
 *          node Poenglop_v2.12_server.js --demo   (demodata, ingen database)
 * Åpne:    http://127.0.0.1:8090
 */
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn, exec } = require('child_process');

const VERSION = '2.12';
const DIR = __dirname;
const CONFIG_FILE = path.join(DIR, 'poeng-config.json');
const DATA_DIR = path.join(DIR, 'poeng-data');
const DEMO = process.argv.includes('--demo');
const NO_BROWSER = process.argv.includes('--no-browser');

// ---------------------------------------------------------------------------
// Konfigurasjon
// ---------------------------------------------------------------------------
// «mapping» forteller hvilke tabeller og kolonner i Brikkesys som brukes.
// Standardverdiene er et utgangspunkt og må kontrolleres mot struktur.md fra API-eksporten.
const DEFAULT_CONFIG = {
  server: { host: '127.0.0.1', port: 8090 },
  brikkesysApi: { url: 'http://127.0.0.1:8091', folder: '', autoStart: true },
  // Direkte tilkobling til MySQL. Tom user = bruk tilkoblingen fra API-mappens poeng-brikkesys-config.json.
  brikkesysDb: { mode: 'auto', host: '127.0.0.1', port: 3306, user: '', password: '', database: 'resultatdatabase', charset: 'utf8mb4' },
  timeDivisor: 1,
  autoRefresh: { enabled: false, seconds: 30 },
  testData: { hide: false },
  mapping: {
    // Tabellnavn bekreftet av bruker: races, names, controltimes, classes. controltimes.controlcode og classes.codes
    // er bekreftet. Øvrige kolonnenavn er antatt og kan rettes med «Finn tabeller automatisk».
    races: { table: 'races', id: 'id', name: 'name', date: 'racedate' },
    runners: { table: 'names', race: 'raceid', id: 'id', name: 'name', club: 'club', cls: 'class', course: 'cource', ecard: 'ecardno', time: 'times', status: 'status', birth: '', regTime: '', start: '' },
    punches: { table: 'controltimes', race: '', link: 'iid', linkTo: 'id', code: 'controlcode', time: 'mintime' },
    classCodes: { table: 'classes', race: 'raceid', id: 'id', cls: 'class', course: 'course', codes: 'codes' }
  }
};

function deepMerge(base, extra) {
  const out = { ...base };
  for (const k of Object.keys(extra || {})) {
    out[k] = extra[k] && typeof extra[k] === 'object' && !Array.isArray(extra[k]) && base[k] && typeof base[k] === 'object'
      ? deepMerge(base[k], extra[k]) : extra[k];
  }
  return out;
}
function loadConfig() {
  if (!fs.existsSync(CONFIG_FILE)) { fs.writeFileSync(CONFIG_FILE, JSON.stringify(DEFAULT_CONFIG, null, 2), 'utf8'); return JSON.parse(JSON.stringify(DEFAULT_CONFIG)); }
  const c = deepMerge(DEFAULT_CONFIG, JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8')));
  delete c.mysql; delete c.queries; // fra v1.0, brukes ikke lenger
  delete c.mapping.courseControls; delete c.mapping.races.finishCode; // erstattet av classes (v2.11)
  return c;
}
let config = loadConfig();
const saveConfig = () => fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf8');

// ---------------------------------------------------------------------------
// Brikkesys-API: oppkobling og automatisk start
// ---------------------------------------------------------------------------
const apiState = { startError: null, connected: false, info: null, error: null, child: null, startedByPoeng: false, folder: null, log: [] };
const apiUrl = () => String(config.brikkesysApi.url || '').replace(/\/$/, '');

async function apiGet(p) {
  const ctrl = new AbortController(); const t = setTimeout(() => ctrl.abort(), 15000);
  try {
    const res = await fetch(apiUrl() + p, { signal: ctrl.signal });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(body.error || 'HTTP ' + res.status);
    return body;
  } catch (e) {
    if (e.name === 'AbortError') throw new Error('Brikkesys-API svarte ikke innen 15 sekunder');
    if (e.cause && e.cause.code === 'ECONNREFUSED') throw new Error('Brikkesys-API kjører ikke på ' + apiUrl());
    throw e;
  } finally { clearTimeout(t); }
}

async function checkApi() {
  try { apiState.info = await apiGet('/api/info'); apiState.connected = true; apiState.error = null; apiState.startError = null; }
  catch (e) { apiState.connected = false; apiState.info = null; apiState.error = e.message; }
  return apiState.connected;
}

const verNum = f => { const m = f.match(/v([\d.]+)\.js$/i); return (m ? m[1] : '0').split('.').map(Number); };
const cmpVer = (a, b) => { for (let i = 0; i < 3; i++) { const d = (b[i] || 0) - (a[i] || 0); if (d) return d; } return 0; };

function findApiScript() {
  const candidates = [];
  const dirs = config.brikkesysApi.folder ? [config.brikkesysApi.folder] : [];
  const parent = path.dirname(DIR);
  try { for (const d of fs.readdirSync(parent)) { const full = path.join(parent, d); if (full !== DIR && fs.statSync(full).isDirectory()) dirs.push(full); } } catch (e) { /* ignorer */ }
  for (const d of dirs) {
    try { for (const f of fs.readdirSync(d)) if (/^Poeng(lop)?_BrikkesysAPI_v[\d.]+\.js$/i.test(f)) candidates.push({ dir: d, file: f, ver: verNum(f) }); } catch (e) { /* ignorer */ }
  }
  candidates.sort((a, b) => cmpVer(a.ver, b.ver));
  return candidates[0] || null;
}

function startApi() {
  if (apiState.child) return { ok: true, message: 'Brikkesys-API er allerede startet av Poengløp.' };
  const found = findApiScript();
  if (!found) return { ok: false, message: 'Fant ikke Poenglop_BrikkesysAPI_v*.js. Legg API-mappen ved siden av Poengløp-mappen, eller angi mappen under Oppsett.' };
  if (!fs.existsSync(path.join(found.dir, 'node_modules', 'mysql2'))) {
    return { ok: false, message: 'Brikkesys-API i ' + found.dir + ' er ikke installert. Kjør 0_Test_tilkobling.bat i den mappen én gang.' };
  }
  apiState.folder = found.dir; apiState.log = [];
  const child = spawn(process.execPath, [found.file], { cwd: found.dir, stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true });
  const keep = d => { for (const l of String(d).split(/\r?\n/)) if (l.trim()) { apiState.log.push(l.trim()); if (apiState.log.length > 30) apiState.log.shift(); console.log('  [API] ' + l.trim()); } };
  child.stdout.on('data', keep); child.stderr.on('data', keep);
  child.on('exit', code => { apiState.child = null; apiState.startedByPoeng = false; apiState.connected = false; console.log('  [API] stoppet (kode ' + code + ')'); });
  apiState.child = child; apiState.startedByPoeng = true;
  return { ok: true, message: 'Starter Brikkesys-API fra ' + found.dir };
}

async function connectApi() {
  if (DEMO) return;
  if (await checkApi()) return;
  if (!config.brikkesysApi.autoStart) return;
  const r = startApi();
  if (!r.ok) { apiState.error = r.message; apiState.startError = r.message; console.log('  ' + r.message); return; }
  console.log('  ' + r.message);
  for (let i = 0; i < 20 && !(await checkApi()); i++) await new Promise(res => setTimeout(res, 500));
  if (!apiState.connected && apiState.log.length) apiState.error = apiState.log.slice(-3).join(' | ');
}
function stopApi() { if (apiState.child) { try { apiState.child.kill(); } catch (e) { /* ignorer */ } } }
process.on('exit', stopApi);
process.on('SIGINT', () => { stopApi(); process.exit(0); });
process.on('SIGTERM', () => { stopApi(); process.exit(0); });

// ---------------------------------------------------------------------------
// Direkte tilkobling til MySQL (mysql2). Leser bare – alle spørringer er SELECT.
// ---------------------------------------------------------------------------
const dbState = { pool: null, key: null, connected: false, info: null, error: null, credFrom: null, tables: null };
const DB_MODES = ['auto', 'direct', 'api'];
const dbMode = () => (DB_MODES.includes(config.brikkesysDb.mode) ? config.brikkesysDb.mode : 'auto');

// mysql2 hentes fra Poengløp-mappen eller fra API-mappen, der den allerede er installert
let mysql2 = undefined;
function loadMysql2() {
  if (mysql2) return mysql2;
  const paths = [DIR]; const api = findApiScript(); if (api) paths.push(api.dir);
  try { mysql2 = require(require.resolve('mysql2/promise', { paths })); } catch (e) { mysql2 = null; }
  return mysql2;
}

// Tilkoblingen: egne verdier i poeng-config.json, ellers API-mappens poeng-brikkesys-config.json
function dbSettings() {
  const own = config.brikkesysDb;
  if (own.user) { dbState.credFrom = 'poeng-config.json'; return own; }
  const api = findApiScript();
  const f = api && path.join(api.dir, 'poeng-brikkesys-config.json');
  if (f && fs.existsSync(f)) {
    try {
      const m = JSON.parse(fs.readFileSync(f, 'utf8')).mysql || {};
      if (m.user) { dbState.credFrom = f; return { ...own, ...m }; }
    } catch (e) { /* ugyldig fil – behandles som manglende */ }
  }
  dbState.credFrom = null;
  return null;
}
const directPossible = () => !!loadMysql2() && !!dbSettings();

function dbPool() {
  const s = dbSettings();
  if (!s) throw new Error('Mangler brukernavn for MySQL. Fyll inn under Oppsett → Tilkobling til Brikkesys.');
  if (!loadMysql2()) throw new Error('Pakken mysql2 mangler. Kjør «npm install» i ' + DIR + ', eller installer Brikkesys-API ved siden av.');
  const key = JSON.stringify([s.host, s.port, s.user, s.password, s.database, s.charset]);
  if (dbState.pool && dbState.key === key) return dbState.pool;
  if (dbState.pool) dbState.pool.end().catch(() => {});
  dbState.pool = mysql2.createPool({
    host: s.host, port: Number(s.port) || 3306, user: s.user, password: s.password, database: s.database, charset: s.charset || 'utf8mb4',
    dateStrings: true, connectionLimit: 4, connectTimeout: 5000, supportBigNumbers: true, bigNumberStrings: true
  });
  dbState.key = key; dbState.tables = null; dbState.settings = s;
  return dbState.pool;
}
function dbError(e) {
  const s = dbState.settings || config.brikkesysDb;
  if (e.code === 'ECONNREFUSED') return new Error(`MySQL svarer ikke på ${s.host}:${s.port}. Kjører Brikkesys/MySQL?`);
  if (e.code === 'ER_ACCESS_DENIED_ERROR') return new Error(`Feil brukernavn eller passord for MySQL (${s.user}@${s.host}).`);
  if (e.code === 'ER_BAD_DB_ERROR') return new Error(`Databasen «${s.database}» finnes ikke på ${s.host}.`);
  if (e.code === 'ETIMEDOUT') return new Error(`Tidsavbrudd mot MySQL på ${s.host}:${s.port}.`);
  return e;
}
async function dbQuery(sql, params) {
  try { const [rows] = await dbPool().query(sql, params); return rows; } catch (e) { throw dbError(e); }
}
const qi = id => '`' + String(id).replace(/`/g, '``') + '`';
const cleanRow = row => { const o = {}; for (const k of Object.keys(row)) o[k] = Buffer.isBuffer(row[k]) ? '0x' + row[k].toString('hex') : row[k]; return o; };
const dbName = () => (dbState.settings || dbSettings() || config.brikkesysDb).database;

async function dbListTables() {
  const rows = await dbQuery(`SELECT TABLE_NAME AS name, TABLE_ROWS AS approxRows FROM information_schema.TABLES WHERE TABLE_SCHEMA = ? ORDER BY TABLE_NAME`, [dbName()]);
  dbState.tables = new Set(rows.map(r => r.name));
  return rows.map(r => ({ name: r.name, approxRows: Number(r.approxRows || 0) }));
}
// Tabell- og kolonnenavn kommer fra oppsettet og kontrolleres mot information_schema før de brukes i SQL
async function dbKnownTable(name) {
  if (!dbState.tables || !dbState.tables.has(name)) await dbListTables();
  if (!dbState.tables.has(name)) { const e = new Error('Ukjent tabell: ' + name); e.status = 404; throw e; }
  return name;
}
async function dbColumns(name) {
  await dbKnownTable(name);
  return dbQuery(`SELECT COLUMN_NAME AS name, COLUMN_TYPE AS type FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ? ORDER BY ORDINAL_POSITION`, [dbName(), name]);
}
async function dbTable(name) {
  const columns = await dbColumns(name);
  const [cnt] = await dbQuery(`SELECT COUNT(*) AS n FROM ${qi(name)}`);
  return { table: name, rowCount: Number(cnt.n), columns };
}
async function dbRows(name, filters = {}, limit = null) {
  const cols = new Set((await dbColumns(name)).map(c => c.name));
  const where = [], params = [];
  for (const [k, v] of Object.entries(filters)) {
    if (!cols.has(k)) { const e = new Error('Ukjent kolonne: ' + k); e.status = 400; throw e; }
    const vals = [].concat(v);
    if (!vals.length) return [];
    where.push(vals.length === 1 ? `${qi(k)} = ?` : `${qi(k)} IN (${vals.map(() => '?').join(',')})`); params.push(...vals);
  }
  const sql = `SELECT * FROM ${qi(name)}${where.length ? ' WHERE ' + where.join(' AND ') : ''}${limit ? ' LIMIT ' + Number(limit) : ''}`;
  return (await dbQuery(sql, params)).map(cleanRow);
}
async function dbInfo() {
  const [v] = await dbQuery('SELECT VERSION() AS v');
  const tables = await dbListTables(), s = dbState.settings;
  return { database: s.database, host: s.host, port: Number(s.port) || 3306, mysqlVersion: v.v, tableCount: tables.length };
}
async function checkDb() {
  try { dbState.info = await dbInfo(); dbState.connected = true; dbState.error = null; }
  catch (e) { dbState.connected = false; dbState.info = null; dbState.error = e.message; }
  return dbState.connected;
}
function resetDb() {
  if (dbState.pool) dbState.pool.end().catch(() => {});
  Object.assign(dbState, { pool: null, key: null, connected: false, info: null, error: null, tables: null });
  if (mysql2 === null) mysql2 = undefined; // prøv å finne mysql2 på nytt
}

// ---------------------------------------------------------------------------
// Datakilde: direkte MySQL eller Brikkesys-API
// ---------------------------------------------------------------------------
let source = null; // 'direct' eller 'api' etter tilkobling
const useDirect = () => source === 'direct';

async function connectSource() {
  if (DEMO) return;
  const mode = dbMode();
  if (mode === 'direct' || (mode === 'auto' && directPossible())) {
    source = 'direct';
    if (await checkDb()) return;
    if (mode === 'direct') return;
    console.log('  Direkte tilkobling feilet (' + dbState.error + '). Prøver Brikkesys-API.');
  }
  source = 'api';
  await connectApi();
  if (apiState.connected) return;
  if (mode === 'auto' && directPossible()) source = 'direct'; // vis feilen fra MySQL, den er mest nyttig
}
// Brukes ved hver statusforespørsel når vi ikke er tilkoblet. I auto prøves direkte først igjen,
// slik at Poengløp går over til direkte lesing når MySQL kommer opp.
async function checkSource() {
  if (DEMO) return true;
  if (!source) { await connectSource(); return sourceConnected(); }
  const mode = dbMode();
  if (mode === 'direct' || (mode === 'auto' && directPossible())) {
    if (await checkDb()) { source = 'direct'; return true; }
    if (mode === 'direct') { source = 'direct'; return false; }
  }
  if (await checkApi()) { source = 'api'; return true; }
  if (mode === 'auto' && directPossible()) source = 'direct'; // vis feilen fra MySQL, den er mest nyttig
  return false;
}
const sourceConnected = () => (useDirect() ? dbState.connected : apiState.connected);

// Felles lesefunksjoner som brukes av resten av serveren
async function srcTables() { return useDirect() ? dbListTables() : apiGet('/api/tables'); }
async function srcTable(name) { return useDirect() ? dbTable(name) : apiGet('/api/tables/' + encodeURIComponent(name)); }
async function srcSample(name, n) { return useDirect() ? dbRows(name, {}, n) : (await apiGet('/api/tables/' + encodeURIComponent(name) + '/rows?limit=' + n)).rows; }
async function srcSchema() {
  if (!useDirect()) return apiGet('/api/schema');
  const tables = [];
  for (const t of await dbListTables()) tables.push(await dbTable(t.name));
  return { info: dbState.info || await dbInfo(), tables };
}

// ---------------------------------------------------------------------------
// Lesing av løp, deltakere og stemplinger
// ---------------------------------------------------------------------------
async function fetchAll(table, filters = {}) {
  if (useDirect()) return dbRows(table, filters);
  const out = []; const limit = 5000;
  for (let offset = 0; ; offset += limit) {
    const q = new URLSearchParams({ limit, offset });
    for (const [k, v] of Object.entries(filters)) for (const x of [].concat(v)) q.append(k, x);
    const r = await apiGet('/api/tables/' + encodeURIComponent(table) + '/rows?' + q);
    out.push(...r.rows);
    if (out.length >= r.total || !r.rows.length) return out;
  }
}
const pick = (row, col) => (col ? row[col] ?? null : null);
// API v1.1 eller nyere, eller direkte tilkobling
const apiSupportsIn = () => useDirect() || (!!apiState.info && cmpVer(verNum('v' + apiState.info.version + '.js'), [1, 1]) <= 0);

async function readRaces() {
  const m = config.mapping.races;
  const rows = await fetchAll(m.table);
  return rows.map(r => ({ race_id: pick(r, m.id), race_name: pick(r, m.name), race_date: pick(r, m.date) }))
    .sort((a, b) => String(b.race_date || '').localeCompare(String(a.race_date || '')));
}

async function readRace(raceId) {
  const M = config.mapping, warnings = [];
  const rr = await fetchAll(M.runners.table, M.runners.race ? { [M.runners.race]: raceId } : {});
  const runners = rr.map(r => ({
    runner_id: pick(r, M.runners.id), name: pick(r, M.runners.name), club: pick(r, M.runners.club), class_name: pick(r, M.runners.cls),
    course_name: pick(r, M.runners.course), ecard: pick(r, M.runners.ecard), time_raw: pick(r, M.runners.time),
    status: pick(r, M.runners.status), birth_year: pick(r, M.runners.birth), reg_time: pick(r, M.runners.regTime), start_raw: pick(r, M.runners.start)
  }));

  let punches = [];
  const P = M.punches;
  if (P.table && P.link && P.code) {
    try {
      const linkField = P.linkTo === 'ecard' ? 'ecard' : 'runner_id';
      const byLink = new Map(runners.filter(r => r[linkField] !== null).map(r => [String(r[linkField]), r.runner_id]));
      let rows = [];
      if (P.race) rows = await fetchAll(P.table, { [P.race]: raceId });
      else if (apiSupportsIn()) {
        const keys = [...byLink.keys()];
        for (let i = 0; i < keys.length; i += 200) rows.push(...await fetchAll(P.table, { [P.link]: keys.slice(i, i + 200) }));
      } else {
        warnings.push('Brikkesys-API er eldre enn v1.1, så alle stemplinger leses og filtreres i Poengløp. Oppgrader API-et for raskere lesing.');
        rows = await fetchAll(P.table);
      }
      for (const r of rows) {
        const rid = byLink.get(String(r[P.link]));
        if (rid !== undefined) punches.push({ runner_id: rid, code: r[P.code], time_raw: pick(r, P.time) });
      }
    } catch (e) { warnings.push('Stemplinger kunne ikke leses: ' + e.message); }
  } else warnings.push('Tabell for stemplinger er ikke satt opp under Oppsett.');

  // Postkoder pr klasse fra Brikkesys (classes.codes). Siste verdi er målposten.
  let classCodes = [];
  const K = M.classCodes;
  if (K && K.table && K.codes && (K.cls || K.id)) {
    try {
      const rows = await fetchAll(K.table, K.race ? { [K.race]: raceId } : {});
      classCodes = rows.map(r => ({ class_id: pick(r, K.id), class_name: pick(r, K.cls), course_name: pick(r, K.course), codes: pick(r, K.codes) }));
    } catch (e) { warnings.push('Postkoder pr klasse (målpost) kunne ikke leses: ' + e.message); }
  }
  return { runners, punches, classCodes, warnings };
}

// ---------------------------------------------------------------------------
// Automatisk gjenkjenning av tabeller og kolonner
// ---------------------------------------------------------------------------
// Leser hele strukturen fra Brikkesys-API og foreslår hvilke tabeller og kolonner som
// inneholder løp, deltakere og stemplinger, ut fra kolonnenavn. Forslaget lagres ikke
// før brukeren godkjenner det.
const P = {
  raceFk: [/^raceid$/, /^race_id$/, /^race$/, /^lopid$/, /^løpid$/, /^eventid$/, /^event_id$/, /^arrid$/, /^arrangementid$/, /^competitionid$/, /race/, /event/, /^lop/],
  id: [/^id$/, /^nameid$/, /^runnerid$/, /^deltakerid$/, /^id_/],
  name: [/^name$/, /^navn$/, /^fullname$/, /^fulltnavn$/, /^runnername$/, /^racename$/, /^lopsnavn$/, /^title$/, /name/, /navn/],
  club: [/^club$/, /^klubb$/, /^team$/, /^lag$/, /^clubname$/, /club/, /klubb/],
  cls: [/^class$/, /^klasse$/, /^classname$/, /^klassenavn$/, /^classid$/, /class/, /klasse/],
  course: [/^cource$/, /^course$/, /^loype$/, /^løype$/, /^coursename$/, /^courseid$/, /^cource/, /cour/, /løype|loype/],
  ecard: [/^ecardno$/, /^ecard$/, /^brikke$/, /^brikkenr$/, /^brikkenummer$/, /^ecard1$/, /^cardno$/, /^chipno$/, /^si$/, /^sicard$/, /ecard|brikke|card|chip/],
  time: [/^times$/, /^time$/, /^tid$/, /^racetime$/, /^totaltid$/, /^runtime$/, /^lopstid$/, /^løpstid$/, /^result$/, /^resulttime$/, /time|tid/],
  status: [/^status$/, /^state$/, /^dsq$/, /status/],
  finishCode: [/^finishcode$/, /^finish_code$/, /^finishcontrol$/, /^finishstation$/, /^maalpost$/, /^målpost$/, /^maalkode$/, /^målkode$/, /^finish$/, /^maal$/, /^mål$/],
  start: [/^starttime$/, /^start$/, /^starttid$/, /^stime$/, /^start_time$/, /^starttidspunkt$/],
  regTime: [/^readtime$/, /^readouttime$/, /^readout$/, /^registered$/, /^registrert$/, /^regtime$/, /^changed$/, /^modified$/, /^updated$/, /^lastchanged$/, /^timestamp$/, /readout|registr|changed|modified|updated/],
  birth: [/^birthyear$/, /^birth_year$/, /^fodselsar$/, /^fødselsår$/, /^born$/, /^yob$/, /^year$/, /birth|fodt|født/],
  date: [/^racedate$/, /^date$/, /^dato$/, /^day$/, /^eventdate$/, /^startdate$/, /date|dato/],
  code: [/^controlcode$/, /^stasjon$/, /^station$/, /^code$/, /^control$/, /^post$/, /^postnr$/, /^postkode$/, /^cn$/, /stasjon|station|control|code|post/],
  ptime: [/^mintime$/, /^time$/, /^punchtime$/, /^tid$/, /^splittime$/, /^stempletid$/, /time|tid/],
  linkId: [/^iid$/, /^nameid$/, /^name_id$/, /^runnerid$/, /^runner_id$/, /^deltakerid$/, /^personid$/, /^entryid$/],
  linkEcard: [/^nr$/, /^ecardno$/, /^ecard$/, /^brikke$/, /^brikkenr$/, /^cardno$/, /^chipno$/],
  seq: [/^seq$/, /^nr$/, /^no$/, /^order$/, /^sortorder$/, /^rekkefolge$/, /^rekkefølge$/, /seq|order|rekke/]
};
function findCol(cols, pats, exclude = []) {
  const names = cols.map(c => c.name).filter(n => !exclude.includes(n));
  for (const re of pats) { const hit = names.find(n => re.test(n.toLowerCase())); if (hit) return hit; }
  return '';
}
async function detectMapping() {
  const schema = await srcSchema();
  const tables = schema.tables.filter(t => t.columns && t.columns.length);
  const notes = [];
  const best = (cands) => cands.sort((a, b) => b.score - a.score || b.rows - a.rows)[0];

  // Løp
  const raceCands = tables.map(t => {
    const id = findCol(t.columns, [/^id$/, /^raceid$/, /^race_id$/, /^eventid$/]);
    const name = findCol(t.columns, P.name, [id]); const date = findCol(t.columns, P.date);
    let score = (id ? 2 : 0) + (name ? 2 : 0) + (date ? 3 : 0) + (/race|lop|løp|event|arr|competition/i.test(t.table) ? 4 : 0);
    if (findCol(t.columns, P.ecard)) score -= 4;
    return { t, rows: t.rowCount, score, m: { table: t.table, id, name, date } };
  }).filter(c => c.m.id && c.m.name);
  const race = best(raceCands);

  // Deltakere
  const runCands = tables.filter(t => !race || t.table !== race.t.table).map(t => {
    const race_ = findCol(t.columns, P.raceFk);
    const id = findCol(t.columns, P.id, [race_]);
    const m = { table: t.table, race: race_, id, name: findCol(t.columns, P.name), club: findCol(t.columns, P.club), cls: findCol(t.columns, P.cls),
      course: findCol(t.columns, P.course), ecard: findCol(t.columns, P.ecard), time: findCol(t.columns, P.time), status: findCol(t.columns, P.status), birth: findCol(t.columns, P.birth), regTime: findCol(t.columns, P.regTime), start: findCol(t.columns, P.start) };
    const score = (m.race ? 4 : 0) + (m.name ? 3 : 0) + (m.ecard ? 3 : 0) + (m.time ? 2 : 0) + (m.cls ? 2 : 0) + (m.course ? 1 : 0) + (m.club ? 1 : 0) + (m.status ? 1 : 0);
    return { t, rows: t.rowCount, score, m };
  }).filter(c => c.m.race && c.m.name && c.m.id);
  const run = best(runCands);

  // Stemplinger
  const punchCands = tables.filter(t => (!race || t.table !== race.t.table) && (!run || t.table !== run.t.table)).map(t => {
    let link = findCol(t.columns, P.linkId), linkTo = 'id';
    if (!link) { link = findCol(t.columns, P.linkEcard); linkTo = 'ecard'; }
    const code = findCol(t.columns, P.code, [link]), time = findCol(t.columns, P.ptime, [link, code]);
    const m = { table: t.table, race: findCol(t.columns, P.raceFk), link, linkTo, code, time };
    const score = (link ? 3 : 0) + (code ? 3 : 0) + (time ? 2 : 0) + (/controltime/i.test(t.table) ? 5 : /mellom|split|punch|stempl|stasjon|post|ecard|control/i.test(t.table) ? 3 : 0);
    return { t, rows: t.rowCount, score, m };
  }).filter(c => c.m.link && c.m.code);
  const punch = best(punchCands);

  // Klasser med postkoder: tabell med klassenavn og en kolonne med postkodene (målpost = siste verdi)
  const classCands = tables.filter(t => (!run || t.table !== run.t.table) && (!punch || t.table !== punch.t.table)).map(t => {
    const codes = findCol(t.columns, [/^codes$/, /^controlcodes$/, /^controls$/, /^postkoder$/, /^poster$/, /codes|controls|postkode/]);
    const m = { table: t.table, race: findCol(t.columns, P.raceFk), id: findCol(t.columns, [/^id$/, /^classid$/, /^class_id$/]), cls: findCol(t.columns, [/^class$/, /^classname$/, /^name$/, /^klasse$/, /^navn$/]), course: findCol(t.columns, P.course), codes };
    const score = (codes ? 4 : 0) + (m.cls ? 2 : 0) + (m.race ? 1 : 0) + (/^class(es)?$|klasse/i.test(t.table) ? 4 : 0);
    return { t, rows: t.rowCount, score, m };
  }).filter(c => c.m.codes && (c.m.cls || c.m.id));
  const klass = best(classCands);

  const out = JSON.parse(JSON.stringify(config.mapping));
  const report = [];
  const add = (key, label, c, cands) => {
    if (!c) { report.push({ key, label, found: false, text: 'Fant ingen tabell som ligner. Velg tabell og kolonner manuelt.' }); return; }
    Object.assign(out[key], c.m);
    const others = cands.filter(x => x !== c).slice(0, 3).map(x => x.t.table);
    report.push({ key, label, found: true, table: c.t.table, rows: c.rows, alternatives: others,
      text: `${c.t.table} (${c.rows} rader)` + (others.length ? `. Andre mulige: ${others.join(', ')}` : '') });
  };
  add('races', 'Løp', race, raceCands); add('runners', 'Deltakere', run, runCands); add('punches', 'Stemplinger', punch, punchCands);
  add('classCodes', 'Klasser med målpost', klass, classCands);
  if (run && !run.m.time) notes.push('Fant ingen kolonne for løpstid i ' + run.t.table + '.');
  if (punch && !punch.m.time) notes.push('Fant ingen kolonne for stempletid i ' + punch.t.table + '. Strekktider kan ikke beregnes.');
  return { database: schema.info?.database, mapping: out, report, notes, tables: tables.map(t => t.table) };
}

// Kontrollerer at tabellene og kolonnene i oppsettet finnes i databasen
async function validateMapping() {
  const tables = await srcTables();
  const names = new Set(tables.map(t => t.name));
  const problems = [];
  const M = config.mapping;
  for (const [key, label] of [['races', 'Løp'], ['runners', 'Deltakere'], ['punches', 'Stemplinger'], ['classCodes', 'Klasser med målpost']]) {
    const m = M[key]; if (!m.table) continue;
    if (!names.has(m.table)) { problems.push(`${label}: tabellen «${m.table}» finnes ikke`); continue; }
    const s = await srcTable(m.table);
    const cols = new Set(s.columns.map(c => c.name));
    for (const [f, v] of Object.entries(m)) if (f !== 'table' && f !== 'linkTo' && v && !cols.has(v)) problems.push(`${label}: kolonnen «${v}» finnes ikke i «${m.table}»`);
  }
  return problems;
}

// ---------------------------------------------------------------------------
// Parameterfiler: lagres og hentes fra en mappe på PC-en (standard: programmappen)
// ---------------------------------------------------------------------------
const RESERVED_FILES = ['poeng-config.json', 'package.json', 'package-lock.json'];
function cleanFileName(n) {
  // eslint-disable-next-line no-control-regex
  let f = String(n || '').replace(/[<>:"/\\|?*\x00-\x1f]/g, '').trim().replace(/[. ]+$/, '');
  if (!f) throw new Error('Skriv inn et filnavn.');
  if (!/\.json$/i.test(f)) f += '.json';
  if (RESERVED_FILES.includes(f.toLowerCase())) throw new Error('Filnavnet ' + f + ' er reservert for programmet. Velg et annet navn.');
  return f;
}
function resolveFolder(folder) {
  const d = folder && String(folder).trim() ? String(folder).trim() : DIR;
  if (!path.isAbsolute(d)) throw new Error('Mappen må være en full sti, for eksempel ' + DIR);
  if (!fs.existsSync(d) || !fs.statSync(d).isDirectory()) throw new Error('Mappen finnes ikke: ' + d);
  return d;
}
function listParamFiles(folder) {
  const d = resolveFolder(folder);
  const files = fs.readdirSync(d).filter(f => /\.json$/i.test(f) && !RESERVED_FILES.includes(f.toLowerCase())).map(f => {
    const full = path.join(d, f); let meta = null;
    try { const j = JSON.parse(fs.readFileSync(full, 'utf8')); if (!j || !Array.isArray(j.params)) return null; meta = j._meta || {}; } catch (e) { return null; }
    return { name: f, modified: fs.statSync(full).mtime.toISOString(), race: meta.race_name || '' };
  }).filter(Boolean).sort((a, b) => b.modified.localeCompare(a.modified));
  return { folder: d, defaultFolder: DIR, files };
}

// ---------------------------------------------------------------------------
// Demodata
// ---------------------------------------------------------------------------
// Testløp ligger bare i Poengløp og skrives aldri til Brikkesys.
// «TEST – Lommelyktløp» har navngitte testløpere med kjente fasitsvar (se Bruksanvisning).
// «TEST – Live» slipper deltakerne i mål fortløpende for å teste automatisk oppdatering.
const LIVE_REAL_SECONDS = Number(process.env.POENG_LIVE_SECONDS) || 600;   // hele live-løpet spilles av på 10 minutter
let liveStart = Date.now();

function buildTestRace() {
  let seed = 20261015;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  const ri = (a, b) => a + Math.floor(rnd() * (b - a + 1));
  const pick = a => a[Math.floor(rnd() * a.length)];
  const first = ['Ingrid', 'Ola', 'Kari', 'Lars', 'Sigrid', 'Henrik', 'Mari', 'Jonas', 'Ida', 'Emil', 'Nora', 'Magnus', 'Thea', 'Sander', 'Selma', 'Tobias', 'Astrid', 'Jakob', 'Hedda', 'Even', 'Frida', 'Martin', 'Ane', 'Vetle', 'Oda', 'Kasper'];
  const last = ['Haugen', 'Berg', 'Moe', 'Lie', 'Dahl', 'Strand', 'Bakke', 'Solberg', 'Lund', 'Holm', 'Nilsen', 'Aas', 'Ødegård', 'Sæther'];
  const clubs = ['Wing OK', 'NTNUI', 'Freidig', 'Byåsen IL', 'Malvik IL', 'Trollelg', 'Melhus OL'];
  const range = (a, b) => Array.from({ length: b - a + 1 }, (_, i) => String(a + i));
  const courses = { Lang: range(31, 50), Kort: range(31, 42), Familie: range(31, 38) };
  const classes = { Lang: [['H21', 1996], ['D21', 1998], ['H40', 1983], ['D40', 1985]], Kort: [['H16', 2010], ['D16', 2010], ['H50', 1974], ['D50', 1975]], Familie: [['Åpen', 1990], ['H12', 2014], ['D12', 2014]] };
  const runners = [], punches = []; let id = 0;
  const add = (r, codes, legs, finishLeg, opts = {}) => {
    id++; const rid = 't' + id; let t = 0; const ps = [];
    codes.forEach((c, i) => { t += legs[i]; ps.push({ runner_id: rid, code: c, time_raw: t }); });
    const total = opts.time !== undefined ? opts.time : t + finishLeg;
    if (total !== null && opts.finishPunch !== false) ps.push({ runner_id: rid, code: r.course_name === 'Familie' ? '150' : '100', time_raw: total });
    runners.push({ runner_id: rid, ecard: 500000 + id, status: 'OK', ...r, time_raw: total });
    punches.push(...(opts.reverse ? ps.reverse() : ps));
    return rid;
  };
  // Vanlige deltakere: score-o med tilfeldig utvalg og rekkefølge, strekktider 2–6,5 min
  for (const course of Object.keys(courses)) for (let i = 0; i < 12; i++) {
    const [cls, by] = pick(classes[course]);
    const pool = courses[course].slice().sort(() => rnd() - 0.5);
    const n = Math.max(3, Math.min(pool.length, ri(Math.ceil(pool.length * 0.35), Math.ceil(pool.length * 0.8))));
    add({ name: pick(first) + ' ' + pick(last), club: pick(clubs), class_name: cls, course_name: course, birth_year: by - ri(0, 3) },
      pool.slice(0, n), Array.from({ length: n }, () => ri(120, 390)), ri(60, 200));
  }
  // Testløpere med kjent fasit (alle i løype Lang, H21 med mindre annet er oppgitt)
  const T = (name, extra = {}) => ({ name: 'Test ' + name, club: 'Testklubb', class_name: 'H21', course_name: 'Lang', birth_year: 1996, ...extra });
  const L = n => Array(n).fill(150);
  add(T('Rekke rett'), ['45', '31', '32', '33', '47'], L(5), 120);
  add(T('Rekke med post imellom'), ['31', '40', '32', '33'], L(4), 120);
  add(T('Rekke baklengs'), ['33', '32', '31'], L(3), 120);
  add(T('Dobbelstempling'), ['31', '31', '32', '33'], [150, 5, 150, 150], 120);
  add(T('Usortert'), ['31', '32', '33'], L(3), 120, { reverse: true });
  add(T('Lik tid A'), ['35', '36', '37', '38'], [150, 150, 95, 150], 120);
  add(T('Lik tid B', { class_name: 'D21', birth_year: 1998 }), ['35', '36', '37', '39'], [160, 140, 95, 170], 120);
  add(T('Overtid'), ['41', '42', '43', '44', '45', '46'], L(6), 0, { time: 63 * 60 + 30 });
  add(T('Feilstemplet', { status: 'MP' }), ['31', '34'], L(2), 0, { time: 45 * 60 });
  add(T('Brutt', { status: 'DNF' }), ['31', '32'], L(2), 0, { time: null });
  add(T('Ikke startet', { status: 'DNS' }), [], [], 0, { time: null });
  add(T('Ungdom', { class_name: 'H12', course_name: 'Familie', birth_year: 2014 }), ['31', '32', '34'], L(3), 150);
  add(T('Startsprint'), ['31', '35', '36'], [40, 150, 150], 120);
  add(T('Målspurt'), ['48', '49', '50'], L(3), 20);
  // Som i Brikkesys: classes.codes med postene og målposten sist
  const classCodes = [];
  for (const c of Object.keys(classes)) for (const [cls] of classes[c]) classCodes.push({ class_id: cls, class_name: cls, course_name: c, codes: [...courses[c], c === 'Familie' ? '150' : '100'].join(',') });
  return { runners, punches, classCodes };
}
const TEST_BASE = buildTestRace();
const TEST_RACES = [
  { race_id: 'test-1', race_name: 'TEST – Lommelyktløp (testløpere med fasit)', race_date: '2026-10-15' },
  { race_id: 'test-live', race_name: 'TEST – Live (deltakere kommer i mål)', race_date: '2026-10-15' }
];
function testRace(id) {
  if (id === 'test-1') return { ...JSON.parse(JSON.stringify(TEST_BASE)), warnings: [] };
  if (id !== 'test-live') throw new Error('Ukjent testløp');
  // Starttider spres over 20 minutter. Klokken skaleres slik at siste deltaker er i mål etter 10 minutter.
  const startOf = i => (i * 397) % 1200;
  const lastEnd = Math.max(...TEST_BASE.runners.map((r, i) => startOf(i) + (r.time_raw || 0)));
  const clock = (Date.now() - liveStart) / 1000 * (lastEnd / LIVE_REAL_SECONDS);
  const runners = [], punches = []; let finished = 0;
  TEST_BASE.runners.forEach((r, i) => {
    const start = startOf(i);
    const mine = TEST_BASE.punches.filter(p => p.runner_id === r.runner_id);
    const done = r.time_raw !== null && start + r.time_raw <= clock;
    if (done) finished++;
    runners.push({ ...r, time_raw: done ? r.time_raw : null, status: done || r.status === 'DNS' ? r.status : '',
      // registreringstidspunkt = når deltakeren kom i mål i avspillingen (gjør at markeringen virker også ved første lesing)
      reg_time: done ? new Date(liveStart + (start + r.time_raw) / (lastEnd / LIVE_REAL_SECONDS) * 1000).toISOString() : null });
    if (!done && r.status === 'DNF' && start + Math.max(0, ...mine.map(p => p.time_raw)) + 300 <= clock) runners[runners.length - 1].status = 'DNF';
    punches.push(...mine.filter(p => start + p.time_raw <= clock));
  });
  const pct = Math.min(100, Math.round(clock / lastEnd * 100));
  return { runners, punches, classCodes: TEST_BASE.classCodes,
    warnings: [`Live-testløp: ${finished} av ${runners.length} i mål (løpsklokke ${Math.floor(Math.min(clock, lastEnd) / 60)} min, ${pct} % av avspillingen).`] };
}
const showTest = () => DEMO || !config.testData.hide;

// ---------------------------------------------------------------------------
// HTTP
// ---------------------------------------------------------------------------
const host = config.server.host || '127.0.0.1', port = Number(config.server.port) || 8090;
if (!['127.0.0.1', 'localhost', '::1'].includes(host)) console.warn('\n  ADVARSEL: server.host er ' + host + '. Poengløp bør bare lytte på 127.0.0.1.\n');
// Sikkerhet: ingen CORS (bare samme opprinnelse), sikkerhetshoder, og innholdsregler for appen.
const SECURITY_HEADERS = {
  'Cache-Control': 'no-store',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'Referrer-Policy': 'no-referrer',
  'Cross-Origin-Resource-Policy': 'same-origin'
};
const APP_CSP = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'";
function send(res, code, body, type) {
  const h = { 'Content-Type': type || 'application/json; charset=utf-8', ...SECURITY_HEADERS };
  if (type && type.startsWith('text/html')) h['Content-Security-Policy'] = APP_CSP;
  res.writeHead(code, h);
  res.end(type ? body : JSON.stringify(body));
}
// Beskytter mot DNS-rebinding: bare forespørsler til 127.0.0.1/localhost på riktig port godtas.
function hostAllowed(req) {
  const h = String(req.headers.host || '').toLowerCase();
  return [`127.0.0.1:${port}`, `localhost:${port}`, `[::1]:${port}`].includes(h);
}
// Beskytter mot CSRF fra andre nettsider: skrivende kall må ha egen header og JSON-innhold.
// En annen nettside kan ikke sette denne headeren uten CORS-godkjenning, som serveren aldri gir.
function writeAllowed(req) {
  return req.headers['x-poenglop'] === '1' && String(req.headers['content-type'] || '').startsWith('application/json');
}
function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', c => { data += c; if (data.length > 2e6) { reject(new Error('For stor forespørsel')); req.destroy(); } });
    req.on('end', () => { try { resolve(data ? JSON.parse(data) : {}); } catch (e) { reject(new Error('Ugyldig JSON')); } });
  });
}
function findAppFile() {
  const files = fs.readdirSync(DIR).filter(f => /^Poeng(lop)?_v[\d.]+\.html$/i.test(f));
  files.sort((a, b) => cmpVer(verNum(a.replace(/html$/, 'js')), verNum(b.replace(/html$/, 'js'))));
  return files[0] || null;
}
function safeRaceFile(raceId) {
  const id = String(raceId).replace(/[^A-Za-z0-9_-]/g, '');
  if (!id) throw new Error('Ugyldig løps-ID');
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR);
  return path.join(DATA_DIR, (DEMO ? 'demo-' : '') + 'race-' + id + '.json');
}

async function handleApi(req, res, u) {
  const p = u.pathname, raceId = u.searchParams.get('id') || u.searchParams.get('race');

  if (p === '/api/status') {
    if (!DEMO && !sourceConnected()) await checkSource();
    const direct = useDirect(), info = direct ? dbState.info : apiState.info;
    const error = DEMO ? null : direct ? dbState.error : [apiState.error, apiState.startError].filter((x, i, a) => x && a.indexOf(x) === i).join('. ');
    return send(res, 200, {
      version: VERSION, demo: DEMO, testData: showTest(), connected: DEMO || sourceConnected(), error,
      database: DEMO ? 'demo' : info?.database, host: info?.host, timeDivisor: Number(config.timeDivisor) || 1, source: DEMO ? 'demo' : source,
      db: { mode: dbMode(), host: dbState.info?.host, port: dbState.info?.port, mysqlVersion: dbState.info?.mysqlVersion || null, credFrom: dbState.credFrom },
      api: { url: apiUrl(), version: apiState.info?.version || null, startedByPoeng: apiState.startedByPoeng, folder: apiState.folder }
    });
  }
  if (p === '/api/apiconfig' && req.method === 'GET') {
    // Passordet sendes aldri til nettleseren
    const { password, ...db } = config.brikkesysDb;
    return send(res, 200, { ...config.brikkesysApi, db: { ...db, passwordSet: !!password, mysql2: !!loadMysql2() }, timeDivisor: config.timeDivisor, autoRefresh: config.autoRefresh, testData: { show: showTest(), demo: DEMO }, detected: findApiScript()?.dir || null });
  }
  if (p === '/api/testdata' && req.method === 'POST') {
    const b = await readBody(req);
    if (typeof b.show === 'boolean') { config.testData.hide = !b.show; delete config.testData.show; saveConfig(); }
    if (b.restartLive) liveStart = Date.now();
    return send(res, 200, { ok: true, show: showTest() });
  }
  if (p === '/api/refresh' && req.method === 'POST') {
    const b = await readBody(req);
    if (typeof b.enabled === 'boolean') config.autoRefresh.enabled = b.enabled;
    if (b.seconds !== undefined) config.autoRefresh.seconds = Math.min(3600, Math.max(5, Math.round(Number(b.seconds) || 30)));
    saveConfig(); return send(res, 200, { ok: true, autoRefresh: config.autoRefresh });
  }
  if (p === '/api/apiconfig' && req.method === 'POST') {
    const b = await readBody(req);
    if (typeof b.url === 'string' && b.url.trim()) config.brikkesysApi.url = b.url.trim();
    if (typeof b.folder === 'string') config.brikkesysApi.folder = b.folder.trim();
    if (typeof b.autoStart === 'boolean') config.brikkesysApi.autoStart = b.autoStart;
    if (b.timeDivisor) config.timeDivisor = Number(b.timeDivisor) || 1;
    if (b.db && typeof b.db === 'object') {
      const d = config.brikkesysDb;
      if (DB_MODES.includes(b.db.mode)) d.mode = b.db.mode;
      for (const f of ['host', 'user', 'database', 'charset']) if (typeof b.db[f] === 'string') d[f] = b.db[f].trim();
      if (b.db.port !== undefined) d.port = Number(b.db.port) || 3306;
      if (typeof b.db.password === 'string' && b.db.password !== '') d.password = b.db.password; // tomt felt = behold passordet
      if (b.db.clearPassword === true) d.password = '';
      if (!d.host) d.host = '127.0.0.1';
      if (!d.database) d.database = 'resultatdatabase';
    }
    saveConfig(); resetDb(); await connectSource();
    const ok = sourceConnected();
    return send(res, 200, { ok, source, error: useDirect() ? dbState.error : apiState.error });
  }
  if (p === '/api/apiconfig/start' && req.method === 'POST') {
    if (DEMO) return send(res, 200, { ok: true });
    source = 'api';
    if (await checkApi()) return send(res, 200, { ok: true, message: 'Brikkesys-API kjører allerede.' });
    const r = startApi(); apiState.startError = r.ok ? null : r.message;
    if (r.ok) for (let i = 0; i < 20 && !(await checkApi()); i++) await new Promise(res2 => setTimeout(res2, 500));
    return send(res, 200, { ok: apiState.connected, message: apiState.connected ? 'Tilkoblet.' : (r.ok ? (apiState.log.slice(-3).join(' | ') || 'API-et startet ikke.') : r.message) });
  }

  if (p === '/api/mapping' && req.method === 'GET') return send(res, 200, config.mapping);
  if (p === '/api/mapping' && req.method === 'POST') {
    const b = await readBody(req);
    for (const k of Object.keys(DEFAULT_CONFIG.mapping)) if (b[k] && typeof b[k] === 'object') {
      for (const f of Object.keys(DEFAULT_CONFIG.mapping[k])) if (typeof b[k][f] === 'string') config.mapping[k][f] = b[k][f].trim();
    }
    saveConfig(); return send(res, 200, { ok: true });
  }
  if (p === '/api/mapping/detect') {
    if (DEMO) return send(res, 200, { mapping: config.mapping, report: [], notes: ['Demomodus – ingen database å lese.'], tables: [] });
    return send(res, 200, await detectMapping());
  }
  if (p === '/api/mapping/validate') {
    if (DEMO) return send(res, 200, { problems: [] });
    return send(res, 200, { problems: await validateMapping() });
  }
  if (p === '/api/mapping/reset' && req.method === 'POST') { config.mapping = JSON.parse(JSON.stringify(DEFAULT_CONFIG.mapping)); saveConfig(); return send(res, 200, { ok: true }); }

  if (p === '/api/bapi/tables') {
    if (DEMO) return send(res, 200, []);
    return send(res, 200, await srcTables());
  }
  if (p === '/api/bapi/table') {
    const t = u.searchParams.get('name') || '';
    const [s, rows] = await Promise.all([srcTable(t), srcSample(t, 5)]);
    return send(res, 200, { columns: s.columns.map(c => c.name + ' (' + c.type + ')'), rowCount: s.rowCount, rows });
  }

  if (p === '/api/races') {
    if (DEMO) return send(res, 200, TEST_RACES);
    let real = [];
    try { real = await readRaces(); } catch (e) { if (!showTest()) throw e; }
    return send(res, 200, showTest() ? [...real, ...TEST_RACES] : real);
  }
  if (p === '/api/race') {
    if (!raceId) throw new Error('Mangler løps-ID');
    if (String(raceId).startsWith('test-')) return send(res, 200, testRace(String(raceId)));
    if (DEMO) throw new Error('Ukjent løp');
    return send(res, 200, await readRace(raceId));
  }

  if (p === '/api/paramfiles' && req.method === 'GET') return send(res, 200, listParamFiles(u.searchParams.get('folder')));
  if (p === '/api/paramfiles/save' && req.method === 'POST') {
    const b = await readBody(req);
    const d = resolveFolder(b.folder), f = cleanFileName(b.name), full = path.join(d, f);
    if (!b.data || !Array.isArray(b.data.params)) throw new Error('Mangler parametere å lagre.');
    if (fs.existsSync(full) && !b.overwrite) return send(res, 409, { exists: true, name: f, path: full, error: 'Filen finnes allerede' });
    fs.writeFileSync(full, JSON.stringify(b.data, null, 2), 'utf8');
    return send(res, 200, { ok: true, name: f, path: full });
  }
  if (p === '/api/paramfiles/load' && req.method === 'GET') {
    const d = resolveFolder(u.searchParams.get('folder')), f = cleanFileName(u.searchParams.get('name'));
    const full = path.join(d, f);
    if (!fs.existsSync(full)) throw new Error('Fant ikke filen ' + full);
    return send(res, 200, JSON.parse(fs.readFileSync(full, 'utf8')));
  }

  if (p === '/api/settings' && req.method === 'GET') {
    const f = safeRaceFile(raceId);
    return send(res, 200, fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : null);
  }
  if (p === '/api/settings' && req.method === 'POST') {
    const b = await readBody(req); fs.writeFileSync(safeRaceFile(raceId), JSON.stringify(b, null, 2), 'utf8');
    return send(res, 200, { ok: true, savedAt: new Date().toISOString() });
  }
  send(res, 404, { error: 'Ukjent adresse: ' + p });
}

const server = http.createServer(async (req, res) => {
  const u = new URL(req.url, 'http://localhost');
  if (!hostAllowed(req)) return send(res, 403, { error: 'Ugyldig vertsnavn' });
  if (req.method !== 'GET' && req.method !== 'POST') return send(res, 405, { error: 'Metoden er ikke tillatt' });
  if (req.method === 'POST' && !writeAllowed(req)) return send(res, 403, { error: 'Forespørselen mangler godkjenning' });
  try {
    if (u.pathname.startsWith('/api/')) return await handleApi(req, res, u);
    if (u.pathname === '/' || /^\/Poeng(lop)?_v[\d.]+\.html$/i.test(u.pathname)) {
      const file = u.pathname === '/' ? findAppFile() : u.pathname.slice(1);
      if (!file || !fs.existsSync(path.join(DIR, file))) return send(res, 404, 'Fant ingen Poenglop_v*.html i mappen ' + DIR, 'text/plain; charset=utf-8');
      return send(res, 200, fs.readFileSync(path.join(DIR, file)), 'text/html; charset=utf-8');
    }
    send(res, 404, 'Ikke funnet', 'text/plain; charset=utf-8');
  } catch (e) { send(res, 500, { error: e.message }); }
});


server.on('error', e => {
  if (e.code === 'EADDRINUSE') console.error('\n  Port ' + port + ' er i bruk. Poengløp kjører kanskje allerede i et annet vindu.\n');
  else console.error(e);
  stopApi(); process.exit(1);
});
server.listen(port, host, async () => {
  const url = 'http://' + host + ':' + port;
  console.log('\n  Poengløp v' + VERSION + (DEMO ? '  (DEMOMODUS – ingen database)' : ''));
  console.log('  Åpne i nettleseren: ' + url + '\n  Stopp med Ctrl+C\n');
  await connectSource();
  if (!DEMO && useDirect()) console.log(dbState.connected
    ? `  Brikkesys tilkoblet direkte: ${dbState.info.database} på ${dbState.info.host}:${dbState.info.port} (MySQL ${dbState.info.mysqlVersion})`
    : '  Direkte tilkobling til MySQL feilet: ' + dbState.error);
  else if (!DEMO) console.log(apiState.connected
    ? '  Brikkesys-API tilkoblet: ' + apiState.info.database + ' (API v' + apiState.info.version + ')' + (apiState.startedByPoeng ? ', startet av Poengløp' : '')
    : '  Brikkesys-API ikke tilkoblet: ' + apiState.error);
  // Nettleseren åpnes bare med en kontrollert adresse (ingen skallkommandoer fra konfigurasjonen)
  if (!NO_BROWSER && process.platform === 'win32' && /^http:\/\/[\w.-]+:\d+$/.test(url)) exec('start "" "' + url + '"');
});
