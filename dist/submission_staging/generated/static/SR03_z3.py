# Mode: mapping-aware harness scaffold; production objects are not guessed. 
# charging -> . (src/safety/giam_sat_an_toan.c) 
# power -> cong->cong_suat_kw (src/safety/giam_sat_an_toan.c) 
# state -> cong->trang_thai (src/safety/giam_sat_an_toan.c) 
# temperature -> xe->pin.nhiet_do (src/safety/quy_tac_an_toan.c) 
from z3 import Bool, Int, Real, Solver, And, Or, Not

FAULT = 1
charging = Bool("charging")
power = Real("power")
state = Int("state")
temperature = Real("temperature")

s = Solver()
s.add(power >= 0)
s.add(temperature >= 0)
s.add(And(temperature >= 60, charging == True))
s.add(Not(And(power == 0, state == FAULT)))

print(s.check())
