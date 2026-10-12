def check_requirement(total_power):
    return total_power <= 100


def test_REQ_01_boundary():
    cases = [
        (99, True),
        (100, True),
        (101, False)
    ]

    for value, expected in cases:
        assert check_requirement(value) == expected
