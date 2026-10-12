def check_requirement(soc):
    return soc >= 0 and soc <= 100


def test_REQ_02_boundary():
    cases = [
        (-0.1, False),
        (0, True),
        (0.1, True),
        (99.9, True),
        (100, True),
        (100.1, False)
    ]

    for value, expected in cases:
        assert check_requirement(value) == expected
