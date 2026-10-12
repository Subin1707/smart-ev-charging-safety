from z3 import *

def check_power_boundary():
    solver = Solver()
    p = [Real(f'p_{i}') for i in range(5)]
    
    # Thuáº­t toĂ¡n an toĂ n chia Ä‘á»u: má»—i xe nháº­n tá»‘i Ä‘a 20 kW
    for p_i in p:
        solver.add(p_i >= 0.0, p_i <= 20.0)
        
    total = Sum(p)
    # TĂ¬m vi pháº¡m tá»•ng cĂ´ng suáº¥t > 100 kW
    solver.add(total > 100.0)
    
    if solver.check() == sat:
        print("  -> COUNTEREXAMPLE FOUND")
    else:
        print("  -> NO COUNTEREXAMPLE FOUND (Proved: Sum(P_i) <= 100 kW luon thoa man)")

if __name__ == '__main__':
    print("==================================================")
    print(" BMC: KIEM CHUNG GIOI HAN CONG SUAT TRAM (SR10)")
    print("==================================================")
    check_power_boundary()
