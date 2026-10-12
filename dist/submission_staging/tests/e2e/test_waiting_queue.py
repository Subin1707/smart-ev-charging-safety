from conftest import post, wait_until


def vehicle(state, vehicle_id):
    return next(item for item in state["vehicles"] if item["id"] == vehicle_id)


def test_waiting_queue_is_fifo_when_port_becomes_available(connected_vehicles):
    response = post("/api/start")
    assert response["accepted"] is True

    queued_state = wait_until(
        lambda state: state["queue"]["vehicles"] == ["EV06", "EV07"]
    )
    assert queued_state["queue"]["count"] == 2
    assert vehicle(queued_state, "EV06")["assignedPort"] is None
    assert vehicle(queued_state, "EV07")["assignedPort"] is None

    assigned_state = wait_until(
        lambda state: vehicle(state, "EV06")["assignedPort"] is not None
        and vehicle(state, "EV07")["assignedPort"] is None
        and any(
            event["code"] == "PORT_ASSIGNED_FROM_QUEUE"
            and event["vehicleId"] == "EV06"
            for event in state["events"]
        )
    )

    ev06 = vehicle(assigned_state, "EV06")
    assert assigned_state["queue"]["vehicles"] == ["EV07"]
    assert ev06["assignedPort"] == 4
    assert any(
        port["id"] == 4
        and port["state"] == "RESERVED"
        and port["vehicleId"] == "EV06"
        for port in assigned_state["ports"]
    )
