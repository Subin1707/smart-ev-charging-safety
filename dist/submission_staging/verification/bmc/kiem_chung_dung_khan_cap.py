from z3 import *

def check_bmc_emergency(is_vulnerable=False):
    solver = Solver()
    emergency = Bool('emergency')
    powers = [Real(f'p_{i}') for i in range(5)]
    
    for p in powers:
        solver.add(p >= 0.0)
        
    total_power = Sum(powers)
    
    if is_vulnerable:
        rule = Implies(emergency, total_power > 0.0) # Lá»—i khĂ´ng cáº¯t nguá»“n
    else:
        rule = Implies(emergency, total_power == 0.0) # An toĂ n cáº¯t toĂ n bá»™ vá» 0
        
    solver.add(rule)
    solver.add(emergency == True, total_power > 0.0) # TĂ¬m vi pháº¡m
    
    if solver.check() == sat:
        m = solver.model()
        print(f"  -> COUNTEREXAMPLE FOUND: Emergency = True nhung Total Power = {m.eval(total_power)} kW > 0")
        return False
    else:
        print("  -> NO COUNTEREXAMPLE FOUND (Proved: Emergency -> Total Power == 0)")
        return True

if __name__ == '__main__':
    print("==================================================")
    print(" BMC: KIEM CHUNG DUNG KHAN CAP (SR05)")
    print("==================================================")
    print("\n[1] Phien ban Vulnerable:")
    check_bmc_emergency(is_vulnerable=True)
    print("\n[2] Phien ban Secure:")
    check_bmc_emergency(is_vulnerable=False)
