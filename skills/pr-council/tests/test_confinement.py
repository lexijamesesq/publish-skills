#!/usr/bin/env python3
"""Corrective-L guard for the council's reviewer surfaces.

The reviewer takes PR evidence only from the `evidence` MCP server's read-only
tools — never a home path or a mounted volume. During the cutover the review ran
from an empty cwd, so a card's "grep the repo" sent the model into home paths and
mounted volumes, storming macOS TCC (~8 consent dialogs). This test greps the
reviewer's surfaces so a future edit can't silently reintroduce an out-of-tree
search.

The agents run natively under a lockdown where frontmatter `tools:` is the
grant: a shipped Grep or Glob got past `--tools ""`. So this test also pins each
agent's grant to exactly its evidence tools and refuses Bash, Grep, Glob and gh,
and requires the fields the Margot package reads (description, model, effort).

The confinement now lives in the reviewer's OWN skill (pr-council), not in the
spawner's file — that ownership is what makes the own-card carve-out below true
rather than an exception bolted onto a foreign rule.

Usage: python3 skills/pr-council/tests/test_confinement.py
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills" / "pr-council" / "SKILL.md"
AGENT = ROOT / "agents" / "pr-reviewer.md"
CARDS = sorted((ROOT / "skills" / "pr-council" / "playbooks").glob("*.md"))
MARGOT = ROOT / "agents" / "margot.md"
SURFACES = [SKILL, AGENT, MARGOT, *CARDS]

LINEAR = [
    "mcp__linear-tactic__linear_getIssueById",
    "mcp__linear-tactic__linear_getComments",
    "mcp__linear-tactic__linear_getProjectById",
]
EXPECTED_TOOLS = {
    AGENT: {
        "Skill",
        "Read",
        "mcp__evidence__read_diff",
        "mcp__evidence__read_file",
        "mcp__evidence__search_file",
        "mcp__evidence__list_files",
        "mcp__evidence__read_reference",
        *LINEAR,
    },
    MARGOT: {"mcp__evidence__read_file", "mcp__evidence__read_diff"},
}
FORBIDDEN_TOOLS = {"bash", "grep", "glob", "gh"}


def frontmatter(path):
    """Top-level keys of an agent's YAML frontmatter, with `tools:` as a list.

    Handles the two list shapes the agents use (block `- x` and flow `[x, y]`);
    stdlib only, so CI needs no YAML package.
    """
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    keys, current = {}, None
    for line in m.group(1).splitlines():
        top = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if top:
            current, value = top.group(1), top.group(2).strip()
            if value.startswith("[") and value.endswith("]"):
                keys[current] = [v.strip() for v in value[1:-1].split(",") if v.strip()]
            else:
                keys[current] = value if value else []
        elif (
            current
            and isinstance(keys[current], list)
            and line.strip().startswith("- ")
        ):
            keys[current].append(line.strip()[2:].strip())
    return keys


fail = []

# 1. the reviewer's skill must state the confinement explicitly
s = SKILL.read_text().lower()
if "`evidence` tools" not in s or "read_diff" not in s:
    fail.append(
        "pr-council/SKILL.md: missing the `evidence` tools confinement statement"
    )
if "/volumes" not in s and "mounted volume" not in s:
    fail.append(
        "pr-council/SKILL.md: confinement must forbid mounted volumes (/Volumes)"
    )
if "~/repos" not in s and "home path" not in s:
    fail.append("pr-council/SKILL.md: confinement must forbid home paths (~/…)")

# 1b. the confinement must scope to PR EVIDENCE and explicitly carve out the
#     reviewer's own card/skill under the plugin root. Without this the clause
#     reads as forbidding a reviewer from loading its own playbook (which sits
#     under the plugin root / $HOME in the runtime), and all six reviewers
#     returned 'incomplete' on the canary PR. Guard both directions.
if "for pr evidence" not in s and "for evidence" not in s:
    fail.append(
        "pr-council/SKILL.md: confinement must scope to PR evidence (else it blocks own-card loading)"
    )
if not (("own card" in s or "own reviewer files" in s) and "permitted" in s):
    fail.append(
        "pr-council/SKILL.md: must explicitly permit reading the reviewer's own card/skill"
    )

# 1c. the agent must point at its own skill by name — the ownership that keeps
#     the carve-out true. A card handed over as text is the shape #25 broke on.
#     A `skills:` preload does not reach an `--agent` session, so the agent
#     invokes the skill itself with the Skill tool.
a = AGENT.read_text()
if "pr-council" not in a:
    fail.append("agents/pr-reviewer.md: must name its own `pr-council` skill")
if "`Skill` tool" not in a:
    fail.append("agents/pr-reviewer.md: must invoke `pr-council` with the `Skill` tool")

# 1d. frontmatter `tools:` is the grant: exactly the evidence tools each agent
#     needs, never a shell, Grep, Glob or gh; and the fields the package reads.
for path, expected in EXPECTED_TOOLS.items():
    rel = path.relative_to(ROOT)
    fm = frontmatter(path)
    if fm is None:
        fail.append(f"{rel}: no YAML frontmatter")
        continue
    for key in ("description", "model", "effort"):
        if not fm.get(key):
            fail.append(
                f"{rel}: frontmatter must keep `{key}` (the Margot package reads it)"
            )
    tools = fm.get("tools", [])
    if not isinstance(tools, list) or set(tools) != expected:
        fail.append(f"{rel}: tools are {tools}, expected exactly {sorted(expected)}")
    for tool in tools if isinstance(tools, list) else [tools]:
        name = re.split(r"[(:]", tool, maxsplit=1)[0].strip().lower()
        if name in FORBIDDEN_TOOLS or re.search(r"\bgh\b", tool):
            fail.append(
                f"{rel}: grants {tool!r}; no agent may hold Bash, Grep, Glob or gh"
            )

# 2. no reviewer surface may tell the model to 'grep the repo' (bare), or send it
#    to a checkout or gh for evidence — there is none; the evidence tools serve
#    the repository, so "the repo" can never mean the disk
for f in SURFACES:
    body = f.read_text().lower()
    for phrase in (
        "grep the repo",
        "working-directory checkout",
        "base-sha checkout",
        "gh api",
        "gh pr",
        "gh` shim",
    ):
        if phrase in body:
            fail.append(
                f"{f.relative_to(ROOT)}: says {phrase!r} — PR evidence comes only from the `evidence` tools"
            )

for m in fail:
    print("FAIL:", m)
if fail:
    sys.exit(1)
print(
    f"OK: {len(SURFACES)} council reviewer surfaces confine evidence to the `evidence` tools; no agent grants Bash, Grep, Glob or gh"
)
