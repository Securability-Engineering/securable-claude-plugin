#!/usr/bin/env python3
"""Validate the repo-resident securable contract files.

Checks .securable/requirements.yaml and .securable/boundaries.yaml against the
contract rules (schema/securable/*.schema.json documents the same shape for
external tools; this validator is dependency-light and adds the semantic rules
a generic schema cannot express):

  - structural shape, required fields, enums, id patterns, duplicate ids
  - requirement ids must belong to their feature (F-03-R2 lives under F-03)
  - level above the baseline requires `escalation: true`
  - `status: verified` requires `evidence`
  - feature boundary ids must exist in boundaries.yaml when both files exist
  - ASVS references must resolve against the bundled ASVS 5.0 catalog
    (skipped with a warning when the catalog is not present, e.g. in a
    consuming repo that installed only the contract)

Exit 0 = valid; 1 = at least one error. Warnings do not fail the run.

Usage:
  scripts/validate_securable.py [--dir .securable] [--asvs-dir data/asvs] [--quiet]
  scripts/validate_securable.py --requirements PATH [--boundaries PATH]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("error: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent

FEATURE_ID = re.compile(r"^F-[0-9]+$")
REQ_ID = re.compile(r"^(F-[0-9]+)-R[0-9]+$")
CC_REQ_ID = re.compile(r"^CC-R[0-9]+$")
BOUNDARY_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ASVS_REF = re.compile(r"^V([0-9]{1,2})(?:\.([0-9]{1,2}))?(?:\.([0-9]{1,2}))?$")

STATUSES = {"planned", "implemented", "verified"}
BOUNDARY_KINDS = {"http", "rpc", "queue", "file", "cli", "env", "webhook", "db", "third-party", "other"}
LEVELS = {1, 2, 3}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def load_yaml(path: Path, rep: Report):
    try:
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        rep.error(f"{path}: not parseable YAML: {e}")
        return None
    if not isinstance(data, dict):
        rep.error(f"{path}: top level must be a mapping")
        return None
    return data


def check_asvs_ref(ref: str, where: str, asvs_dir: Path | None, rep: Report) -> None:
    m = ASVS_REF.match(ref)
    if not m:
        rep.error(f"{where}: ASVS ref '{ref}' is not of the form V6, V6.3, or V6.3.8")
        return
    if asvs_dir is None:
        return
    chapter, section, req = m.group(1), m.group(2), m.group(3)
    if not any(asvs_dir.glob(f"V{chapter}.*.md")):
        rep.error(f"{where}: ASVS chapter V{chapter} not found in {asvs_dir}")
        return
    if section is None:
        return
    section_file = asvs_dir / f"V{chapter}.{section}.md"
    if not section_file.is_file():
        rep.error(f"{where}: no {section_file.name} in {asvs_dir}")
        return
    if req is not None:
        body = section_file.read_text(encoding="utf-8")
        if f"**{chapter}.{section}.{req}**" not in body:
            rep.error(f"{where}: requirement {chapter}.{section}.{req} not found in {section_file.name}")


def check_requirement(req, where: str, baseline: int | None, feature_id: str | None,
                      asvs_dir: Path | None, rep: Report) -> str | None:
    if not isinstance(req, dict):
        rep.error(f"{where}: requirement must be a mapping")
        return None
    rid = req.get("id")
    if not isinstance(rid, str) or not (REQ_ID.match(rid) or CC_REQ_ID.match(rid)):
        rep.error(f"{where}: id '{rid}' must match F-<n>-R<n> or CC-R<n>")
        rid = None
    elif feature_id is not None:
        m = REQ_ID.match(rid)
        if m is None:
            rep.error(f"{where}: id '{rid}' — a feature requirement cannot use the CC- prefix")
        elif m.group(1) != feature_id:
            rep.error(f"{where}: id '{rid}' does not belong to feature {feature_id}")
    elif feature_id is None and rid and REQ_ID.match(rid):
        rep.error(f"{where}: id '{rid}' — cross-cutting requirements use CC-R<n>")

    if not isinstance(req.get("text"), str) or not req["text"].strip():
        rep.error(f"{where}: 'text' is required and must be non-empty")

    acceptance = req.get("acceptance")
    ok_str = isinstance(acceptance, str) and acceptance.strip()
    ok_list = (isinstance(acceptance, list) and acceptance
               and all(isinstance(a, str) and a.strip() for a in acceptance))
    if not (ok_str or ok_list):
        rep.error(f"{where}: 'acceptance' must be a non-empty string or list of non-empty strings")

    status = req.get("status")
    if status not in STATUSES:
        rep.error(f"{where}: 'status' must be one of {sorted(STATUSES)}, got {status!r}")
    elif status == "verified" and not (isinstance(req.get("evidence"), str) and req["evidence"].strip()):
        rep.error(f"{where}: status 'verified' requires non-empty 'evidence' — only a review or test run flips to verified")

    level = req.get("level")
    if level is not None:
        if level not in LEVELS:
            rep.error(f"{where}: 'level' must be 1, 2, or 3")
        elif baseline is not None and level > baseline and req.get("escalation") is not True:
            rep.error(f"{where}: level {level} exceeds baseline {baseline} — set 'escalation: true' (above-baseline items are explicit escalations)")

    for key in req:
        if key not in {"id", "text", "asvs", "level", "escalation", "acceptance", "status", "evidence", "notes"}:
            rep.error(f"{where}: unknown key '{key}'")

    asvs = req.get("asvs", [])
    if asvs is not None:
        if not isinstance(asvs, list):
            rep.error(f"{where}: 'asvs' must be a list")
        else:
            for ref in asvs:
                check_asvs_ref(str(ref), where, asvs_dir, rep)
    return rid


def validate_requirements(path: Path, boundary_ids: set[str] | None,
                          asvs_dir: Path | None, rep: Report) -> None:
    data = load_yaml(path, rep)
    if data is None:
        return
    if data.get("securable_contract") != 1:
        rep.error(f"{path}: 'securable_contract: 1' is required")
    baseline = data.get("asvs_level")
    if baseline not in LEVELS:
        rep.error(f"{path}: 'asvs_level' must be 1, 2, or 3")
        baseline = None
    for key in data:
        if key not in {"securable_contract", "asvs_level", "generated_by", "system", "features", "cross_cutting"}:
            rep.error(f"{path}: unknown top-level key '{key}'")

    seen_ids: set[str] = set()
    features = data.get("features")
    if not isinstance(features, list) or not features:
        rep.error(f"{path}: 'features' must be a non-empty list")
        features = []
    for i, feat in enumerate(features):
        fwhere = f"{path}: features[{i}]"
        if not isinstance(feat, dict):
            rep.error(f"{fwhere}: must be a mapping")
            continue
        fid = feat.get("id")
        if not isinstance(fid, str) or not FEATURE_ID.match(fid):
            rep.error(f"{fwhere}: id '{fid}' must match F-<n>")
            fid = None
        elif fid in seen_ids:
            rep.error(f"{fwhere}: duplicate feature id {fid}")
        elif fid:
            seen_ids.add(fid)
        if not isinstance(feat.get("title"), str) or not feat["title"].strip():
            rep.error(f"{fwhere}: 'title' is required")
        for key in feat:
            if key not in {"id", "title", "actor", "data", "boundaries", "requirements"}:
                rep.error(f"{fwhere}: unknown key '{key}'")
        for b in feat.get("boundaries", []) or []:
            if not isinstance(b, str) or not BOUNDARY_ID.match(b):
                rep.error(f"{fwhere}: boundary id '{b}' must be lowercase-kebab")
            elif boundary_ids is not None and b not in boundary_ids:
                rep.error(f"{fwhere}: boundary '{b}' not defined in boundaries.yaml")
        reqs = feat.get("requirements")
        if not isinstance(reqs, list) or not reqs:
            rep.error(f"{fwhere}: 'requirements' must be a non-empty list")
            continue
        for j, req in enumerate(reqs):
            rid = check_requirement(req, f"{fwhere}.requirements[{j}]", baseline, fid, asvs_dir, rep)
            if rid:
                if rid in seen_ids:
                    rep.error(f"{fwhere}.requirements[{j}]: duplicate id {rid}")
                seen_ids.add(rid)

    cc = data.get("cross_cutting", [])
    if cc is not None and not isinstance(cc, list):
        rep.error(f"{path}: 'cross_cutting' must be a list")
        cc = []
    for j, req in enumerate(cc or []):
        rid = check_requirement(req, f"{path}: cross_cutting[{j}]", baseline, None, asvs_dir, rep)
        if rid:
            if rid in seen_ids:
                rep.error(f"{path}: cross_cutting[{j}]: duplicate id {rid}")
            seen_ids.add(rid)


def validate_boundaries(path: Path, rep: Report) -> set[str] | None:
    data = load_yaml(path, rep)
    if data is None:
        return None
    if data.get("securable_contract") != 1:
        rep.error(f"{path}: 'securable_contract: 1' is required")
    for key in data:
        if key not in {"securable_contract", "system", "boundaries"}:
            rep.error(f"{path}: unknown top-level key '{key}'")
    boundaries = data.get("boundaries")
    if not isinstance(boundaries, list) or not boundaries:
        rep.error(f"{path}: 'boundaries' must be a non-empty list")
        return set()
    ids: set[str] = set()
    for i, b in enumerate(boundaries):
        where = f"{path}: boundaries[{i}]"
        if not isinstance(b, dict):
            rep.error(f"{where}: must be a mapping")
            continue
        bid = b.get("id")
        if not isinstance(bid, str) or not BOUNDARY_ID.match(bid):
            rep.error(f"{where}: id '{bid}' must be lowercase-kebab")
        elif bid in ids:
            rep.error(f"{where}: duplicate boundary id {bid}")
        else:
            ids.add(bid)
        if b.get("kind") not in BOUNDARY_KINDS:
            rep.error(f"{where}: 'kind' must be one of {sorted(BOUNDARY_KINDS)}")
        if not isinstance(b.get("description"), str) or not b["description"].strip():
            rep.error(f"{where}: 'description' is required")
        for key in b:
            if key not in {"id", "kind", "description", "entry_points", "data", "authority", "notes"}:
                rep.error(f"{where}: unknown key '{key}'")
    return ids


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=".securable", help="directory holding the contract files (default .securable)")
    ap.add_argument("--requirements", help="explicit path to requirements.yaml")
    ap.add_argument("--boundaries", help="explicit path to boundaries.yaml")
    ap.add_argument("--asvs-dir", help="ASVS catalog directory (default: data/asvs next to this script's repo)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    req_path = Path(args.requirements) if args.requirements else Path(args.dir) / "requirements.yaml"
    bnd_path = Path(args.boundaries) if args.boundaries else Path(args.dir) / "boundaries.yaml"

    asvs_dir = Path(args.asvs_dir) if args.asvs_dir else REPO / "data" / "asvs"
    rep = Report()
    if not asvs_dir.is_dir() or not any(asvs_dir.glob("V*.md")):
        rep.warn(f"ASVS catalog not found at {asvs_dir} — reference format checked, existence not verified")
        asvs_dir = None

    if not req_path.is_file() and not bnd_path.is_file():
        print(f"error: neither {req_path} nor {bnd_path} exists", file=sys.stderr)
        return 1

    boundary_ids: set[str] | None = None
    if bnd_path.is_file():
        boundary_ids = validate_boundaries(bnd_path, rep)
    if req_path.is_file():
        validate_requirements(req_path, boundary_ids, asvs_dir, rep)

    if not args.quiet:
        for w in rep.warnings:
            print(f"warning: {w}")
    if rep.errors:
        print(f"{len(rep.errors)} contract error(s):")
        for e in rep.errors:
            print(f"  {e}")
        return 1
    if not args.quiet:
        checked = [str(p) for p in (req_path, bnd_path) if p.is_file()]
        print(f"OK — securable contract valid: {', '.join(checked)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
