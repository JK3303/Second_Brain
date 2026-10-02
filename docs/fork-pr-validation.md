# Fork PR validation and follow-up trust

```text
Fork pull_request -> restricted read-only gate -> checks + job summary
GitHub workflow_run -> trusted default-branch code -> verify live PR -> status link
```

## Problem

The previous gate checked out a fork head during `pull_request_target`.
GitHub's checkout action refuses that combination by default. The failure occurs
before contribution checks, so a correct contribution cannot obtain a gate result.
The former privileged follow-up also consumed an artifact to select a PR, trust
an author association, clear security labels, and start an API-key-backed AI review.
Such artifact fields are not an appropriate authority source after a fork run.

## Changes

- The gate runs on `pull_request` with `contents: read`, no persisted checkout
  credentials, and the existing validation rules and job summary.
- The follow-up checks out only trusted default-branch code. It fetches the run,
  workflow identity, associated PRs, and current head from GitHub's API.
- Only one open PR with matching repository, branch, base, and head receives a
  status link. Stale or ambiguous associations produce no comment.
- The follow-up neither reads artifacts nor automatically starts an AI review.
  It does not modify security or triage labels. Existing labels remain unchanged.
- Detailed rule results remain in the gate's job summary. Maintainers decide when
  to request any additional review; workflow success is not contribution approval.

The automatic AI-review and label side effects are deliberately removed from this
untrusted-to-privileged chain. The separate maintainer-dispatched review workflow
is unchanged by this patch and is not claimed to have been security-audited here.

## Maintainer verification

1. Review and merge this workflow change using the normal maintainer process.
2. Approve a first-time fork contributor's workflow run when GitHub requests it.
3. Confirm `OB1 Review` reaches the checks and job summary without an unsafe-checkout
   override. A failed contribution should still fail the job.
4. Confirm the follow-up comment identifies the current head and links to that run.
5. Push a new head, then rerun an older job: the stale run must not overwrite the
   current PR status. No automatic AI review or security-label removal should occur.

This PR cannot activate its own default-branch follow-up code before merge.
Local tests use mocked GitHub API responses; they do not establish hosted success.
First-contributor approval and repository policy remain maintainer decisions.

## Local tests

```bash
node --test .github/scripts/gate-followup.test.cjs
```

Coverage includes fork association without artifacts, event/workflow identity,
stale heads, wrong source repositories, ambiguous PRs, head-change races,
comment ownership, idempotence, rerun order, and API failures.

## References

- [GitHub: securely using pull_request_target](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)
- [GitHub: secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [Checkout's safer defaults announcement](https://github.blog/changelog/2026-06-18-safer-pull_request_target-defaults-for-github-actions-checkout/)

This preserves the contribution workflow of Second_Brain and
[Nate B. Jones's Open Brain](https://github.com/NateBJones-Projects/OB1).
More practical systems: [Nate's writing](https://substack.com/@natesnewsletter)
and [website](https://natebjones.com).
