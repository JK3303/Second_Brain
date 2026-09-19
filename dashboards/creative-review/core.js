(function (root) {
  'use strict';
  const STATES = ['explore', 'revise', 'held', 'rejected'];
  const FIELDS = ['title', 'proposition', 'audience', 'protect', 'change', 'questions', 'rights', 'critique', 'revision'];
  const clone = value => JSON.parse(JSON.stringify(value));
  const option = id => Object.fromEntries([['id', id], ['state', 'explore'], ...FIELDS.map(k => [k, ''])]);
  function empty() { return { version: 1, objective: '', reviewer: '', roundNote: '', options: [option('direction-1'), option('direction-2')], history: [] }; }
  function text(value, label) {
    if (typeof value !== 'string' || value.length > 6000) throw Error(`${label} must be text of at most 6000 characters.`);
    return value;
  }
  function snapshot(value) {
    if (!value || typeof value !== 'object' || !Array.isArray(value.options) || value.options.length < 1 || value.options.length > 8) {
      throw Error('A review needs one to eight directions.');
    }
    const ids = new Set();
    const options = value.options.map(o => {
      if (!o || typeof o.id !== 'string' || !/^[a-z0-9-]{1,60}$/.test(o.id) || ids.has(o.id)) throw Error('Direction IDs must be unique.');
      ids.add(o.id);
      if (!STATES.includes(o.state)) throw Error('Unknown direction state.');
      return { id: o.id, state: o.state, ...Object.fromEntries(FIELDS.map(k => [k, text(o[k], k)])) };
    });
    return { objective: text(value.objective, 'Objective'), reviewer: text(value.reviewer, 'Reviewer'), options };
  }
  function validate(value) {
    if (!value || value.version !== 1 || !Array.isArray(value.history) || value.history.length > 30) throw Error('Unsupported or oversized review record.');
    const current = snapshot(value);
    const history = value.history.map((entry, index) => {
      if (!entry || entry.number !== index + 1 || typeof entry.at !== 'string' || !Number.isFinite(Date.parse(entry.at))) throw Error('Invalid round history.');
      return { number: entry.number, at: entry.at, reason: text(entry.reason, 'Round note'), ...snapshot(entry) };
    });
    return { version: 1, ...current, roundNote: text(value.roundNote ?? '', 'Draft round note'), history };
  }
  function capture(value, reason, at = new Date().toISOString()) {
    const result = validate(value);
    if (!reason.trim()) throw Error('Add a round note before recording.');
    if (!result.objective.trim() || !result.reviewer.trim()) throw Error('Add the objective and reviewer first.');
    if (result.history.length >= 30) throw Error('This review has 30 rounds. Export it before starting a new review.');
    if (result.options.some(o => !o.title.trim())) throw Error('Give each direction a name before recording.');
    result.history.push({ number: result.history.length + 1, at, reason: text(reason, 'Round note'), ...clone(snapshot(result)) });
    result.roundNote = '';
    const checked = validate(result);
    if (new TextEncoder().encode(JSON.stringify(checked, null, 2)).length > 512000) throw Error('Recording would exceed 512 KB. Export this review and start a separate review.');
    return checked;
  }
  function parse(raw) {
    if (typeof raw !== 'string' || new TextEncoder().encode(raw).length > 512000) throw Error('Review files must be at most 512 KB.');
    return validate(JSON.parse(raw));
  }
  function changes(before, after) {
    const a = snapshot(before), b = snapshot(after), result = [];
    for (const key of ['objective', 'reviewer']) if (a[key] !== b[key]) result.push({ direction: 'Review', field: key, before: a[key], after: b[key] });
    const old = new Map(a.options.map(o => [o.id, o]));
    const now = new Map(b.options.map(o => [o.id, o]));
    for (const id of new Set([...old.keys(), ...now.keys()])) {
      if (!old.has(id) || !now.has(id)) {
        result.push({ direction: (now.get(id) || old.get(id)).title, field: 'direction', before: old.has(id) ? 'present' : 'absent', after: now.has(id) ? 'present' : 'absent' });
      } else {
        for (const key of ['state', ...FIELDS]) if (old.get(id)[key] !== now.get(id)[key]) {
          result.push({ direction: now.get(id).title, field: key, before: old.get(id)[key], after: now.get(id)[key] });
        }
      }
    }
    return result;
  }
  const api = { STATES, FIELDS, empty, option, validate, capture, parse, changes };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.ReviewCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
