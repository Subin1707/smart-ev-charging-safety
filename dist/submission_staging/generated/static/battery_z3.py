# Generated from specification/battery.json
from z3 import Bool, Int, Solver, unsat

# enum SOC
SOC_INVALID = 0
SOC_OK = 1
SOC_FULL = 2
SOC = Int('SOC')
# enum TEMP
TEMP_INVALID = 0
TEMP_SAFE = 1
TEMP_OVERHEAT = 2
TEMP = Int('TEMP')

s = Solver()
s.add(SOC >= 0, SOC < 3)
s.add(TEMP >= 0, TEMP < 3)

s.push()
s.add(~(SOC != SOC_INVALID))
if s.check() != unsat:
    print('Counter-example found for BAT-01:', s.model())
else:
    print('BAT-01: PASS')
s.pop()

s.push()
s.add(~(SOC != SOC_FULL))
if s.check() != unsat:
    print('Counter-example found for BAT-02:', s.model())
else:
    print('BAT-02: PASS')
s.pop()

s.push()
s.add(~(TEMP != TEMP_OVERHEAT))
if s.check() != unsat:
    print('Counter-example found for BAT-03:', s.model())
else:
    print('BAT-03: PASS')
s.pop()

s.push()
s.add(~(SOC != SOC_INVALID))
if s.check() != unsat:
    print('Counter-example found for BAT-04:', s.model())
else:
    print('BAT-04: PASS')
s.pop()

s.push()
s.add(~(TEMP != TEMP_INVALID))
if s.check() != unsat:
    print('Counter-example found for BAT-05:', s.model())
else:
    print('BAT-05: PASS')
s.pop()
