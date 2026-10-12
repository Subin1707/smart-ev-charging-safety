def trigger_holds(pressure, temperature):
    return (pressure > 200 or temperature >= 80)


def property_check(pressure, temperature, alarm):
    return not trigger_holds(pressure, temperature) or alarm == True


def test_REQ_OR_truth_table_and_boundaries():
    cases = [
        ((200, 79.9), False),
        ((200.1, 79.9), True),
        ((200, 80), True),
        ((200.1, 80), True)
    ]
    for values, expected in cases:
        arguments = values if isinstance(values, tuple) else (values,)
        assert trigger_holds(*arguments) is expected
