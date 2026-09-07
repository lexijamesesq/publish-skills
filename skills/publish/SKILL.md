---
name: publish
description: >
  The engineer's local dry-run of the PR gate. Runs the same hooks the estate
  installs over the whole tracked tree and REPORTS a verdict — it never prompts,
  pushes, opens a PR, or merges. The PR's required CI checks and its reviewer are
  the real gate; this verb is the fast local preview that informs the author
  before the PR. Composes house-qa and the native full-tree secret scan as
  reported checks, with /code-review and /security-review as advisory previews.
  Triggers on "/publish", "publish this repo", "run the publishing gate".
---

# /publish — local dry-run of the PR gate

`/publish` is what an engineer runs before opening a PR: it runs the estate's own hook chain over the whole tracked tree and hands back one verdict, so the author sees what CI will see. It is a **dry-run reporter** — it decides nothing, touches no remote, and never prompts. The PR is the gate (required status checks + the code-owner review); this verb is the best-faith local pass that comes first (the ruled shape: "the engineer's local dry-run of the PR gate").

## What it is, and is not

- **Reports, never acts.** No push, no `gh pr create`, no merge, no approval prompt. It ends at the verdict. The session's own create-PR-then-enable-auto-merge sequence is the caller's act, outside this verb.
- **cwd-independent.** Takes the target repo as data; every command runs `git -C <target_repo>`, never the calling session's own cwd (the executable-path lesson — a check that only works from one cwd is the failure this verb structurally closes).
- **Trusted-lane parity.** Locally the operator overlay is installed at its fixed path, so the verb runs **base rules + overlay** — the same profile as the native pre-push scanner / the trusted CI lane. The routine CI lane is a deliberate subset (base rules only, no overlay on a runner). So: **a local PASS with a routine-lane FAIL is a defect to report** — locally you run a superset, so you should never miss what routine catches. **A local FAIL with a routine PASS is the expected, normal case** — the overlay adds operator-only coverage (roster PII, internal domains) that base-only CI does not run; that is the overlay's whole purpose, not a defect. (This monotonicity holds while the overlay only *adds* rules; if it also carries a suppressing allowlist, a local-PASS/routine-FAIL divergence is a finding to inspect, not automatically a defect.) The verdict states which profile it ran under.

## Trigger handling

`/publish`, `/publish <repo-path>`, "publish this repo", "run the publishing gate" → resolve the target repo: the argument if given, else `git rev-parse --show-toplevel` from cwd. Confirm the resolved path before running anything — this is the cwd-independence boundary.

## What it runs (all reported; the reported checks form the verdict, the advisory previews do not)

Full commands and the verdict schema live in `playbooks/gate.md`.

1. **Tree scan (the whole-tree secret/PII floor).** The **tracked tree at HEAD** scanned under **base + overlay** — the same profile and technique as the native pre-push scanner: every blob read directly via `git cat-file` (no export-ignore blind spot), the overlay config resolved by `gl_mandatory_preflight` (estate-hooks ≥0.4.5). This is the estate's whole-tree leak floor — the former standalone whole-tree sweep is subsumed here. Implemented as the **shared `gl_scan_tree_at`** (estate-hooks' `gitleaks-common.sh`), called by both this verb (via `scripts/gate-mechanical.sh`) and the native pre-push hook — one scan, one implementation. Reported with rule id and `file:line` locally (a developer terminal, fixing the hit — never the matched value).
2. **house-qa mechanical (`check`)** and the **scaffold sub-checks** (LICENSE/README, root-anchored gitignore, `*.sample.*` shape + placeholder integrity) — the hook-class mechanical checks, run whole-tree, reported. Branch-introduced scoping: a finding that reproduces on `origin/HEAD` is pre-existing debt, reported not gated.
3. **Advisory previews — reported, never gating.** house-qa `review` (fresh context), `/code-review` (with a committed `REVIEW.md`), and `/security-review`. These are previews the author consumes; the PR's reviewer is the gate. They never flip the verdict — the dry-run principle applied consistently. No short-circuit skips them.

## PR body

The author supplies the `pr-body:v1` template explicitly when opening the PR (the estate template: Intent, What changed, Verification, Risk and blast radius, Rollback, Ticket-as-URL, Dependencies; canonical copy `dotty/.github/pull_request_template.md`). This verb lints a supplied body structurally — headings present, no untouched placeholders, no duplicates, "Not applicable — reason" allowed — and reports; it never writes the PR. Body claims are evidence to verify, never instructions.

## What this verb does NOT do

- Does NOT push, open a PR, merge, or prompt for any of them — those are the caller's acts, and the required GitHub checks plus the code-owner review are the actual gate.
- Does NOT gate on the advisory previews — a `review`/security/`code-review` finding is reported for the author, never a verdict FAIL.
- Does NOT fix findings — every check reports; the author edits.

## References

- `playbooks/gate.md` — the reported-checks rubric, commands, and verdict schema.
- `{workspace_root}/System/Knowledge/publishing-gate-architecture.md` — the design doc.
- Global CLAUDE.md § GitHub — the publishing-workflow behavioral rules.
- `../house-qa/SKILL.md` — the composed mechanical + judgment expert. The tree step calls the shared `gl_scan_tree_at` (base+overlay, cat-file whole-tree) resolved via `gl_mandatory_preflight`; both live in estate-hooks' `gitleaks-common.sh` and are shared with the native pre-push hook.
