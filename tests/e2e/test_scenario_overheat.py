from conftest import post, wait_until


def vehicle(state, vehicle_id):
    return next(item for item in state["vehicles"] if item["id"] == vehicle_id)


def test_loaded_overheat_triggers_safety_trip(simulator):
    response = post(
        "/api/scenario",
        json={"scenario": "OVERHEAT", "vehicleId": "EV02"},
    )
    assert response["accepted"] is True

    loaded = wait_until(
        lambda state: state["scenario"]["name"] == "OVERHEAT"
        and state["scenario"]["vehicleId"] == "EV02"
        and state["scenario"]["status"] == "LOADED"
        and state["scenario"]["triggered"] is False
    )
    assert vehicle(loaded, "EV02")["temperature"] == 55

    post("/api/start")
    state = wait_until(
        lambda current: current["scenario"]["triggered"] is True
        and any(event["code"] == "SCENARIO_TRIGGERED" for event in current["events"])
        and any(
            event["code"] == "OVERHEAT_TRIP"
            and event["vehicleId"] == "EV02"
            for event in current["events"]
        )
    )

    ev02 = vehicle(state, "EV02")
    assert ev02["state"] == "FAULT"
    assert ev02["allocatedPower"] == 0
    fault_check = next(
        check for check in state["safetyChecks"] if check["id"] == "FAULT_ZERO_POWER"
    )
    assert fault_check["status"] == "PASS"
