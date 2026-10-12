from z3 import And, Bool, Real, Solver, sat

MAX_SAFE_TEMP = 60


def solve_smt_temp(is_vulnerable):
    solver = Solver()
    temperature = Real("temperature")
    charging = Bool("charging")
    solver.add(temperature >= -20, temperature <= 120)
    if is_vulnerable:
        solver.add(charging == True)
    else:
        solver.add(charging == (temperature < MAX_SAFE_TEMP))
    solver.add(And(temperature >= MAX_SAFE_TEMP, charging))
    if solver.check() == sat:
        print("[VULNERABLE] SAT - overheat while charging")
        print(f"  counterexample: temperature={solver.model()[temperature]}, charging=True")
        return False
    print("[FIXED] UNSAT - No counterexample; OVERHEAT -> NOT CHARGING")
    return True


if __name__ == "__main__":
    print("SMT-02: TEMPERATURE SAFETY")
    solve_smt_temp(is_vulnerable=True)
    solve_smt_temp(is_vulnerable=False)
