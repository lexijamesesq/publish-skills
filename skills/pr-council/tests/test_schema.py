#!/usr/bin/env python3
"""Contract guard for the two result schemas.

The first proof run's verdict crashed the poster: a field came back a string
where a structured value was expected, and no fenced schema existed anywhere for
the model to copy — the contract lived only as an inline prose key list. Both
schemas are now fenced at their producer, and this test pins them:

  * the AGGREGATE, in agents/margot.md — the object Margot returns and a
    deterministic poster reads. Two axes: `outcome` (adequacy) and `risk`
    (authority, a {band, R, vector} object). No `verdict` and no `completion`
    dict — an incomplete summoned card is ERROR, and `checked` is the sole
    completeness signal (one non-empty entry per summoned card).
  * the PER-CARD result, in skills/pr-council/SKILL.md — what one reviewer
    returns to Margot.

The literal key lists below are this side of a cross-repo anchor. The poster
(dotty-private) mirrors AGGREGATE_KEYS in its own schema eval; keep the two
byte-in-sync so a rename that crosses the repo boundary is caught on both sides.

Usage: python3 skills/pr-council/tests/test_schema.py
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
MARGOT = ROOT / "agents" / "margot.md"
SKILL = ROOT / "skills" / "pr-council" / "SKILL.md"

AGGREGATE_KEYS = [
    "outcome", "risk", "risk_reason", "rationale", "authority", "clarification",
    "summoned", "not_summoned", "checked", "findings", "dismissals", "ticket",
]
RISK_KEYS = ["band", "R", "vector"]
VECTOR_KEYS = [
    "blast_radius", "reversibility", "data_security", "operations", "verification_gap",
]
AGGREGATE_FINDING_KEYS = [
    "reviewers", "clause", "location", "sentence", "severity", "confidence",
    "consequence", "action",
]
PER_CARD_KEYS = ["reviewer", "completion", "checked", "not_covered", "findings"]
PER_CARD_FINDING_KEYS = [
    "reviewer", "clause", "severity", "confidence", "location", "sentence",
    "consequence", "action",
]
CARD_NAMES = [
    "house-style", "works-and-proven", "achieves-the-objective",
    "maintainable-no-slop", "principal-engineer", "safety",
]

fail = []


def fenced_json(path):
    """Return every ```json block in path, parsed. A block that won't parse is a failure."""
    blocks = re.findall(r"```json\n(.*?)\n```", path.read_text(), re.DOTALL)
    out = []
    for i, b in enumerate(blocks):
        try:
            out.append(json.loads(b))
        except json.JSONDecodeError as e:
            fail.append(f"{path.relative_to(ROOT)}: fenced json block {i} does not parse: {e}")
    return out


agg_blocks = fenced_json(MARGOT)
card_blocks = fenced_json(SKILL)

if len(agg_blocks) != 1:
    fail.append(f"agents/margot.md: expected exactly 1 fenced json schema, found {len(agg_blocks)}")
if len(card_blocks) != 1:
    fail.append(f"pr-council/SKILL.md: expected exactly 1 fenced json schema, found {len(card_blocks)}")

if agg_blocks:
    agg = agg_blocks[0]
    if list(agg) != AGGREGATE_KEYS:
        fail.append(f"agents/margot.md: aggregate keys are {list(agg)}, expected {AGGREGATE_KEYS}")
    # risk is the authority axis: a {band, R, vector} object; vector is a NAMED
    # object of the five dimensions so a positional mistake cannot mis-score one.
    risk = agg.get("risk")
    if not isinstance(risk, dict) or list(risk) != RISK_KEYS:
        fail.append(f"agents/margot.md: risk must be an object with keys {RISK_KEYS}")
    else:
        vec = risk.get("vector")
        if not isinstance(vec, dict) or list(vec) != VECTOR_KEYS:
            fail.append(f"agents/margot.md: risk.vector must be a named object with keys {VECTOR_KEYS}")
    # the poster builds its per-card lines from findings[].reviewers as a LIST —
    # a finding carrying a bare `reviewer` string is silently dropped from them
    finding = (agg.get("findings") or [{}])[0]
    if not isinstance(finding.get("reviewers"), list):
        fail.append("agents/margot.md: findings[].reviewers must be a list")
    if list(finding) != AGGREGATE_FINDING_KEYS:
        fail.append(f"agents/margot.md: finding keys are {list(finding)}, expected {AGGREGATE_FINDING_KEYS}")
    # summoned is the list of cards that ran; not_summoned carries the ❓ fact per
    # card that did not — never rendered green.
    if not isinstance(agg.get("summoned"), list):
        fail.append("agents/margot.md: summoned must be a list of card names")
    ns = (agg.get("not_summoned") or [{}])[0]
    if sorted(ns) != ["card", "fact"]:
        fail.append(f"agents/margot.md: not_summoned[] keys are {sorted(ns)}, expected ['card', 'fact']")
    # checked is the sole completeness signal — one non-empty entry per summoned card
    if not isinstance(agg.get("checked"), dict):
        fail.append("agents/margot.md: checked must be a dict of card name to probe list")
    # appeals: a dismissed finding carries its reason back for calibration
    dis = (agg.get("dismissals") or [{}])[0]
    if sorted(dis) != ["finding", "reason"]:
        fail.append(f"agents/margot.md: dismissals[] keys are {sorted(dis)}, expected ['finding', 'reason']")
    if not isinstance(agg.get("ticket"), dict) or "id" not in (agg.get("ticket") or {}):
        fail.append("agents/margot.md: ticket must be an object carrying an id")

if card_blocks:
    card = card_blocks[0]
    if list(card) != PER_CARD_KEYS:
        fail.append(f"pr-council/SKILL.md: per-card keys are {list(card)}, expected {PER_CARD_KEYS}")
    # a green card is earnable only through its Checked list
    if not isinstance(card.get("checked"), list) or not card.get("checked"):
        fail.append("pr-council/SKILL.md: checked must be a non-empty list of probes")
    if not isinstance(card.get("not_covered"), list):
        fail.append("pr-council/SKILL.md: not_covered must be a list")
    cf = (card.get("findings") or [{}])[0]
    if list(cf) != PER_CARD_FINDING_KEYS:
        fail.append(f"pr-council/SKILL.md: finding keys are {list(cf)}, expected {PER_CARD_FINDING_KEYS}")

for m in fail:
    print("FAIL:", m)
if fail:
    sys.exit(1)
print("OK: both fenced schemas parse and carry exactly their pinned keys")
