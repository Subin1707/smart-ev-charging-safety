# Generated Gateway Auth aggregate Z3 proof checks.
from z3 import Bool, BoolVal, Solver, And, Not, Or, unsat

connected = Bool("connected")
token_valid = Bool("token_valid")
authenticated = Bool("authenticated")
start_request = Bool("start_request")
safety_ok = Bool("safety_ok")
emergency = Bool("emergency")
charging = Bool("charging")
start_allowed = Bool("start_allowed")

gateway_states = [
    # C, T, A, R, S, E, charging, start_allowed
    (False, False, False, False, True,  False, False, False), # WAITING
    (True,  False, False, False, True,  False, False, False), # CONNECTED
    (True,  True,  True,  False, True,  False, False, False), # AUTH_OK
    (True,  False, False, False, True,  False, False, False), # AUTH_FAIL
    (True,  True,  True,  True,  True,  False, True,  True),  # CHARGING
    (True,  True,  True,  False, True,  False, False, False), # STOPPED
    (True,  True,  True,  True,  False, False, False, False), # FAULT
    (True,  True,  True,  True,  False, True,  False, False), # EMERGENCY
]

state_formula = Or(*[
    And(
        connected == BoolVal(C),
        token_valid == BoolVal(T),
        authenticated == BoolVal(A),
        start_request == BoolVal(R),
        safety_ok == BoolVal(S),
        emergency == BoolVal(E),
        charging == BoolVal(CH),
        start_allowed == BoolVal(SA),
    )
    for C, T, A, R, S, E, CH, SA in gateway_states
])

def check(constraint_id, violation_formula):
    solver = Solver()
    solver.add(state_formula)
    solver.add(violation_formula)
    result = solver.check()
    if result == unsat:
        print(f"{constraint_id} : PASS")
    else:
        print(f"{constraint_id} : FAIL {solver.model()}")

check("GA-C01", And(authenticated, Not(connected)))
check("GA-C02", And(authenticated, Not(token_valid)))
check("GA-C03", And(charging, Not(connected)))
check("GA-C04", And(charging, Not(authenticated)))
check("GA-C05", And(charging, Not(safety_ok)))
check("GA-C06", And(emergency, charging))
check("GA-C07", And(Not(connected), authenticated))
check("GA-C08", And(start_allowed, Not(And(connected, token_valid, authenticated, start_request, safety_ok, Not(emergency)))))
