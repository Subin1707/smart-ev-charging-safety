# Mode: mapping-aware harness scaffold; production objects are not guessed. 
# port_power -> tram->cong[port_index].cong_suat_kw (src/station/quan_ly_cong_suat.c) 
# total_power -> tram->cong_suat_hien_tai (src/station/tram_sac.c) 
from z3 import Bool, Int, Real, Solver, And, Or, Not


port_power = Real("port_power")
total_power = Real("total_power")

s = Solver()
s.add(port_power >= 0)
s.add(total_power >= 0)
s.add(Not(And(total_power <= 100, port_power <= 22)))

print(s.check())
