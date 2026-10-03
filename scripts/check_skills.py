#!/usr/bin/env python3
"""Validate the published InsightSocial skills against the manifests and the live API."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"
CURSOR_MANIFEST = ROOT / ".cursor-plugin" / "plugin.json"
GEMINI_MANIFEST = ROOT / "gemini-extension.json"
CATALOGUE_URL = "https://api.insightsocial.app/v1/endpoints"
USER_AGENT = "insightsocial-skills-check/1"
CLI_SKILL_RAW = "https://raw.githubusercontent.com/insightsocial/cli/main/skills/insightsocial"

# Text that must never ship in a public skill. The private term list comes from
# the FORBIDDEN_TERMS secret (comma-separated) so this public file does not
# carry it; a real key is a secret either way.
FORBIDDEN = {
    "live API key": re.compile(r"isk_(?:live|test)_[A-Za-z0-9_-]{20,}"),
}
_terms = [term.strip() for term in os.environ.get("FORBIDDEN_TERMS", "").split(",") if term.strip()]
if _terms:
    FORBIDDEN["private term"] = re.compile("|".join(map(re.escape, _terms)), re.IGNORECASE)
ENDPOINT_PATH = re.compile(r"/v1/[a-z]+(?:/[a-z0-9-]+)+")
DOCS_URL = re.compile(r"https://www\.insightsocial\.app/[^\s)`'\"]*")
META_PATHS = {"/v1/endpoints", "/v1/credits"}


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        fail(f"cannot read {path.relative_to(ROOT)}: {error}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def split_frontmatter(path: Path, content: str) -> tuple[str, str]:
    lines = content.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        fail(f"{path.relative_to(ROOT)} is missing YAML frontmatter")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        fail(f"{path.relative_to(ROOT)} has unterminated YAML frontmatter")
    return "".join(lines[1:end]), "".join(lines[end + 1 :])


def frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"(?m)^\s*{key}:\s*(.+)$", frontmatter)
    return match.group(1).strip().strip('"') if match else ""


def check_versions() -> str:
    plugin = load_json(PLUGIN_MANIFEST)
    marketplace = load_json(MARKETPLACE_MANIFEST)
    metadata = marketplace.get("metadata")
    versions = {
        ".claude-plugin/plugin.json": plugin.get("version"),
        ".claude-plugin/marketplace.json": metadata.get("version") if isinstance(metadata, dict) else None,
        ".cursor-plugin/plugin.json": load_json(CURSOR_MANIFEST).get("version"),
        "gemini-extension.json": load_json(GEMINI_MANIFEST).get("version"),
    }
    if len(set(versions.values())) != 1:
        fail(f"manifest versions must match: {versions}")
    return str(plugin["version"])


def manifest_skill_paths() -> list[Path]:
    skills = load_json(PLUGIN_MANIFEST).get("skills")
    if not isinstance(skills, list) or not skills:
        fail("plugin manifest must list at least one skill")
    paths: list[Path] = []
    for raw_path in skills:
        if not isinstance(raw_path, str):
            fail("plugin manifest skill paths must be strings")
        path = (ROOT / raw_path).resolve()
        try:
            path.relative_to(ROOT)
        except ValueError:
            fail(f"manifest skill path escapes the repository: {raw_path}")
        skill_file = path / "SKILL.md"
        if not skill_file.is_file():
            fail(f"manifest-listed skill does not exist: {raw_path}/SKILL.md")
        paths.append(skill_file)
    return paths


def fetch(url: str) -> tuple[int, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8")
    except HTTPError as error:
        return error.code, ""
    except (OSError, UnicodeError, URLError) as error:
        fail(f"cannot fetch {url}: {error}")
    return 0, ""


def live_endpoints() -> set[str]:
    status, body = fetch(CATALOGUE_URL)
    if status != 200:
        fail(f"{CATALOGUE_URL} returned {status}")
    catalogue = json.loads(body)
    return {entry["path"] for entry in catalogue["endpoints"] if entry.get("available")}


def main() -> None:
    version = check_versions()
    skill_files = manifest_skill_paths()
    for path in skill_files:
        frontmatter, _ = split_frontmatter(path, path.read_text())
        # An unquoted value containing ": " is invalid YAML; strict loaders
        # (npx skills) then report "No valid skills found" with no other hint.
        for line in frontmatter.splitlines():
            match = re.match(r"^\s*[\w-]+:\s+(.+)$", line)
            if match and ": " in match.group(1) and match.group(1)[0] not in "\"'":
                fail(f"{path.relative_to(ROOT)} frontmatter value needs quotes: {line[:60]}...")
        for key in ("name", "description", "when_to_use"):
            if not frontmatter_value(frontmatter, key):
                fail(f"{path.relative_to(ROOT)} frontmatter is missing {key}")
        if frontmatter_value(frontmatter, "version") != version:
            fail(f"{path.relative_to(ROOT)} metadata.version must be {version}")

    published = sorted((ROOT / "skills").rglob("*.md")) + [ROOT / "README.md"]
    texts = {path: path.read_text() for path in published}
    for path, text in texts.items():
        for label, pattern in FORBIDDEN.items():
            if pattern.search(text):
                fail(f"{path.relative_to(ROOT)} contains {label}")

    if os.environ.get("SKIP_LIVE_CHECKS"):
        print(f"skills checks passed offline ({len(skill_files)} skill, v{version})")
        return

    # Every endpoint path a skill names must exist and be callable today; an
    # agent that copies a dead path gets UNKNOWN_ENDPOINT and stops trusting us.
    available = live_endpoints() | META_PATHS
    for path, text in texts.items():
        for endpoint in sorted(set(ENDPOINT_PATH.findall(text))):
            if endpoint not in available:
                fail(f"{path.relative_to(ROOT)} names {endpoint}, which the live catalogue does not list as available")

    # The CLI bundles this skill and installs it on `insightsocial init`; two
    # copies with one name must not drift, or whichever installs last wins.
    for relative in ("SKILL.md", "references/rest.md"):
        local = (ROOT / "skills" / "insightsocial" / relative).read_text()
        status, bundled = fetch(f"{CLI_SKILL_RAW}/{relative}")
        if status != 200 or bundled != local:
            fail(f"skills/insightsocial/{relative} differs from the copy in insightsocial/cli; copy it there and release both")

    for url in sorted({url.rstrip(".,") for text in texts.values() for url in DOCS_URL.findall(text)}):
        status, _ = fetch(url)
        if status != 200:
            fail(f"{url} returned {status}")

    print(f"skills checks passed ({len(skill_files)} skill, v{version}, {len(available)} live endpoints)")


if __name__ == "__main__":
    main()
