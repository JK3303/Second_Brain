'use strict';

const MARKER = '<!-- ob1-gate-status -->';
const WORKFLOW = '.github/workflows/ob1-gate-v2.yml';
const CONCLUSIONS = new Set(['success', 'failure', 'cancelled', 'timed_out', 'action_required', 'neutral', 'skipped', 'stale']);

function eligibleRun(run, repository, workflowId) {
  return run.repository?.full_name === repository &&
    run.workflow_id === workflowId && run.path === WORKFLOW &&
    run.event === 'pull_request' && run.status === 'completed' &&
    CONCLUSIONS.has(run.conclusion) && Number.isSafeInteger(run.id) && run.id > 0 &&
    Number.isSafeInteger(run.run_attempt) && run.run_attempt > 0 &&
    /^[0-9a-f]{40}$/.test(run.head_sha || '') &&
    typeof run.head_repository?.full_name === 'string';
}

function matches(pr, run, repository) {
  return Number.isSafeInteger(pr.number) && pr.number > 0 && pr.state === 'open' &&
    pr.base?.repo?.full_name === repository && pr.base?.ref === 'main' &&
    pr.head?.sha === run.head_sha &&
    pr.head?.repo?.full_name === run.head_repository.full_name &&
    pr.head?.ref === run.head_branch;
}

function bodyFor(run, repository) {
  const url = `https://github.com/${repository}/actions/runs/${run.id}`;
  return `${MARKER}\n<!-- run:${run.id}:${run.run_attempt} -->\n` +
    `## OB1 gate status\n\nWorkflow conclusion: **${run.conclusion}**.\n\n` +
    `Head: \`${run.head_sha}\`. [Read the checks and job summary](${url}).\n\n` +
    'This reports GitHub workflow status only. It does not approve the contribution, ' +
    'verify author trust, clear security labels, or authorize an AI review. ' +
    'Maintainer review is still required.';
}

function newerThan(comment, run) {
  const stamp = /<!-- run:(\d+):(\d+) -->/.exec(comment.body || '');
  if (!stamp) return false;
  return Number(stamp[1]) > run.id ||
    (Number(stamp[1]) === run.id && Number(stamp[2]) > run.run_attempt);
}

async function followup({ github, context, core }) {
  const { owner, repo } = context.repo;
  const repository = `${owner}/${repo}`;
  const runId = context.payload.workflow_run?.id;
  if (!Number.isSafeInteger(runId) || runId <= 0) throw new Error('Invalid workflow run ID');
  const { data: workflow } = await github.rest.actions.getWorkflow({ owner, repo, workflow_id: 'ob1-gate-v2.yml' });
  const { data: run } = await github.rest.actions.getWorkflowRun({ owner, repo, run_id: runId });
  if (!eligibleRun(run, repository, workflow.id)) {
    core.info('No follow-up: run identity, event, or terminal state does not match.');
    return;
  }
  // Fork workflow_run payloads can omit pull_requests. Ask GitHub for association,
  // then fetch live PRs instead of trusting artifact-supplied PR numbers.
  const associated = await github.paginate(github.rest.repos.listPullRequestsAssociatedWithCommit,
    { owner, repo, commit_sha: run.head_sha, per_page: 100 });
  const candidates = [];
  for (const number of new Set(associated.map(pr => pr.number))) {
    if (!Number.isSafeInteger(number) || number <= 0) continue;
    const { data: pr } = await github.rest.pulls.get({ owner, repo, pull_number: number });
    if (matches(pr, run, repository)) candidates.push(pr);
  }
  if (candidates.length !== 1) {
    core.info('No follow-up: no unique open PR matches the source repository, branch, and head.');
    return;
  }
  const pr = candidates[0];
  const comments = await github.paginate(github.rest.issues.listComments,
    { owner, repo, issue_number: pr.number, per_page: 100 });
  const existing = comments.filter(c => c.user?.login === 'github-actions[bot]' &&
    c.user?.type === 'Bot' && c.body?.startsWith(MARKER)).sort((a, b) => b.id - a.id)[0];
  if (existing && newerThan(existing, run)) return;
  // Narrow the push race by rechecking head immediately before writing.
  const { data: current } = await github.rest.pulls.get({ owner, repo, pull_number: pr.number });
  if (!matches(current, run, repository)) return;
  const body = bodyFor(run, repository);
  if (existing?.body === body) return;
  if (existing) {
    await github.rest.issues.updateComment({ owner, repo, comment_id: existing.id, body });
  } else {
    await github.rest.issues.createComment({ owner, repo, issue_number: pr.number, body });
  }
}

module.exports = followup;
Object.assign(module.exports, { eligibleRun, matches, bodyFor, newerThan });
