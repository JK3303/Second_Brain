/* global ReviewCore */
'use strict';
const C = ReviewCore;
let state = C.empty();
let dirty = false;
const byId = id => document.getElementById(id);
const labels = { title: 'Direction name', proposition: 'Creative proposition', audience: 'Audience effect',
  protect: 'Protect this', change: 'Change this', questions: 'Open questions', rights: 'Evidence / rights questions',
  critique: 'Human critique — exact words', revision: 'Revision response — what changed and why' };
const statuses = { explore: 'Explore', revise: 'Selected for revision', held: 'Held', rejected: 'Rejected' };
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function message(text) { byId('message').textContent = text; }
function bind(input, update) { input.addEventListener('input', () => { update(input.value); dirty = true; byId('backup-panel').hidden = true; }); }
bind(byId('objective'), value => { state.objective = value; });
bind(byId('reviewer'), value => { state.reviewer = value; });
bind(byId('reason'), value => { state.roundNote = value; });
function render() {
  byId('backup-panel').hidden = true;
  byId('backup-text').value = '';
  byId('objective').value = state.objective;
  byId('reviewer').value = state.reviewer;
  byId('reason').value = state.roundNote;
  const container = byId('directions'); container.replaceChildren();
  state.options.forEach((option, index) => {
    const card = element('article', undefined, 'direction');
    card.append(element('p', `DIRECTION ${String(index + 1).padStart(2, '0')}`, 'eyebrow'));
    for (const key of C.FIELDS) {
      const label = element('label', labels[key]);
      const input = element(key === 'title' ? 'input' : 'textarea');
      input.id = `${option.id}-${key}`;
      label.htmlFor = input.id;
      input.value = option[key]; input.maxLength = 6000;
      if (key !== 'title') input.rows = key === 'critique' || key === 'revision' ? 3 : 2;
      bind(input, value => { option[key] = value; });
      label.append(input); card.append(label);
    }
    const label = element('label', 'Human disposition');
    const select = element('select'); select.id = `${option.id}-state`; label.htmlFor = select.id;
    for (const status of C.STATES) { const choice = element('option', statuses[status]); choice.value = status; select.append(choice); }
    select.value = option.state;
    bind(select, value => { option.state = value; });
    label.append(select); card.append(label);
    const remove = element('button', 'Remove direction', 'quiet');
    remove.disabled = state.options.length === 1;
    remove.addEventListener('click', () => {
      if (!window.confirm('Remove this direction from the current round? Previously recorded rounds are preserved.')) return;
      state.options = state.options.filter(o => o.id !== option.id); dirty = true; render();
    });
    card.append(remove); container.append(card);
  });
  byId('add').disabled = state.options.length >= 8;
  byId('round-count').textContent = `${state.history.length} recorded round${state.history.length === 1 ? '' : 's'}`;
  const history = byId('history'); history.replaceChildren();
  if (!state.history.length) history.append(element('p', 'Your first round will appear here. Record it before revising.', 'empty'));
  state.history.forEach((round, index) => {
    const details = element('details');
    details.append(element('summary', `Round ${round.number} · ${round.reviewer} · ${new Date(round.at).toLocaleString()}`));
    details.append(element('p', round.reason, 'verbatim'));
    details.append(element('p', `Objective: ${round.objective}`, 'verbatim'));
    for (const option of round.options) {
      details.append(element('h3', `${option.title} — ${statuses[option.state]}`));
      for (const field of C.FIELDS.filter(k => k !== 'title')) {
        if (option[field]) details.append(element('p', `${labels[field]}: ${option[field]}`, 'verbatim'));
      }
    }
    if (index > 0) {
      const delta = C.changes(state.history[index - 1], round);
      details.append(element('h3', 'Changes since the previous round'));
      if (!delta.length) details.append(element('p', 'No field changes; the round note may record a new interpretation.'));
      for (const item of delta) details.append(element('p', `${item.direction} / ${labels[item.field] || item.field}\nBefore: ${item.before || '(empty)'}\nAfter: ${item.after || '(empty)'}`, 'verbatim delta'));
    }
    history.append(details);
  });
}
byId('add').addEventListener('click', () => {
  let id = 1;
  const used = new Set([...state.options, ...state.history.flatMap(r => r.options)].map(o => o.id));
  while (used.has(`direction-${id}`)) id++;
  state.options.push(C.option(`direction-${id}`)); dirty = true; render();
  byId(`direction-${id}-title`).focus();
});
byId('capture').addEventListener('click', () => {
  try { state = C.capture(state, byId('reason').value); dirty = true; byId('reason').value = ''; render(); message('Round recorded in this page. Export to keep it after closing.'); }
  catch (error) { message(error.message); }
});
function serialize() {
  const raw = JSON.stringify(C.validate(state), null, 2);
  if (new TextEncoder().encode(raw).length > 512000) throw Error('Review exceeds the 512 KB import limit. Shorten current fields or preserve the review in smaller files.');
  return raw;
}
byId('backup').addEventListener('click', () => {
  try {
    byId('backup-text').value = serialize(); byId('backup-panel').hidden = false;
    byId('backup-text').focus(); byId('backup-text').select();
    message('Copy this JSON into a private .json file. This backup reflects the review when you clicked Show JSON backup.');
  } catch (error) { message(error.message); }
});
byId('export').addEventListener('click', () => {
  try {
    const raw = serialize();
    const url = URL.createObjectURL(new Blob([raw], { type: 'application/json' }));
    const link = element('a'); link.href = url; link.download = 'creative-review.json';
    document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    // A browser download can be cancelled: do not clear the unsaved-change warning.
    message('Download requested. Verify creative-review.json is saved before closing.');
  } catch (error) { message(error.message); }
});
byId('import').addEventListener('change', async event => {
  const file = event.target.files[0]; if (!file) return;
  try {
    if (file.size > 512000) throw Error('Review files must be at most 512 KB.');
    const imported = C.parse(await file.text());
    if (dirty && !window.confirm('Replace the current review? Export it first if you want to keep it.')) return;
    state = imported; dirty = false; byId('reason').value = ''; render(); message('Imported review loaded locally. No data was uploaded.');
  } catch (error) { message(`Import failed: ${error.message}`); }
  finally { event.target.value = ''; }
});
window.addEventListener('beforeunload', event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } });
render();
