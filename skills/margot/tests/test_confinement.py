#!/usr/bin/env python3
"""Corrective-L guard for Margot's reviewer surfaces.

The reviewer must confine every search to the WORKING-DIRECTORY CHECKOUT (the
base-sha checkout margot-tick runs it in) plus PR evidence fetched via gh —
never a home path or a mounted volume. During the cutover the review ran from an
empty cwd, so a card's "grep the repo" sent the model into ~/Repos, ~/Vaults and
/Volumes, storming macOS TCC (~8 consent dialogs). This test greps the agent and
cards so a future edit can't silently reintroduce an out-of-tree search.

Usage: python3 skills/margot/tests/test_confinement.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
AGENT = ROOT / "agents" / "pr-reviewer.md"
CARDS = sorted((ROOT / "skills" / "margot" / "playbooks").glob("*.md"))
SURFACES = [AGENT, ROOT / "agents" / "margot.md", *CARDS]

fail = []

# 1. the pr-reviewer agent must state the confinement explicitly
a = AGENT.read_text().lower()
if "working directory" not in a:
    fail.append("agents/pr-reviewer.md: missing the 'working directory' confinement statement")
if "/volumes" not in a and "mounted volume" not in a:
    fail.append("agents/pr-reviewer.md: confinement must forbid mounted volumes (/Volumes)")
if "~/repos" not in a and "home path" not in a:
    fail.append("agents/pr-reviewer.md: confinement must forbid home paths (~/…)")

# 2. no reviewer surface may tell the model to 'grep the repo' (bare) — it must
#    say the working-directory checkout, so "the repo" can never mean the disk
for f in SURFACES:
    if "grep the repo" in f.read_text().lower():
        rel = f.relative_to(ROOT)
        fail.append(f"{rel}: bare 'grep the repo' — say 'grep the working-directory checkout'")

for m in fail:
    print("FAIL:", m)
if fail:
    sys.exit(1)
print(f"OK: {len(SURFACES)} Margot reviewer surfaces confine searches to the working-directory checkout")
