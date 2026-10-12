from z3 import If, Real, Solver, sat


def solve_smt_soc(is_vulnerable=False):
    solver = Solver()
    current_soc = Real("current_soc")
    delta_soc = Real("delta_soc")
    new_soc = Real("new_soc")
    solver.add(current_soc >= 0, current_soc <= 100)
    solver.add(delta_soc >= 0, delta_soc <= 50)
    if is_vulnerable:
        solver.add(new_soc == current_soc + delta_soc)
    else:
        solver.add(new_soc == If(current_soc + delta_soc > 100, 100, current_soc + delta_soc))
    solver.add(new_soc > 100)
    if solver.check() == sat:
        model = solver.model()
        print("[VULNERABLE] SAT - SOC range counterexample")
        print(f"  current_soc={model[current_soc]}, delta_soc={model[delta_soc]}, new_soc={model[new_soc]}")
        return False
    print("[FIXED] UNSAT - No counterexample; 0 <= SOC <= 100")
    return True


if __name__ == "__main__":
    print("SMT-01: SOC RANGE VERIFICATION")
    solve_smt_soc(is_vulnerable=True)
    solve_smt_soc(is_vulnerable=False)
