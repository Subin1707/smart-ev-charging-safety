from conftest import post, wait_until


def test_emergency_stop_cuts_all_power_and_emits_event(simulator):
    response = post("/api/emergency-stop")
    assert response["accepted"] is True
    assert response["command"] == "EMERGENCY_STOP"

    state = wait_until(
        lambda current: current["station"]["emergency"] is True
        and current["station"]["totalPower"] == 0
        and all(vehicle["allocatedPower"] == 0 for vehicle in current["vehicles"])
        and any(event["code"] == "EMERGENCY_STOP" for event in current["events"])
    )

    assert state["safetyChecks"]
    emergency_check = next(
        check for check in state["safetyChecks"] if check["id"] == "EMERGENCY_ZERO_POWER"
    )
    assert emergency_check["status"] == "PASS"
