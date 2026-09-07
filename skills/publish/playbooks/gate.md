
# Playbook: gate

The dry-run reporter's rubric. Every check here **reports**; the verb never gates a remote action, because it takes none. The reported checks (tree scan, house-qa mechanical, scaffold) form the verdict; the advisory previews (house-qa `review`, `/code-review`, `/security-review`) are reported but never flip it. Cheapest first, but there is no FAIL short-circuit — a local dry-run runs every check so the author sees the whole picture before the PR — the dry-run principle applied consistently.

## Input

```yaml
target_repo: <abs path>                 # resolved by SKILL.md; every command runs `-C <target_repo>`
visibility: public | private | unknown  # from `git -C <target_repo> remote get-url origin`; unknown -> ask
base_ref: origin/HEAD                    # requires `git remote set-head origin --auto` once per repo
scan_profile: base+overlay               # trusted-lane parity — the overlay is installed locally at its fixed path
```

## Reported checks (form the verdict)

**Branch-introduced scoping.** A scaffold or house-qa-mechanical finding that reproduces identically against an `origin/HEAD` worktree is PRE-EXISTING DEBT — carried in the verdict's `pre_existing_debt` block, reported on every run until dispositioned, never gated. Compare via `git -C <target_repo> worktree add <tmp> origin/HEAD`, re-run the failing sub-check, set-diff by `(check, file)`, `worktree remove`.

### 1. Tree scan — the whole-tree secret/PII floor

The **tracked tree at HEAD** scanned under **base + overlay** — the same profile and technique as the native pre-push scanner: every blob read directly via `git cat-file` (no `git archive` export-ignore blind spot), scanned under the operator overlay resolved at its fixed path. This is the estate's whole-tree leak floor; the former standalone tracked-HEAD sweep is subsumed here, so the verb carries no separate floor.

`scripts/gate-mechanical.sh <target_repo>` resolves `gitleaks-common.sh` from the **installed estate-hooks plugin** (its `resolve_gitleaks_common` order — never `~/bin/dotty`, which is a stale source), runs `gl_mandatory_preflight` (sets `GL_MANDATORY_CONFIG` = base+overlay from the fixed path; refuses on a missing/malformed overlay), then calls **`gl_scan_tree_at <repo> <report> HEAD`** — the single shared whole-tree scan (gitleaks-common.sh) that the native pre-push hook also calls — one implementation, not a second copy. If `gl_scan_tree_at` is absent from the resolved copy (an estate-hooks release predating it), the step fails **closed**, naming the release it needs — never a local reimplementation. This playbook never hand-writes a source path.

Locally this reports rule id + `file:line` for the author to fix (a developer terminal, never the matched value — redacted). PASS = zero findings under base+overlay. **Trusted-lane parity:** this profile equals the trusted CI lane's; the routine CI lane is base-only, a deliberate subset, so a local PASS with a routine-lane FAIL is a defect to report; a local FAIL with a routine PASS is expected (the overlay adds coverage), not a defect.

### 2. house-qa mechanical (`check`) + scaffold

`scripts/gate-mechanical.sh <target_repo> [--base <ref>] [--visibility …]` runs, in one invocation with per-step PASS/FAIL:
- **Scaffold:** root-anchored `.gitignore` effective (no tracked `evals/`/`scratch/`); LICENSE + README present; every operator-config referenced by tracked machinery has a `*.sample.*` counterpart; every tracked `*.sample.*` carries a placeholder marker.
- **house-qa `check`:** `qa.py <target_repo> --git-tracked-only --vault-root "$VAULT_ROOT" --json` with `--rosters-path` resolved live via `resolve-references-key.sh` (never hand-typed). PASS = zero HIGH outside `*/tests/fixtures/*`. Branch-introduced scoping applies.
- **Universe conformance:** zero WARNING+ `unlisted-fiction-entity` / HIGH `fiction-continuity-mismatch` from that same `check` run.

These are hook-class checks CI re-runs; here they are the local dry-run of them.

## Advisory previews (reported, never gate)

Run and report; they never flip the verdict — the PR's code-owner review is the gate for judgment, not this verb.

- **house-qa `review`** (fresh context, per `playbooks/review.md`): report the KEEP/SIMPLIFY/REWORK verdict and its notes.
- **`/code-review`** with a committed `REVIEW.md`, and **`/security-review`**: cwd-independent — `git -C <target_repo> diff origin/HEAD...` and report >80%-confidence exploitable findings (injection, authz bypass, path traversal, unsafe deserialization, hardcoded secrets, data exposure); skip style/DoS/theoretical. Markdown-only delta → recorded as skipped, nothing to review.

## Verdict schema

```yaml
verdict: pass | fail            # from the reported checks only (tree scan, house-qa mechanical, scaffold)
scan_profile: base+overlay      # trusted-lane parity; state it so a routine-lane comparison is unambiguous
target_repo: <abs path>
pre_existing_debt: [...]        # reproduces on origin/HEAD; informational, carried until dispositioned
reported:
  tree_scan:          {status: pass|fail, findings: [...]}   # rule + file:line, value redacted
  house_qa_mechanical: {status: pass|fail, findings: [...]}
  scaffold:           {status: pass|fail, findings: [...]}
  universe_conformance: {status: pass|fail, findings: [...]}
advisory:                        # reported for the author; NEVER affects `verdict`
  house_qa_review:  {verdict: KEEP|SIMPLIFY|REWORK, notes: [...]}
  code_review:      {findings: [...]}
  security_review:  {status: reviewed|skipped, findings: [...]}
pr_body_lint: {status: pass|fail|not-supplied, findings: [...]}   # structural lint of a supplied pr-body:v1; the '<!-- pr-body:v1 -->' marker (first line) is REQUIRED — a body missing it is FAIL, never pass
```

A future autonomous consumer reads `verdict` directly; human mode reads it as the per-check dry-run report. Either way `verdict` derives from `reported` only.

## What this playbook does NOT do

- Does NOT invoke push/PR/merge mechanics — the verb takes no remote action; the caller opens the PR and the required checks + review gate it.
- Does NOT gate on the advisory previews — they are the author's preview, never a verdict input.
- Does NOT fix any finding — every check reports; the author edits.
