import time

from conftest import get_state, post, wait_until


def test_next_tick_advances_exactly_one_tick(simulator):
    before = get_state()["tick"]

    response = post("/api/tick")
    assert response["accepted"] is True
    assert response["command"] == "NEXT_TICK"

    state = wait_until(lambda current: current["tick"] == before + 1)
    assert state["simulation"]["status"] == "PAUSED"

    time.sleep(0.5)
    assert get_state()["tick"] == before + 1
