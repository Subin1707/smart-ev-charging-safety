# Smart EV bridge

The bridge exposes the latest C simulator snapshot to the React frontend.

From the repository root:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn bridge.main:app --reload --port 8000
```

The read-only endpoints are:

- `GET /api/health`
- `GET /api/state`

The C simulator writes `logs/telemetry/latest_state.json` after each simulation
tick. Set `SMART_EV_SNAPSHOT_PATH` to override that location.