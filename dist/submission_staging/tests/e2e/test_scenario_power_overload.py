from conftest import post, wait_until


def test_loaded_power_overload_stays_within_station_limit(simulator):
    response = post(
        "/api/scenario",
        json={"scenario": "POWER_OVERLOAD", "vehicleId": "EV01"},
    )
    assert response["accepted"] is True
    wait_until(lambda state: state["scenario"]["status"] == "LOADED")

    post("/api/start")
    state = wait_until(
        lambda current: current["scenario"]["triggered"] is True
        and any(event["code"] == "SCENARIO_TRIGGERED" for event in current["events"])
    )

    assert state["station"]["totalPower"] <= state["station"]["maxPower"]
    power_check = next(
        check for check in state["safetyChecks"] if check["id"] == "POWER_LIMIT"
    )
    assert power_check["status"] == "PASS"
