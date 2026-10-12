# Mode: mapping-aware harness scaffold; production objects are not guessed. 
# soc -> xe->pin.soc (src/vehicle/pin.c) 
from z3 import Int, Real, Solver

soc = Real("soc")

s = Solver()
s.add(soc >= 0)
s.add(soc < 0)
s.add(soc > 100)

print(s.check())
