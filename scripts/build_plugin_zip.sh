#!/usr/bin/env bash
set -euo pipefail

# --- CONFIG ---
PLUGIN_ID="${PLUGIN_ID:-securable}"
DIST_DIR="${DIST_DIR:-dist}"
TAG="${1:-${GITHUB_REF_NAME:-}}"
PLUGIN_JSON_SOURCE=".claude-plugin/plugin.json"

if [[ -z "${TAG}" ]]; then
  echo "Tag is required. Pass it as the first argument or set GITHUB_REF_NAME." >&2
  exit 1
fi

if [[ ! -f "${PLUGIN_JSON_SOURCE}" ]]; then
  echo "Missing ${PLUGIN_JSON_SOURCE}" >&2
  exit 1
fi

ZIP_NAME="${PLUGIN_ID}-${TAG}.zip"
PLUGIN_VERSION="${TAG#v}"

# --- PREP ---
echo "-> Cleaning dist directory"
rm -rf "${DIST_DIR}"
mkdir -p "${DIST_DIR}"

echo "-> Creating temporary build directory"
BUILD_DIR="$(mktemp -d)"
PLUGIN_DIR="${BUILD_DIR}/${PLUGIN_ID}"
mkdir -p "${PLUGIN_DIR}"

cleanup() {
  rm -rf "${BUILD_DIR}"
}
trap cleanup EXIT

# --- COPY FILES ---
echo "-> Copying plugin files into build directory"
rsync -av \
  --exclude ".git" \
  --exclude "dist" \
  --exclude ".DS_Store" \
  --exclude ".*.swp" \
  --exclude "tests" \
  --exclude ".github" \
  --exclude ".vscode" \
  --exclude ".claude" \
  --exclude "template" \
  ./ "${PLUGIN_DIR}/"

# Stamp the release version into every agent manifest (.claude-plugin/ is the
# canonical one Claude Code reads; .cursor-plugin/ and .devin-plugin/ must stay
# in lockstep with it — scripts/check_manifests.py enforces that in CI).
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Python is required to generate ${PLUGIN_DIR}/plugin.json" >&2
  exit 1
fi

"${PYTHON_BIN}" - <<PYEOF
import json
import os

plugin_dir = "${PLUGIN_DIR}"
version = "${PLUGIN_VERSION}"

with open("${PLUGIN_JSON_SOURCE}", "r", encoding="utf-8") as f:
    plugin = json.load(f)
plugin["version"] = version

target_path = os.path.join(plugin_dir, ".claude-plugin/plugin.json")
os.makedirs(os.path.dirname(target_path), exist_ok=True)
with open(target_path, "w", encoding="utf-8") as f:
    json.dump(plugin, f, indent=2)
    f.write("\n")

for rel in (".cursor-plugin/plugin.json", ".devin-plugin/plugin.json"):
    manifest_path = os.path.join(plugin_dir, rel)
    if not os.path.isfile(manifest_path):
        continue
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    manifest["version"] = version
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

marketplace_path = os.path.join(plugin_dir, ".claude-plugin/marketplace.json")
if os.path.isfile(marketplace_path):
    with open(marketplace_path, "r", encoding="utf-8") as f:
        marketplace = json.load(f)
    plugins = marketplace.get("plugins")
    if isinstance(plugins, list) and plugins:
        if isinstance(plugins[0], dict):
            plugins[0]["version"] = version
    with open(marketplace_path, "w", encoding="utf-8") as f:
        json.dump(marketplace, f, indent=2)
        f.write("\n")
PYEOF

# --- ZIP ---
echo "-> Creating ZIP archive"
(
  cd "${BUILD_DIR}"
  zip -r "${ZIP_NAME}" "${PLUGIN_ID}"
)

mv "${BUILD_DIR}/${ZIP_NAME}" "${DIST_DIR}/"

# --- HASH ---
echo "-> Generating SHA256 hash"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum "${DIST_DIR}/${ZIP_NAME}" | awk '{print $1}' > "${DIST_DIR}/${ZIP_NAME}.sha256"
else
  shasum -a 256 "${DIST_DIR}/${ZIP_NAME}" | awk '{print $1}' > "${DIST_DIR}/${ZIP_NAME}.sha256"
fi

# --- DONE ---
echo
echo "ZIP created: ${DIST_DIR}/${ZIP_NAME}"
echo "SHA256 written to: ${DIST_DIR}/${ZIP_NAME}.sha256"
echo
echo "SHA256:"
cat "${DIST_DIR}/${ZIP_NAME}.sha256"
echo
echo "Done."
