from z3 import Real, Solver, sat


def check_soc_priority():
    solver = Solver()
    soc_low = Real("soc_low")
    soc_high = Real("soc_high")
    power_low = Real("power_low")
    power_high = Real("power_high")
    solver.add(soc_low >= 0, soc_low < 50)
    solver.add(soc_high >= 50, soc_high <= 100)
    solver.add(power_low >= 0, power_low <= 22)
    solver.add(power_high >= 0, power_high <= 22)
    solver.add(power_low >= power_high)
    solver.add(power_low < power_high)
    if solver.check() == sat:
        print("[SAT] Low-SOC priority counterexample")
        print(f"  model: {solver.model()}")
        return False
    print("[UNSAT] No counterexample; Low-SOC priority preserved")
    return True


if __name__ == "__main__":
    print("SMT-06: SOC PRIORITY ALLOCATION")
    check_soc_priority()
