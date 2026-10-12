from conftest import post, wait_until


def vehicle(state, vehicle_id):
    return next(item for item in state["vehicles"] if item["id"] == vehicle_id)


def safety_check(state, check_id):
    return next(item for item in state["safetyChecks"] if item["id"] == check_id)


def test_overheat_trip_stops_vehicle_and_emits_event(connected_vehicles):
    post("/api/start")
    wait_until(
        lambda state: state["simulation"]["status"] == "RUNNING"
        and state["tick"] >= 1
        and vehicle(state, "EV02")["state"] == "CHARGING"
    )

    response = post(
        "/api/fault",
        json={"vehicleId": "EV02", "faultType": "OVERHEAT"},
    )
    assert response["accepted"] is True

    state = wait_until(lambda current: vehicle(current, "EV02")["state"] == "FAULT")
    ev02 = vehicle(state, "EV02")

    assert ev02["allocatedPower"] == 0
    assert ev02["fault"] == "FAULT"
    assert any(
        event["code"] == "OVERHEAT_TRIP" and event["vehicleId"] == "EV02"
        for event in state["events"]
    )
    assert safety_check(state, "FAULT_ZERO_POWER")["status"] == "PASS"
    assert state["station"]["totalPower"] <= state["station"]["maxPower"]
