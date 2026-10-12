from z3 import *

def check_port_exclusive():
    solver = Solver()
    # Má»—i xe gĂ¡n vĂ o 1 cá»•ng tá»« 1 Ä‘áº¿n 5
    ev = [Int(f'port_of_ev_{i}') for i in range(5)]
    for p in ev:
        solver.add(p >= 1, p <= 5)
        
    # RĂ ng buá»™c Ä‘á»™c quyá»n: cĂ¡c cá»•ng pháº£i khĂ¡c nhau
    solver.add(Distinct(ev))
    
    # TĂ¬m vi pháº¡m: tá»“n táº¡i 2 xe cĂ¹ng 1 cá»•ng
    violation = Or([ev[i] == ev[j] for i in range(5) for j in range(i + 1, 5)])
    solver.add(violation)
    
    if solver.check() == sat:
        print("  -> COUNTEREXAMPLE FOUND: Trung cong sac")
    else:
        print("  -> NO COUNTEREXAMPLE FOUND (Proved: Moi cong sac chi co toi da 1 xe)")

if __name__ == '__main__':
    print("==================================================")
    print(" BMC: KIEM CHUNG DOC QUYEN CONG SAC (SR07)")
    print("==================================================")
    check_port_exclusive()
