from conftest import post, wait_until


def vehicle(state, vehicle_id):
    return next(item for item in state["vehicles"] if item["id"] == vehicle_id)


def test_loaded_auth_failure_blocks_charging(connected_vehicles):
    response = post(
        "/api/scenario",
        json={"scenario": "AUTH_FAILURE", "vehicleId": "EV02"},
    )
    assert response["accepted"] is True
    wait_until(lambda state: state["scenario"]["status"] == "LOADED")

    post("/api/start")
    state = wait_until(
        lambda current: current["scenario"]["triggered"] is True
        and any(
            event["code"] == "SCENARIO_TRIGGERED"
            and event["vehicleId"] == "EV02"
            for event in current["events"]
        )
    )

    ev02 = vehicle(state, "EV02")
    assert ev02["authenticated"] is False
    assert ev02["allocatedPower"] == 0
    assert ev02["state"] != "CHARGING"
    assert any(port["vehicleId"] == "EV02" and port["state"] == "FAULT" for port in state["ports"])
