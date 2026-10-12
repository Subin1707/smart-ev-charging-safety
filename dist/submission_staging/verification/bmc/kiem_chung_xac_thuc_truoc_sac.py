import sys
from z3 import *

def check_bmc_auth(is_vulnerable=False, k=5):
    """
    Kiá»ƒm chá»©ng BMC cho thuá»™c tĂ­nh: CHARGING -> AUTHENTICATED
    Vá»›i k bÆ°á»›c chuyá»ƒn tráº¡ng thĂ¡i.
    """
    solver = Solver()
    
    # Äá»‹nh nghÄ©a cĂ¡c tráº¡ng thĂ¡i dáº¡ng Int: 0: IDLE, 1: CONNECTED, 2: AUTHENTICATED, 3: READY, 4: CHARGING, 5: STOPPED, 6: FAULT
    IDLE, CONNECTED, AUTHENTICATED, READY, CHARGING, STOPPED, FAULT = 0, 1, 2, 3, 4, 5, 6
    
    state = [Int(f'state_{i}') for i in range(k + 1)]
    is_auth = [Bool(f'is_auth_{i}') for i in range(k + 1)]
    
    # Khá»Ÿi Ä‘áº§u táº¡i IDLE
    solver.add(state[0] == IDLE)
    solver.add(is_auth[0] == False)
    
    # Luáº­t chuyá»ƒn Ä‘á»•i tráº¡ng thĂ¡i táº¡i tá»«ng bÆ°á»›c
    for t in range(k):
        # Miá»n giĂ¡ trá»‹
        solver.add(state[t] >= 0, state[t] <= 6)
        solver.add(state[t+1] >= 0, state[t+1] <= 6)
        
        # Chuyá»ƒn Ä‘á»•i tráº¡ng thĂ¡i
        if is_vulnerable:
            # Báº£n lá»—i cho phĂ©p CONNECTED -> CHARGING mĂ  khĂ´ng qua AUTHENTICATED
            valid_transition = Or(
                And(state[t] == IDLE, state[t+1] == CONNECTED, is_auth[t+1] == False),
                And(state[t] == CONNECTED, state[t+1] == CHARGING, is_auth[t+1] == False), # Lá»–I Bá» QUA XĂC THá»°C!
                And(state[t] == CONNECTED, state[t+1] == AUTHENTICATED, is_auth[t+1] == True),
                And(state[t] == AUTHENTICATED, state[t+1] == READY, is_auth[t+1] == is_auth[t]),
                And(state[t] == READY, state[t+1] == CHARGING, is_auth[t+1] == is_auth[t]),
                And(state[t] == CHARGING, state[t+1] == STOPPED, is_auth[t+1] == is_auth[t]),
                And(state[t] == CHARGING, state[t+1] == FAULT, is_auth[t+1] == False)
            )
        else:
            # Báº£n an toĂ n báº¯t buá»™c pháº£i qua AUTHENTICATED vĂ  READY
            valid_transition = Or(
                And(state[t] == IDLE, state[t+1] == CONNECTED, is_auth[t+1] == False),
                And(state[t] == CONNECTED, state[t+1] == AUTHENTICATED, is_auth[t+1] == True),
                And(state[t] == AUTHENTICATED, state[t+1] == READY, is_auth[t+1] == True),
                And(state[t] == READY, state[t+1] == CHARGING, is_auth[t+1] == True),
                And(state[t] == CHARGING, state[t+1] == STOPPED, is_auth[t+1] == True),
                And(state[t] == CHARGING, state[t+1] == FAULT, is_auth[t+1] == False)
            )
        solver.add(valid_transition)
        
    # TĂ¬m vi pháº¡m: Tá»“n táº¡i bÆ°á»›c t mĂ  state[t] == CHARGING nhÆ°ng is_auth[t] == False
    violation = Or([And(state[t] == CHARGING, is_auth[t] == False) for t in range(1, k + 1)])
    solver.add(violation)
    
    state_names = {0: "IDLE", 1: "CONNECTED", 2: "AUTHENTICATED", 3: "READY", 4: "CHARGING", 5: "STOPPED", 6: "FAULT"}
    
    if solver.check() == sat:
        m = solver.model()
        trace = []
        for t in range(k + 1):
            st_val = m[state[t]].as_long()
            au_val = is_true(m[is_auth[t]])
            trace.append(f"{state_names[st_val]} (auth={au_val})")
            if st_val == CHARGING and not au_val:
                break
        print("  -> KET QUA: COUNTEREXAMPLE FOUND!")
        print("  -> Trace vi pham:", " -> ".join(trace))
        return False
    else:
        print("  -> KET QUA: NO COUNTEREXAMPLE FOUND (Proved safe within bound k)")
        return True

if __name__ == '__main__':
    print("==================================================")
    print(" BMC: KIEM CHUNG THUOC TINH CHARGING -> AUTH")
    print("==================================================")
    print("\n[1] Kiem chung phien ban VULNERABLE (co loi auth bypass):")
    res_vuln = check_bmc_auth(is_vulnerable=True, k=5)
    
    print("\n[2] Kiem chung phien ban SECURE (da fix):")
    res_sec = check_bmc_auth(is_vulnerable=False, k=5)
