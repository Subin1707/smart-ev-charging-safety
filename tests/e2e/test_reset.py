from conftest import post, wait_until


def test_reset_returns_to_paused_zero_state(simulator):
    response = post("/api/reset")
    assert response["accepted"] is True
    assert response["command"] == "RESET"

    state = wait_until(
        lambda current: current["tick"] == 0
        and current["simulation"]["status"] == "PAUSED"
        and all(vehicle["allocatedPower"] == 0 for vehicle in current["vehicles"])
        and any(event["code"] == "RESET" for event in current["events"])
    )

    assert state["station"]["emergency"] is False
    assert all(vehicle["allocatedPower"] == 0 for vehicle in state["vehicles"])
