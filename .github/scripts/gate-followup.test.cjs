'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const followup = require('./gate-followup.cjs');

const repository = 'example/brain';
const makeRun = () => ({ id: 100, run_attempt: 1, workflow_id: 7,
  path: '.github/workflows/ob1-gate-v2.yml', repository: { full_name: repository },
  event: 'pull_request', status: 'completed', conclusion: 'success', head_sha: 'a'.repeat(40),
  head_repository: { full_name: 'contributor/brain' }, head_branch: 'feature' });
const makePR = () => ({ number: 4, state: 'open',
  base: { ref: 'main', repo: { full_name: repository } },
  head: { sha: 'a'.repeat(40), ref: 'feature', repo: { full_name: 'contributor/brain' } } });

function harness({ run = makeRun(), prs = [makePR()], comments = [], lastPR } = {}) {
  const writes = [];
  let reads = 0;
  const listPRs = () => {};
  const listComments = () => {};
  const github = { rest: {
    actions: { getWorkflow: async () => ({ data: { id: 7 } }), getWorkflowRun: async () => ({ data: run }) },
    repos: { listPullRequestsAssociatedWithCommit: listPRs },
    pulls: { get: async ({ pull_number }) => ({ data: (++reads > prs.length && lastPR) || prs.find(p => p.number === pull_number) }) },
    issues: { listComments,
      createComment: async v => writes.push({ kind: 'create', ...v }),
      updateComment: async v => writes.push({ kind: 'update', ...v }) } },
  paginate: async method => method === listPRs ? prs : comments };
  return { writes, args: { github, context: { repo: { owner: 'example', repo: 'brain' },
    payload: { workflow_run: { id: 100 } } }, core: { info() {} } } };
}

test('posts status for unique verified fork PR without any artifact', async () => {
  const h = harness(); await followup(h.args);
  assert.equal(h.writes.length, 1);
  assert.equal(h.writes[0].issue_number, 4);
  assert.match(h.writes[0].body, /workflow status only/);
});

test('wrong workflow, target event, and incomplete runs cannot write', async () => {
  for (const patch of [{ workflow_id: 8 }, { event: 'pull_request_target' }, { status: 'in_progress' },
    { path: '.github/workflows/other.yml' }, { repository: { full_name: 'other/repo' } },
    { conclusion: 'invented' }]) {
    const h = harness({ run: { ...makeRun(), ...patch } }); await followup(h.args);
    assert.deepEqual(h.writes, []);
  }
});

test('closed, stale, wrong source, and wrong base PRs cannot write', async () => {
  for (const patch of [{ state: 'closed' }, { head: { ...makePR().head, sha: 'b'.repeat(40) } },
    { head: { ...makePR().head, repo: { full_name: 'different/brain' } } },
    { base: { ...makePR().base, ref: 'release' } }]) {
    const h = harness({ prs: [{ ...makePR(), ...patch }] }); await followup(h.args);
    assert.deepEqual(h.writes, []);
  }
});

test('ambiguous associations do not pick an arbitrary PR', async () => {
  const h = harness({ prs: [makePR(), { ...makePR(), number: 5 }] }); await followup(h.args);
  assert.deepEqual(h.writes, []);
});

test('head change while reading comments prevents write', async () => {
  const h = harness({ lastPR: { ...makePR(), head: { ...makePR().head, sha: 'c'.repeat(40) } } });
  await followup(h.args); assert.deepEqual(h.writes, []);
});

test('another user cannot spoof the owned comment marker', async () => {
  const h = harness({ comments: [{ id: 9, body: '<!-- ob1-gate-status -->',
    user: { login: 'someone', type: 'User' } }] });
  await followup(h.args); assert.equal(h.writes[0].kind, 'create');
});

test('rerun updates only the GitHub Actions owned comment', async () => {
  const h = harness({ comments: [{ id: 9, body: '<!-- ob1-gate-status -->\n<!-- run:99:1 -->',
    user: { login: 'github-actions[bot]', type: 'Bot' } }] });
  await followup(h.args); assert.equal(h.writes[0].kind, 'update');
  assert.equal(h.writes[0].comment_id, 9);
});

test('idempotent delivery and older reruns leave current status alone', async () => {
  for (const body of [followup.bodyFor(makeRun(), repository),
    '<!-- ob1-gate-status -->\n<!-- run:101:1 -->', '<!-- ob1-gate-status -->\n<!-- run:100:2 -->']) {
    const h = harness({ comments: [{ id: 9, body, user: { login: 'github-actions[bot]', type: 'Bot' } }] });
    await followup(h.args); assert.deepEqual(h.writes, []);
  }
});

test('API failures surface rather than imply successful follow-up', async () => {
  const h = harness(); h.args.github.rest.actions.getWorkflowRun = async () => { throw Error('offline'); };
  await assert.rejects(() => followup(h.args), /offline/);
  assert.deepEqual(h.writes, []);
});

test('workflow trust boundary has no artifact consumption or automatic AI escalation', () => {
  const workflow = fs.readFileSync(path.join(__dirname, '../workflows/ob1-pr-followups.yml'), 'utf8');
  assert.doesNotMatch(workflow, /download-artifact|unzip|ANTHROPIC|id-token|allow-unsafe-pr-checkout/);
  assert.match(workflow, /ref: \$\{\{ github.event.repository.default_branch \}\}/);
  assert.match(workflow, /persist-credentials: false/);
  const gate = fs.readFileSync(path.join(__dirname, '../workflows/ob1-gate-v2.yml'), 'utf8');
  assert.match(gate, /\r?\n  pull_request:\r?\n/);
  assert.doesNotMatch(gate, /pull_request_target|allow-unsafe-pr-checkout/);
});
