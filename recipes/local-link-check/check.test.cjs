const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {audit} = require('./check.cjs');

function fixture(t, text) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'local-links-'));
  t.after(() => fs.rmSync(root, {recursive: true, force: true}));
  fs.writeFileSync(path.join(root, 'README.md'), text);
  fs.writeFileSync(path.join(root, 'one (two).md'), '# Target');
  return root;
}

test('encoded spaces and balanced parentheses with titles', t => {
  const root = fixture(t, '[target](<one (two).md> "A title")');
  const report = audit(root, ['README.md']);
  assert.equal(report.references.length, 1);
  assert.equal(report.failures, 0);
});
test('reference links and images checked, fenced and inline code ignored', t => {
  const root = fixture(t, '[reference][id]\n\n[id]: <one (two).md>\n\n![image](missing.png)\n\n`[ignore](no.md)`\n\n```md\n[ignore](no.md)\n```');
  const report = audit(root, ['README.md']);
  assert.equal(report.references.length, 2);
  assert.equal(report.failures, 1);
});
test('source ranges point to containing block', t => {
  const root = fixture(t, '# Title\n\nA paragraph\nwith [link](missing.md).');
  const row = audit(root, ['README.md']).references[0];
  assert.equal(row.start_line, 3);
  assert.equal(row.end_line, 4);
});
test('root escape rejected without opening target', t => {
  const root = fixture(t, '[outside](../outside.md)');
  assert.equal(audit(root, ['README.md']).references[0].state, 'outside-root');
});
test('external and fragments explicitly unchecked', t => {
  const root = fixture(t, '[remote](https://example.com) [section](#missing)');
  const rows = audit(root, ['README.md']).references;
  assert.equal(rows[0].state, 'external-unchecked');
  assert.equal(rows[1].fragment_unchecked, true);
});
test('case mismatch detected even on case-insensitive hosts', t => {
  const root = fixture(t, '[case](readme.md)');
  assert.equal(audit(root, ['README.md']).references[0].state, 'path-case-mismatch');
});
test('raw HTML reported as unvalidated', t => {
  const root = fixture(t, '<a href="missing.md">HTML</a>');
  assert.ok(audit(root, ['README.md']).skipped_html.length);
});
test('invalid inputs fail', t => {
  const root = fixture(t, 'text');
  for (const files of [[], ['README.md', 'README.md'], ['../outside.md'], ['missing.md']]) {
    assert.throws(() => audit(root, files));
  }
  fs.writeFileSync(path.join(root, 'README.md'), Buffer.from([255]));
  assert.throws(() => audit(root, ['README.md']));
});
test('root-relative paths use explicit repository root', t => {
  const root = fixture(t, '[home](/README.md)');
  assert.equal(audit(root, ['README.md']).references[0].state, 'file-exists');
});
test('table cells without individual source maps retain an enclosing range', t => {
  const root = fixture(t, '# Links\n\n| Name |\n| --- |\n| [home](README.md) |');
  const row = audit(root, ['README.md']).references[0];
  assert.equal(row.state, 'file-exists');
  assert.ok(row.start_line <= 5 && row.end_line >= 5);
});
