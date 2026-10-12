from z3 import Real, Solver, sat


def solve_smt_energy(is_vulnerable=False):
    solver = Solver()
    power = Real("power_kw")
    duration = Real("duration_h")
    energy = Real("energy_kwh")
    if is_vulnerable:
        solver.add(power >= -22, power <= 22)
    else:
        solver.add(power >= 0, power <= 22)
    solver.add(duration >= 0, duration <= 24)
    solver.add(energy == power * duration)
    solver.add(energy < 0)
    if solver.check() == sat:
        print("[VULNERABLE] SAT - negative energy counterexample")
        print(f"  model: {solver.model()}")
        return False
    print("[FIXED] UNSAT - No counterexample; energy is non-negative")
    return True


if __name__ == "__main__":
    print("SMT-05: ENERGY CALCULATION")
    solve_smt_energy(is_vulnerable=True)
    solve_smt_energy(is_vulnerable=False)
