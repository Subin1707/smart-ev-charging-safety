from z3 import Int, Real, Solver, sat


def generate_boundary_inputs():
	port = Int("port")
	power = Real("power")
	cases = []

	for constraint, label in [
		(port < 1, "port below lower bound"),
		(port > 5, "port above upper bound"),
		(power < 0, "negative power"),
		(power > 22, "power above port limit"),
	]:
		solver = Solver()
		solver.add(port >= -100, port <= 100, power >= -100, power <= 100, constraint)
		if solver.check() != sat:
			raise RuntimeError(f"No model for white-box constraint: {label}")
		model = solver.model()
		cases.append((label, f"START|EV01|{model.eval(port)}|{model.eval(power)}"))

	return cases
