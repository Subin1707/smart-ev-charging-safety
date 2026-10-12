# HTTP E2E tests

These tests exercise the real boundary:

`pytest -> FastAPI bridge -> command.json -> C simulator -> telemetry JSON -> FastAPI`

Run the first E2E scenarios with:

```powershell
python -m pytest tests/e2e -q
```

By default, `conftest.py` starts FastAPI on port `8010` and starts a fresh fixed-demo C simulator for each test. Use `SMART_EV_E2E_EXTERNAL_SERVICES=1` and `SMART_EV_E2E_BASE_URL` when the bridge and simulator are already running.

Managed tests compile their own executable and keep telemetry, commands and logs
in a temporary runtime directory. They do not share the dashboard's live files.
Charging tests explicitly reserve ports and send vehicle-arrival requests before
starting charging; reserving a port alone does not connect a vehicle.

To rerun only this stage and save its evidence:

```powershell
python scripts/verify_all.py --stage e2e-test
```

Read `evidence/06_e2e/results.txt` and `evidence/summary_e2e-test.json` for this
rerun. The full dashboard summary still describes the last full pipeline run.

The current suite covers:

- Reset returns to tick zero and paused state.
- Next tick advances exactly one tick while paused.
- Overheat stops EV02, cuts power, emits `OVERHEAT_TRIP`, and passes `FAULT_ZERO_POWER`.
