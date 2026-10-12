def trigger_holds(temperature, charging):
    return (temperature >= 60 and charging == True)


def property_check(temperature, charging, power, state):
    return not trigger_holds(temperature, charging) or (power == 0 and state == 'FAULT')


def test_SR03_truth_table_and_boundaries():
    cases = [
        ((59.9, False), False),
        ((60, False), False),
        ((59.9, True), False),
        ((60, True), True)
    ]
    for values, expected in cases:
        arguments = values if isinstance(values, tuple) else (values,)
        assert trigger_holds(*arguments) is expected
