# Changelog

All notable changes to this project are documented here.

---

## [Unreleased] — Phase 1: Origination + Multi-Network + ISO→JPF Mapping

### T1 — Network profiles (`backend/network/profiles/*.yaml` + `router.py`)
- Created four network dialect YAML profiles: `visa.yaml`, `mastercard.yaml`,
  `amex.yaml`, `discover.yaml` — each defining BIN ranges, MTI codes,
  private DE fields, and `private_de_values` templates.
- Added `backend/network/router.py` with `select_network(pan, override=None)`:
  routes by BIN prefix/range, override wins, fallback to Visa.
- **Verified:** Visa PAN → visa (private DEs 44/62/63); MC PAN → mastercard (48/61/63);
  Amex → amex (47/63); Discover → discover (62/63); override wins.

### T2 — ISO engine (`backend/network/packer.py`)
- Implemented pure-Python ISO 8583 packer/unpacker using `pyiso8583` (`iso8583` package).
- `pack(fields, network, mti, private_field_values)` → `PackResult(hex, fields, mti, network, private_des)`.
- `unpack(hex_str, network)` → `UnpackResult(fields, mti, network)`.
- Auto-populates network-private DEs from profile template with `{stan}` substitution.
- **Key fix:** `iso8583` library requires string keys throughout (not int); bitmap `"p"` and
  secondary bitmap `"1"` stripped from unpack output.
- **Verified:** All 4 networks round-trip losslessly; private DEs present; Visa ≠ MC field sets.

### T3 — Acquirer origination (`backend/network/originator.py`)
- Added `build_0100(request, network_override=None)` → `OriginationResult`.
- Stamps DE2/3/4/7/11/12/13/18/22/32/37/41/42/49; fresh STAN (6-digit) and RRN (12-char).
- **Key fix:** `_rrn()` format `%y%j%H%M%S` (11 chars) + 1 random digit = exactly 12 chars
  (ISO 8583 DE37 fixed width).
- **Verified:** Visa private DEs {44,62,63}; MC {48,61,63}; override works; round-trip clean.

### T4 — Mapping engine (`backend/mapping/engine.py` + `specs/*.yaml`)
- YAML-spec-driven ISO 8583 → JPF (JSON Payment Format) mapper.
- Four per-network spec files: `specs/visa.yaml`, `mastercard.yaml`, `amex.yaml`, `discover.yaml`.
- `map_to_jpf(iso_fields, network, icc_hex=None)` → `MappingResult(jpf, pii_safe, warnings, network)`.
- PII enforcement: PAN never stored clear; `card.pan_token` / `card.pan_last_four` / `card.pan_hash` stored.
- Minimal BER-TLV parser for DE55 EMV data; validation rules flag DE4↔9F02 / DE49↔5F2A mismatches.
- **Verified:** Visa JPF == MC JPF (ignoring network-private blocks, STAN/RRN, PAN fields);
  mismatch in 9F02 correctly flagged as warning.

### T5 — Wire into existing path (`backend/main.py`)
- Added imports for `build_0100` and `map_to_jpf` with graceful fallback (`_ISO_AVAILABLE`).
- Extended `_execute_scenario_internal(scenario, unique, network_override)`:
  builds ISO 8583 in-process alongside the HTTP path to the acquirer microservice.
- `/execute/{scenario_id}` response now includes `iso_message`, `jpf`, `iso_warnings`.
- `/execute/{scenario_id}?network=mastercard` forces network override via query param.
- **Verified:** iso_message present with correct private_des; full PAN absent from jpf;
  network_override flows through correctly.

### T6 — Vertical-slice pytest (`tests/test_vertical_slice.py`)
- 26 parametrized tests covering 3 scenario rows (grocery/electronics/e-commerce).
- `TestIsoNetworkDialects`: Visa {44,62,63} ≠ MC {48,61,63}; field key sets differ.
- `TestJpfDialectAgnostic`: JPF identical across networks; private blocks differ; PII safe.
- `TestSutDecision`: RC and decision match expectation for Visa and Mastercard.
- `TestStanRrnUniqueness`: STAN diverse (≥15 unique in 20 draws); RRN exactly 12 chars.
- `TestMismatchFlagging`: 9F02 mismatch flagged; clean message has zero warnings.
- Added `.github/workflows/vertical_slice.yml` GitHub Actions CI workflow.
- **Result:** 26/26 PASSED (no Docker required — acquirer HTTP call is mocked).

### T7 — UI: network selector (`frontend/pages/02_scenario_lab.py`)
- Added **Network** sidebar selector: "(auto — BIN routing)" / Visa / Mastercard / Amex / Discover.
- Run button passes `?network=<override>` to `/execute/{scenario_id}` when a network is chosen.
- After each run, renders **ISO 8583 ↔ JPF contrast panel**:
  - Left column: DE table with private DEs highlighted in amber (★).
  - Right column: JPF canonical JSON viewer + packed hex expander.
  - Network badge shows active dialect; MTI / STAN / RRN shown inline.
  - EMV validation warnings surfaced as `st.warning()` banners.

---

## [Unreleased] — P0 AI Copilot fixes

### T0.1 — Fixed: `agent_repository.py` import break that silenced all `/ai/*` endpoints
- **Root cause:** `from backend.mongo_repository import db` — `mongo_repository.py` exports
  no `db` alias; this `ImportError` cascaded into `main.py`'s `try/except`, setting
  `ai_router = None` and silently removing every `/ai/*` route.
- **Fix:** Rewrote `agent_repository.py` to import the collection objects already exported
  by `mongo_repository.py` (`agents`, `prompts`, `guardrails`, `templates`) and query them
  by `_id` (matching the seed file key), not by the non-existent `db.agent_definitions`.
- **Verification:** `python3 -c "import backend.ai_routes"` succeeds; all 5 `/ai/*` routes
  listed in router.

### T0.2 — Fixed: `generate_with_fallback` undefined references + wired into endpoints
- **Root cause:** `ai_provider.py` referenced undefined `execute_agent` and `user_prompt`;
  instantiated an unused `OllamaClient()`; would raise `NameError` immediately.
- **Fix:** Replaced function body with correct Claude-first / Ollama-fallback logic using
  a lazy `from backend.agent_service import execute_agent` to avoid circular imports.
- **Wired in:** `/generate_scenario` and `/run_test` now call `generate_with_fallback`
  instead of calling `execute_agent` directly.
- **Verification:** `python3 -c "import backend.ai_routes"` — no `NameError`.

### T0.3 — Fixed: `_InMemoryCollection.find_one` only matched `"id"` queries
- **Root cause:** Mongo-down fallback returned `None` for any `_id` or `{}` query, so
  `get_agent()`, `get_prompt()`, and `get_template()` all returned `None`, causing the
  Ollama path to die with "No scenario template found".
- **Fix:** Extended `find_one` to match on `_id` (seed files use `_id`), `id` (scenario
  files use `id`), and `{}` (empty query returns first doc, used by `get_template()`).
  Also fixed `replace_one` key resolution order to prefer `_id`.
- **Verification:** Unit assertions pass for all three query shapes.

### T0.4 — Fixed: normalized provider return shapes
- **Root cause:** Claude system prompt returned a wrapper
  `{"scenario": {...}, "explanation": ..., "suggested_rc": ..., "jit_behavior": ...}`,
  while `execute_agent` (Ollama) returned the bare scenario dict. `/run_test` fed the
  wrapper directly to `_execute_scenario_internal`, which expected a bare dict.
- **Fix:** Introduced `_claude_scenario_fn(prompt)` that unpacks the Claude wrapper and
  attaches metadata under `_meta` (non-conflicting key). Both providers now return a
  bare scenario dict. `/run_test` strips `_meta` before execution and persists the bare
  dict. The `_meta` fields are still available to callers that need explanation text.
- **Verification:** `/run_test` response always has `{"scenario": <bare>, "execution_result": <trace>, "analysis": <dict>}`.

### T0.5 — Fixed: dead `_call_ollama` helper with wrong `OllamaClient` method
- **Root cause:** `_call_ollama` called `client.generate_scenario(prompt)` but
  `OllamaClient` only has `generate(model, prompt)` — `AttributeError` if invoked.
- **Fix:** Removed `_call_ollama` entirely. The Ollama path goes through `execute_agent`
  (in `agent_service.py`) which correctly calls `client.generate(model=..., prompt=...)`.
- **Verification:** `grep -rn "client.generate_scenario" backend/` → no matches.

### T0.6 — Fixed: Claude model hardcoded; now reads `ANTHROPIC_MODEL` env var
- **Root cause:** `_call_claude` used `model="claude-opus-4-5-20251101"` (hardcoded,
  also an invalid/stale model ID).
- **Fix:** `_call_claude` reads `os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-5")`
  at call time. Updated `docker-compose.yml` to pass
  `ANTHROPIC_MODEL=${ANTHROPIC_MODEL:-claude-opus-4-5}` so the default can be overridden
  via host env or `.env` file with no code changes.
- **Verification:** `inspect.getsource(_call_claude)` confirms `ANTHROPIC_MODEL` is read;
  model string `claude-opus-4-5` is a valid current Claude API model.
