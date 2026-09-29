# Local verification

- Baseline repository: `Wanyiava/jhu_software_concepts`, commit `30b9e207c28e898cc603b357e07240425ee60dfe`.
- Local platform: Windows, Python 3.13.5, PostgreSQL 16.15 in an isolated Docker container.
- Full marker-union run: **94 passed**, **100% statements and branches** across all nine Python modules in `src` (including the empty package initializer).
- Default invocation from repository root also passed all 94 tests at 100% coverage.
- Fresh official Linux container: Python 3.13.15, pinned requirements installed from scratch; 94 tests passed in 1.38 seconds at 100% statement/branch coverage; strict Sphinx build succeeded.
- Sphinx 8.2.3: strict `-W --keep-going` HTML build succeeded.
- Generated documentation: 18 HTML pages; local href/src references checked with no missing files.
- Browser review: application and Sphinx pages rendered; Update Analysis refreshed successfully, all percentage strings had two decimals, and no browser JavaScript errors were recorded.
- No source coverage exclusions, skipped tests, live HTTP calls in tests, or arbitrary busy-check sleeps.

`coverage_summary.txt` contains the full terminal report. `linux_verification.txt`
records a separate fresh Linux-container dependency/test/docs check. These are
local verification records, not GitHub Actions evidence. Remote publication and
final submission are delegated to the recipient as requested by the user.
