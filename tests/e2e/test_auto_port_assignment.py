from conftest import get_state, post, wait_until


def test_scheduler_assigns_unique_reserved_ports_on_next_tick(simulator):
    response = post("/api/reset")
    assert response["accepted"] is True

    reset_state = wait_until(
        lambda state: state["tick"] == 0
        and all(vehicle["state"] == "WAITING" for vehicle in state["vehicles"])
        and all(vehicle["assignedPort"] is None for vehicle in state["vehicles"])
        and all(port["state"] == "IDLE" for port in state["ports"])
    )
    assert reset_state["station"]["totalPower"] == 0

    response = post("/api/tick")
    assert response["accepted"] is True

    state = wait_until(
        lambda current: current["tick"] == 1
        and any(vehicle["assignedPort"] is not None for vehicle in current["vehicles"])
    )
    assigned_vehicles = [
        vehicle for vehicle in state["vehicles"] if vehicle["assignedPort"] is not None
    ]
    assigned_ports = [vehicle["assignedPort"] for vehicle in assigned_vehicles]

    assert assigned_ports
    assert len(assigned_ports) == len(set(assigned_ports))
    assert all(vehicle["state"] == "WAITING" for vehicle in assigned_vehicles)

    for vehicle in assigned_vehicles:
        assigned_port = next(
            port for port in state["ports"] if port["id"] == vehicle["assignedPort"]
        )
        assert assigned_port["state"] == "RESERVED"
        assert assigned_port["vehicleId"] == vehicle["id"]

    assert any(event["code"] == "PORT_ASSIGNED" for event in state["events"])
    assert get_state()["tick"] == 1


def test_vehicle_arrival_connects_only_its_reserved_port(simulator):
    post("/api/reset")
    wait_until(
        lambda state: state["tick"] == 0
        and any(event["code"] == "RESET" for event in state["events"])
    )
    post("/api/tick")

    reserved_state = wait_until(
        lambda state: state["tick"] == 1
        and next(vehicle for vehicle in state["vehicles"] if vehicle["id"] == "EV01")["assignedPort"] is not None
    )
    assigned_port = next(
        vehicle for vehicle in reserved_state["vehicles"] if vehicle["id"] == "EV01"
    )["assignedPort"]

    response = post(
        "/api/vehicle-arrived",
        json={"vehicleId": "EV01", "portId": assigned_port},
    )
    assert response["accepted"] is True

    state = wait_until(
        lambda current: next(
            vehicle for vehicle in current["vehicles"] if vehicle["id"] == "EV01"
        )["state"] == "CONNECTED"
    )
    port = next(port for port in state["ports"] if port["id"] == assigned_port)
    assert port["state"] == "CONNECTED"
    assert port["vehicleId"] == "EV01"
    assert any(
        event["code"] == "VEHICLE_ARRIVED_AT_PORT"
        and event["vehicleId"] == "EV01"
        for event in state["events"]
    )
