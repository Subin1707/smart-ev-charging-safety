# Generated from specification/charging.json
from z3 import Bool, Int, Solver, unsat

C = Bool('C')
A = Bool('A')
B = Bool('B')
T = Bool('T')
P = Bool('P')
E = Bool('E')
F = Bool('F')

s = Solver()

s.push()
s.add(~(C & A & B & T & P & (~ E) & (~ F)))
if s.check() != unsat:
    print('Counter-example found for CHG-01:', s.model())
else:
    print('CHG-01: PASS')
s.pop()
