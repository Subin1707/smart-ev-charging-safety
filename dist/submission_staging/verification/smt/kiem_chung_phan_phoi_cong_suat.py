from z3 import Real, Solver, Sum, sat

PORT_COUNT = 5
PORT_LIMIT = 22
STATION_LIMIT = 100


def solve_smt_power(is_vulnerable=False):
    solver = Solver()
    power = [Real(f"power_{i}") for i in range(PORT_COUNT)]
    for value in power:
        solver.add(value >= 0, value <= PORT_LIMIT)
    total_power = Sum(power)
    if not is_vulnerable:
        solver.add(total_power <= STATION_LIMIT)
    solver.add(total_power > STATION_LIMIT)
    if solver.check() == sat:
        model = solver.model()
        print("[VULNERABLE] SAT - station overload possible")
        print(f"  total power={model.eval(total_power)} kW")
        return False
    print("[FIXED] UNSAT - No counterexample; SUM(PORT_POWER) <= 100 kW")
    return True


if __name__ == "__main__":
    print("SMT-03/04: POWER ALLOCATION VERIFICATION")
    solve_smt_power(is_vulnerable=True)
    solve_smt_power(is_vulnerable=False)
