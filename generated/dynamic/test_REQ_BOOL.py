def trigger_holds(soc):
    return soc >= 100


def check_requirement(soc, charging):
    return not trigger_holds(soc) or charging == False


def test_REQ_BOOL_boundary():
    trigger_cases = [
        (99.9, False),
        (100, True),
        (100.1, True)
    ]

    for value, trigger_expected in trigger_cases:
        assert trigger_holds(value) == trigger_expected
        if trigger_expected:
            assert check_requirement(value, False)

    violation_cases = [
        (100, True, False),
        (100.1, True, False)
    ]
    for value, property_value, expected_result in violation_cases:
        assert check_requirement(value, property_value) is expected_result
