# Generated from specification/auth.json
from z3 import Bool, Int, Solver, unsat

C = Bool('C')
T = Bool('T')
A = Bool('A')
X = Bool('X')
A_after_disconnect = Bool('A_after_disconnect')

s = Solver()

s.push()
s.add(~((~ A) | C))
if s.check() != unsat:
    print('Counter-example found for AUTH-01:', s.model())
else:
    print('AUTH-01: PASS')
s.pop()

s.push()
s.add(~((~ A) | T))
if s.check() != unsat:
    print('Counter-example found for AUTH-02:', s.model())
else:
    print('AUTH-02: PASS')
s.pop()

s.push()
s.add(~(C | (~ A)))
if s.check() != unsat:
    print('Counter-example found for AUTH-03:', s.model())
else:
    print('AUTH-03: PASS')
s.pop()

s.push()
s.add(~((~ X) | (~ A_after_disconnect)))
if s.check() != unsat:
    print('Counter-example found for AUTH-04:', s.model())
else:
    print('AUTH-04: PASS')
s.pop()
