"""
MĂ´ hĂ¬nh Kripke cáº¥u trĂºc há»‡ thá»‘ng sáº¡c xe Ä‘iá»‡n thĂ´ng minh.
Kripke Structure M = (S, S0, R, L)
S: Táº­p cĂ¡c tráº¡ng thĂ¡i {IDLE, CONNECTED, AUTHENTICATED, READY, CHARGING, STOPPED, FAULT}
S0: Tráº¡ng thĂ¡i ban Ä‘áº§u {IDLE}
R: Quan há»‡ chuyá»ƒn tráº¡ng thĂ¡i
L: HĂ m gĂ¡n nhĂ£n vá»‹ tá»« nguyĂªn tá»­
"""

STATES = ["IDLE", "CONNECTED", "AUTHENTICATED", "READY", "CHARGING", "STOPPED", "FAULT"]

# Quan há»‡ chuyá»ƒn Ä‘á»•i an toĂ n (Secure Transitions)
TRANSITIONS_SECURE = {
    "IDLE": ["CONNECTED"],
    "CONNECTED": ["AUTHENTICATED", "IDLE"],
    "AUTHENTICATED": ["READY", "IDLE"],
    "READY": ["CHARGING", "IDLE"],
    "CHARGING": ["STOPPED", "FAULT"],
    "STOPPED": ["IDLE", "READY"],
    "FAULT": ["IDLE"]
}

# Quan há»‡ chuyá»ƒn Ä‘á»•i lá»—i (Vulnerable Transitions: cho phĂ©p Ä‘i táº¯t CONNECTED -> CHARGING)
TRANSITIONS_VULNERABLE = {
    "IDLE": ["CONNECTED"],
    "CONNECTED": ["AUTHENTICATED", "CHARGING", "IDLE"], # Lá»–I: Auth bypass
    "AUTHENTICATED": ["READY", "IDLE"],
    "READY": ["CHARGING", "IDLE"],
    "CHARGING": ["STOPPED", "FAULT"],
    "STOPPED": ["IDLE", "READY"],
    "FAULT": ["IDLE"]
}

LABELS = {
    "IDLE": {"is_connected": False, "is_authenticated": False, "is_charging": False, "is_fault": False},
    "CONNECTED": {"is_connected": True, "is_authenticated": False, "is_charging": False, "is_fault": False},
    "AUTHENTICATED": {"is_connected": True, "is_authenticated": True, "is_charging": False, "is_fault": False},
    "READY": {"is_connected": True, "is_authenticated": True, "is_charging": False, "is_fault": False},
    "CHARGING": {"is_connected": True, "is_authenticated": True, "is_charging": True, "is_fault": False},
    "STOPPED": {"is_connected": True, "is_authenticated": True, "is_charging": False, "is_fault": False},
    "FAULT": {"is_connected": True, "is_authenticated": False, "is_charging": False, "is_fault": True}
}

if __name__ == '__main__':
    print("MĂ´ hĂ¬nh Kripke Há»‡ thá»‘ng Sáº¡c ThĂ´ng Minh:")
    print("Táº­p tráº¡ng thĂ¡i S:", STATES)
    print("Tráº¡ng thĂ¡i khá»Ÿi Ä‘áº§u S0: ['IDLE']")
