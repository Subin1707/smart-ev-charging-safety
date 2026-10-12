# Mode: mapping-aware harness scaffold; production objects are not guessed. 
# soc -> xe->pin.soc (src/vehicle/pin.c) 
from z3 import Bool, Int, Real, Solver, And, Or, Not


soc = Real("soc")

s = Solver()
s.add(soc >= 0)
s.add(Not(And(soc >= 0, soc <= 100)))

print(s.check())
