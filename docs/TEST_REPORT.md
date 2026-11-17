# Development test report

Run in the provided build environment on 2026-10-21.

- Python source compilation: passed for API, database, configuration, security, retrieval, training/evaluation and role-promotion modules.
- Pytest: 3 tests passed — password hashing round trip, text chunking, and API authentication/role guard integration.
- API smoke test: health returned 200; registration returned 201; authenticated `/api/auth/me`, courses and SHAAN chat returned 200; student access to admin users returned 403.
- ML training: completed on 231 synthetic text examples across 11 intents.
- ML holdout evaluation: 58 holdout examples, accuracy approximately 0.81, with per-class metrics emitted by `python -m app.ml.evaluate`.
- Frontend build: not verified in this environment because npm dependency installation timed out. Run `npm install` and `npm run build` locally.
- Cloud deployment: not performed. Docker files are provided for a local container deployment.

This is a development smoke-test report, not a production security audit or institutional acceptance test.
