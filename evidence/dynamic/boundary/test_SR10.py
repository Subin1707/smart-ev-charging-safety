def check_requirement(total_power, port_power):
    return (total_power <= 100 and port_power <= 22)

def test_SR10_boundaries():
    for values, expected in [((99, 21), True), ((99, 22), True), ((99, 23), False), ((100, 21), True), ((100, 22), True), ((100, 23), False), ((101, 21), False), ((101, 22), False), ((101, 23), False)]:
        assert check_requirement(*values) == expected
