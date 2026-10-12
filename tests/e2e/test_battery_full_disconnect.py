from conftest import post, wait_until


def vehicle(state, vehicle_id):
    return next(item for item in state["vehicles"] if item["id"] == vehicle_id)


def port(state, port_id):
    return next(item for item in state["ports"] if item["id"] == port_id)


def test_full_vehicle_stops_and_disconnects_from_port(connected_vehicles):
    response = post("/api/start")
    assert response["accepted"] is True

    full_state = wait_until(
        lambda state: vehicle(state, "EV04")["state"] == "FULL"
        and any(
            event["code"] == "BATTERY_FULL"
            and event["vehicleId"] == "EV04"
            for event in state["events"]
        )
        and any(
            event["code"] == "CHARGING_STOPPED"
            and event["vehicleId"] == "EV04"
            for event in state["events"]
        )
    )
    full_vehicle = vehicle(full_state, "EV04")
    assert full_vehicle["soc"] == 100
    assert full_vehicle["allocatedPower"] == 0
    assert full_vehicle["connected"] is True
    assert full_vehicle["port"] == 4

    disconnected_state = wait_until(
        lambda state: vehicle(state, "EV04")["state"] == "DISCONNECTED"
        and vehicle(state, "EV04")["connected"] is False
        and vehicle(state, "EV04")["port"] is None
        and any(
            event["code"] == "VEHICLE_DISCONNECTED"
            and event["vehicleId"] == "EV04"
            for event in state["events"]
        )
    )
    disconnected_vehicle = vehicle(disconnected_state, "EV04")
    assert disconnected_vehicle["allocatedPower"] == 0
    assert port(disconnected_state, 4) == {
        "id": 4,
        "state": "IDLE",
        "vehicleId": None,
        "power": 0.0,
    }
