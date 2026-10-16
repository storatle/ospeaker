#!/usr/bin/env node
/*
 * Poengløp Brikkesys-API v1.4
 * Standard lesegrensesnitt mot Brikkesys (MySQL). Endrer aldri data.
 *
 *   node Poenglop_BrikkesysAPI_v1.4.js            Start nettleservisning og API på http://127.0.0.1:8091
 *   node Poenglop_BrikkesysAPI_v1.4.js --eksport  Skriv alle tabeller og strukturen til en mappe og avslutt
 *   node Poenglop_BrikkesysAPI_v1.4.js --test     Test tilkoblingen og avslutt
 *
 * Tilkobling settes i poeng-brikkesys-config.json (lages automatisk første gang).
 */
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');

const VERSION = '1.4';
const DIR = __dirname;
const CONFIG_FILE = path.join(DIR, 'poeng-brikkesys-config.json');
const DEFAULT_CONFIG = {
  mysql: { host: '127.0.0.1', port: 3306, user: 'poeng', password: '', database: 'resultatdatabase', charset: 'utf8mb4' },
  server: { host: '127.0.0.1', port: 8091 },
  export: { folder: 'eksport', chunkRows: 5000 },
  maxRowsPerRequest: 5000
};

let mysql;
try { mysql = require('mysql2/promise'); }
catch (e) { console.error('\n  Pakken mysql2 mangler. Kjør «npm install» i mappen ' + DIR + '\n'); process.exit(1); }

// ---------------- Konfigurasjon ----------------
function loadConfig() {
  if (!fs.existsSync(CONFIG_FILE)) {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(DEFAULT_CONFIG, null, 2), 'utf8');
    console.log('  Laget ' + path.basename(CONFIG_FILE) + '. Fyll inn brukernavn og passord og start på nytt.');
  }
  const c = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  return {
    mysql: { ...DEFAULT_CONFIG.mysql, ...c.mysql },
    server: { ...DEFAULT_CONFIG.server, ...c.server },
    export: { ...DEFAULT_CONFIG.export, ...c.export },
    maxRowsPerRequest: c.maxRowsPerRequest || DEFAULT_CONFIG.maxRowsPerRequest
  };
}
const config = loadConfig();
const DB = config.mysql.database;

const pool = mysql.createPool({
  host: config.mysql.host, port: Number(config.mysql.port), user: config.mysql.user, password: config.mysql.password,
  database: DB, charset: config.mysql.charset, dateStrings: true, connectionLimit: 4, connectTimeout: 5000,
  supportBigNumbers: true, bigNumberStrings: true
});

// ---------------- Struktur (information_schema) ----------------
async function listTables() {
  const [rows] = await pool.query(
    `SELECT TABLE_NAME AS name, TABLE_TYPE AS type, ENGINE AS engine, TABLE_ROWS AS approxRows,
            DATA_LENGTH + INDEX_LENGTH AS bytes, TABLE_COMMENT AS comment
     FROM information_schema.TABLES WHERE TABLE_SCHEMA = ? ORDER BY TABLE_NAME`, [DB]);
  return rows.map(r => ({ ...r, approxRows: Number(r.approxRows || 0), bytes: Number(r.bytes || 0) }));
}

let tableCache = null;
async function knownTable(name) {
  if (!tableCache) tableCache = new Set((await listTables()).map(t => t.name));
  if (!tableCache.has(name)) { tableCache = null; const again = new Set((await listTables()).map(t => t.name)); tableCache = again; }
  if (!tableCache.has(name)) { const e = new Error('Ukjent tabell: ' + name); e.status = 404; throw e; }
  return name;
}
const qi = id => '`' + String(id).replace(/`/g, '``') + '`';

async function tableStructure(name) {
  await knownTable(name);
  const [columns] = await pool.query(
    `SELECT COLUMN_NAME AS name, COLUMN_TYPE AS type, IS_NULLABLE AS nullable, COLUMN_KEY AS keyType,
            COLUMN_DEFAULT AS defaultValue, EXTRA AS extra, COLUMN_COMMENT AS comment
     FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ? ORDER BY ORDINAL_POSITION`, [DB, name]);
  const [idx] = await pool.query(
    `SELECT INDEX_NAME AS name, NON_UNIQUE AS nonUnique, COLUMN_NAME AS col, SEQ_IN_INDEX AS seq
     FROM information_schema.STATISTICS WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ? ORDER BY INDEX_NAME, SEQ_IN_INDEX`, [DB, name]);
  const indexes = {};
  for (const i of idx) (indexes[i.name] ??= { name: i.name, unique: Number(i.nonUnique) === 0, columns: [] }).columns.push(i.col);
  const [fks] = await pool.query(
    `SELECT COLUMN_NAME AS col, REFERENCED_TABLE_NAME AS refTable, REFERENCED_COLUMN_NAME AS refCol
     FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ? AND REFERENCED_TABLE_NAME IS NOT NULL`, [DB, name]);
  const [[cnt]] = await pool.query(`SELECT COUNT(*) AS n FROM ${qi(name)}`);
  let createSql = '';
  try { const [[c]] = await pool.query(`SHOW CREATE TABLE ${qi(name)}`); createSql = c['Create Table'] || c['Create View'] || ''; } catch (e) { /* visninger */ }
  return { table: name, rowCount: Number(cnt.n), columns, indexes: Object.values(indexes), foreignKeys: fks, createSql };
}

// Brikkesys bruker ofte ingen fremmednøkler. Vi foreslår derfor koblinger ut fra kolonnenavn (merket som antatt).
async function relations() {
  const tables = await listTables();
  const names = tables.map(t => t.name);
  const [cols] = await pool.query(
    `SELECT TABLE_NAME AS t, COLUMN_NAME AS c FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = ?`, [DB]);
  const [fks] = await pool.query(
    `SELECT TABLE_NAME AS t, COLUMN_NAME AS c, REFERENCED_TABLE_NAME AS rt, REFERENCED_COLUMN_NAME AS rc
     FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = ? AND REFERENCED_TABLE_NAME IS NOT NULL`, [DB]);
  const out = fks.map(f => ({ fromTable: f.t, fromColumn: f.c, toTable: f.rt, toColumn: f.rc, source: 'fremmednøkkel' }));
  const lower = Object.fromEntries(names.map(n => [n.toLowerCase(), n]));
  for (const { t, c } of cols) {
    const m = c.toLowerCase().match(/^(.+?)_?id$/);
    if (!m || c.toLowerCase() === 'id') continue;
    const base = m[1];
    const target = lower[base] || lower[base + 's'] || lower[base + 'es'] || lower[base.replace(/s$/, '')];
    if (target && target !== t && !out.some(o => o.fromTable === t && o.fromColumn === c)) {
      out.push({ fromTable: t, fromColumn: c, toTable: target, toColumn: 'id', source: 'antatt ut fra kolonnenavn' });
    }
  }
  return out;
}

// ---------------- Data ----------------
function clean(row) {
  const o = {};
  for (const k of Object.keys(row)) {
    const v = row[k];
    o[k] = Buffer.isBuffer(v) ? '0x' + v.toString('hex') : v;
  }
  return o;
}

async function tableRows(name, q) {
  await knownTable(name);
  const s = await tableStructure(name);
  const colNames = new Set(s.columns.map(c => c.name));
  const limit = Math.min(Math.max(1, Number(q.get('limit')) || 100), config.maxRowsPerRequest);
  const offset = Math.max(0, Number(q.get('offset')) || 0);
  const where = []; const params = [];
  for (const k of new Set(q.keys())) {
    if (['limit', 'offset', 'order', 'dir', 'search'].includes(k)) continue;
    if (!colNames.has(k)) { const e = new Error('Ukjent kolonne: ' + k); e.status = 400; throw e; }
    const vals = q.getAll(k);
    if (vals.length === 1) { where.push(`${qi(k)} = ?`); params.push(vals[0]); }
    else { where.push(`${qi(k)} IN (${vals.map(() => '?').join(',')})`); params.push(...vals); }
  }
  const search = q.get('search');
  if (search) {
    where.push('(' + s.columns.map(c => `CAST(${qi(c.name)} AS CHAR) LIKE ?`).join(' OR ') + ')');
    s.columns.forEach(() => params.push('%' + search + '%'));
  }
  const order = q.get('order');
  if (order && !colNames.has(order)) { const e = new Error('Ukjent kolonne for sortering: ' + order); e.status = 400; throw e; }
  const dir = String(q.get('dir')).toLowerCase() === 'desc' ? 'DESC' : 'ASC';
  const w = where.length ? ' WHERE ' + where.join(' AND ') : '';
  const [[cnt]] = await pool.query(`SELECT COUNT(*) AS n FROM ${qi(name)}${w}`, params);
  const [rows] = await pool.query(`SELECT * FROM ${qi(name)}${w}${order ? ` ORDER BY ${qi(order)} ${dir}` : ''} LIMIT ? OFFSET ?`, [...params, limit, offset]);
  return { table: name, total: Number(cnt.n), limit, offset, rows: rows.map(clean) };
}

function csvCell(v) {
  if (v === null || v === undefined) return '';
  let s = typeof v === 'object' ? JSON.stringify(v) : String(v);
  // Hindrer at tekst som starter med = + - @ tolkes som formel i Excel (tall berøres ikke)
  if (typeof v === 'string' && /^[=+\-@\t\r]/.test(s) && !/^[+-]?\d+([.,]\d+)?$/.test(s)) s = "'" + s;
  return /[;"\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

async function* streamRows(name) {
  const chunk = config.export.chunkRows;
  for (let off = 0; ; off += chunk) {
    const [rows] = await pool.query(`SELECT * FROM ${qi(name)} LIMIT ? OFFSET ?`, [chunk, off]);
    if (!rows.length) return;
    yield rows.map(clean);
    if (rows.length < chunk) return;
  }
}

async function writeTableFiles(name, folder, columns) {
  const csv = fs.createWriteStream(path.join(folder, name + '.csv'), 'utf8');
  const json = fs.createWriteStream(path.join(folder, name + '.json'), 'utf8');
  csv.write('\ufeff' + columns.map(csvCell).join(';') + '\r\n');
  json.write('[\n'); let first = true, n = 0;
  for await (const rows of streamRows(name)) {
    for (const r of rows) {
      csv.write(columns.map(c => csvCell(r[c])).join(';') + '\r\n');
      json.write((first ? '' : ',\n') + JSON.stringify(r)); first = false; n++;
    }
  }
  json.write('\n]\n');
  await Promise.all([new Promise(r => csv.end(r)), new Promise(r => json.end(r))]);
  return n;
}

function structureMarkdown(info, structures, rels) {
  const L = [`# Brikkesys – databasestruktur`, '', `Database: **${DB}** på ${config.mysql.host}:${config.mysql.port}  `,
    `MySQL-versjon: ${info.mysqlVersion}  `, `Eksportert: ${new Date().toLocaleString('nb-NO')} med Poengløp Brikkesys-API v${VERSION}`, '',
    '## Oversikt', '', '| Tabell | Rader | Kolonner |', '| --- | ---: | ---: |'];
  for (const s of structures) L.push(`| ${s.table} | ${s.rowCount} | ${s.columns.length} |`);
  if (rels.length) {
    L.push('', '## Koblinger mellom tabeller', '', '| Fra | Til | Kilde |', '| --- | --- | --- |');
    for (const r of rels) L.push(`| ${r.fromTable}.${r.fromColumn} | ${r.toTable}.${r.toColumn} | ${r.source} |`);
  }
  for (const s of structures) {
    L.push('', `## ${s.table}`, '', `${s.rowCount} rader.`, '', '| Kolonne | Type | Null | Nøkkel | Standard | Ekstra |', '| --- | --- | --- | --- | --- | --- |');
    for (const c of s.columns) L.push(`| ${c.name} | ${c.type} | ${c.nullable} | ${c.keyType || ''} | ${c.defaultValue ?? ''} | ${c.extra || ''} |`);
    if (s.indexes.length) L.push('', 'Indekser: ' + s.indexes.map(i => `${i.name} (${i.columns.join(', ')})${i.unique ? ' unik' : ''}`).join('; '));
  }
  return L.join('\n') + '\n';
}

async function info() {
  const [[v]] = await pool.query('SELECT VERSION() AS v');
  const tables = await listTables();
  return { api: 'Poengløp Brikkesys-API', version: VERSION, database: DB, host: config.mysql.host, port: config.mysql.port,
    mysqlVersion: v.v, tableCount: tables.length };
}

async function exportAll(log = console.log) {
  const d = new Date(), z = n => String(n).padStart(2, '0');
  const stamp = `${d.getFullYear()}-${z(d.getMonth() + 1)}-${z(d.getDate())}_${z(d.getHours())}${z(d.getMinutes())}`;
  const folder = path.join(DIR, config.export.folder, `${DB}_${stamp}`);
  fs.mkdirSync(folder, { recursive: true });
  const inf = await info();
  const tables = await listTables();
  const structures = [];
  log(`  Eksporterer ${tables.length} tabeller til ${folder}`);
  for (const t of tables) {
    const s = await tableStructure(t.name);
    const n = await writeTableFiles(t.name, folder, s.columns.map(c => c.name));
    structures.push(s);
    log(`    ${t.name.padEnd(30)} ${String(n).padStart(8)} rader`);
  }
  const rels = await relations();
  fs.writeFileSync(path.join(folder, 'struktur.json'), JSON.stringify({ info: inf, relations: rels, tables: structures }, null, 2), 'utf8');
  fs.writeFileSync(path.join(folder, 'struktur.md'), structureMarkdown(inf, structures, rels), 'utf8');
  log('  Ferdig. Åpne struktur.md for oversikt.');
  return { folder, tables: structures.length };
}

// ---------------- HTTP ----------------
// Sikkerhet: ingen CORS (andre nettsider kan ikke lese data), sikkerhetshoder og vern mot DNS-rebinding.
const SECURITY_HEADERS = { 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY',
  'Referrer-Policy': 'no-referrer', 'Cross-Origin-Resource-Policy': 'same-origin' };
const PAGE_CSP = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'";
function send(res, code, body, type) {
  const h = { 'Content-Type': type || 'application/json; charset=utf-8', ...SECURITY_HEADERS };
  if (type && type.startsWith('text/html')) h['Content-Security-Policy'] = PAGE_CSP;
  res.writeHead(code, h);
  res.end(type ? body : JSON.stringify(body, null, 2));
}
function hostAllowed(req) {
  const h = String(req.headers.host || '').toLowerCase(), port = Number(config.server.port);
  return [`127.0.0.1:${port}`, `localhost:${port}`, `[::1]:${port}`].includes(h);
}

const server = http.createServer(async (req, res) => {
  const u = new URL(req.url, 'http://localhost');
  if (!hostAllowed(req)) return send(res, 403, { error: 'Ugyldig vertsnavn' });
  let p;
  try { p = decodeURIComponent(u.pathname); } catch (e) { return send(res, 400, { error: 'Ugyldig adresse' }); }
  try {
    if (req.method !== 'GET' && !(req.method === 'POST' && p === '/api/export')) return send(res, 405, { error: 'Kun lesing er tillatt' });
    // Eksport skriver filer: krever egen header, som andre nettsider ikke kan sette
    if (req.method === 'POST' && req.headers['x-poenglop'] !== '1') return send(res, 403, { error: 'Forespørselen mangler godkjenning' });
    if (p === '/') return send(res, 200, PAGE, 'text/html; charset=utf-8');
    if (p === '/api' || p === '/api/') return send(res, 200, { ...(await info()), endpoints: ENDPOINTS });
    if (p === '/api/info') return send(res, 200, await info());
    if (p === '/api/tables') return send(res, 200, await listTables());
    if (p === '/api/relations') return send(res, 200, await relations());
    if (p === '/api/schema') {
      const tables = await listTables(); const out = [];
      for (const t of tables) out.push(await tableStructure(t.name));
      return send(res, 200, { info: await info(), relations: await relations(), tables: out });
    }
    if (p === '/api/export' && req.method === 'POST') return send(res, 200, await exportAll(() => {}));
    let m;
    if ((m = p.match(/^\/api\/tables\/([^/]+)$/))) return send(res, 200, await tableStructure(m[1]));
    if ((m = p.match(/^\/api\/tables\/([^/]+)\/rows$/))) return send(res, 200, await tableRows(m[1], u.searchParams));
    if ((m = p.match(/^\/api\/tables\/([^/]+)\/(csv|json)$/))) {
      const name = await knownTable(m[1]); const s = await tableStructure(name); const cols = s.columns.map(c => c.name);
      res.writeHead(200, { 'Content-Type': m[2] === 'csv' ? 'text/csv; charset=utf-8' : 'application/json; charset=utf-8',
        'Content-Disposition': `attachment; filename="${name}.${m[2]}"` });
      if (m[2] === 'csv') res.write('\ufeff' + cols.map(csvCell).join(';') + '\r\n'); else res.write('[\n');
      let first = true;
      for await (const rows of streamRows(name)) for (const r of rows) {
        if (m[2] === 'csv') res.write(cols.map(c => csvCell(r[c])).join(';') + '\r\n');
        else { res.write((first ? '' : ',\n') + JSON.stringify(r)); first = false; }
      }
      return res.end(m[2] === 'csv' ? '' : '\n]\n');
    }
    send(res, 404, { error: 'Ukjent adresse: ' + p, se: '/api' });
  } catch (e) {
    send(res, e.status || 500, { error: e.message });
  }
});

const ENDPOINTS = {
  'GET /api/info': 'Versjon, database og antall tabeller',
  'GET /api/tables': 'Alle tabeller med omtrentlig antall rader og størrelse',
  'GET /api/tables/{tabell}': 'Kolonner, indekser, nøkler, eksakt antall rader og CREATE TABLE',
  'GET /api/tables/{tabell}/rows?limit=100&offset=0&order=kolonne&dir=desc&search=tekst&kolonne=verdi&kolonne=verdi2': 'Rader med sidevisning, sortering, søk og filter (gjentatt kolonne = en av verdiene)',
  'GET /api/tables/{tabell}/csv': 'Hele tabellen som CSV (semikolon, UTF-8)',
  'GET /api/tables/{tabell}/json': 'Hele tabellen som JSON',
  'GET /api/relations': 'Koblinger mellom tabeller (fremmednøkler og antatte)',
  'GET /api/schema': 'Hele strukturen samlet',
  'POST /api/export': 'Full eksport til filer i eksportmappen'
};

// ---------------- Nettleservisning ----------------
const PAGE = `<!DOCTYPE html><html lang="no"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Poengløp Brikkesys-API v${VERSION}</title><style>
:root{--ink:#1B2A21;--muted:#5A6A5F;--line:#D2DBD1;--paper:#EDF1EB;--accent:#A3238E}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,"Segoe UI",Roboto,Arial,sans-serif;color:var(--ink);background:var(--paper);font-size:14px;font-variant-numeric:tabular-nums}
header{display:flex;flex-wrap:wrap;gap:10px 20px;align-items:center;padding:12px 20px;background:#fff;border-bottom:1px solid var(--line)}
header h1{font-size:20px;margin:0 auto 0 0}header span{color:var(--muted)}
.wrap{display:grid;grid-template-columns:260px 1fr;min-height:calc(100vh - 56px)}
aside{background:#fff;border-right:1px solid var(--line);overflow:auto;max-height:calc(100vh - 56px)}
aside input{width:calc(100% - 20px);margin:10px;padding:7px 9px;border:1px solid var(--line);border-radius:4px}
aside button{display:flex;justify-content:space-between;width:100%;border:0;background:none;padding:7px 14px;text-align:left;cursor:pointer;font:inherit}
aside button:hover{background:var(--paper)}aside button.on{background:var(--paper);box-shadow:inset 3px 0 var(--accent);font-weight:600}
aside small{color:var(--muted)}main{padding:18px 22px;overflow:auto}
h2{margin:0 0 4px;font-size:22px}.tabs{display:flex;gap:4px;margin:14px 0}
.tabs button,.btn{border:1px solid var(--line);background:#fff;padding:6px 12px;border-radius:4px;cursor:pointer;font:inherit;color:inherit;text-decoration:none}
.tabs button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.tw{overflow:auto;background:#fff;border:1px solid var(--line);border-radius:6px;max-height:70vh}
table{border-collapse:collapse;font-size:13px;width:100%}th,td{padding:5px 9px;border-bottom:1px solid var(--line);white-space:nowrap;text-align:left;max-width:360px;overflow:hidden;text-overflow:ellipsis}
th{position:sticky;top:0;background:#FAFBF9;color:var(--muted);cursor:pointer}td.null{color:#aab}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px}.bar input{padding:6px 9px;border:1px solid var(--line);border-radius:4px}
pre{background:#fff;border:1px solid var(--line);border-radius:6px;padding:12px;overflow:auto;font-size:12px}
.muted{color:var(--muted)}.err{background:#FBE7E5;border-left:4px solid #B3261E;padding:10px 14px;border-radius:4px}
@media(max-width:760px){.wrap{grid-template-columns:1fr}aside{max-height:240px}}
</style></head><body>
<header><h1>Poengløp Brikkesys-API <span>v${VERSION}</span></h1><span id="info">Kobler til …</span>
<a class="btn" href="/api" target="_blank">API-oversikt</a><button class="btn" id="exp">Eksporter alt til filer</button></header>
<div class="wrap"><aside><input id="filter" placeholder="Finn tabell"><div id="list"></div></aside>
<main id="main"><p class="muted">Velg en tabell til venstre.</p></main></div>
<script>
const $=s=>document.querySelector(s);const esc=v=>String(v??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const get=async u=>{const r=await fetch(u);const j=await r.json();if(!r.ok)throw new Error(j.error);return j};
let tables=[],cur=null,view='data',st={offset:0,limit:100,order:'',dir:'asc',search:''};
async function init(){try{const i=await get('/api/info');$('#info').textContent=i.database+' @ '+i.host+' · MySQL '+i.mysqlVersion+' · '+i.tableCount+' tabeller';
tables=await get('/api/tables');list()}catch(e){$('#main').innerHTML='<div class="err">Får ikke koblet til databasen: <b>'+esc(e.message)+'</b><br>Kontroller poeng-brikkesys-config.json og start programmet på nytt.</div>';$('#info').textContent='Ikke tilkoblet'}}
function list(){const f=$('#filter').value.toLowerCase();$('#list').innerHTML=tables.filter(t=>t.name.toLowerCase().includes(f)).map(t=>'<button data-t="'+esc(t.name)+'" class="'+(t.name===cur?'on':'')+'"><span>'+esc(t.name)+'</span><small>'+t.approxRows+'</small></button>').join('')}
$('#filter').oninput=list;$('#list').onclick=e=>{const b=e.target.closest('[data-t]');if(b){cur=b.dataset.t;st={offset:0,limit:100,order:'',dir:'asc',search:''};list();show()}};
async function show(){const m=$('#main');const t=encodeURIComponent(cur);
m.innerHTML='<h2>'+esc(cur)+'</h2><div class="tabs"><button data-v="data" class="'+(view==='data'?'on':'')+'">Data</button><button data-v="struct" class="'+(view==='struct'?'on':'')+'">Struktur</button><a class="btn" href="/api/tables/'+t+'/csv">Last ned CSV</a><a class="btn" href="/api/tables/'+t+'/json">Last ned JSON</a></div><div id="body" class="muted">Leser …</div>';
m.querySelector('.tabs').onclick=e=>{const v=e.target.dataset.v;if(v){view=v;show()}};
try{if(view==='struct'){const s=await get('/api/tables/'+t);
$('#body').innerHTML='<p>'+s.rowCount+' rader, '+s.columns.length+' kolonner.</p><div class="tw"><table><thead><tr><th>Kolonne</th><th>Type</th><th>Null</th><th>Nøkkel</th><th>Standard</th><th>Ekstra</th></tr></thead><tbody>'+s.columns.map(c=>'<tr><td><b>'+esc(c.name)+'</b></td><td>'+esc(c.type)+'</td><td>'+esc(c.nullable)+'</td><td>'+esc(c.keyType)+'</td><td>'+esc(c.defaultValue)+'</td><td>'+esc(c.extra)+'</td></tr>').join('')+'</tbody></table></div><h3>CREATE TABLE</h3><pre>'+esc(s.createSql)+'</pre>'}
else{const q=new URLSearchParams({limit:st.limit,offset:st.offset});if(st.order){q.set('order',st.order);q.set('dir',st.dir)}if(st.search)q.set('search',st.search);
const d=await get('/api/tables/'+t+'/rows?'+q);const cols=d.rows.length?Object.keys(d.rows[0]):[];
$('#body').innerHTML='<div class="bar"><input id="s" placeholder="Søk i alle kolonner" value="'+esc(st.search)+'"><button class="btn" id="prev">Forrige</button><span>'+(d.total?d.offset+1:0)+'–'+Math.min(d.offset+d.limit,d.total)+' av '+d.total+'</span><button class="btn" id="next">Neste</button></div>'+
(cols.length?'<div class="tw"><table><thead><tr>'+cols.map(c=>'<th data-c="'+esc(c)+'">'+esc(c)+(st.order===c?(st.dir==='asc'?' ▲':' ▼'):'')+'</th>').join('')+'</tr></thead><tbody>'+d.rows.map(r=>'<tr>'+cols.map(c=>r[c]===null?'<td class="null">NULL</td>':'<td title="'+esc(r[c])+'">'+esc(r[c])+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>':'<p class="muted">Ingen rader.</p>');
$('#s').onchange=e=>{st.search=e.target.value;st.offset=0;show()};$('#prev').onclick=()=>{st.offset=Math.max(0,st.offset-st.limit);show()};$('#next').onclick=()=>{if(st.offset+st.limit<d.total){st.offset+=st.limit;show()}};
$('#body').querySelector('thead')?.addEventListener('click',e=>{const c=e.target.closest('[data-c]');if(!c)return;st.dir=st.order===c.dataset.c&&st.dir==='asc'?'desc':'asc';st.order=c.dataset.c;show()})}}
catch(e){$('#body').innerHTML='<div class="err">'+esc(e.message)+'</div>'}}
$('#exp').onclick=async()=>{const b=$('#exp');b.disabled=true;b.textContent='Eksporterer …';try{const r=await fetch('/api/export',{method:'POST',headers:{'X-Poenglop':'1'}});const j=await r.json();if(!r.ok)throw new Error(j.error);alert('Eksportert '+j.tables+' tabeller til:\\n'+j.folder)}catch(e){alert('Eksport feilet: '+e.message)}b.disabled=false;b.textContent='Eksporter alt til filer'};
init();
</script></body></html>`;

// ---------------- Start ----------------
(async () => {
  const args = process.argv.slice(2);
  if (args.includes('--test') || args.includes('--eksport')) {
    try {
      const i = await info();
      console.log(`\n  Tilkoblet ${i.database} på ${i.host}:${i.port} (MySQL ${i.mysqlVersion}), ${i.tableCount} tabeller.`);
      if (args.includes('--eksport')) await exportAll();
      console.log('');
    } catch (e) { console.error('\n  Feil: ' + e.message + '\n  Kontroller ' + path.basename(CONFIG_FILE) + '.\n'); process.exitCode = 1; }
    await pool.end(); return;
  }
  if (!['127.0.0.1', 'localhost', '::1'].includes(config.server.host)) console.warn('\n  ADVARSEL: server.host er ' + config.server.host + '. API-et bør bare lytte på 127.0.0.1.\n');
  server.listen(config.server.port, config.server.host, () => {
    console.log(`\n  Poengløp Brikkesys-API v${VERSION}`);
    console.log(`  Database: ${config.mysql.user}@${config.mysql.host}:${config.mysql.port}/${DB}`);
    console.log(`  Åpne i nettleseren: http://${config.server.host}:${config.server.port}`);
    console.log('  Stopp med Ctrl+C\n');
  });
})();
