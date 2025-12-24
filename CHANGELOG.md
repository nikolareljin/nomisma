# Changelog

## 2025-12-21
- Fix Docker build issues (frontend install/build, backend deps) and CI workflow.
- Make database init idempotent and add microscope compose override + prompt.
- Improve camera device detection and allow microscope endpoints without auth.
- Add note on the project name origin in README.

## 2025-12-22
- Add Docker-based test runner for backend, frontend, E2E, and API health checks.
- Tweak test script output formatting.

## 2025-12-23
- Add cross-platform setup scripts and one-line installers.
- Prompt for install path during setup.
- Fix backend test runner to rebuild image and run pytest via Python module.
- Add Gemini analysis option to `./test -t api` with image input and jq output.
- Refresh README structure and test docs.
- Update frontend tests.

## 2025-12-20
- Initial project import and README.
- Update start scripts to help configure API keys.
- Refresh `.env` examples.
