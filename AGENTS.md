# Repository instructions

Read `../AGENTS.md` first if it exists, then this file and `README.md`.

- Keep this project independent of the maintainer's production services and private data.
- Use Python 3.10+ standard library at runtime; keep the browser example dependency-free.
- Preserve exact Unicode input. Do not silently normalize characters, strip whitespace or infer pronunciation, meaning, registration eligibility or name quality.
- Regenerate data only through `scripts/build_data.py` from the pinned Unihan snapshot. Retain Unicode attribution and the separate data license.
- Changes to the dataset must keep JSON, CSV, TXT and manifest consistent. Update both READMEs when behavior changes.
- Use synthetic examples rather than personal information. Do not add credentials or trackers.
- Run the checks documented in `README.md`; when local workspace rules require Docker, run them inside a container.
- Do not publish, push or change repository settings without the owner's authorization for that operation.
