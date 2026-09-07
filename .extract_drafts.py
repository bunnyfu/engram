#!/usr/bin/env python3
"""t_902e3b12 — analyze the mirror-soul rebase interaction.

Classifies every 655-token checker pattern against base (4d8801d):
  - RETIRED: pattern text is defected by the amendment (must be re-pointed or dropped)
  - SURVIVES: pattern describes content that continues to exist post-amendment
"""
import re

WS = "/Users/ikavt/Developer/git/engram/.worktrees/t_902e3b12"
src = open(f"{WS}/scratch/verify_slim.py").read()
m = re.search(r'"engram-mirror-soul": \[(.*?)\n\],', src, re.S)
if not m:
    raise SystemExit("CHECKS block for engram-mirror-soul not found")
raw = m.group(1)
pats = []
for item in re.findall(r'"((?:[^"\\]|\\.)*)"', raw):
    pats.append(item.encode().decode("unicode_escape"))

BASE = open("/tmp/ms-base.md").read()
AMEND = open("/tmp/ms-amend.md").find
AMEND = open("/tmp/ms-amend.md").read()

retired_vocab = [
    "exemplar-anchored", "synthesis block", "synthesis tag", "quote block",
    "synthesis:", "claim contract", "anchor", "verbatim quote",
]
# Amendment defect-forms and their replacement grammar, for classification:
RETIRE_MAP = [
    ("exemplar-anchored memory layer", "intro rewritten to cited-dossier doctrine"),
    ("SOUL.md\n*of the subject*", "intro rewritten (metaphor retired with quote-first grammar)"),
    ("verbatim quote from the raw\narchive", "intro rewritten"),
    ("explicit synthesis", "synthesis-block form retired"),
    ("inference drawn", "synthesis-block form retired"),
    ("claim contract lint", "renamed claim-contract lint → lint (synthesis-tag definition gone)"),
    ("structure reconcile", "mirror step descriptor changed"),
    ("Verbatim quote block", "quote-block form retired as defect"),
    ("I always hated waiting in lines", "quote-block example retired"),
    ("[artifact: eng_20260827_001]", "pointer-line form retired (citation bracket replaces it)"),
    ("Explicit synthesis block", "retired defect form"),
    ("[synthesis: eng_20260827_001, eng_2026082003003]", "retired defect form"),
    ("dislikes inefficiency and low autonomy", "example retired with synthesis block"),
    ("waiting and rigid scheduling", "example retired with synthesis block"),
    ("Unquoted claims are forbidden", "replaced by terminal-citation-bracket grammar"),
    ("loosely related quote", "quote-based framing retired"),
    ("generalizes named quotes", "synthesis framing retired"),
    ("confidence: hint", "confidence moved into entry parenthetical"),
    ("confidence: pattern", "confidence moved into entry parenthetical"),
    ("slim-derived", "slim-derived"),
]
