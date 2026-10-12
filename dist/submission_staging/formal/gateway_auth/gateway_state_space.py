from itertools import product


VARIABLES = [
    "connected",
    "token_valid",
    "authenticated",
    "start_request",
    "safety_ok",
    "emergency",
]

SYMBOLS = ["C", "T", "A", "R", "S", "E"]


def valid_state(C, T, A, R, S, E):
    # GA-C01
    # Authenticated -> Connected
    if A and not C:
        return False

    # GA-C02
    # Authenticated -> Token Valid
    if A and not T:
        return False

    return True


def bits(values):
    return "".join(str(value) for value in values)


def main():
    total = 0
    valid = []
    invalid = []

    for values in product([0, 1], repeat=len(VARIABLES)):
        total += 1
        if valid_state(*values):
            valid.append(values)
        else:
            invalid.append(values)

    print("Gateway Authentication state-space analysis")
    print("Variables:", " ".join(SYMBOLS))
    print(f"Candidate states: {total}")
    print(f"Valid states after GA-C01 and GA-C02: {len(valid)}")
    print(f"Invalid states removed: {len(invalid)}")
    print()

    print("Valid states:")
    for state in valid:
        print(bits(state))

    print()
    print("Invalid states:")
    for state in invalid:
        print(bits(state))


if __name__ == "__main__":
    main()
