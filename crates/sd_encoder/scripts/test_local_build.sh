#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_LOCAL=1
test_venv=""

cleanup() {
  if [[ "${KEEP_TEST_VENV:-0}" != "1" && -n "$test_venv" ]]; then
    rm -rf "$test_venv"
  fi
}
trap cleanup EXIT

if [[ "${1:-}" == "--skip-build" ]]; then
  BUILD_LOCAL=0
fi

cd "$ROOT_DIR"

if [[ "$BUILD_LOCAL" == "1" ]]; then
  make build-local
fi

wheel_path="$(ls -t "$ROOT_DIR"/dist/sd_encoder-*.whl 2>/dev/null | head -n 1 || true)"
if [[ -z "$wheel_path" ]]; then
  echo "No local sd_encoder wheel found in $ROOT_DIR/dist" >&2
  exit 1
fi

test_venv="$(mktemp -d "${TMPDIR:-/tmp}/sd_encoder_local_test.XXXXXX")"

python3 -m venv "$test_venv"
"$test_venv/bin/python" -m pip install --no-cache-dir --no-index --no-deps "$wheel_path"

"$test_venv/bin/python" - <<'PY'
from sd_encoder import SDCompressionConfig, SDEncoderV2, FieldImportance

config = SDCompressionConfig(
    required_fields=["id", "title", "status"],
    drop_non_required_fields=True,
    importance_threshold=FieldImportance.LOW,
)
encoder = SDEncoderV2(config)

payload = {
    "id": "T-42",
    "title": "Login fails",
    "status": "open",
    "internal_notes": "should not be emitted",
}

raw_result = encoder.encode(payload)
result = encoder.encode_validated(payload)

assert raw_result.component == "ds_compression", raw_result.component
assert raw_result.compressed == "{id,title,status}[T-42,Login fails,open]", raw_result.compressed
assert result.component == "ds_compression", result.component
assert result.compressed == "{id,title,status}[T-42,Login fails,open]", result.compressed
assert result.n_tokens() > 0
assert result.c_tokens() > 0
assert isinstance(result.compression_ratio(), float)
assert FieldImportance.HIGH > FieldImportance.LOW

print("Local sd_encoder wheel smoke test passed")
print(f"compressed={result.compressed}")
print(f"wheel_api={SDEncoderV2.__name__}")
PY

if [[ "${KEEP_TEST_VENV:-0}" == "1" ]]; then
  echo "Test venv left at: $test_venv"
fi
