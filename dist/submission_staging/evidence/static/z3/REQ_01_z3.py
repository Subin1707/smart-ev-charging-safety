# Mode: mapping-aware harness scaffold; production objects are not guessed. 
# total_power -> tram->cong_suat_hien_tai (src/station/tram_sac.c) 
from z3 import Int, Real, Solver

total_power = Real("total_power")

s = Solver()
s.add(total_power >= 0)
s.add(total_power > 100)

print(s.check())
