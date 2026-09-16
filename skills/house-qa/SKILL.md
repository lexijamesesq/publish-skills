---
name: house-qa
description: >
  DORMANT — the corpus-conformance judgment brief, awaiting absorption into
  Margot's house-style review. Its mechanical pass (`qa.py`) is RETIRED: the
  deterministic checks worth keeping were re-homed to the estate's shared core
  (self-narration → Vale; cited-paths → a house pre-commit + CI hook), the
  high-false-positive ones (size-vs-exemplar-median, CamelCase fiction) were
  dropped, and the leak-pattern scan was always a duplicate of house-code +
  the gitleaks operator overlay. Only the fresh-context JUDGMENT critic
  (`playbooks/review.md`) survives here, and nothing invokes it now that
  `/publish` is retired. Not a live operation — do not invoke.
---

# house-qa (dormant)

**Status: DORMANT.** This skill no longer runs. It is preserved for exactly one
thing: `playbooks/review.md`, the fresh-context corpus-conformance JUDGMENT
brief (grade an authored artifact against its class exemplars, weigh criticisms
over confirmations, never self-grade). That brief is the **input for Margot's
house-style card** — when that card is built, `review.md` is absorbed into it
and this skill is retired then (retire-what-you-replace, at the point its
replacement exists).

## What changed (why this is dormant)

The mechanical pass (`qa.py`) and the `/publish` verb that invoked it were
retired in the CI-standardization work. Its checks were dispositioned, not lost:

- **Re-homed as enforced checks** in the shared core (pre-commit locally +
  required CI, inherited by every repo): **cited-paths-exist** → a house hook
  (live); **self-narration** (literal-phrase ban) → Vale (landing with the Vale
  slice).
- **Dropped** (high-false-positive / low-signal): size-vs-exemplar-median, and
  the CamelCase fiction-detection regex + its allow-list.
- **Was always a duplicate** (dropped, no loss): the leak-pattern scan
  (ticket-id / vault-path / §-reference / roster-name) — `house-code.py` + the
  gitleaks operator overlay own it, enforced.
- **Preserved here, dormant** (this file + `playbooks/review.md`): the fuzzy
  JUDGMENT conformance review — Margot's territory, folded into her house-style
  card in a later slice.

## What this skill does NOT do

- Does NOT run a mechanical pass — `qa.py` is gone; its deterministic checks
  live in the shared core now (the cited-paths hook; self-narration lands with the Vale slice).
- Does NOT get invoked — `/publish` (its only invoker) is retired. Reaching for
  a corpus-conformance judgment before Margot's card exists means reading
  `playbooks/review.md` directly, in a fresh context.

## References

- `playbooks/review.md` — the preserved judgment critic brief (the live payload
  of this dormant skill).
- corpus-conformance-methodology.md — the contract this brief executes:
  `{workspace_root}/System/Knowledge/corpus-conformance-methodology.md`.
- `../sample-universe/universe.md` — the canonical fictional-entity reference
  the (kept) `/sample-universe` skill owns; the judgment review draws on it.
