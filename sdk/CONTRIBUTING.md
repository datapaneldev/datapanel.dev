# Contributing

Install the development extra, run the offline examples, then read the small shared client and workflow modules. A new scenario should have a copyable user goal, runnable entry point, documented inputs/side effects, clear output, and a behavior test. Keep transport simulations separate from assertions about real services.

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
ruff check .
ruff format --check .
python scripts/verify_examples.py
python scripts/check_repository.py
```

For API changes, compare against the current upstream contract and retain a versioned, sanitized verification record. Never amend mock behavior merely to hide a mismatch in the real service. Document unsupported execution modes, negative results and missing evidence.

The exact dependency lock reflects the tested Python 3.10 environment. `pyproject.toml` defines the supported compatibility bounds. To reproduce that environment, install the lock first, then `pip install -e . --no-deps`. Other Python/platform combinations are checked by the configured CI matrix when published.

Public pull requests should not include credentials, private data, `work/`, temporary integration environments, account details, production logs or internal infrastructure. Keep useful failures reproducible using synthetic fixtures.
