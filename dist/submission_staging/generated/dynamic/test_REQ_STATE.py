def trigger_holds(temperature):
    return temperature >= 60


def check_requirement(temperature, state):
    return not trigger_holds(temperature) or state == 'FAULT'


def test_REQ_STATE_boundary():
    trigger_cases = [
        (59.9, False),
        (60, True),
        (60.1, True)
    ]

    for value, trigger_expected in trigger_cases:
        assert trigger_holds(value) == trigger_expected
        if trigger_expected:
            assert check_requirement(value, 'FAULT')

    violation_cases = [
        (60, '__VIOLATION__', False),
        (60.1, '__VIOLATION__', False)
    ]
    for value, property_value, expected_result in violation_cases:
        assert check_requirement(value, property_value) is expected_result
