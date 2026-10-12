def trigger_holds(soc):
    return soc >= 100


def check_requirement(soc, charging):
    return not trigger_holds(soc) or charging == 'false'


def test_REQ_05_boundary():
    trigger_cases = [
        (99.9, False),
        (100, True),
        (100.1, True)
    ]

    for value, trigger_expected in trigger_cases:
        assert trigger_holds(value) == trigger_expected
        if trigger_expected:
            assert check_requirement(value, 'false')
