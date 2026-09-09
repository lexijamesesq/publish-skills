#!/usr/bin/env python3
"""Corrective-L guard for the council's reviewer surfaces.

The reviewer must confine every search to the WORKING-DIRECTORY CHECKOUT (the
base-sha checkout the runtime runs it in) plus PR evidence fetched via gh —
never a home path or a mounted volume. During the cutover the review ran from an
empty cwd, so a card's "grep the repo" sent the model into home paths and mounted
volumes, storming macOS TCC (~8 consent dialogs). This test greps the reviewer's
surfaces so a future edit can't silently reintroduce an out-of-tree search.

The confinement now lives in the reviewer's OWN skill (pr-council), not in the
spawner's file — that ownership is what makes the own-card carve-out below true
rather than an exception bolted onto a foreign rule.

Usage: python3 skills/pr-council/tests/test_confinement.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills" / "pr-council" / "SKILL.md"
AGENT = ROOT / "agents" / "pr-reviewer.md"
CARDS = sorted((ROOT / "skills" / "pr-council" / "playbooks").glob("*.md"))
SURFACES = [SKILL, AGENT, ROOT / "agents" / "margot.md", *CARDS]

fail = []

# 1. the reviewer's skill must state the confinement explicitly
s = SKILL.read_text().lower()
if "working directory" not in s:
    fail.append("pr-council/SKILL.md: missing the 'working directory' confinement statement")
if "/volumes" not in s and "mounted volume" not in s:
    fail.append("pr-council/SKILL.md: confinement must forbid mounted volumes (/Volumes)")
if "~/repos" not in s and "home path" not in s:
    fail.append("pr-council/SKILL.md: confinement must forbid home paths (~/…)")

# 1b. the confinement must scope to PR EVIDENCE and explicitly carve out the
#     reviewer's own card/skill under the plugin root. Without this the clause
#     reads as forbidding a reviewer from loading its own playbook (which sits
#     under the plugin root / $HOME in the runtime), and all six reviewers
#     returned 'incomplete' on the canary PR. Guard both directions.
if "for pr evidence" not in s and "for evidence" not in s:
    fail.append("pr-council/SKILL.md: confinement must scope to PR evidence (else it blocks own-card loading)")
if not (("own card" in s or "own reviewer files" in s) and "permitted" in s):
    fail.append("pr-council/SKILL.md: must explicitly permit reading the reviewer's own card/skill")

# 1c. the agent must point at its own skill by name — the ownership that keeps
#     the carve-out true. A card handed over as text is the shape #25 broke on.
a = AGENT.read_text()
if "pr-council" not in a:
    fail.append("agents/pr-reviewer.md: must name its own `pr-council` skill")
if "skills:" not in a or "- pr-council" not in a:
    fail.append("agents/pr-reviewer.md: frontmatter must declare `skills: [pr-council]`")

# 2. no reviewer surface may tell the model to 'grep the repo' (bare) — it must
#    say the working-directory checkout, so "the repo" can never mean the disk
for f in SURFACES:
    if "grep the repo" in f.read_text().lower():
        fail.append(f"{f.relative_to(ROOT)}: bare 'grep the repo' — say 'grep the working-directory checkout'")

for m in fail:
    print("FAIL:", m)
if fail:
    sys.exit(1)
print(f"OK: {len(SURFACES)} council reviewer surfaces confine searches to the working-directory checkout")
