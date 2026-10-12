# Generated from specification/port.json
from z3 import Bool, Int, Solver, unsat

C = Bool('C')
O = Bool('O')
P = Bool('P')
F = Bool('F')

s = Solver()

s.push()
s.add(~((~ P) | C))
if s.check() != unsat:
    print('Counter-example found for PORT-01:', s.model())
else:
    print('PORT-01: PASS')
s.pop()

s.push()
s.add(~((~ P) | O))
if s.check() != unsat:
    print('Counter-example found for PORT-02:', s.model())
else:
    print('PORT-02: PASS')
s.pop()

s.push()
s.add(~((~ F) | (~ P)))
if s.check() != unsat:
    print('Counter-example found for PORT-03:', s.model())
else:
    print('PORT-03: PASS')
s.pop()
