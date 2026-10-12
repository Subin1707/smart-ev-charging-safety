from z3 import *

def check_bmc_overheat(is_vulnerable=False):
    solver = Solver()
    temp = Real('temp')
    is_charging = Bool('is_charging')
    
    if is_vulnerable:
        # Lá»—i: Tiáº¿p tá»¥c sáº¡c khi nhiá»‡t Ä‘á»™ = 62 C
        rule = Implies(temp >= 60.0, is_charging == True)
    else:
        # An toĂ n: Ngáº¯t sáº¡c ngay láº­p tá»©c khi temp >= 60.0
        rule = Implies(temp >= 60.0, is_charging == False)
        
    solver.add(rule)
    # TĂ¬m vi pháº¡m: temp >= 60.0 mĂ  váº«n is_charging == True
    solver.add(temp >= 60.0, is_charging == True)
    
    if solver.check() == sat:
        m = solver.model()
        print(f"  -> COUNTEREXAMPLE FOUND: Temp = {m[temp]} C nhung Charging = True")
        return False
    else:
        print("  -> NO COUNTEREXAMPLE FOUND (Proved: Temp >= 60C -> Charging OFF)")
        return True

if __name__ == '__main__':
    print("==================================================")
    print(" BMC: KIEM CHUNG QUY TAC QUA NHIET (SR03)")
    print("==================================================")
    print("\n[1] Phien ban Vulnerable:")
    check_bmc_overheat(is_vulnerable=True)
    print("\n[2] Phien ban Secure:")
    check_bmc_overheat(is_vulnerable=False)
