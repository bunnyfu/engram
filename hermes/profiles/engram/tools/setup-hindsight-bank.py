#!/usr/bin/env python3
"""Create or refresh the Engram Hindsight bank from the seeded directives.

Idempotent: reads hindsight/bank-missions.json (sibling of the profile root),
creates the bank if missing, PATCHes the three mission fields otherwise, and
verifies the resolved config. Also upserts the hard-rule reflect directives
from hindsight/directives.json (matched by name). Never deletes anything.

Usage:
    python3 tools/setup-hindsight-bank.py [--base http://localhost:8888]

Environment:
    HINDSIGHT_URL   base URL override (same as --base)
"""
import json
import os
import sys
import urllib.error
import urllib.request

PROFILE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # tools/ -> profile/
MISSIONS_PATH = os.path.join(PROFILE_ROOT, "hindsight", "bank-missions.json")
DIRECTIVES_PATH = os.path.join(PROFILE_ROOT, "hindsight", "directives.json")
MISSION_FIELDS = ("retain_mission", "reflect_mission", "observations_mission")


def base_url(argv: list[str]) -> str:
    if "--base" in argv:
        return argv[argv.index("--base") + 1]
    return os.environ.get("HINDSIGHT_URL", "http://localhost:8888")


def req(base: str, method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(
        f"{base}/v1/default/banks{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except json.JSONDecodeError:
            return e.code, {}


def main() -> int:
    with open(MISSIONS_PATH) as f:
        d = json.load(f)
    bank_id = d["bank_id"]
    base = base_url(sys.argv)
    print(f"directives: {os.path.relpath(DIRECTIVES_PATH, PROFILE_ROOT)}")
    print(f"target:     {base} bank '{bank_id}'")

    _, banks = req(base, "GET", "")
    existing = {b.get("bank_id") for b in banks.get("banks", banks) if isinstance(b, dict)}
    missions = {k: d[k] for k in MISSION_FIELDS}
    updates = dict(missions)
    updates["enable_observations"] = True

    if bank_id not in existing:
        payload = {"name": d["name"], **updates}
        mode = d.get("notes", {}).get("retain_extraction_mode")
        if mode:
            payload["retain_extraction_mode"] = mode
        status, resp = req(base, "PUT", f"/{bank_id}", payload)
        if status >= 400 and mode:  # retry without the optional enum
            payload.pop("retain_extraction_mode", None)
            status, resp = req(base, "PUT", f"/{bank_id}", payload)
        print(f"created:    HTTP {status}")
        if status >= 400:
            print(json.dumps(resp, indent=2)[:2000])
            return 1
    else:
        status, resp = req(base, "PATCH", f"/{bank_id}/config", {"updates": updates})
        print(f"patched:    HTTP {status}")
        if status >= 400:
            print(json.dumps(resp, indent=2)[:2000])
            return 1

    status, cfg = req(base, "GET", f"/{bank_id}/config")
    resolved = (cfg.get("config") or {})
    overrides = (cfg.get("overrides") or {})
    ok = True
    for field in MISSION_FIELDS:
        want, got = missions[field], resolved.get(field)
        flag = "OK " if got == want else ("SET-OTHERWISE" if got else "MISSING")
        if got != want:
            ok = got is not None or False
        print(f"  {field:22s} {flag} ({len(got or '')} chars resolved, "
              f"override={'yes' if overrides.get(field) else 'no'})")
    print(f"observations enabled:  {resolved.get('enable_observations', overrides.get('enable_observations'))}")
    print("verify:     " + ("all three missions active" if ok else "MISMATCH — inspect /config"))

    # Hard-rule reflect directives from hindsight/directives.json, upsert by name.
    directives = []
    if os.path.exists(DIRECTIVES_PATH):
        with open(DIRECTIVES_PATH) as f:
            directives = json.load(f).get("directives", [])
    _, listed = req(base, "GET", f"/{bank_id}/directives")
    existing = {x.get("name"): x.get("id") for x in listed.get("items", [])}
    for dr in directives:
        body = {k: dr[k] for k in ("name", "content", "priority", "is_active", "tags")}
        if dr["name"] in existing:
            status, _ = req(base, "PATCH", f"/{bank_id}/directives/{existing[dr['name']]}", body)
            print(f"directive:  {dr['name']} patched (HTTP {status})")
        else:
            status, _ = req(base, "POST", f"/{bank_id}/directives", body)
            print(f"directive:  {dr['name']} created (HTTP {status})")
        if status >= 400:
            return 1
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
