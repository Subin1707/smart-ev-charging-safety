# Generated Gateway Auth Z3 counterexample search.
# Source constraint: GA-C06
# Meaning: Emergency implies not Charging
from z3 import Bool, Solver, And, Not

connected = Bool("connected")
token_valid = Bool("token_valid")
authenticated = Bool("authenticated")
start_request = Bool("start_request")
safety_ok = Bool("safety_ok")
emergency = Bool("emergency")
charging = Bool("charging")

s = Solver()

# A satisfiable result means the constraint can be violated.
s.add(And(emergency, charging))

print(s.check())
print(s.model())
