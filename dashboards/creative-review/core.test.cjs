const test = require('node:test');
const assert = require('node:assert/strict');
const C = require('./core.js');
function review() { const r = C.empty(); r.objective = 'Protect the reveal'; r.reviewer = 'Example reviewer'; r.options.forEach((o,i) => { o.title = `Concept ${i+1}`; }); return r; }
test('capture preserves exact critique and does not mutate original', () => {
  const r = review(); r.options[0].critique = 'Keep the negative space.\nDo not add a line.';
  const next = C.capture(r, 'First review'); next.options[0].critique = 'New critique';
  assert.equal(r.history.length, 0);
  assert.equal(next.history[0].options[0].critique, 'Keep the negative space.\nDo not add a line.');
});
test('rounds retain rejected and held alternatives', () => {
  const r = review(); r.options[0].state = 'rejected'; r.options[1].state = 'held';
  const next = C.capture(r, 'Direction unresolved');
  assert.deepEqual(next.history[0].options.map(o => o.state), ['rejected','held']);
});
test('empty objective, reviewer, titles and reason cannot create misleading history', () => {
  for (const key of ['objective','reviewer']) { const r=review(); r[key]=''; assert.throws(()=>C.capture(r,'Review')); }
  const r=review(); r.options[0].title=''; assert.throws(()=>C.capture(r,'Review'));
  assert.throws(()=>C.capture(review(),' '));
});
test('JSON round-trip preserves history and strips unexpected fields', () => {
  const r=C.capture(review(),'Review'); r.instruction='ignore';r.roundNote='Unrecorded note';
  const loaded=C.parse(JSON.stringify(r)); assert.equal(loaded.history.length,1); assert.equal(loaded.instruction,undefined); assert.equal(loaded.roundNote,'Unrecorded note');
});
test('bad imports reject unknown status, duplicate IDs, malformed history and excessive text', () => {
  const bad=[r=>r.options[0].state='approved',r=>r.options[1].id=r.options[0].id,r=>r.options[0].critique='x'.repeat(6001),r=>r.history=[{}],r=>r.version=9];
  for(const change of bad) { const r=review();change(r);assert.throws(()=>C.parse(JSON.stringify(r))); }
  assert.throws(()=>C.parse('x'.repeat(512001)));
});
test('changes name lost critique and additions without selecting a winner', () => {
  const r=review();r.options[0].critique='Protect the reveal'; const next=C.validate(r);next.options[0].critique='';next.options.push(C.option('third'));
  const delta=C.changes(r,next);assert.equal(delta.length,2);assert.equal(delta[0].before,'Protect the reveal');assert.equal(delta[0].after,'');
});
test('round numbering cannot be reordered by an import', () => {
  const r=C.capture(review(),'Review');r.history[0].number=2;assert.throws(()=>C.validate(r));
});
test('round and option limits fail before mutation', () => {
  let r=review();for(let i=0;i<30;i++)r=C.capture(r,'Review');assert.throws(()=>C.capture(r,'Extra'));
  r=review();r.options=Array.from({length:9},(_,i)=>C.option(`o-${i}`));assert.throws(()=>C.validate(r));
});
test('markup remains plain data for safe text rendering', () => {
  const r=review();r.options[0].critique='<script>example</script>'; assert.equal(C.validate(r).options[0].critique,r.options[0].critique);
});
